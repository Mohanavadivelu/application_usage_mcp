# Application Usage MCP System

## 1. Project Overview

The **Application Usage MCP System** is a production-ready implementation of the Model Context Protocol (MCP) designed for tracking and managing application usage data. This system provides a secure, standards-compliant interface that enables AI assistants to interact with application usage logs through a well-defined protocol.

### Key Features:
- **Full MCP Protocol Compliance**: Implements the official MCP specification with JSON-RPC 2.0
- **Secure Operations**: Input validation, schema validation, and explicit command whitelisting
- **Tool System**: Database operations exposed as standardized MCP tools
- **Resource System**: Real-time usage statistics accessible as MCP resources
- **Database Management**: SQLite database with automatic schema migration
- **Async Architecture**: Built on Python's asyncio for high performance
- **Comprehensive Testing**: Full test suite ensuring protocol compliance

---

## 2. Quick Start Guide

### 🚀 Interactive Client (Recommended)

The easiest way to test and explore all MCP functionality is through the interactive client:

```bash
# 1. Start the MCP server (in one terminal)
cd examples
python start_server.py

# 2. Run the interactive client (in another terminal)
cd examples
python interactive_client.py
```

The interactive client provides a menu-driven interface to test all MCP tools:

```
🛠️  MCP CLIENT INTERACTIVE TOOL TESTER
============================================================
1️⃣  Create Usage Log           6️⃣  Get Unique Users
2️⃣  Get Usage Logs (All)       7️⃣  Get Unique Applications
3️⃣  Get Usage Logs (Filtered)  8️⃣  Get Unique Platforms
4️⃣  Update Usage Log           9️⃣  Get Usage Statistics
5️⃣  Delete Usage Log           🔟  Test Duration Aggregation
📊  Show All Data Summary       🧪  Run All Tests (Auto)
❌  Exit
============================================================
```

**Features:**
- **Smart Defaults**: Quick testing with sensible default values
- **Input Validation**: Type checking and format validation
- **Duration Aggregation**: Test automatic duration aggregation for duplicates
- **Comprehensive Testing**: Automated test suite for all functionality
- **User-Friendly**: Clear prompts and formatted output

### 📋 Manual Testing

The interactive client includes comprehensive automated testing options (menu option 🧪).

### 📚 Documentation

- **Interactive Interface**: The `interactive_client.py` includes built-in help and guidance
- **Architecture Details**: Continue reading this README for technical details

---

## 3. Folder Structure

```
application_usage_mcp/
├── README.md                           # This documentation file
├── requirements.txt                    # Python dependencies
├── main.py                            # Application entry point
├── usage.db                           # SQLite database (auto-created)
│
├── config/                            # Configuration management
│   ├── __init__.py                    # Package initialization
│   └── settings.py                    # Application settings and constants
│
├── database/                          # Database layer
│   ├── __init__.py                    # Package initialization
│   ├── db_manager.py                  # Database operations manager
│   └── schema.sql                     # Database schema definition
│
├── mcp/                               # MCP protocol implementation
│   ├── __init__.py                    # Package initialization
│   ├── mcp_server.py                  # MCP protocol server
│   └── mcp_client.py                  # MCP protocol client
│
├── schemas/                           # JSON schema validation
│   ├── __init__.py                    # Package initialization
│   ├── validator.py                   # Schema validation utilities
│   ├── initialize_request.json        # Initialize request schema
│   ├── tool_call_request.json         # Tool call request schema
│   └── resource_read_request.json     # Resource read request schema
│
└── examples/                          # Usage examples and utilities
    ├── start_server.py                # Server startup script
    └── interactive_client.py          # Interactive CLI for testing all tools
```

### Folder Purposes:

- **`config/`**: Contains application configuration and settings
- **`database/`**: Database abstraction layer and schema management
- **`mcp/`**: Core MCP protocol implementation (server and client)
- **`schemas/`**: JSON schema definitions for request validation
- **`examples/`**: Practical usage examples and helper scripts

