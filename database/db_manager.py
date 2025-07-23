import sqlite3
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from config import settings

class DatabaseManager:
    def __init__(self, db_path=settings.DB_PATH):
        self.db_path = db_path
        self.conn = None
        self.logger = logging.getLogger(self.__class__.__name__)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.logger.info(f"Successfully connected to database at {self.db_path}")
        except sqlite3.Error as e:
            self.logger.error(f"Error connecting to database: {e}")
            raise

    def disconnect(self):
        if self.conn:
            self.conn.close()
            self.logger.info("Database connection closed.")

    def initialize_database(self, schema_path=settings.SCHEMA_PATH):
        if self.conn is None:
            self.connect()

        if not os.path.exists(schema_path):
            self.logger.error(f"Schema file not found at {schema_path}")
            return

        with open(schema_path, 'r') as f:
            schema = f.read()

        try:
            cursor = self.conn.cursor()
            cursor.executescript(schema)
            self.conn.commit()
            self.logger.info("Database initialized successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Error initializing database: {e}")
            raise

    def create_usage_log(self, log_data: dict):
        columns = ', '.join(log_data.keys())
        placeholders = ', '.join('?' for _ in log_data)
        sql = f"INSERT INTO usage_data ({columns}) VALUES ({placeholders})"
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute(sql, list(log_data.values()))
                self.conn.commit()
                self.logger.info(f"New usage log created with ID: {cursor.lastrowid}")
                return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            self.logger.error(f"Integrity error creating usage log: {e}")
            return None
        except sqlite3.Error as e:
            self.logger.error(f"Database error creating usage log: {e}")
            return None

    def get_usage_logs(self, filters: dict = None):
        sql = "SELECT * FROM usage_data"
        params = []
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f"{key} = ?")
                params.append(value)
            sql += " WHERE " + " AND ".join(conditions)

        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                self.logger.info(f"Retrieved {len(rows)} usage logs.")
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving usage logs: {e}")
            return []

    def update_usage_log(self, log_id: int, updates: dict):
        if not updates:
            self.logger.warning("No update data provided.")
            return False

        columns = ', '.join(f"{key} = ?" for key in updates)
        sql = f"UPDATE usage_data SET {columns} WHERE id = ?"
        params = list(updates.values()) + [log_id]

        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute(sql, params)
                self.conn.commit()
                if cursor.rowcount == 0:
                    self.logger.warning(f"No usage log found with ID: {log_id}")
                    return False
                self.logger.info(f"Usage log with ID {log_id} updated successfully.")
                return True
        except sqlite3.Error as e:
            self.logger.error(f"Error updating usage log {log_id}: {e}")
            return False

    def delete_usage_log(self, log_id: int):
        sql = "DELETE FROM usage_data WHERE id = ?"
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute(sql, (log_id,))
                self.conn.commit()
                if cursor.rowcount == 0:
                    self.logger.warning(f"No usage log found with ID: {log_id} to delete.")
                    return False
                self.logger.info(f"Usage log with ID {log_id} deleted successfully.")
                return True
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting usage log {log_id}: {e}")
            return False
