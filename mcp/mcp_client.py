import asyncio
import json
import logging
import uuid
from typing import Dict, Any, Optional, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from config import settings

# MCP Protocol Constants
MCP_PROTOCOL_VERSION = "2024-11-05"

class MCPClient:
    def __init__(self, host=settings.MCP_HOST, port=settings.MCP_PORT):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None
        self.initialized = False
        self.server_capabilities = {}
        self.available_tools = []
        self.available_resources = []

    async def connect(self) -> bool:
        """Establish connection to MCP server"""
        try:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
            logger.info(f"Connected to MCP server at {self.host}:{self.port}")
            return True
        except ConnectionRefusedError:
            logger.error(f"Connection refused. Is the server running at {self.host}:{self.port}?")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to server: {e}")
            return False

    async def disconnect(self):
        """Close connection to MCP server"""
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
            logger.info("Disconnected from MCP server")

    async def initialize(self) -> bool:
        """Initialize MCP session with handshake"""
        if not self.reader or not self.writer:
            if not await self.connect():
                return False

        init_request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "initialize",
            "params": {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "capabilities": {
                    "tools": {},
                    "resources": {}
                },
                "clientInfo": {
                    "name": "application-usage-client",
                    "version": "1.0.0"
                }
            }
        }

        response = await self.send_request(init_request)
        if response and "result" in response:
            self.server_capabilities = response["result"].get("capabilities", {})
            self.initialized = True
            logger.info("MCP initialization successful")
            
            # Load available tools and resources
            await self.load_tools()
            await self.load_resources()
            return True
        else:
            logger.error("MCP initialization failed")
            return False

    async def send_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send JSON-RPC request to server and return response"""
        if not self.writer:
            logger.error("Not connected to server")
            return None

        try:
            message = json.dumps(request)
            logger.debug(f"Sending: {message}")

            self.writer.write(message.encode())
            await self.writer.drain()

            data = await self.reader.read(4096)
            if not data:
                logger.error("No response from server")
                return None

            response = json.loads(data.decode())
            logger.debug(f"Received: {response}")
            return response

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode server response: {e}")
            return None
        except Exception as e:
            logger.error(f"Error sending request: {e}")
            return None

    async def load_tools(self) -> List[Dict[str, Any]]:
        """Load available tools from server"""
        request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/list"
        }

        response = await self.send_request(request)
        if response and "result" in response:
            self.available_tools = response["result"].get("tools", [])
            logger.info(f"Loaded {len(self.available_tools)} tools")
            return self.available_tools
        return []

    async def load_resources(self) -> List[Dict[str, Any]]:
        """Load available resources from server"""
        request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "resources/list"
        }

        response = await self.send_request(request)
        if response and "result" in response:
            self.available_resources = response["result"].get("resources", [])
            logger.info(f"Loaded {len(self.available_resources)} resources")
            return self.available_resources
        return []

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call a specific tool on the server"""
        if not self.initialized:
            logger.error("Client not initialized")
            return None

        request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        response = await self.send_request(request)
        if response and "result" in response:
            return response["result"]
        elif response and "error" in response:
            logger.error(f"Tool call failed: {response['error']}")
            return None
        return None

    async def read_resource(self, uri: str) -> Optional[Dict[str, Any]]:
        """Read a resource from the server"""
        if not self.initialized:
            logger.error("Client not initialized")
            return None

        request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "resources/read",
            "params": {
                "uri": uri
            }
        }

        response = await self.send_request(request)
        if response and "result" in response:
            return response["result"]
        elif response and "error" in response:
            logger.error(f"Resource read failed: {response['error']}")
            return None
        return None

    async def ping(self) -> bool:
        """Ping server to check connectivity"""
        request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "ping"
        }

        response = await self.send_request(request)
        return response is not None and "result" in response

    # Convenience methods for database operations
    async def create_usage_log(self, log_data: Dict[str, Any]) -> Optional[int]:
        """Create a new usage log entry"""
        result = await self.call_tool("create_usage_log", log_data)
        if result and "content" in result:
            content = json.loads(result["content"][0]["text"])
            return content.get("result")
        return None

    async def get_usage_logs(self, filters: Dict[str, Any] = None) -> Optional[List[Dict[str, Any]]]:
        """Get usage logs with optional filters"""
        arguments = {"filters": filters} if filters else {}
        result = await self.call_tool("get_usage_logs", arguments)
        if result and "content" in result:
            content = json.loads(result["content"][0]["text"])
            return content.get("result")
        return None

    async def update_usage_log(self, log_id: int, updates: Dict[str, Any]) -> Optional[bool]:
        """Update an existing usage log"""
        result = await self.call_tool("update_usage_log", {"log_id": log_id, "updates": updates})
        if result and "content" in result:
            content = json.loads(result["content"][0]["text"])
            return content.get("result")
        return None

    async def delete_usage_log(self, log_id: int) -> Optional[bool]:
        """Delete a usage log entry"""
        result = await self.call_tool("delete_usage_log", {"log_id": log_id})
        if result and "content" in result:
            content = json.loads(result["content"][0]["text"])
            return content.get("result")
        return None

    async def get_usage_stats(self) -> Optional[Dict[str, Any]]:
        """Get usage statistics from the server"""
        result = await self.read_resource("usage://stats")
        if result and "contents" in result:
            stats_text = result["contents"][0]["text"]
            return json.loads(stats_text)
        return None


# Example usage
async def main():
    """Example client usage"""
    client = MCPClient()
    
    try:
        # Initialize connection
        if not await client.initialize():
            logger.error("Failed to initialize MCP client")
            return

        # Test ping
        if await client.ping():
            logger.info("Server is responsive")

        # List available tools
        tools = client.available_tools
        logger.info(f"Available tools: {[tool['name'] for tool in tools]}")

        # Test creating a usage log
        log_data = {
            "module_name": "test_module",
            "command": "test_command",
            "timestamp": "2025-07-26T10:00:00Z",
            "user_id": "test_user"
        }
        
        log_id = await client.create_usage_log(log_data)
        if log_id:
            logger.info(f"Created usage log with ID: {log_id}")

            # Get logs
            logs = await client.get_usage_logs()
            logger.info(f"Retrieved {len(logs) if logs else 0} logs")

            # Get usage statistics
            stats = await client.get_usage_stats()
            if stats:
                logger.info(f"Usage stats: {stats}")

    except Exception as e:
        logger.error(f"Client error: {e}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