---

## 4. Documentation

### Core Files Documentation

#### `main.py`
**Purpose**: Application entry point that initializes and starts the MCP server.
```python
# Functionality:
- Configures logging
- Initializes MCPServer instance
- Starts the async event loop
- Handles graceful shutdown
```

#### `config/settings.py`
**Purpose**: Centralized configuration management for the entire application.
```python
# Configuration includes:
- Database settings (path, name, schema location)
- MCP server settings (host, port)
- Protocol constants and defaults
```

#### `database/db_manager.py`
**Purpose**: Database abstraction layer providing CRUD operations for usage logs.
```python
# Key Methods:
- initialize_database(): Sets up database schema
- create_usage_log(): Creates new usage entries
- get_usage_logs(): Retrieves logs with optional filtering
- update_usage_log(): Updates existing log entries
- delete_usage_log(): Removes log entries
```

### Database Schema

The database uses the following schema for tracking application usage across different platforms and applications:

#### Table: `usage_data`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier for each usage record |
| `monitor_app_version` | TEXT | NOT NULL | Version of the monitoring tool that logged the data |
| `platform` | TEXT | NOT NULL | Operating system (e.g., Windows, macOS, Android) |
| `user` | TEXT | NOT NULL | Username or device ID |
| `application_name` | TEXT | NOT NULL | Name of the application (e.g., chrome.exe) |
| `application_version` | TEXT | NOT NULL | Application version number |
| `log_date` | TEXT | NOT NULL | Date in YYYY-MM-DD format |
| `legacy_app` | BOOLEAN | NOT NULL | Indicates if the application is legacy (true/false) |
| `duration_seconds` | INTEGER | NOT NULL | Usage time in seconds |

#### Database Indexes

| Index Name | Column(s) | Purpose |
|------------|-----------|---------|
| `idx_usage_app` | `application_name` | Efficient application-based queries |
| `idx_usage_user` | `user` | User-based filtering and analytics |
| `idx_usage_date` | `log_date` | Time-based queries and reporting |
| `idx_usage_platform` | `platform` | Platform-specific analysis |

#### Example Data

```json
{
  "id": 1,
  "monitor_app_version": "1.0.0",
  "platform": "Windows",
  "user": "john_doe",
  "application_name": "chrome.exe",
  "application_version": "119.0.6045.105",
  "log_date": "2025-07-27",
  "legacy_app": false,
  "duration_seconds": 3600
}
```

#### Query Examples

```sql
-- Get all Chrome usage logs
SELECT * FROM usage_data WHERE application_name = 'chrome.exe';

-- Get usage logs for a specific user on Windows
SELECT * FROM usage_data WHERE user = 'john_doe' AND platform = 'Windows';

-- Get legacy applications only
SELECT * FROM usage_data WHERE legacy_app = 1;

-- Get usage logs from the last 24 hours
SELECT * FROM usage_data 
WHERE log_date >= datetime('now', '-1 day')
ORDER BY log_date DESC;

-- Get total usage time per application
SELECT application_name, SUM(duration_seconds) as total_seconds
FROM usage_data 
GROUP BY application_name 
ORDER BY total_seconds DESC;
```

#### `mcp/mcp_server.py`
**Purpose**: Complete MCP protocol server implementation with JSON-RPC 2.0 compliance.
```python
# Key Components:
- MCPServer class: Main server implementation
- Message handling: Process all MCP message types
- Tool system: Expose database operations as MCP tools
- Resource system: Provide usage statistics as resources
- Security: Input validation and error handling
```

#### `mcp/mcp_client.py`
**Purpose**: MCP protocol client for interacting with the server programmatically.
```python
# Key Features:
- Connection management with auto-reconnection
- Protocol handshake and initialization
- Tool discovery and execution
- Resource reading capabilities
- Convenience methods for database operations
```

#### `schemas/validator.py`
**Purpose**: JSON schema validation utilities for ensuring message compliance.
```python
# Validation Functions:
- validate_initialize_request(): Validates handshake messages
- validate_tool_call_request(): Validates tool execution requests
- validate_resource_read_request(): Validates resource access requests
```

