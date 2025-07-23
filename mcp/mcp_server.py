import sys
import os
import asyncio
import json
import logging

# Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import DatabaseManager
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPServer:
    def __init__(self, host=settings.MCP_HOST, port=settings.MCP_PORT):
        self.host = host
        self.port = port
        self.db_manager = DatabaseManager()
        # Connect to the database and initialize schema
        self.db_manager.initialize_database()

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        logger.info(f"New connection from {addr}")

        try:
            while True:
                data = await reader.read(4096)
                if not data:
                    logger.info(f"Connection from {addr} closed.")
                    break

                message = data.decode()
                logger.info(f"Received from {addr}: {message}")

                try:
                    request = json.loads(message)
                    response = await self.process_request(request)
                except json.JSONDecodeError:
                    response = {'status': 'error', 'message': 'Invalid JSON format.'}
                except Exception as e:
                    response = {'status': 'error', 'message': str(e)}

                writer.write(json.dumps(response).encode())
                await writer.drain()

        except asyncio.CancelledError:
            logger.info(f"Connection from {addr} cancelled.")
        except Exception as e:
            logger.error(f"Error with connection {addr}: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    async def process_request(self, request: dict):
        module = request.get('module')
        command = request.get('command')
        payload = request.get('payload', {})

        if module != 'database':
            return {'status': 'error', 'message': f'Unknown module: {module}'}

        if not hasattr(self.db_manager, command):
            return {'status': 'error', 'message': f'Unknown command: {command}'}

        try:
            method = getattr(self.db_manager, command)
            result = method(**payload)
            return {'status': 'success', 'data': result}
        except Exception as e:
            logger.error(f"Error processing command '{command}': {e}")
            return {'status': 'error', 'message': f"Error executing command: {e}"}

    async def start(self):
        server = await asyncio.start_server(
            self.handle_client, self.host, self.port)

        addr = server.sockets[0].getsockname()
        logger.info(f'MCP Server listening on {addr}')

        async with server:
            await server.serve_forever()

    async def shutdown(self):
        logger.info("Shutting down server...")
        self.db_manager.disconnect()
