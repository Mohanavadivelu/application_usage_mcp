import sys
import os
import asyncio
import unittest

# Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp.mcp_client import MCPClient
from mcp.mcp_server import MCPServer
from config import settings

class TestMCPIntegration(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Use test-specific settings if needed, otherwise defaults are from config
        self.server = MCPServer()
        self.server_task = asyncio.create_task(self.server.start())
        await asyncio.sleep(0.1) # Give server time to start

    async def asyncTearDown(self):
        self.server_task.cancel()
        await self.server.shutdown()

    async def test_client_requests(self):
        client = MCPClient()

        # 1. Create
        create_request = {
            "module": "database",
            "command": "create_usage_log",
            "payload": {
                "log_data": {
                    'monitor_app_version': '1.1.0',
                    'platform': 'macOS',
                    'user': 'integration_test',
                    'application_name': 'test_app',
                    'application_version': '3.0.0',
                    'log_date': '2023-10-27T12:00:00Z',
                    'legacy_app': False,
                    'duration_seconds': 120
                }
            }
        }
        create_response = await client.send_request(create_request)
        self.assertEqual(create_response['status'], 'success')
        log_id = create_response['data']
        self.assertIsInstance(log_id, int)

        # 2. Read
        get_request = {
            "module": "database",
            "command": "get_usage_logs",
            "payload": {"filters": {"id": log_id}}
        }
        get_response = await client.send_request(get_request)
        self.assertEqual(get_response['status'], 'success')
        self.assertEqual(len(get_response['data']), 1)
        self.assertEqual(get_response['data'][0]['user'], 'integration_test')

if __name__ == '__main__':
    unittest.main()
