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
# 1. Generate demo data (optional - creates 50K realistic records)
cd demo_data
python generate_demo_data.py

# 2. Start the MCP server (in one terminal)
cd ../mcp
python start_server.py

# 3. Run the interactive client (in another terminal)
cd ../examples
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

### 🎲 Demo Data Generation

For comprehensive testing with realistic data, use the demo data generator:

```bash
cd demo_data
python generate_demo_data.py
```

This creates:
- **50,000 usage records** spanning 2 years (July 2023 - July 2025)
- **150 users** with realistic activity patterns (developers, admins, designers, managers, analysts)
- **5 applications** across different categories (browsers, development tools, communication)
- **All platforms** with realistic distribution (Windows 60%, macOS 25%, Linux 10%, Android 3%, iOS 2%)
- **Seasonal patterns** including weekends, holidays, and vacation periods
- **Realistic session durations** based on application types

The generated data is perfect for testing all analytics features and understanding system capabilities.

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

└── demo_data/                         # Demo data generation tools
    ├── generate_demo_data.py          # Main demo data generator (50K records)
    └── test_analytics.py              # Analytics function tester
```

### Folder Purposes:

- **`config/`**: Contains application configuration and settings
- **`database/`**: Database abstraction layer and schema management
- **`mcp/`**: Core MCP protocol implementation (server and client)
- **`schemas/`**: JSON schema definitions for request validation
- **`examples/`**: Practical usage examples and helper scripts
- **`demo_data/`**: Demo data generation tools for testing with realistic data (50K records)

---

## 4. Available MCP Tools & Analytics

The system provides comprehensive tools for database operations and advanced analytics through the MCP protocol. All tools are accessible via the interactive client or programmatically through the MCP client.

### 📝 Basic Database Operations

#### 1. **create_usage_log** - Create New Usage Log Entry

**Purpose**: Creates a new application usage log entry in the database.

**Request Parameters**:
```json
{
  "monitor_app_version": "1.0.0",    // REQUIRED: Version of monitoring tool
  "platform": "Windows",             // REQUIRED: Operating system
  "user": "john_doe",                 // REQUIRED: Username or device identifier
  "application_name": "chrome.exe",   // REQUIRED: Name of the application
  "application_version": "120.0.0",   // REQUIRED: Version of the application
  "log_date": "2025-01-15",          // REQUIRED: Date in YYYY-MM-DD format
  "legacy_app": false,               // REQUIRED: Whether app is legacy (true/false)
  "duration_seconds": 3600           // REQUIRED: Usage duration in seconds
}
```

**Note**: All parameters are required for creating a usage log entry.

**Response Examples**:
```json
{
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"result\": 123, \"tool\": \"create_usage_log\"}"
      }
    ]
  }
}
```

#### 2. **get_usage_logs** - Retrieve Usage Logs

**Purpose**: Retrieves usage logs with optional filtering.

**Request Parameters**:
```json
{
  "filters": {                    // OPTIONAL: Object for filtering results
    "application_name": "chrome.exe",  // OPTIONAL: Filter by application name
    "platform": "Windows",            // OPTIONAL: Filter by platform
    "user": "john_doe"                 // OPTIONAL: Filter by user
  }
}
```

**Note**: All parameters are optional. If no filters are provided, returns all usage logs.
    "user": "john_doe"
  }
}
```