---

## 5. Architecture

### System Architecture Overview

The system follows a **layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP CLIENT LAYER                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   AI Assistant  │  │  Python Client  │  │  Web Client  │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
                                │ JSON-RPC 2.0 / TCP
                                │
┌──────────────────────────────────────────────────────────────┐
│                   MCP SERVER LAYER                           │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                 MCPServer                               │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │ │
│  │  │  Message    │  │   Tool      │  │    Resource     │  │ │
│  │  │  Handler    │  │   System    │  │    System       │  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
                                │
                                │ Method Calls
                                │
┌──────────────────────────────────────────────────────────────┐
│                  DATABASE LAYER                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │               DatabaseManager                           │ │
│  │  ┌─────────────┐  ┌─────────────────┐                  │ │
│  │  │   CRUD      │  │   Connection    │                  │ │
│  │  │ Operations  │  │   Manager       │                  │ │
│  │  └─────────────┘  └─────────────────┘                  │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
                                │
                                │ SQL
                                │
┌─────────────────────────────────────────────────────────────┐
│                   STORAGE LAYER                             │
│                    SQLite Database                          │
│                     (usage.db)                              │
└─────────────────────────────────────────────────────────────┘
```

### Class Diagram (ASCII Art)

```
┌─────────────────────────────────────────────────────────────┐
│                       MCPServer                             │
├─────────────────────────────────────────────────────────────┤
│ - host: str                                                 │
│ - port: int                                                 │
│ - db_manager: DatabaseManager                               │
│ - initialized: bool                                         │
│ - tools: Dict[str, Dict]                                    │
│ - resources: Dict[str, Dict]                                │
├─────────────────────────────────────────────────────────────┤
│ + handle_client(reader, writer)                             │
│ + process_message(message) -> Dict                          │
│ + handle_initialize(id, params) -> Dict                     │
│ + handle_tools_list(id) -> Dict                             │
│ + handle_tools_call(id, params) -> Dict                     │
│ + handle_resources_list(id) -> Dict                         │
│ + handle_resources_read(id, params) -> Dict                 │
│ + start()                                                   │
│ + shutdown()                                                │
└─────────────────────────────────────────────────────────────┘
                                │
                                │ uses
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    DatabaseManager                          │
├─────────────────────────────────────────────────────────────┤
│ - db_path: str                                              │
│ - conn: sqlite3.Connection                                  │
│ - logger: Logger                                            │
├─────────────────────────────────────────────────────────────┤
│ + connect()                                                 │
│ + disconnect()                                              │
│ + initialize_database()                                     │
│ + create_usage_log(data) -> int                             │
│ + get_usage_logs(filters) -> List[Dict]                     │
│ + update_usage_log(id, updates) -> bool                     │
│ + delete_usage_log(id) -> bool                              │
└─────────────────────────────────────────────────────────────┘
                                │
                                │ creates/manages
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                       MCPClient                             │
├─────────────────────────────────────────────────────────────┤
│ - host: str                                                 │
│ - port: int                                                 │
│ - reader: StreamReader                                      │
│ - writer: StreamWriter                                      │
│ - initialized: bool                                         │
│ - available_tools: List[Dict]                               │
│ - available_resources: List[Dict]                           │
├─────────────────────────────────────────────────────────────┤
│ + connect() -> bool                                         │
│ + disconnect()                                              │
│ + initialize() -> bool                                      │
│ + send_request(request) -> Dict                             │
│ + call_tool(name, args) -> Dict                             │
│ + read_resource(uri) -> Dict                                │
│ + create_usage_log(data) -> int                             │
│ + get_usage_logs(filters) -> List[Dict]                     │
│ + update_usage_log(id, updates) -> bool                     │
│ + delete_usage_log(id) -> bool                              │
└─────────────────────────────────────────────────────────────┘
                                │
                                │ validates with
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    SchemaValidator                          │
├─────────────────────────────────────────────────────────────┤
│ - schemas: Dict[str, Dict]                                  │
├─────────────────────────────────────────────────────────────┤
│ + validate_message(message, schema) -> Optional[str]        │
│ + validate_initialize_request(message) -> Optional[str]     │
│ + validate_tool_call_request(message) -> Optional[str]      │
│ + validate_resource_read_request(message) -> Optional[str]  │
└─────────────────────────────────────────────────────────────┘
```

### Component Relationships

1. **MCPServer** ↔ **DatabaseManager**: Server uses database manager for all data operations
2. **MCPClient** → **MCPServer**: Client communicates with server via JSON-RPC 2.0
3. **MCPServer** → **SchemaValidator**: Server validates all incoming messages
4. **DatabaseManager** → **SQLite**: Direct database operations and connection management
5. **MCPClient** ↔ **MCPServer**: Bidirectional communication for tools and resources

---

## 5. Deployment Instructions

### Prerequisites
- Python 3.8 or higher
- pip package manager
- 50MB available disk space

### Step-by-Step Deployment

#### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/application_usage_mcp.git
cd application_usage_mcp
```

#### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 3: Start the Server
```bash
# Option 1: Using the main entry point
python main.py

# Option 2: Using the example server script
python examples/start_server.py
```

#### Step 4: Verify Server is Running
```bash
# In a new terminal, run the client example
python examples/client_usage.py
```

#### Step 5: Configure (Optional)
Edit `config/settings.py` to customize:
```python
# Change server port
MCP_PORT = 9000

# Change database location
DB_PATH = "/path/to/your/database.db"
```

### Production Deployment

#### Docker Deployment (Recommended)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

EXPOSE 58888
CMD ["python", "main.py"]
```

```bash
# Build and run
docker build -t mcp-usage-tracker .
docker run -p 58888:58888 -v $(pwd)/data:/app/data mcp-usage-tracker
```

#### Systemd Service (Linux)
```ini
[Unit]
Description=MCP Usage Tracker
After=network.target

[Service]
Type=simple
User=mcp-user
WorkingDirectory=/opt/mcp-usage-tracker
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Health Check
```bash
# Test server connectivity
curl -X POST http://localhost:58888 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"1","method":"ping"}'
```

---

## 6. Required Libraries

### Core Dependencies
```
jsonschema>=4.17.0          # JSON schema validation
```

### Development Dependencies
```
pytest>=7.0.0               # Testing framework
pytest-asyncio>=0.21.0      # Async testing support
pytest-cov>=4.0.0           # Code coverage
```

### Optional Dependencies
```
aiosqlite>=0.19.0           # Async SQLite operations (future enhancement)
python-dotenv>=1.0.0        # Environment variable management
```

### Python Standard Library (No Installation Required)
```
asyncio                     # Async programming
json                       # JSON handling
sqlite3                    # SQLite database
logging                    # Logging system
uuid                       # UUID generation
datetime                   # Date/time operations
typing                     # Type hints
os                         # Operating system interface
sys                        # System-specific parameters
signal                     # Signal handling
```

### Complete requirements.txt
```txt
# Core dependencies
jsonschema>=4.17.0

# Development dependencies
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0

# Optional dependencies for enhanced features
aiosqlite>=0.19.0
python-dotenv>=1.0.0
```

### Installation Commands
```bash
# Install core dependencies only
pip install jsonschema

# Install all dependencies including development tools
pip install -r requirements.txt

# Install with specific versions (production)
pip install jsonschema==4.17.0 pytest==7.0.0 pytest-asyncio==0.21.0
```

---

## 7. Sequence Flow

### 7.1 System Initialization Flow

```
1. Application Startup
   ├── Load configuration from config/settings.py
   ├── Initialize logging system
   ├── Create DatabaseManager instance
   │   ├── Check if database exists
   │   └── Initialize database tables
   ├── Create MCPServer instance
   │   ├── Load tool definitions
   │   ├── Load resource definitions
   │   └── Set up message handlers
   └── Start TCP server on configured host/port
```

