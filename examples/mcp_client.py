import asyncio
import json
import logging
import uuid
from typing import Dict, Any, Optional, List
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from config import settings

# MCP Protocol Constants
MCP_PROTOCOL_VERSION = "2024-11-05"

class MCPClient:
    """
    Model Context Protocol (MCP) Client Implementation.
    
    This class provides a comprehensive client interface for communicating with MCP servers
    following the MCP 2024-11-05 specification. It handles connection management, protocol
    handshaking, tool calling, and resource access through JSON-RPC 2.0 messaging.
    
    The client supports:
    - Async TCP connection management
    - MCP protocol initialization and handshaking
    - Tool discovery and execution
    - Resource discovery and reading
    - Comprehensive error handling and logging
    - Convenience methods for database operations
    
    Attributes:
        host (str): Server hostname or IP address
        port (int): Server port number
        reader (asyncio.StreamReader): TCP stream reader for receiving data
        writer (asyncio.StreamWriter): TCP stream writer for sending data
        initialized (bool): Whether MCP handshake has been completed
        server_capabilities (dict): Server capabilities received during handshake
        available_tools (list): List of tools exposed by the server
        available_resources (list): List of resources exposed by the server
    
    Example:
        async with MCPClient() as client:
            if await client.initialize():
                result = await client.create_usage_log(log_data)
    """
    
    def __init__(self, host=settings.MCP_HOST, port=settings.MCP_PORT):
        """
        Initialize MCP client with connection parameters.
        
        Args:
            host (str): Server hostname or IP address. Defaults to settings.MCP_HOST
            port (int): Server port number. Defaults to settings.MCP_PORT
        """
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None
        self.initialized = False
        self.server_capabilities = {}
        self.available_tools = []
        self.available_resources = []

    async def connect(self) -> bool:
        """
        Establish TCP connection to MCP server.
        
        Creates an asyncio TCP connection to the server using the configured
        host and port. Handles common connection errors gracefully.
        
        Returns:
            bool: True if connection successful, False otherwise
            
        Raises:
            ConnectionRefusedError: If server is not running or refusing connections
            Exception: For other network-related errors
            
        Example:
            if await client.connect():
                print("Connected successfully!")
        """
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
        """
        Close TCP connection to MCP server.
        
        Properly closes the TCP connection and waits for the connection to be
        fully closed. Safe to call multiple times.
        
        Example:
            await client.disconnect()
        """
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
            logger.info("Disconnected from MCP server")

    async def initialize(self) -> bool:
        """
        Initialize MCP session with protocol handshake.
        
        Performs the MCP initialization sequence according to the MCP 2024-11-05
        specification. This includes:
        1. Establishing TCP connection (if not already connected)
        2. Sending initialize request with client capabilities
        3. Receiving server capabilities
        4. Loading available tools and resources
        
        The initialization must be completed before calling any other MCP methods.
        
        Returns:
            bool: True if initialization successful, False otherwise
            
        Example:
            if await client.initialize():
                # Client is ready for tool calls and resource access
                tools = client.available_tools
        """
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
        """
        Send JSON-RPC request to server and return response.
        
        Handles the low-level communication with the MCP server, including:
        - JSON serialization of requests
        - TCP transmission
        - Response reading and JSON deserialization
        - Error handling for network and parsing issues
        
        Args:
            request (Dict[str, Any]): JSON-RPC request dictionary containing
                                     method, params, id, and jsonrpc fields
        
        Returns:
            Optional[Dict[str, Any]]: Parsed JSON response from server, or None on error
            
        Raises:
            json.JSONDecodeError: If server response is not valid JSON
            Exception: For network or other communication errors
            
        Example:
            request = {
                "jsonrpc": "2.0",
                "id": "123",
                "method": "tools/list"
            }
            response = await client.send_request(request)
        """
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
        """
        Load available tools from server.
        
        Queries the server for all available tools using the tools/list method.
        Tools are cached in the available_tools attribute for later reference.
        
        Returns:
            List[Dict[str, Any]]: List of tool definitions, each containing
                                 name, description, and inputSchema
        
        Example:
            tools = await client.load_tools()
            for tool in tools:
                print(f"Tool: {tool['name']} - {tool['description']}")
        """
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
        """
        Load available resources from server.
        
        Queries the server for all available resources using the resources/list method.
        Resources are cached in the available_resources attribute for later reference.
        
        Returns:
            List[Dict[str, Any]]: List of resource definitions, each containing
                                 uri, name, description, and mimeType
        
        Example:
            resources = await client.load_resources()
            for resource in resources:
                print(f"Resource: {resource['name']} at {resource['uri']}")
        """
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
        """
        Call a specific tool on the server.
        
        Executes a tool on the server using the tools/call method. The tool must
        be available in the server's tool list (loaded during initialization).
        
        Args:
            tool_name (str): Name of the tool to execute
            arguments (Dict[str, Any]): Arguments to pass to the tool
        
        Returns:
            Optional[Dict[str, Any]]: Tool execution result, or None on error
            
        Raises:
            ValueError: If client is not initialized
            
        Example:
            result = await client.call_tool("create_usage_log", {
                "user": "john_doe",
                "application_name": "chrome.exe",
                "duration_seconds": 3600
            })
        """
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
        """
        Read a resource from the server.
        
        Accesses a server resource using the resources/read method. Resources
        can contain various types of data (text, binary, etc.) identified by URI.
        
        Args:
            uri (str): URI of the resource to read (e.g., "usage://stats")
        
        Returns:
            Optional[Dict[str, Any]]: Resource content and metadata, or None on error
            
        Raises:
            ValueError: If client is not initialized
            
        Example:
            stats = await client.read_resource("usage://stats")
            if stats and "contents" in stats:
                content = stats["contents"][0]["text"]
        """
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
        """
        Ping server to check connectivity.
        
        Sends a ping request to verify that the server is responsive.
        Useful for health checks and connection validation.
        
        Returns:
            bool: True if server responds to ping, False otherwise
            
        Example:
            if await client.ping():
                print("Server is responsive")
            else:
                print("Server not responding")
        """
        request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "ping"
        }

        response = await self.send_request(request)
        return response is not None and "result" in response

    # Convenience methods for database operations
    async def create_usage_log(self, log_data: Dict[str, Any]) -> Optional[int]:
        """
        Create a new usage log entry.
        
        High-level convenience method for creating usage logs. Handles the
        tool call formatting and response parsing automatically.
        
        Args:
            log_data (Dict[str, Any]): Usage log data containing required fields:
                - monitor_app_version (str): Version of monitoring tool
                - platform (str): Operating system (Windows, macOS, Linux, etc.)
                - user (str): Username or device identifier
                - application_name (str): Application name (e.g., chrome.exe)
                - application_version (str): Application version
                - log_date (str): Date in YYYY-MM-DD format
                - legacy_app (bool): Whether application is legacy
                - duration_seconds (int): Usage duration in seconds
        
        Returns:
            Optional[int]: ID of created log entry, or None on failure
            
        Example:
            log_id = await client.create_usage_log({
                "monitor_app_version": "1.0.0",
                "platform": "Windows",
                "user": "john_doe",
                "application_name": "chrome.exe",
                "application_version": "120.0.0",
                "log_date": "2025-07-27",
                "legacy_app": False,
                "duration_seconds": 3600
            })
        """
        result = await self.call_tool("create_usage_log", log_data)
        if result and "content" in result:
            content = json.loads(result["content"][0]["text"])
            return content.get("result")
        return None

    async def get_usage_logs(self, filters: Dict[str, Any] = None) -> Optional[List[Dict[str, Any]]]:
        """
        Get usage logs with optional filters.
        
        Retrieves usage logs from the database. Supports filtering by various
        criteria to narrow down results.
        
        Args:
            filters (Dict[str, Any], optional): Filter criteria:
                - application_name (str): Filter by application name
                - user (str): Filter by user
                - platform (str): Filter by platform
                - legacy_app (bool): Filter by legacy status
                - log_date (str): Filter by specific date
        
        Returns:
            Optional[List[Dict[str, Any]]]: List of usage log dictionaries,
                                           or None on failure
        
        Example:
            # Get all logs
            all_logs = await client.get_usage_logs()
            
            # Get logs for specific user and application
            filtered_logs = await client.get_usage_logs({
                "user": "john_doe",
                "application_name": "chrome.exe"
            })
        """
        arguments = {"filters": filters} if filters else {}
        result = await self.call_tool("get_usage_logs", arguments)
        if result and "content" in result:
            content = json.loads(result["content"][0]["text"])
            return content.get("result")
        return None

    async def update_usage_log(self, log_id: int, updates: Dict[str, Any]) -> Optional[bool]:
        """
        Update an existing usage log.
        
        Modifies specific fields of an existing usage log entry. Only the
        fields provided in the updates dictionary will be changed.
        
        Args:
            log_id (int): ID of the log entry to update
            updates (Dict[str, Any]): Fields to update with new values
        
        Returns:
            Optional[bool]: True if update successful, False if failed or
                           log not found, None on error
        
        Example:
            success = await client.update_usage_log(123, {
                "duration_seconds": 7200,
                "application_version": "121.0.0"
            })
        """
        result = await self.call_tool("update_usage_log", {"log_id": log_id, "updates": updates})
        if result and "content" in result:
            content = json.loads(result["content"][0]["text"])
            return content.get("result")
        return None

    async def delete_usage_log(self, log_id: int) -> Optional[bool]:
        """
        Delete a usage log entry.
        
        Permanently removes a usage log entry from the database.
        This operation cannot be undone.
        
        Args:
            log_id (int): ID of the log entry to delete
        
        Returns:
            Optional[bool]: True if deletion successful, False if log not found,
                           None on error
        
        Warning:
            This operation is irreversible. Ensure you have backups if needed.
        
        Example:
            success = await client.delete_usage_log(123)
            if success:
                print("Log deleted successfully")
        """
        result = await self.call_tool("delete_usage_log", {"log_id": log_id})
        if result and "content" in result:
            content = json.loads(result["content"][0]["text"])
            return content.get("result")
        return None

    async def get_usage_stats(self) -> Optional[Dict[str, Any]]:
        """
        Get usage statistics from the server.
        
        Retrieves comprehensive usage statistics by reading the usage stats
        resource from the server.
        
        Returns:
            Optional[Dict[str, Any]]: Dictionary containing usage statistics,
                                     or None on failure
        
        Example:
            stats = await client.get_usage_stats()
            if stats:
                print(f"Total logs: {stats['total_logs']}")
                print(f"Last updated: {stats['last_updated']}")
        """
        result = await self.read_resource("usage://stats")
        if result and "contents" in result:
            stats_text = result["contents"][0]["text"]
            return json.loads(stats_text)
        return None

    async def get_unique_users(self) -> Optional[List[str]]:
        """
        Get list of unique users from the database.
        
        Retrieves all distinct user identifiers from the usage logs,
        sorted alphabetically.
        
        Returns:
            Optional[List[str]]: List of unique user names/identifiers,
                                or None on failure
        
        Example:
            users = await client.get_unique_users()
            if users:
                print(f"Users: {', '.join(users)}")
        """
        result = await self.call_tool("get_unique_users", {})
        if result and "content" in result:
            content = json.loads(result["content"][0]["text"])
            return content.get("result")
        return None

    async def get_unique_applications(self) -> Optional[List[str]]:
        """
        Get list of unique applications from the database.
        
        Retrieves all distinct application names from the usage logs,
        sorted alphabetically.
        
        Returns:
            Optional[List[str]]: List of unique application names,
                                or None on failure
        
        Example:
            apps = await client.get_unique_applications()
            if apps:
                for app in apps:
                    print(f"Application: {app}")
        """
        result = await self.call_tool("get_unique_applications", {})
        if result and "content" in result:
            content = json.loads(result["content"][0]["text"])
            return content.get("result")
        return None

    async def get_unique_platforms(self) -> Optional[List[str]]:
        """
        Get list of unique platforms from the database.
        
        Retrieves all distinct platform names from the usage logs,
        sorted alphabetically.
        
        Returns:
            Optional[List[str]]: List of unique platform names,
                                or None on failure
        
        Example:
            platforms = await client.get_unique_platforms()
            if platforms:
                print(f"Supported platforms: {', '.join(platforms)}")
        """
        result = await self.call_tool("get_unique_platforms", {})
        if result and "content" in result:
            content = json.loads(result["content"][0]["text"])
            return content.get("result")
        return None