**Response Examples** (5 sample records):
```json
{
  "result": [
    {
      "id": 1,
      "monitor_app_version": "1.0.0",
      "platform": "Windows",
      "user": "john_doe",
      "application_name": "chrome.exe",
      "application_version": "120.0.0",
      "log_date": "2025-01-15",
      "legacy_app": false,
      "duration_seconds": 3600
    },
    {
      "id": 2,
      "monitor_app_version": "1.0.0",
      "platform": "macOS",
      "user": "alice_smith",
      "application_name": "safari.app",
      "application_version": "17.2",
      "log_date": "2025-01-15",
      "legacy_app": false,
      "duration_seconds": 2400
    },
    {
      "id": 3,
      "monitor_app_version": "1.0.0",
      "platform": "Windows",
      "user": "bob_wilson",
      "application_name": "firefox.exe",
      "application_version": "121.0",
      "log_date": "2025-01-14",
      "legacy_app": false,
      "duration_seconds": 1800
    },
    {
      "id": 4,
      "monitor_app_version": "1.0.0",
      "platform": "Linux",
      "user": "charlie_brown",
      "application_name": "code",
      "application_version": "1.85.0",
      "log_date": "2025-01-14",
      "legacy_app": false,
      "duration_seconds": 7200
    },
    {
      "id": 5,
      "monitor_app_version": "1.0.0",
      "platform": "Windows",
      "user": "diana_prince",
      "application_name": "notepad.exe",
      "application_version": "10.0",
      "log_date": "2025-01-13",
      "legacy_app": true,
      "duration_seconds": 600
    }
  ]
}
```

#### 3. **update_usage_log** - Update Existing Log

**Purpose**: Updates specific fields of an existing usage log.

**Request Parameters**:
```json
{
  "log_id": 123,                     // REQUIRED: ID of the log entry to update
  "updates": {                       // REQUIRED: Object containing fields to update
    "duration_seconds": 7200,        // OPTIONAL: New duration value
    "application_version": "120.0.1" // OPTIONAL: New application version
  }
}
```

**Note**: `log_id` and `updates` object are required. Within `updates`, specify only the fields you want to change.

**Response Examples**:
```json
{
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"result\": true, \"tool\": \"update_usage_log\"}"
      }
    ]
  }
}
```

#### 4. **delete_usage_log** - Delete Usage Log

**Purpose**: Permanently removes a usage log entry.

**Request Parameters**:
```json
{
  "log_id": 123                      // REQUIRED: ID of the log entry to delete
}
```

**Response Examples**:
```json
{
  "result": {
    "content": [
      {
        "type": "text", 
        "text": "{\"result\": true, \"tool\": \"delete_usage_log\"}"
      }
    ]
  }
}
```

### 📊 Advanced Analytics Tools

#### 5. **analyze_top_users** - Top Users by Application

**Purpose**: Get top N users by total usage time for a specific application.

**Request Parameters**:
```json
{
  "app_name": "chrome.exe",      // REQUIRED: Name of the application to analyze
  "limit": 5                     // OPTIONAL: Number of users to return (default: 10)
}
```

**Response Examples** (5 sample records):
```json
{
  "result": [
    {
      "user": "john_doe",
      "session_count": 45,
      "total_seconds": 163800,
      "total_hours": 45.5
    },
    {
      "user": "alice_smith", 
      "session_count": 38,
      "total_seconds": 133200,
      "total_hours": 37.0
    },
    {
      "user": "bob_wilson",
      "session_count": 32,
      "total_seconds": 115200,
      "total_hours": 32.0
    },
    {
      "user": "charlie_brown",
      "session_count": 28,
      "total_seconds": 100800,
      "total_hours": 28.0
    },
    {
      "user": "diana_prince",
      "session_count": 25,
      "total_seconds": 90000,
      "total_hours": 25.0
    }
  ]
}
```

#### 6. **analyze_new_users** - New User Analysis

**Purpose**: Find users who started using the system within a date range.

**Request Parameters**:
```json
{
  "start_date": "2025-01-01",    // REQUIRED: Start date in YYYY-MM-DD format
  "end_date": "2025-01-31",      // REQUIRED: End date in YYYY-MM-DD format
  "app_name": "chrome.exe"       // OPTIONAL: Specific application to analyze
}
```

