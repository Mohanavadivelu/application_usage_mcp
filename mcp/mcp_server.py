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
    """
    MCP Protocol Message Types.
    
    Defines the standard message types used in the Model Context Protocol.
    These constants ensure consistent message handling across the server.
    """
    INITIALIZE = "initialize"
    INITIALIZED = "initialized"
    TOOLS_LIST = "tools/list"
    TOOLS_CALL = "tools/call"
    RESOURCES_LIST = "resources/list"
    RESOURCES_READ = "resources/read"
    PING = "ping"

# Error Codes
class ErrorCode:
    """
    JSON-RPC 2.0 Error Codes.
    
    Standard error codes used in JSON-RPC responses to indicate
    different types of errors during request processing.
    """
    PARSE_ERROR = -32700      # Invalid JSON was received
    INVALID_REQUEST = -32600  # The JSON sent is not a valid Request object
    METHOD_NOT_FOUND = -32601 # The method does not exist / is not available
    INVALID_PARAMS = -32602   # Invalid method parameter(s)
    INTERNAL_ERROR = -32603   # Internal JSON-RPC error

class MCPServer:
    """
    Model Context Protocol (MCP) Server Implementation.
    
    This class implements a full MCP server following the MCP 2024-11-05 specification.
    It provides a standardized interface for AI assistants to interact with application
    usage data through well-defined tools and resources.
    
    Key Features:
    - Full MCP protocol compliance with JSON-RPC 2.0
    - Async TCP server for handling multiple concurrent connections
    - Database operations exposed as MCP tools
    - Usage statistics exposed as MCP resources
    - Comprehensive error handling and logging
    - Input validation and schema compliance
    - Automatic database initialization
    
    The server exposes the following tools:
    - create_usage_log: Create new usage log entries
    - get_usage_logs: Retrieve usage logs with filtering
    - update_usage_log: Update existing log entries
    - delete_usage_log: Delete log entries
    - get_unique_users: Get list of unique users
    - get_unique_applications: Get list of unique applications
    - get_unique_platforms: Get list of unique platforms
    
    The server exposes the following resources:
    - usage://stats: Real-time usage statistics
    
    Attributes:
        host (str): Server bind address
        port (int): Server bind port
        db_manager (DatabaseManager): Database interface
        initialized (bool): Whether server initialization is complete
        client_capabilities (dict): Capabilities reported by connected clients
        tools (dict): Available tools with their schemas
        resources (dict): Available resources with their metadata
    
    Example:
        server = MCPServer(host="127.0.0.1", port=58888)
        await server.start()
    """
    
    def __init__(self, host=settings.MCP_HOST, port=settings.MCP_PORT):
        """
        Initialize MCP server with database and tool definitions.
        
        Args:
            host (str): Server bind address. Defaults to settings.MCP_HOST
            port (int): Server bind port. Defaults to settings.MCP_PORT
        """
        self.host = host
        self.port = port
        self.db_manager = DatabaseManager()
        self.db_manager.initialize_database()
        self.initialized = False
        self.client_capabilities = {}
        
        # Define available tools with JSON schemas for input validation
        # Each tool corresponds to a database operation and includes:
        # - name: Tool identifier
        # - description: Human-readable description
        # - inputSchema: JSON schema for parameter validation
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
            },
            "analyze_top_users": {
                "name": "analyze_top_users",
                "description": "Get top N users by total usage time for a specific application",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "app_name": {
                            "type": "string",
                            "description": "Name of the application to analyze"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of top users to return (default: 10)",
                            "default": 10
                        }
                    },
                    "required": ["app_name"]
                }
            },
            "analyze_new_users": {
                "name": "analyze_new_users",
                "description": "Find new users within a specified date range",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "description": "Start date in YYYY-MM-DD format"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "End date in YYYY-MM-DD format"
                        },
                        "app_name": {
                            "type": "string",
                            "description": "Optional: specific application to analyze"
                        }
                    },
                    "required": ["start_date", "end_date"]
                }
            },
            "analyze_inactive_users": {
                "name": "analyze_inactive_users",
                "description": "Find users who haven't been active since a specific date",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "cutoff_date": {
                            "type": "string",
                            "description": "Date in YYYY-MM-DD format (users inactive since this date)"
                        },
                        "app_name": {
                            "type": "string",
                            "description": "Optional: specific application to analyze"
                        }
                    },
                    "required": ["cutoff_date"]
                }
            },
            "analyze_weekly_additions": {
                "name": "analyze_weekly_additions",
                "description": "Get weekly breakdown of new user registrations",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "description": "Start date in YYYY-MM-DD format"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "End date in YYYY-MM-DD format"
                        }
                    },
                    "required": ["start_date", "end_date"]
                }
            },
            "analyze_application_stats": {
                "name": "analyze_application_stats",
                "description": "Get comprehensive usage statistics for applications",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "app_name": {
                            "type": "string",
                            "description": "Optional: specific application to analyze, or omit for all apps"
                        }
                    }
                }
            },
            "analyze_platform_distribution": {
                "name": "analyze_platform_distribution",
                "description": "Get usage distribution across different platforms",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            "analyze_daily_trends": {
                "name": "analyze_daily_trends",
                "description": "Get daily usage trends over a specified period",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "description": "Start date in YYYY-MM-DD format"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "End date in YYYY-MM-DD format"
                        },
                        "app_name": {
                            "type": "string",
                            "description": "Optional: specific application to analyze"
                        }
                    },
                    "required": ["start_date", "end_date"]
                }
            },
            "analyze_user_activity": {
                "name": "analyze_user_activity",
                "description": "Get comprehensive activity summary for a specific user",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "user_name": {
                            "type": "string",
                            "description": "Username to analyze"
                        }
                    },
                    "required": ["user_name"]
                }
            },
            "analyze_system_overview": {
                "name": "analyze_system_overview",
                "description": "Get high-level system statistics and overview",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
        
        # Define available resources with metadata
        # Resources provide read-only access to server data and state
        # Each resource includes:
        # - uri: Unique resource identifier
        # - name: Human-readable name
        # - description: Resource description
        # - mimeType: Content type of the resource
        self.resources = {
            "usage_stats": {
                "uri": "usage://stats",
                "name": "Usage Statistics",
                "description": "Current usage statistics and metrics",
                "mimeType": "application/json"
            }
        }

    async def handle_client(self, reader, writer):
        """
        Handle incoming client connections.
        
        Manages the lifecycle of a client connection, including:
        - Reading incoming messages
        - Processing JSON-RPC requests
        - Sending responses
        - Error handling and logging
        - Connection cleanup
        
        This method runs in a loop for each connected client and handles
        multiple requests over a single connection.
        
        Args:
            reader (asyncio.StreamReader): Stream for reading client data
            writer (asyncio.StreamWriter): Stream for writing responses
            
        Example:
            # This method is called automatically by the TCP server
            # when a new client connects
        """
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
        """
        Process incoming JSON-RPC messages and route to appropriate handlers.
        
        This is the main message dispatcher that routes incoming requests
        to the appropriate handler based on the message method. Implements
        the MCP protocol specification for JSON-RPC 2.0 message handling.
        
        The method enforces proper initialization order - all methods except
        'initialize' require the server to be initialized first.
        
        Supported MCP protocol methods:
        - initialize: Server initialization handshake
        - tools/list: List available tools
        - tools/call: Execute a specific tool
        - resources/list: List available resources
        - resources/read: Read resource content
        - ping: Server health check
        
        Args:
            message (Dict[str, Any]): JSON-RPC message containing:
                - jsonrpc (str): Protocol version (should be "2.0")
                - method (str): RPC method name
                - params (dict, optional): Method parameters
                - id (str/int, optional): Request identifier
                
        Returns:
            Optional[Dict[str, Any]]: JSON-RPC response with result or error,
                                     None for notification messages
                
        Example:
            message = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {"name": "create_usage_log", "arguments": {...}},
                "id": "req-1"
            }
            response = await process_message(message)
        """
        message_id = message.get("id")
        method = message.get("method")
        params = message.get("params", {})
        
        # Validate message structure - method is required
        if not method:
            return self.create_error_response(message_id, ErrorCode.INVALID_REQUEST, "Missing method")
        
        # Handle initialization - this is the only method allowed before initialization
        if method == MessageType.INITIALIZE:
            return await self.handle_initialize(message_id, params)
        
        # Ensure server is initialized before processing other methods
        if not self.initialized and method != MessageType.INITIALIZE:
            return self.create_error_response(
                message_id, ErrorCode.INVALID_REQUEST, "Server not initialized"
            )
        
        # Route to appropriate method handlers
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
        """
        Handle MCP initialization handshake.
        
        Processes the client's initialization request and establishes the
        MCP protocol session. This must be the first message sent by any
        client before other operations can be performed.
        
        Validates the protocol version and stores client capabilities for
        future reference. Sets the server to initialized state on success.
        
        Args:
            message_id (str): Request identifier for response matching
            params (Dict[str, Any]): Initialization parameters containing:
                - protocolVersion (str): Client's protocol version
                - capabilities (dict): Client capability declarations
                - clientInfo (dict, optional): Client information
                
        Returns:
            Dict[str, Any]: JSON-RPC response with server capabilities and info
            
        Example:
            params = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}, "resources": {}},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
            response = await handle_initialize("init-1", params)
        """
        self.client_capabilities = params.get("capabilities", {})
        protocol_version = params.get("protocolVersion")
        
        # Validate protocol version compatibility
        if protocol_version != MCP_PROTOCOL_VERSION:
            return self.create_error_response(
                message_id, ErrorCode.INVALID_PARAMS, 
                f"Unsupported protocol version: {protocol_version}"
            )
        
        # Mark server as initialized
        self.initialized = True
        logger.info("MCP initialization completed successfully")
        
        # Return server capabilities and information
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "result": {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "capabilities": {
                    "tools": {},    # Tool capabilities (currently empty)
                    "resources": {} # Resource capabilities (currently empty)
                },
                "serverInfo": {
                    "name": SERVER_NAME,
                    "version": SERVER_VERSION
                }
            }
        }

    async def handle_tools_list(self, message_id: str) -> Dict[str, Any]:
        """
        Return list of available tools.
        
        Provides the client with metadata about all available tools that
        can be executed via the tools/call method. Each tool definition
        includes its name, description, and input schema for validation.
        
        Args:
            message_id (str): Request identifier for response matching
            
        Returns:
            Dict[str, Any]: JSON-RPC response containing:
                - tools: List of tool definitions with metadata
                
        Example:
            response = await handle_tools_list("list-1")
            # Returns: {
            #     "jsonrpc": "2.0",
            #     "id": "list-1",
            #     "result": {
            #         "tools": [
            #             {
            #                 "name": "create_usage_log",
            #                 "description": "Create a new usage log entry",
            #                 "inputSchema": {...}
            #             },
            #             ...
            #         ]
            #     }
            # }
        """
        tools_list = list(self.tools.values())
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "result": {
                "tools": tools_list
            }
        }

    async def handle_tools_call(self, message_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool call with the provided arguments.
        
        Validates the tool name and executes the corresponding database
        operation. Each tool maps to a specific database manager method
        and returns structured results in MCP format.
        
        Available tools:
        - create_usage_log: Create new usage log entry
        - get_usage_logs: Retrieve usage logs with optional filters
        - update_usage_log: Update existing usage log
        - delete_usage_log: Delete usage log by ID
        - get_unique_users: Get list of unique users
        - get_unique_applications: Get list of unique applications
        - get_unique_platforms: Get list of unique platforms
        
        Args:
            message_id (str): Request identifier for response matching
            params (Dict[str, Any]): Tool execution parameters containing:
                - name (str): Tool name to execute
                - arguments (dict): Tool-specific arguments
                
        Returns:
            Dict[str, Any]: JSON-RPC response with tool execution results
            
        Raises:
            Exception: Database operation errors or invalid arguments
            
        Example:
            params = {
                "name": "create_usage_log",
                "arguments": {
                    "user": "john_doe",
                    "application": "Chrome",
                    "date": "2024-01-15",
                    "duration": 3600
                }
            }
            response = await handle_tools_call("call-1", params)
        """
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        # Validate tool existence
        if tool_name not in self.tools:
            return self.create_error_response(
                message_id, ErrorCode.INVALID_PARAMS, f"Unknown tool: {tool_name}"
            )
        
        try:
            # Route to appropriate database manager method
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
            elif tool_name == "analyze_top_users":
                app_name = arguments.get("app_name")
                limit = arguments.get("limit", 10)
                result = self.db_manager.get_top_users_by_app(app_name, limit)
            elif tool_name == "analyze_new_users":
                start_date = arguments.get("start_date")
                end_date = arguments.get("end_date")
                app_name = arguments.get("app_name")
                result = self.db_manager.get_new_users_in_period(start_date, end_date, app_name)
            elif tool_name == "analyze_inactive_users":
                cutoff_date = arguments.get("cutoff_date")
                app_name = arguments.get("app_name")
                result = self.db_manager.get_inactive_users_since(cutoff_date, app_name)
            elif tool_name == "analyze_weekly_additions":
                start_date = arguments.get("start_date")
                end_date = arguments.get("end_date")
                result = self.db_manager.get_user_additions_by_week(start_date, end_date)
            elif tool_name == "analyze_application_stats":
                app_name = arguments.get("app_name")
                result = self.db_manager.get_application_usage_stats(app_name)
            elif tool_name == "analyze_platform_distribution":
                result = self.db_manager.get_platform_distribution()
            elif tool_name == "analyze_daily_trends":
                start_date = arguments.get("start_date")
                end_date = arguments.get("end_date")
                app_name = arguments.get("app_name")
                result = self.db_manager.get_daily_usage_trends(start_date, end_date, app_name)
            elif tool_name == "analyze_user_activity":
                user_name = arguments.get("user_name")
                result = self.db_manager.get_user_activity_summary(user_name)
            elif tool_name == "analyze_system_overview":
                result = self.db_manager.get_system_overview()
            else:
                return self.create_error_response(
                    message_id, ErrorCode.INTERNAL_ERROR, f"Tool implementation missing: {tool_name}"
                )
            
            # Format result in MCP content structure
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
        """
        Return list of available resources.
        
        Provides the client with metadata about all available resources that
        can be read via the resources/read method. Resources are read-only
        data sources providing server state and statistics.
        
        Args:
            message_id (str): Request identifier for response matching
            
        Returns:
            Dict[str, Any]: JSON-RPC response containing:
                - resources: List of resource definitions with metadata
                
        Example:
            response = await handle_resources_list("list-1")
            # Returns: {
            #     "jsonrpc": "2.0",
            #     "id": "list-1",
            #     "result": {
            #         "resources": [
            #             {
            #                 "uri": "usage://stats",
            #                 "name": "Usage Statistics",
            #                 "description": "Current usage statistics and metrics",
            #                 "mimeType": "application/json"
            #             }
            #         ]
            #     }
            # }
        """
        resources_list = list(self.resources.values())
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "result": {
                "resources": resources_list
            }
        }

    async def handle_resources_read(self, message_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Read the content of a specific resource.
        
        Retrieves and returns the content of the requested resource identified
        by its URI. Currently supports usage statistics resource that provides
        real-time database metrics.
        
        Supported resources:
        - usage://stats: Current usage statistics and database metrics
        
        Args:
            message_id (str): Request identifier for response matching
            params (Dict[str, Any]): Resource read parameters containing:
                - uri (str): Resource URI to read
                
        Returns:
            Dict[str, Any]: JSON-RPC response with resource content
            
        Raises:
            Exception: Database access errors or resource generation failures
            
        Example:
            params = {"uri": "usage://stats"}
            response = await handle_resources_read("read-1", params)
            # Returns: {
            #     "jsonrpc": "2.0", 
            #     "id": "read-1",
            #     "result": {
            #         "contents": [{
            #             "uri": "usage://stats",
            #             "mimeType": "application/json",
            #             "text": "{\"total_logs\": 42, ...}"
            #         }]
            #     }
            # }
        """
        uri = params.get("uri")
        
        if uri == "usage://stats":
            # Generate real-time usage statistics
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
        """
        Handle ping request for server health check.
        
        Responds to client ping requests to verify server connectivity and
        responsiveness. This is a simple health check mechanism that
        requires no parameters and returns an empty result.
        
        Args:
            message_id (str): Request identifier for response matching
            
        Returns:
            Dict[str, Any]: JSON-RPC response with empty result indicating success
            
        Example:
            response = await handle_ping("ping-1")
            # Returns: {
            #     "jsonrpc": "2.0",
            #     "id": "ping-1", 
            #     "result": {}
            # }
        """
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "result": {}
        }

    def create_error_response(self, message_id: Optional[str], code: int, message: str) -> Dict[str, Any]:
        """
        Create a JSON-RPC 2.0 compliant error response.
        
        Formats error responses according to the JSON-RPC 2.0 specification,
        which is required by the MCP protocol. Error responses are used to
        communicate failures back to the client.
        
        Standard JSON-RPC error codes:
        - -32700: Parse error (invalid JSON)
        - -32600: Invalid request (malformed JSON-RPC)
        - -32601: Method not found
        - -32602: Invalid params
        - -32603: Internal error
        
        Args:
            message_id (Optional[str]): The ID from the original request,
                                       None for parse errors
            code (int): Standard JSON-RPC error code
            message (str): Human-readable error description
            
        Returns:
            Dict[str, Any]: JSON-RPC error response with:
                - jsonrpc: Protocol version "2.0"
                - id: Original request ID or null
                - error: Error object with code and message
                
        Example:
            error_response = create_error_response(
                "req-1", -32601, "Method not found"
            )
            # Returns: {
            #     "jsonrpc": "2.0",
            #     "id": "req-1", 
            #     "error": {"code": -32601, "message": "Method not found"}
            # }
        """
        return {
            "jsonrpc": "2.0",
            "id": message_id,
            "error": {
                "code": code,
                "message": message
            }
        }

    async def start(self):
        """
        Start the MCP server and begin listening for client connections.
        
        Creates an asyncio TCP server that listens for incoming MCP client
        connections. Each client connection is handled concurrently by the
        handle_client method. The server will continue running until stopped.
        
        The server logs important information including:
        - Listening address and port
        - MCP protocol version
        - Available tools for debugging
        
        Raises:
            OSError: If the port is already in use or other network errors
            Exception: For other server startup failures
            
        Example:
            server = MCPServer()
            await server.start()  # Server starts listening
        """
        server = await asyncio.start_server(
            self.handle_client, self.host, self.port)

        addr = server.sockets[0].getsockname()
        logger.info(f'MCP Server listening on {addr[0]}:{addr[1]}')
        logger.info(f'Protocol version: {MCP_PROTOCOL_VERSION}')
        logger.info(f'Available tools: {list(self.tools.keys())}')

        async with server:
            await server.serve_forever()

    async def shutdown(self):
        """
        Shutdown the MCP server gracefully.
        
        Performs cleanup operations when the server is shutting down:
        - Closes database connections
        - Logs shutdown status
        - Releases resources
        
        This method should be called when the server receives a shutdown
        signal or when the application is terminating.
        
        Example:
            try:
                await server.start()
            finally:
                await server.shutdown()
        """
        logger.info("Shutting down MCP server...")
        self.db_manager.disconnect()


async def main():
    """
    Main entry point for the MCP server application.
    
    Creates and starts the MCP server with proper error handling and
    graceful shutdown. Handles KeyboardInterrupt (Ctrl+C) for clean
    server termination.
    
    The server will:
    1. Initialize the MCPServer instance
    2. Start listening for connections
    3. Handle shutdown signals gracefully
    4. Clean up resources on exit
    
    Example:
        python mcp_server.py  # Starts the server
        # Press Ctrl+C to shutdown gracefully
    """
    server = MCPServer()
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await server.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