# Example usage
async def main():
    """
    Example client usage demonstrating MCP client capabilities.
    
    This function provides a comprehensive example of how to use the MCP client
    to interact with an application usage tracking server. It demonstrates:
    - Client initialization and connection management
    - Server health checking with ping
    - Tool discovery and listing
    - Database operations (create, read)
    - Unique value retrieval
    - Resource reading for statistics
    
    This serves as both documentation and a functional test of the client.
    
    Example:
        python mcp_client.py  # Run this file directly to execute the example
    """
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
            "monitor_app_version": "1.0.0",
            "platform": "Windows",
            "user": "test_user",
            "application_name": "chrome.exe",
            "application_version": "120.0.0",
            "log_date": "2025-07-27",
            "legacy_app": False,
            "duration_seconds": 3600
        }
        
        log_id = await client.create_usage_log(log_data)
        if log_id:
            logger.info(f"Created usage log with ID: {log_id}")

            # Get logs
            logs = await client.get_usage_logs()
            logger.info(f"Retrieved {len(logs) if logs else 0} logs")

            # Test the new unique value methods
            users = await client.get_unique_users()
            if users:
                logger.info(f"Unique users: {users}")

            applications = await client.get_unique_applications()
            if applications:
                logger.info(f"Unique applications: {applications}")

            platforms = await client.get_unique_platforms()
            if platforms:
                logger.info(f"Unique platforms: {platforms}")

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