### 7.2 Client Connection & Handshake Flow

```
1. Client Connection
   ├── TCP connection established
   ├── Client sends 'initialize' request
   │   └── Includes: protocol version, capabilities, client info
   ├── Server validates initialization request
   ├── Server responds with capabilities
   │   └── Includes: protocol version, server info, available tools/resources
   ├── Client sends 'tools/list' request
   ├── Server responds with tool definitions
   ├── Client sends 'resources/list' request
   ├── Server responds with resource definitions
   └── Handshake complete - ready for operations
```

### 7.3 Database Write Operations Flow

```
1. Create Usage Log
   ├── Client sends 'tools/call' request
   │   ├── Method: "tools/call"
   │   ├── Tool name: "create_usage_log"
   │   └── Arguments: {monitor_app_version, platform, user, application_name, 
   │                   application_version, log_date, legacy_app, duration_seconds}
   ├── Server validates request against JSON schema
   ├── Server extracts tool arguments
   ├── DatabaseManager.create_usage_log() called
   │   ├── Validate database connection
   │   ├── Validate required fields for new schema
   │   ├── Convert legacy_app boolean to 1/0 for SQLite
   │   ├── Execute INSERT SQL statement
   │   ├── Commit transaction
   │   └── Return new log ID
   ├── Server formats response with log ID
   └── Client receives success response with log ID
```

### 7.4 Database Read Operations Flow

```
1. Retrieve Usage Logs
   ├── Client sends 'tools/call' request
   │   ├── Method: "tools/call"
   │   ├── Tool name: "get_usage_logs"
   │   └── Arguments: {filters: {application_name: "chrome.exe"}} (optional)
   ├── Server validates request
   ├── DatabaseManager.get_usage_logs() called
   │   ├── Build SELECT query with WHERE clause (if filters)
   │   ├── Execute query
   │   ├── Convert rows to dictionaries
   │   ├── Convert legacy_app from 1/0 to True/False
   │   └── Return list of log entries
   ├── Server formats response with log data
   └── Client receives log entries
```

### 7.5 Database Update Operations Flow

```
1. Update Usage Log
   ├── Client sends 'tools/call' request
   │   ├── Tool name: "update_usage_log"
   │   └── Arguments: {log_id: 123, updates: {user: "new_user", duration_seconds: 7200}}
   ├── Server validates request
   ├── DatabaseManager.update_usage_log() called
   │   ├── Build UPDATE SQL with SET clause
   │   ├── Execute update with log_id WHERE clause
   │   ├── Check if any rows were affected
   │   └── Return success/failure boolean
   ├── Server formats response
   └── Client receives update result
```

### 7.6 Database Delete Operations Flow

```
1. Delete Usage Log
   ├── Client sends 'tools/call' request
   │   ├── Tool name: "delete_usage_log"
   │   └── Arguments: {log_id: 123}
   ├── Server validates request
   ├── DatabaseManager.delete_usage_log() called
   │   ├── Execute DELETE SQL with WHERE clause
   │   ├── Check if any rows were affected
   │   └── Return success/failure boolean
   ├── Server formats response
   └── Client receives deletion result
```

### 7.7 Resource Reading Flow

```
1. Read Usage Statistics
   ├── Client sends 'resources/read' request
   │   └── URI: "usage://stats"
   ├── Server validates request
   ├── Server calls get_usage_logs() to count total logs
   ├── Server generates statistics object
   │   ├── total_logs: count
   │   ├── last_updated: current timestamp
   │   └── summary: description
   ├── Server formats resource response
   │   ├── URI: original request URI
   │   ├── mimeType: "application/json"
   │   └── text: JSON-formatted statistics
   └── Client receives statistics data
```

### 7.7 New Features (Duration Aggregation & Unique Values)

