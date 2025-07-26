import sqlite3
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from config import settings

class DatabaseManager:
    """
    Database abstraction layer for managing application usage data.
    
    This class provides a clean interface for all database operations including
    CRUD operations on usage logs. It handles connection management, error handling,
    and data type conversions (especially for boolean fields in SQLite).
    
    Attributes:
        db_path (str): Path to the SQLite database file
        conn (sqlite3.Connection): Active database connection
        logger (logging.Logger): Logger instance for this class
    """
    
    def __init__(self, db_path=settings.DB_PATH):
        """
        Initialize the DatabaseManager with database path.
        
        Args:
            db_path (str): Path to SQLite database file. Defaults to settings.DB_PATH
        """
        self.db_path = db_path
        self.conn = None
        self.logger = logging.getLogger(self.__class__.__name__)

    def __enter__(self):
        """
        Context manager entry method.
        
        Automatically establishes database connection when entering a 'with' block.
        
        Returns:
            DatabaseManager: Self instance for method chaining
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit method.
        
        Automatically closes database connection when exiting a 'with' block,
        ensuring proper cleanup even if exceptions occur.
        
        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any) 
            exc_tb: Exception traceback (if any)
        """
        self.disconnect()

    def connect(self):
        """
        Establish connection to SQLite database.
        
        Sets up database connection with Row factory for easier data access.
        The Row factory allows accessing columns by name instead of index,
        making the code more readable and maintainable.
        
        Raises:
            sqlite3.Error: If database connection fails
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.logger.info(f"Successfully connected to database at {self.db_path}")
        except sqlite3.Error as e:
            self.logger.error(f"Error connecting to database: {e}")
            raise

    def disconnect(self):
        """
        Close the database connection safely.
        
        Checks if connection exists before attempting to close it.
        Logs the disconnection for tracking purposes.
        """
        if self.conn:
            self.conn.close()
            self.logger.info("Database connection closed.")

    def initialize_database(self, schema_path=settings.SCHEMA_PATH):
        """
        Initialize the database by executing the schema SQL file.
        
        This method reads the SQL schema file and executes it to create tables,
        indexes, and any other database structures. It's safe to run multiple
        times as the schema uses 'IF NOT EXISTS' clauses.
        
        Args:
            schema_path (str): Path to the SQL schema file. Defaults to settings.SCHEMA_PATH
            
        Raises:
            sqlite3.Error: If database initialization fails
            FileNotFoundError: If schema file doesn't exist
        """
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
        """
        Create a new usage log entry in the database.
        
        This method validates all required fields according to the database schema,
        handles boolean conversion for SQLite compatibility, and inserts the record.
        If a record with the same date, user, and application_name already exists,
        it will update the existing record by adding the new duration to the existing duration.
        
        Required fields in log_data:
            - monitor_app_version (str): Version of monitoring tool
            - platform (str): Operating system (Windows, macOS, Android, etc.)
            - user (str): Username or device identifier
            - application_name (str): Name of the application (e.g., chrome.exe)
            - application_version (str): Version of the application
            - log_date (str): Date in YYYY-MM-DD format
            - legacy_app (bool): Whether application is considered legacy
            - duration_seconds (int): Usage duration in seconds
        
        Args:
            log_data (dict): Dictionary containing all required usage log fields
            
        Returns:
            int: ID of the newly created or updated log entry, or None if operation failed
            
        Raises:
            sqlite3.IntegrityError: If data violates database constraints
            sqlite3.Error: For other database-related errors
        """
        # Ensure connection is available
        if self.conn is None:
            self.connect()
        
        # Validate required fields for new schema
        required_fields = ['monitor_app_version', 'platform', 'user', 'application_name', 
                          'application_version', 'log_date', 'legacy_app', 'duration_seconds']
        
        missing_fields = [field for field in required_fields if field not in log_data]
        if missing_fields:
            self.logger.error(f"Missing required fields: {missing_fields}")
            return None
            
        # Ensure legacy_app is properly formatted as boolean
        processed_data = log_data.copy()
        if 'legacy_app' in processed_data:
            # Convert to 1/0 for SQLite boolean storage
            processed_data['legacy_app'] = 1 if processed_data['legacy_app'] else 0

        try:
            with self.conn:
                cursor = self.conn.cursor()
                
                # Check if a record with same date, user, and application_name exists
                check_sql = """
                    SELECT id, duration_seconds FROM usage_data 
                    WHERE log_date = ? AND user = ? AND application_name = ?
                """
                cursor.execute(check_sql, (
                    processed_data['log_date'], 
                    processed_data['user'], 
                    processed_data['application_name']
                ))
                existing_record = cursor.fetchone()
                
                if existing_record:
                    # Update existing record by adding duration
                    existing_id = existing_record['id']
                    existing_duration = existing_record['duration_seconds']
                    new_duration = existing_duration + processed_data['duration_seconds']
                    
                    # Also update other fields from the new data
                    update_sql = """
                        UPDATE usage_data 
                        SET duration_seconds = ?, 
                            monitor_app_version = ?,
                            platform = ?,
                            application_version = ?,
                            legacy_app = ?
                        WHERE id = ?
                    """
                    cursor.execute(update_sql, (
                        new_duration,
                        processed_data['monitor_app_version'],
                        processed_data['platform'],
                        processed_data['application_version'],
                        processed_data['legacy_app'],
                        existing_id
                    ))
                    
                    self.logger.info(f"Updated existing usage log ID {existing_id}. Duration increased from {existing_duration} to {new_duration} seconds.")
                    return existing_id
                else:
                    # Insert new record
                    columns = ', '.join(processed_data.keys())
                    placeholders = ', '.join('?' for _ in processed_data)
                    sql = f"INSERT INTO usage_data ({columns}) VALUES ({placeholders})"
                    cursor.execute(sql, list(processed_data.values()))
                    
                    self.logger.info(f"New usage log created with ID: {cursor.lastrowid}")
                    return cursor.lastrowid
                    
        except sqlite3.IntegrityError as e:
            self.logger.error(f"Integrity error creating usage log: {e}")
            return None
        except sqlite3.Error as e:
            self.logger.error(f"Database error creating usage log: {e}")
            return None

    def get_usage_logs(self, filters: dict = None):
        """
        Retrieve usage logs from the database with optional filtering.
        
        This method fetches usage log records and converts them to a list of dictionaries.
        It handles boolean conversion for the legacy_app field, converting SQLite's
        1/0 storage back to Python True/False values.
        
        Args:
            filters (dict, optional): Dictionary of column-value pairs for filtering.
                                    Keys should match database column names.
                                    Example: {'application_name': 'chrome.exe', 'platform': 'Windows'}
        
        Returns:
            list[dict]: List of dictionaries representing usage log records.
                       Each dictionary contains all columns for a record.
                       Returns empty list if no records found or on error.
        
        Example:
            # Get all logs
            all_logs = db.get_usage_logs()
            
            # Get logs for specific application
            chrome_logs = db.get_usage_logs({'application_name': 'chrome.exe'})
            
            # Get logs with multiple filters
            filtered_logs = db.get_usage_logs({
                'platform': 'Windows',
                'user': 'john_doe'
            })
        """
        # Ensure connection is available
        if self.conn is None:
            self.connect()
            
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
                
                # Convert rows to dict and handle boolean conversion
                result = []
                for row in rows:
                    row_dict = dict(row)
                    # Convert legacy_app from 1/0 to True/False
                    if 'legacy_app' in row_dict:
                        row_dict['legacy_app'] = bool(row_dict['legacy_app'])
                    result.append(row_dict)
                return result
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving usage logs: {e}")
            return []

    def update_usage_log(self, log_id: int, updates: dict):
        """
        Update an existing usage log record in the database.
        
        This method modifies specific fields of an existing usage log record.
        Only the fields provided in the updates dictionary will be changed,
        leaving other fields unchanged. The method validates that update data
        is provided and handles database transaction management.
        
        Args:
            log_id (int): The unique identifier of the log record to update.
                         Must correspond to an existing record's id.
            updates (dict): Dictionary containing field-value pairs to update.
                          Keys must match valid column names in the usage_data table.
                          Cannot be empty.
                          Example: {'duration_seconds': 3600, 'application_version': '2.0.1'}
        
        Returns:
            bool: True if the update was successful and at least one row was affected,
                 False if no data provided, log_id doesn't exist, or on database error.
        
        Raises:
            sqlite3.Error: If there's a database-related error during the update operation.
        
        Example:
            # Update duration for a specific log
            success = db.update_usage_log(123, {'duration_seconds': 7200})
            
            # Update multiple fields
            success = db.update_usage_log(456, {
                'application_version': '3.0.0',
                'platform': 'Windows 11'
            })
            
            # This will return False (no data provided)
            success = db.update_usage_log(789, {})
        """
        # Ensure connection is available
        if self.conn is None:
            self.connect()
            
        # Validate that update data is provided
        if not updates:
            self.logger.warning("No update data provided.")
            return False

        # Build UPDATE query dynamically based on provided fields
        columns = ', '.join(f"{key} = ?" for key in updates)
        sql = f"UPDATE usage_data SET {columns} WHERE id = ?"
        params = list(updates.values()) + [log_id]

        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute(sql, params)
                self.conn.commit()
                
                # Check if any rows were actually updated
                if cursor.rowcount == 0:
                    self.logger.warning(f"No usage log found with ID: {log_id}")
                    return False
                    
                self.logger.info(f"Usage log with ID {log_id} updated successfully.")
                return True
        except sqlite3.Error as e:
            self.logger.error(f"Error updating usage log {log_id}: {e}")
            return False

    def delete_usage_log(self, log_id: int):
        """
        Delete a usage log record from the database.
        
        This method permanently removes a usage log record from the database
        based on its unique identifier. The operation is transactional and
        will be automatically committed if successful.
        
        Args:
            log_id (int): The unique identifier of the log record to delete.
                         Must correspond to an existing record's id.
        
        Returns:
            bool: True if the deletion was successful and a record was removed,
                 False if the log_id doesn't exist or on database error.
        
        Raises:
            sqlite3.Error: If there's a database-related error during the delete operation.
        
        Warning:
            This operation is irreversible. Once a record is deleted, it cannot be recovered
            unless you have a backup of the database.
        
        Example:
            # Delete a specific usage log
            success = db.delete_usage_log(123)
            if success:
                print("Log deleted successfully")
            else:
                print("Log not found or deletion failed")
        """
        # Ensure connection is available
        if self.conn is None:
            self.connect()
            
        sql = "DELETE FROM usage_data WHERE id = ?"
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute(sql, (log_id,))
                self.conn.commit()
                
                # Check if any rows were actually deleted
                if cursor.rowcount == 0:
                    self.logger.warning(f"No usage log found with ID: {log_id} to delete.")
                    return False
                    
                self.logger.info(f"Usage log with ID {log_id} deleted successfully.")
                return True
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting usage log {log_id}: {e}")
            return False
