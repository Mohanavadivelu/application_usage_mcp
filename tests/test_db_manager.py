import sys
import os
import unittest

# Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import DatabaseManager

from config import settings

class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        # Override the default DB_PATH for testing
        self.db_path = 'test_usage.db'
        self.db = DatabaseManager(db_path=self.db_path)
        self.db.initialize_database(schema_path=settings.SCHEMA_PATH)

    def tearDown(self):
        self.db.disconnect()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_crud_operations(self):
        # 1. Create
        log_data = {
            'monitor_app_version': '1.0.0',
            'platform': 'Windows',
            'user': 'testuser',
            'application_name': 'test.exe',
            'application_version': '1.2.3',
            'log_date': '2023-10-27T10:00:00Z',
            'legacy_app': False,
            'duration_seconds': 300
        }
        log_id = self.db.create_usage_log(log_data)
        self.assertIsNotNone(log_id)

        # 2. Read
        logs = self.db.get_usage_logs({'id': log_id})
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]['application_name'], 'test.exe')

        # 3. Update
        update_success = self.db.update_usage_log(log_id, {'duration_seconds': 450})
        self.assertTrue(update_success)
        updated_logs = self.db.get_usage_logs({'id': log_id})
        self.assertEqual(updated_logs[0]['duration_seconds'], 450)

        # 4. Delete
        delete_success = self.db.delete_usage_log(log_id)
        self.assertTrue(delete_success)
        deleted_logs = self.db.get_usage_logs({'id': log_id})
        self.assertEqual(len(deleted_logs), 0)

if __name__ == '__main__':
    unittest.main()