**Response Examples** (5 sample records):
```json
{
  "result": [
    {
      "user": "new_user_1",
      "first_entry_date": "2025-01-15",
      "session_count": 12,
      "total_seconds": 30600,
      "total_hours": 8.5
    },
    {
      "user": "new_user_2",
      "first_entry_date": "2025-01-18",
      "session_count": 18,
      "total_seconds": 44280,
      "total_hours": 12.3
    },
    {
      "user": "new_user_3",
      "first_entry_date": "2025-01-22",
      "session_count": 8,
      "total_seconds": 21600,
      "total_hours": 6.0
    },
    {
      "user": "new_user_4",
      "first_entry_date": "2025-01-25",
      "session_count": 15,
      "total_seconds": 54000,
      "total_hours": 15.0
    },
    {
      "user": "new_user_5",
      "first_entry_date": "2025-01-28",
      "session_count": 5,
      "total_seconds": 18000,
      "total_hours": 5.0
    }
  ]
}
```

#### 7. **analyze_inactive_users** - Inactive User Analysis

**Purpose**: Find users who haven't been active since a specific date.

**Request Parameters**:
```json
{
  "cutoff_date": "2025-01-01",   // REQUIRED: Date in YYYY-MM-DD format (users inactive since this date)
  "app_name": "chrome.exe"       // OPTIONAL: Specific application to analyze
}
```

**Response Examples** (5 sample records):
```json
{
  "result": [
    {
      "user": "inactive_user_1",
      "last_activity_date": "2024-12-28",
      "total_sessions": 156,
      "total_seconds": 561600,
      "total_hours": 156.0
    },
    {
      "user": "inactive_user_2",
      "last_activity_date": "2024-12-25",
      "total_sessions": 89,
      "total_seconds": 320400,
      "total_hours": 89.0
    },
    {
      "user": "inactive_user_3",
      "last_activity_date": "2024-12-20",
      "total_sessions": 67,
      "total_seconds": 241200,
      "total_hours": 67.0
    },
    {
      "user": "inactive_user_4",
      "last_activity_date": "2024-12-15",
      "total_sessions": 45,
      "total_seconds": 162000,
      "total_hours": 45.0
    },
    {
      "user": "inactive_user_5",
      "last_activity_date": "2024-12-10",
      "total_sessions": 23,
      "total_seconds": 82800,
      "total_hours": 23.0
    }
  ]
}
```

#### 8. **analyze_weekly_additions** - Weekly User Additions

**Purpose**: Get weekly breakdown of new user registrations.

**Request Parameters**:
```json
{
  "start_date": "2025-01-01",    // REQUIRED: Start date in YYYY-MM-DD format
  "end_date": "2025-01-31"       // REQUIRED: End date in YYYY-MM-DD format
}
```

**Response Examples** (5 sample records):
```json
{
  "result": [
    {
      "week": "2025-W01",
      "week_start": "2025-01-01",
      "new_users": 12
    },
    {
      "week": "2025-W02", 
      "week_start": "2025-01-06",
      "new_users": 18
    },
    {
      "week": "2025-W03",
      "week_start": "2025-01-13",
      "new_users": 15
    },
    {
      "week": "2025-W04",
      "week_start": "2025-01-20",
      "new_users": 22
    },
    {
      "week": "2025-W05",
      "week_start": "2025-01-27",
      "new_users": 8
    }
  ]
}
```

#### 9. **analyze_application_stats** - Application Usage Statistics

**Purpose**: Get comprehensive usage statistics for applications.

**Request Parameters**:
```json
{
  "app_name": "chrome.exe"       // OPTIONAL: Specific application to analyze (omit for all apps)
}
```

**Note**: If `app_name` is omitted, returns statistics for all applications.

