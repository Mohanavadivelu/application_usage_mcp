import sys
import os
import asyncio
import json
import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

# Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import DatabaseManager
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- MCP Protocol Constants ---
MCP_PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "application-usage-mcp"
SERVER_VERSION = "1.0.0"

# MCP Message Types
class MessageType:
    INITIALIZE = "initialize"
    INITIALIZED = "initialized"
    TOOLS_LIST = "tools/list"
    TOOLS_CALL = "tools/call"
    RESOURCES_LIST = "resources/list"
    RESOURCES_READ = "resources/read"
    PING = "ping"

# Error Codes
class ErrorCode:
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603

class MCPServer:
    def __init__(self, host=settings.MCP_HOST, port=settings.MCP_PORT):
        self.host = host
        self.port = port
        self.db_manager = DatabaseManager()
        self.db_manager.initialize_database()
        self.initialized = False
        self.client_capabilities = {}
        
        # Define available tools
        self.tools = {
            "create_usage_log": {
                "name": "create_usage_log",
                "description": "Create a new usage log entry for application monitoring",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "monitor_app_version": {"type": "string", "description": "Version of the monitoring tool"},
                        "platform": {"type": "string", "description": "Operating system (e.g., Windows, macOS, Android)"},
                        "user": {"type": "string", "description": "Username or device ID"},
                        "application_name": {"type": "string", "description": "Name of the application (e.g., chrome.exe)"},
                        "application_version": {"type": "string", "description": "Application version number"},
                        "log_date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                        "legacy_app": {"type": "boolean", "description": "Indicates if the application is legacy"},
                        "duration_seconds": {"type": "integer", "description": "Usage time in seconds"}
                    },
                    "required": ["monitor_app_version", "platform", "user", "application_name", 
                               "application_version", "log_date", "legacy_app", "duration_seconds"]
                }
            },
            "get_usage_logs": {
                "name": "get_usage_logs",
                "description": "Retrieve usage logs with optional filters",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "filters": {
                            "type": "object",
                            "properties": {
                                "application_name": {"type": "string"},
                                "user": {"type": "string"},
                                "platform": {"type": "string"},
                                "legacy_app": {"type": "boolean"},
                                "start_date": {"type": "string"},
                                "end_date": {"type": "string"}
                            }
                        }
                    }
                }
            },
            "update_usage_log": {
                "name": "update_usage_log",
                "description": "Update an existing usage log entry",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "log_id": {"type": "integer"},
                        "updates": {"type": "object"}
                    },
                    "required": ["log_id", "updates"]
                }
            },
            "delete_usage_log": {
                "name": "delete_usage_log",
                "description": "Delete a usage log entry",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "log_id": {"type": "integer"}
                    },
                    "required": ["log_id"]
                }
            },
            "get_unique_users": {
                "name": "get_unique_users",
                "description": "Get list of unique users from the database",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            "get_unique_applications": {
                "name": "get_unique_applications", 
                "description": "Get list of unique applications from the database",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            "get_unique_platforms": {
                "name": "get_unique_platforms",
                "description": "Get list of unique platforms from the database", 
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
        
        # Define available resources
        self.resources = {
            "usage_stats": {
                "uri": "usage://stats",
                "name": "Usage Statistics",
                "description": "Current usage statistics and metrics",
                "mimeType": "application/json"
            }
        }

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        logger.info(f"New MCP connection from {addr}")
        
        try:
            while True:
                data = await reader.read(4096)
                if not data:
                    logger.info(f"Connection from {addr} closed.")
                    break

                try:
                    # Parse JSON-RPC message
                    message = json.loads(data.decode())
                    logger.info(f"Received from {addr}: {message}")
                    
                    response = await self.process_message(message)
                    if response:
                        response_data = json.dumps(response).encode()
                        writer.write(response_data)
                        await writer.drain()
                        logger.info(f"Sent response: {response}")
                        
                except json.JSONDecodeError:
                    error_response = self.create_error_response(
                        None, ErrorCode.PARSE_ERROR, "Invalid JSON"
                    )
                    writer.write(json.dumps(error_response).encode())
                    await writer.drain()
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    error_response = self.create_error_response(
                        None, ErrorCode.INTERNAL_ERROR, str(e)
                    )
                    writer.write(json.dumps(error_response).encode())
                    await writer.drain()

        except Exception as e:
            logger.error(f"Error with connection {addr}: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
            logger.info(f"Connection {addr} closed")

    async def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process incoming MCP message according to JSON-RPC 2.0 specification"""
        message_id = message.get("id")
        method = message.get("method")
        params = message.get("params", {})
        
        if not method:
            return self.create_error_response(message_id, ErrorCode.INVALID_REQUEST, "Missing method")
        
        # Handle initialization
        if method == MessageType.INITIALIZE:
            return await self.handle_initialize(message_id, params)
        
        if not self.initialized and method != MessageType.INITIALIZE:
            return self.create_error_response(
                message_id, ErrorCode.INVALID_REQUEST, "Server not initialized"
            )
        
        # Handle other methods
        if method == MessageType.TOOLS_LIST:
            return await self.handle_tools_list(message_id)
        elif method == MessageType.TOOLS_CALL:
            return await self.handle_tools_call(message_id, params)
        elif method == MessageType.RESOURCES_LIST:
            return await self.handle_resources_list(message_id)
        elif method == MessageType.RESOURCES_READ:
            return await self.handle_resources_read(message_id, params)
        elif method == MessageType.PING:
            return await self.handle_ping(message_id)
        else:
            return self.create_error_response(
                message_id, ErrorCode.METHOD_NOT_FOUND, f"Unknown method: {method}"
            )

    async def handle_initialize(self, message_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialization handshake"""
        self.client_capabilities = params.get("capabilities", {})
        protocol_version = params.get("protocolVersion")
        
        if protocol_version != MCP_PROTOCOL_VERSION:
            return self.create_error_response(
                message_id, ErrorCode.INVALID_PARAMS, 
                f"Unsupported protocol version: {protocol_version}"
            )
        
        self.initialized = True
        logger.info("MCP initialization completed successfully")
        
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "result": {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "capabilities": {
                    "tools": {},
                    "resources": {}
                },
                "serverInfo": {
                    "name": SERVER_NAME,
                    "version": SERVER_VERSION
                }
            }
        }

    async def handle_tools_list(self, message_id: str) -> Dict[str, Any]:
        """Return list of available tools"""
        tools_list = list(self.tools.values())
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "result": {
                "tools": tools_list
            }
        }

    async def handle_tools_call(self, message_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name not in self.tools:
            return self.create_error_response(
                message_id, ErrorCode.INVALID_PARAMS, f"Unknown tool: {tool_name}"
            )
        
        try:
            # Execute the tool
            if tool_name == "create_usage_log":
                result = self.db_manager.create_usage_log(arguments)
            elif tool_name == "get_usage_logs":
                filters = arguments.get("filters", {})
                result = self.db_manager.get_usage_logs(filters)
            elif tool_name == "update_usage_log":
                log_id = arguments["log_id"]
                updates = arguments["updates"]
                result = self.db_manager.update_usage_log(log_id, updates)
            elif tool_name == "delete_usage_log":
                log_id = arguments["log_id"]
                result = self.db_manager.delete_usage_log(log_id)
            elif tool_name == "get_unique_users":
                result = self.db_manager.get_unique_users()
            elif tool_name == "get_unique_applications":
                result = self.db_manager.get_unique_applications()
            elif tool_name == "get_unique_platforms":
                result = self.db_manager.get_unique_platforms()
            else:
                return self.create_error_response(
                    message_id, ErrorCode.INTERNAL_ERROR, f"Tool implementation missing: {tool_name}"
                )
            
            return {
                "jsonrpc": "2.0",
                "id": message_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({"result": result, "tool": tool_name})
                        }
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return self.create_error_response(
                message_id, ErrorCode.INTERNAL_ERROR, f"Tool execution failed: {e}"
            )

    async def handle_resources_list(self, message_id: str) -> Dict[str, Any]:
        """Return list of available resources"""
        resources_list = list(self.resources.values())
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "result": {
                "resources": resources_list
            }
        }

    async def handle_resources_read(self, message_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read a resource"""
        uri = params.get("uri")
        
        if uri == "usage://stats":
            # Generate usage statistics
            try:
                all_logs = self.db_manager.get_usage_logs()
                stats = {
                    "total_logs": len(all_logs),
                    "last_updated": datetime.now().isoformat(),
                    "summary": "Application usage statistics"
                }
                
                return {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "result": {
                        "contents": [
                            {
                                "uri": uri,
                                "mimeType": "application/json",
                                "text": json.dumps(stats, indent=2)
                            }
                        ]
                    }
                }
            except Exception as e:
                return self.create_error_response(
                    message_id, ErrorCode.INTERNAL_ERROR, f"Failed to read resource: {e}"
                )
        else:
            return self.create_error_response(
                message_id, ErrorCode.INVALID_PARAMS, f"Unknown resource: {uri}"
            )

    async def handle_ping(self, message_id: str) -> Dict[str, Any]:
        """Handle ping request"""
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "result": {}
        }

    def create_error_response(self, message_id: Optional[str], code: int, message: str) -> Dict[str, Any]:
        """Create a JSON-RPC error response"""
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "error": {
                "code": code,
                "message": message
            }
        }

    async def start(self):
        """Start the MCP server"""
        server = await asyncio.start_server(
            self.handle_client, self.host, self.port)

        addr = server.sockets[0].getsockname()
        logger.info(f'MCP Server listening on {addr[0]}:{addr[1]}')
        logger.info(f'Protocol version: {MCP_PROTOCOL_VERSION}')
        logger.info(f'Available tools: {list(self.tools.keys())}')

        async with server:
            await server.serve_forever()

    async def shutdown(self):
        """Shutdown the MCP server"""
        logger.info("Shutting down MCP server...")
        self.db_manager.disconnect()


async def main():
    """Main entry point for the MCP server"""
    server = MCPServer()
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await server.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
