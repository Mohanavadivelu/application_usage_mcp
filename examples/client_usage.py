#!/usr/bin/env python3
"""
Simple MCP Client Usage Example

This script demonstrates how to use the MCP client to interact with the application usage server.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp.mcp_client import MCPClient

async def main():
    """Example usage of the MCP client"""
    client = MCPClient()
    
    try:
        print("🔗 Connecting to MCP server...")
        if not await client.initialize():
            print("❌ Failed to connect to server")
            return
        
        print("✅ Connected successfully!")
        print(f"📋 Available tools: {[tool['name'] for tool in client.available_tools]}")
        print(f"📚 Available resources: {[r['name'] for r in client.available_resources]}")
        
        # Example 1: Create a usage log
        print("\n📝 Creating a usage log...")
        log_data = {
            "monitor_app_version": "1.0.0",
            "platform": "Windows",
            "user": "user123",
            "application_name": "chrome.exe",
            "application_version": "119.0.6045.105",
            "log_date": datetime.now().isoformat() + "Z",
            "legacy_app": False,
            "duration_seconds": 3600
        }
        
        log_id = await client.create_usage_log(log_data)
        if log_id:
            print(f"✅ Created usage log with ID: {log_id}")
        else:
            print("❌ Failed to create usage log")
            return
        
        # Example 2: Retrieve all logs
        print("\n📖 Retrieving all usage logs...")
        logs = await client.get_usage_logs()
        if logs:
            print(f"✅ Found {len(logs)} logs:")
            for log in logs:
                print(f"  - ID {log['id']}: {log['application_name']} v{log['application_version']} by {log['user']} ({log['duration_seconds']}s)")
        
        # Example 3: Filter logs by application
        print(f"\n🔍 Filtering logs for application 'chrome.exe'...")
        filtered_logs = await client.get_usage_logs({"application_name": "chrome.exe"})
        if filtered_logs:
            print(f"✅ Found {len(filtered_logs)} matching logs")
        
        # Example 4: Update a log
        print(f"\n✏️ Updating log {log_id}...")
        success = await client.update_usage_log(log_id, {
            "user": "updated_user123",
            "duration_seconds": 7200
        })
        if success:
            print("✅ Log updated successfully")
        
        # Example 5: Get usage statistics
        print("\n📊 Getting usage statistics...")
        stats = await client.get_usage_stats()
        if stats:
            print(f"✅ Usage statistics:")
            print(f"  - Total logs: {stats['total_logs']}")
            print(f"  - Last updated: {stats['last_updated']}")
        
        # Example 6: Delete the log
        print(f"\n🗑️ Deleting log {log_id}...")
        success = await client.delete_usage_log(log_id)
        if success:
            print("✅ Log deleted successfully")
        
        print("\n🎉 All operations completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.disconnect()
        print("👋 Disconnected from server")

if __name__ == "__main__":
    print("=== MCP Client Usage Example ===")
    asyncio.run(main())