#### 7.7.1 Duration Aggregation Flow
```
1. Create Usage Log with Duplicate Detection
   ├── Client sends 'tools/call' request with log data
   ├── DatabaseManager.create_usage_log() called
   │   ├── Check for existing record with same date, user, application_name
   │   ├── If duplicate found:
   │   │   ├── Retrieve existing duration_seconds
   │   │   ├── Add new duration to existing duration
   │   │   ├── Update record with new total duration
   │   │   ├── Update other fields (monitor_app_version, platform, etc.)
   │   │   └── Return existing record ID
   │   └── If no duplicate:
   │       ├── Insert new record as normal
   │       └── Return new record ID
   └── Client receives log ID (same ID if aggregated)
```

#### 7.7.2 Unique Values Retrieval Flow
```
1. Get Unique Users
   ├── Client sends 'tools/call' request
   │   └── Tool name: "get_unique_users"
   ├── DatabaseManager.get_unique_users() called
   │   ├── Execute: SELECT DISTINCT user FROM usage_data ORDER BY user
   │   └── Return sorted list of unique users
   └── Client receives: ["alice", "bob", "john_doe"]

2. Get Unique Applications  
   ├── Client sends 'tools/call' request
   │   └── Tool name: "get_unique_applications"
   ├── DatabaseManager.get_unique_applications() called
   │   ├── Execute: SELECT DISTINCT application_name FROM usage_data ORDER BY application_name
   │   └── Return sorted list of unique applications
   └── Client receives: ["chrome.exe", "firefox.exe", "vscode.exe"]

3. Get Unique Platforms
   ├── Client sends 'tools/call' request
   │   └── Tool name: "get_unique_platforms" 
   ├── DatabaseManager.get_unique_platforms() called
   │   ├── Execute: SELECT DISTINCT platform FROM usage_data ORDER BY platform
   │   └── Return sorted list of unique platforms
   └── Client receives: ["Linux", "Windows", "macOS"]
```

#### 7.7.3 Updated Data Format
```
- log_date format changed from ISO 8601 timestamp to YYYY-MM-DD
- Composite indexes added for better DISTINCT query performance:
  ├── idx_user_date (user, log_date)
  ├── idx_app_platform (application_name, platform)  
  └── idx_platform_date (platform, log_date)
```

### 7.8 Error Handling Flow

```
1. Error Scenarios
   ├── JSON Parse Error
   │   ├── Invalid JSON received
   │   ├── Server responds with -32700 error code
   │   └── Connection remains open
   ├── Invalid Request
   │   ├── Missing required fields
   │   ├── Server responds with -32600 error code
   │   └── Request rejected
   ├── Method Not Found
   │   ├── Unknown tool or method
   │   ├── Server responds with -32601 error code
   │   └── Available methods logged
   ├── Invalid Parameters
   │   ├── Schema validation fails
   │   ├── Server responds with -32602 error code
   │   └── Validation error details included
   └── Internal Error
       ├── Database or server error
       ├── Server responds with -32603 error code
       ├── Error logged for debugging
       └── Generic error message to client
```

### 7.9 Connection Lifecycle Flow

```
1. Connection Management
   ├── Connection Established
   │   ├── TCP socket created
   │   ├── Client address logged
   │   └── Handshake initiated
   ├── Active Session
   │   ├── Message processing loop
   │   ├── Request/response cycles
   │   └── Error handling
   ├── Graceful Shutdown
   │   ├── Client closes connection
   │   ├── Server detects connection closure
   │   ├── Cleanup resources
   │   └── Log connection closure
   └── Error Shutdown
       ├── Network error or exception
       ├── Server catches exception
       ├── Force close connection
       ├── Log error details
       └── Cleanup resources
```

---

## Additional Resources

- **API Examples**: `examples/client_usage.py`
- **Server Startup**: `examples/start_server.py`
- **Configuration Guide**: `config/settings.py`
- **Database Schema**: `database/schema.sql`

---

**Status**: ✅ Production Ready | **Protocol Version**: 2024-11-05 | **Last Updated**: July 27, 2025