**Response Examples** (5 sample records):
```json
{
  "result": [
    {
      "application_name": "chrome.exe",
      "unique_users": 245,
      "total_sessions": 1567,
      "total_seconds": 5641200,
      "total_hours": 1567.0,
      "avg_session_minutes": 60.0,
      "first_usage": "2024-12-01",
      "last_usage": "2025-01-31"
    },
    {
      "application_name": "firefox.exe",
      "unique_users": 189,
      "total_sessions": 892,
      "total_seconds": 3211200,
      "total_hours": 892.0,
      "avg_session_minutes": 60.0,
      "first_usage": "2024-12-01",
      "last_usage": "2025-01-30"
    },
    {
      "application_name": "code.exe",
      "unique_users": 156,
      "total_sessions": 2341,
      "total_seconds": 8427600,
      "total_hours": 2341.0,
      "avg_session_minutes": 60.0,
      "first_usage": "2024-12-01",
      "last_usage": "2025-01-31"
    },
    {
      "application_name": "notepad.exe",
      "unique_users": 78,
      "total_sessions": 234,
      "total_seconds": 842400,
      "total_hours": 234.0,
      "avg_session_minutes": 60.0,
      "first_usage": "2024-12-01",
      "last_usage": "2025-01-29"
    },
    {
      "application_name": "safari.app",
      "unique_users": 123,
      "total_sessions": 567,
      "total_seconds": 2041200,
      "total_hours": 567.0,
      "avg_session_minutes": 60.0,
      "first_usage": "2024-12-01",
      "last_usage": "2025-01-31"
    }
  ]
}
```

#### 10. **analyze_platform_distribution** - Platform Usage Distribution

**Purpose**: Get usage distribution across different platforms.

**Request Parameters**:
```json
{}
```

**Note**: No parameters required. Returns distribution for all platforms.

**Response Examples** (5 sample records):
```json
{
  "result": [
    {
      "platform": "Windows",
      "unique_users": 456,
      "total_sessions": 2876,
      "total_seconds": 10353600,
      "total_hours": 2876.0,
      "session_percentage": 65.4,
      "time_percentage": 68.2
    },
    {
      "platform": "macOS",
      "unique_users": 234,
      "total_sessions": 1123,
      "total_seconds": 4042800,
      "total_hours": 1123.0,
      "session_percentage": 25.5,
      "time_percentage": 26.6
    },
    {
      "platform": "Linux",
      "unique_users": 123,
      "total_sessions": 345,
      "total_seconds": 1242000,
      "total_hours": 345.0,
      "session_percentage": 7.8,
      "time_percentage": 8.2
    },
    {
      "platform": "Android",
      "unique_users": 89,
      "total_sessions": 234,
      "total_seconds": 842400,
      "total_hours": 234.0,
      "session_percentage": 5.3,
      "time_percentage": 5.5
    },
    {
      "platform": "iOS",
      "unique_users": 67,
      "total_sessions": 156,
      "total_seconds": 561600,
      "total_hours": 156.0,
      "session_percentage": 3.5,
      "time_percentage": 3.7
    }
  ]
}
```

#### 11. **analyze_daily_trends** - Daily Usage Trends

**Purpose**: Get daily usage trends over a specified period.

**Request Parameters**:
```json
{
  "start_date": "2025-01-01",    // REQUIRED: Start date in YYYY-MM-DD format
  "end_date": "2025-01-07",      // REQUIRED: End date in YYYY-MM-DD format
  "app_name": "chrome.exe"       // OPTIONAL: Specific application to analyze
}
```

**Response Examples** (5 sample records):
```json
{
  "result": [
    {
      "log_date": "2025-01-01",
      "active_users": 234,
      "total_sessions": 567,
      "total_seconds": 2041200,
      "total_hours": 567.0,
      "avg_session_minutes": 60.0
    },
    {
      "log_date": "2025-01-02",
      "active_users": 189,
      "total_sessions": 445,
      "total_seconds": 1602000,
      "total_hours": 445.0,
      "avg_session_minutes": 60.0
    },
    {
      "log_date": "2025-01-03",
      "active_users": 267,
      "total_sessions": 623,
      "total_seconds": 2242800,
      "total_hours": 623.0,
      "avg_session_minutes": 60.0
    },
    {
      "log_date": "2025-01-04",
      "active_users": 298,
      "total_sessions": 734,
      "total_seconds": 2642400,
      "total_hours": 734.0,
      "avg_session_minutes": 60.0
    },
    {
      "log_date": "2025-01-05",
      "active_users": 156,
      "total_sessions": 378,
      "total_seconds": 1360800,
      "total_hours": 378.0,
      "avg_session_minutes": 60.0
    }
  ]
}
```

