import asyncio
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from config import settings

class MCPClient:
    def __init__(self, host=settings.MCP_HOST, port=settings.MCP_PORT):
        self.host = host
        self.port = port

    async def send_request(self, request_data: dict):
        try:
            reader, writer = await asyncio.open_connection(self.host, self.port)
        except ConnectionRefusedError:
            logger.error(f"Connection refused. Is the server running at {self.host}:{self.port}?")
            return {'status': 'error', 'message': 'Connection refused.'}

        message = json.dumps(request_data)
        logger.info(f"Sending: {message}")

        writer.write(message.encode())
        await writer.drain()

        data = await reader.read(4096)
        response = data.decode()
        logger.info(f"Received: {response}")

        logger.info("Closing the connection")
        writer.close()
        await writer.wait_closed()

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.error("Failed to decode server response as JSON.")
            return {'status': 'error', 'message': 'Invalid JSON response from server.'}