#### 12. **analyze_user_activity** - Individual User Activity Summary

**Purpose**: Get comprehensive activity summary for a specific user.

**Request Parameters**:
```json
{
  "user_name": "john_doe"        // REQUIRED: Username to analyze
}
```

**Response Examples**:
```json
{
  "result": {
    "user": "john_doe",
    "total_sessions": 156,
    "apps_used": 8,
    "platforms_used": 2,
    "total_seconds": 561600,
    "total_hours": 156.0,
    "avg_session_minutes": 60.0,
    "first_activity": "2024-12-01",
    "last_activity": "2025-01-31",
    "application_breakdown": [
      {
        "application_name": "chrome.exe",
        "sessions": 89,
        "total_seconds": 320400,
        "total_hours": 89.0
      },
      {
        "application_name": "code.exe",
        "sessions": 34,
        "total_seconds": 122400,
        "total_hours": 34.0
      },
      {
        "application_name": "firefox.exe",
        "sessions": 23,
        "total_seconds": 82800,
        "total_hours": 23.0
      },
      {
        "application_name": "notepad.exe",
        "sessions": 10,
        "total_seconds": 36000,
        "total_hours": 10.0
      }
    ]
  }
}
```

#### 13. **analyze_system_overview** - System-Wide Statistics

**Purpose**: Get high-level system statistics and overview.

**Request Parameters**:
```json
{}
```

**Note**: No parameters required. Returns system-wide statistics.

**Response Examples**:
```json
{
  "result": {
    "total_records": 12456,
    "total_users": 1234,
    "total_applications": 45,
    "total_platforms": 5,
    "total_seconds": 44841600,
    "total_hours": 12456.0,
    "avg_session_minutes": 60.0,
    "earliest_record": "2024-12-01",
    "latest_record": "2025-01-31",
    "top_applications": [
      {
        "application_name": "chrome.exe",
        "sessions": 3456
      },
      {
        "application_name": "code.exe",
        "sessions": 2890
      },
      {
        "application_name": "firefox.exe",
        "sessions": 1567
      },
      {
        "application_name": "safari.app",
        "sessions": 1234
      },
      {
        "application_name": "notepad.exe",
        "sessions": 890
      }
    ],
    "top_users": [
      {
        "user": "john_doe",
        "sessions": 234
      },
      {
        "user": "alice_smith", 
        "sessions": 198
      },
      {
        "user": "bob_wilson",
        "sessions": 167
      },
      {
        "user": "charlie_brown",
        "sessions": 145
      },
      {
        "user": "diana_prince",
        "sessions": 134
      }
    ]
  }
}
```

### 🔍 Utility Tools

#### 14. **get_unique_users** - List All Users

**Purpose**: Get list of unique users from the database.

**Request Parameters**:
```json
{}
```

**Note**: No parameters required. Returns all unique users.

**Response Examples**:
```json
{
  "result": ["alice_smith", "bob_wilson", "charlie_brown", "diana_prince", "john_doe"]
}
```

#### 15. **get_unique_applications** - List All Applications

**Purpose**: Get list of unique applications from the database.

**Request Parameters**:
```json
{}
```

**Note**: No parameters required. Returns all unique applications.

**Response Examples**:
```json
{
  "result": ["chrome.exe", "code.exe", "firefox.exe", "notepad.exe", "safari.app"]
}
```

#### 16. **get_unique_platforms** - List All Platforms

**Purpose**: Get list of unique platforms from the database.

**Request Parameters**:
```json
{}
```

**Note**: No parameters required. Returns all unique platforms.

**Response Examples**:
```json
{
  "result": ["Android", "Linux", "Windows", "iOS", "macOS"]
}
```

---

## 5. Component Details

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
│  │  ┌─────────────┐  ┌─────────────────┐                   │ │
│  │  │   CRUD      │  │   Connection    │                   │ │
│  │  │ Operations  │  │   Manager       │                   │ │
│  │  └─────────────┘  └─────────────────┘                   │ │
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
