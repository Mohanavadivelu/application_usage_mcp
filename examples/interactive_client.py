#!/usr/bin/env python3
"""
Interactive MCP Client - Command Line Interface

This script provides an interactive command-line interface to test all MCP tools.
It combines functionality from client_usage.py and test_new_features.py.
"""

import sys
import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp_client import MCPClient

# Configure logging (less verbose for interactive use)
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class InteractiveMCPClient:
    def __init__(self):
        self.client = MCPClient()
        self.connected = False
        
    async def connect(self):
        """Connect to MCP server"""
        print("🔗 Connecting to MCP server...")
        if await self.client.initialize():
            self.connected = True
            print("✅ Connected successfully!")
            print(f"📋 Available tools: {[tool['name'] for tool in self.client.available_tools]}")
            return True
        else:
            print("❌ Failed to connect to server")
            return False
    
    async def disconnect(self):
        """Disconnect from MCP server"""
        if self.connected:
            await self.client.disconnect()
            self.connected = False
            print("👋 Disconnected from server")

    def show_menu(self):
        """Display the main menu"""
        print("\n" + "="*60)
        print("🛠️  MCP CLIENT INTERACTIVE TOOL TESTER")
        print("="*60)
        print("1️⃣  Create Usage Log")
        print("2️⃣  Get Usage Logs (All)")
        print("3️⃣  Get Usage Logs (Filtered)")
        print("4️⃣  Update Usage Log")
        print("5️⃣  Delete Usage Log")
        print("6️⃣  Get Unique Users")
        print("7️⃣  Get Unique Applications")
        print("8️⃣  Get Unique Platforms")
        print("9️⃣  Get Usage Statistics")
        print("🔟  Test Duration Aggregation")
        print("📊  Show All Data Summary")
        print("🧪  Run All Tests (Auto)")
        print("❌  Exit")
        print("="*60)

    def get_user_input(self, prompt: str, input_type: type = str, default: Any = None) -> Any:
        """Get user input with type conversion and default value"""
        while True:
            try:
                if default is not None:
                    value = input(f"{prompt} (default: {default}): ").strip()
                    if not value:
                        return default
                else:
                    value = input(f"{prompt}: ").strip()
                    if not value:
                        print("❌ Input cannot be empty!")
                        continue
                
                if input_type == bool:
                    return value.lower() in ['true', 't', 'yes', 'y', '1']
                elif input_type == int:
                    return int(value)
                else:
                    return value
            except ValueError:
                print(f"❌ Invalid {input_type.__name__} value! Please try again.")

    async def create_usage_log(self):
        """Interactive create usage log"""
        print("\n📝 CREATE USAGE LOG")
        print("-" * 40)
        
        log_data = {
            "monitor_app_version": self.get_user_input("Monitor App Version", str, "1.0.0"),
            "platform": self.get_user_input("Platform (Windows/macOS/Linux/Android)", str, "Windows"),
            "user": self.get_user_input("User", str, f"user_{datetime.now().strftime('%H%M%S')}"),
            "application_name": self.get_user_input("Application Name", str, "chrome.exe"),
            "application_version": self.get_user_input("Application Version", str, "120.0.0"),
            "log_date": self.get_user_input("Log Date (YYYY-MM-DD)", str, datetime.now().strftime("%Y-%m-%d")),
            "legacy_app": self.get_user_input("Legacy App (true/false)", bool, False),
            "duration_seconds": self.get_user_input("Duration (seconds)", int, 3600)
        }
        
        print("\n📋 Creating log with data:")
        for key, value in log_data.items():
            print(f"  {key}: {value}")
        
        log_id = await self.client.create_usage_log(log_data)
        if log_id:
            print(f"✅ Created usage log with ID: {log_id}")
            return log_id
        else:
            print("❌ Failed to create usage log")
            return None

    async def get_usage_logs(self, filtered: bool = False):
        """Get usage logs with optional filtering"""
        print(f"\n📖 GET USAGE LOGS {'(FILTERED)' if filtered else '(ALL)'}")
        print("-" * 40)
        
        filters = {}
        if filtered:
            print("Available filter options (press Enter to skip):")
            filter_options = {
                "application_name": "Application Name",
                "user": "User",
                "platform": "Platform",
                "legacy_app": "Legacy App (true/false)",
                "log_date": "Log Date (YYYY-MM-DD)"
            }
            
            for key, description in filter_options.items():
                value = input(f"{description}: ").strip()
                if value:
                    if key == "legacy_app":
                        filters[key] = value.lower() in ['true', 't', 'yes', 'y', '1']
                    else:
                        filters[key] = value
        
        logs = await self.client.get_usage_logs(filters if filters else None)
        if logs:
            print(f"✅ Found {len(logs)} logs:")
            for log in logs:
                print(f"  ID {log['id']}: {log['application_name']} v{log['application_version']} "
                      f"by {log['user']} on {log['platform']} ({log['duration_seconds']}s) "
                      f"[{log['log_date']}] {'[LEGACY]' if log.get('legacy_app') else ''}")
            return logs
        else:
            print("❌ No logs found or failed to retrieve logs")
            return []

    async def update_usage_log(self):
        """Interactive update usage log"""
        print("\n✏️ UPDATE USAGE LOG")
        print("-" * 40)
        
        # First show available logs
        await self.get_usage_logs()
        
        log_id = self.get_user_input("Enter Log ID to update", int)
        
        print("\nAvailable fields to update (press Enter to skip):")
        updates = {}
        update_fields = {
            "monitor_app_version": str,
            "platform": str,
            "user": str,
            "application_name": str,
            "application_version": str,
            "log_date": str,
            "legacy_app": bool,
            "duration_seconds": int
        }
        
        for field, field_type in update_fields.items():
            value = input(f"{field.replace('_', ' ').title()}: ").strip()
            if value:
                if field_type == bool:
                    updates[field] = value.lower() in ['true', 't', 'yes', 'y', '1']
                elif field_type == int:
                    updates[field] = int(value)
                else:
                    updates[field] = value
        
        if not updates:
            print("❌ No updates provided!")
            return
        
        print(f"\n📋 Updating log {log_id} with:")
        for key, value in updates.items():
            print(f"  {key}: {value}")
        
        success = await self.client.update_usage_log(log_id, updates)
        if success:
            print("✅ Log updated successfully")
        else:
            print("❌ Failed to update log")

    async def delete_usage_log(self):
        """Interactive delete usage log"""
        print("\n🗑️ DELETE USAGE LOG")
        print("-" * 40)
        
        # First show available logs
        await self.get_usage_logs()
        
        log_id = self.get_user_input("Enter Log ID to delete", int)
        
        confirm = input(f"⚠️ Are you sure you want to delete log {log_id}? (yes/no): ").strip().lower()
        if confirm not in ['yes', 'y']:
            print("❌ Delete cancelled")
            return
        
        success = await self.client.delete_usage_log(log_id)
        if success:
            print("✅ Log deleted successfully")
        else:
            print("❌ Failed to delete log")

    async def get_unique_users(self):
        """Get unique users"""
        print("\n👥 GET UNIQUE USERS")
        print("-" * 40)
        
        users = await self.client.get_unique_users()
        if users:
            print(f"✅ Found {len(users)} unique users:")
            for i, user in enumerate(users, 1):
                print(f"  {i}. {user}")
        else:
            print("❌ No users found or failed to retrieve users")

    async def get_unique_applications(self):
        """Get unique applications"""
        print("\n📱 GET UNIQUE APPLICATIONS")
        print("-" * 40)
        
        applications = await self.client.get_unique_applications()
        if applications:
            print(f"✅ Found {len(applications)} unique applications:")
            for i, app in enumerate(applications, 1):
                print(f"  {i}. {app}")
        else:
            print("❌ No applications found or failed to retrieve applications")

    async def get_unique_platforms(self):
        """Get unique platforms"""
        print("\n💻 GET UNIQUE PLATFORMS")
        print("-" * 40)
        
        platforms = await self.client.get_unique_platforms()
        if platforms:
            print(f"✅ Found {len(platforms)} unique platforms:")
            for i, platform in enumerate(platforms, 1):
                print(f"  {i}. {platform}")
        else:
            print("❌ No platforms found or failed to retrieve platforms")

    async def get_usage_stats(self):
        """Get usage statistics"""
        print("\n📊 GET USAGE STATISTICS")
        print("-" * 40)
        
        stats = await self.client.get_usage_stats()
        if stats:
            print("✅ Usage statistics:")
            for key, value in stats.items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
        else:
            print("❌ Failed to retrieve usage statistics")

    async def test_duration_aggregation(self):
        """Test duration aggregation feature"""
        print("\n🔄 TEST DURATION AGGREGATION")
        print("-" * 40)
        
        # Create first entry
        base_data = {
            "monitor_app_version": "1.0.0",
            "platform": "Windows",
            "user": "test_aggregate_user",
            "application_name": "test_app.exe",
            "application_version": "1.0.0",
            "log_date": datetime.now().strftime("%Y-%m-%d"),
            "legacy_app": False,
            "duration_seconds": 1800  # 30 minutes
        }
        
        print("Creating first entry (30 minutes)...")
        log_id1 = await self.client.create_usage_log(base_data)
        if not log_id1:
            print("❌ Failed to create first entry")
            return
        
        # Create duplicate entry (should aggregate)
        duplicate_data = base_data.copy()
        duplicate_data["duration_seconds"] = 2400  # 40 minutes
        duplicate_data["application_version"] = "1.0.1"  # Different version to test update
        
        print("Creating duplicate entry (40 minutes) - should aggregate...")
        log_id2 = await self.client.create_usage_log(duplicate_data)
        
        if log_id2:
            print(f"✅ Returned log ID: {log_id2}")
            print(f"  Same as first ID: {log_id1 == log_id2}")
            
            # Verify aggregation
            logs = await self.client.get_usage_logs({
                "user": "test_aggregate_user", 
                "application_name": "test_app.exe"
            })
            
            if logs and len(logs) == 1:
                log = logs[0]
                expected_duration = 1800 + 2400  # 70 minutes
                actual_duration = log['duration_seconds']
                print(f"  Aggregated duration: {actual_duration}s (expected: {expected_duration}s)")
                if actual_duration == expected_duration:
                    print("✅ Duration aggregation working correctly!")
                else:
                    print(f"⚠️ Duration mismatch!")
            else:
                print(f"⚠️ Expected 1 log, found {len(logs) if logs else 0}")
        else:
            print("❌ Failed to create duplicate entry")

    async def show_data_summary(self):
        """Show a summary of all data"""
        print("\n📊 DATA SUMMARY")
        print("-" * 40)
        
        # Get all logs
        all_logs = await self.client.get_usage_logs()
        if not all_logs:
            print("❌ No data found")
            return
        
        print(f"📊 Total Logs: {len(all_logs)}")
        
        # Get unique values
        users = await self.client.get_unique_users()
        apps = await self.client.get_unique_applications()
        platforms = await self.client.get_unique_platforms()
        
        print(f"👥 Unique Users: {len(users) if users else 0}")
        print(f"📱 Unique Applications: {len(apps) if apps else 0}")
        print(f"💻 Unique Platforms: {len(platforms) if platforms else 0}")
        
        # Show recent logs
        print(f"\n📋 Recent Logs:")
        for i, log in enumerate(all_logs[-5:], 1):  # Show last 5
            print(f"  {i}. ID {log['id']}: {log['application_name']} by {log['user']} "
                  f"({log['duration_seconds']}s) on {log['log_date']}")

    async def run_all_tests(self):
        """Run automated tests of all functionality"""
        print("\n🧪 RUNNING ALL TESTS")
        print("-" * 40)
        
        test_data = [
            {
                "monitor_app_version": "1.0.0",
                "platform": "Windows",
                "user": "auto_test_user1",
                "application_name": "chrome.exe",
                "application_version": "120.0.0",
                "log_date": datetime.now().strftime("%Y-%m-%d"),
                "legacy_app": False,
                "duration_seconds": 3600
            },
            {
                "monitor_app_version": "1.0.0",
                "platform": "macOS",
                "user": "auto_test_user2",
                "application_name": "firefox.exe",
                "application_version": "118.0.0",
                "log_date": datetime.now().strftime("%Y-%m-%d"),
                "legacy_app": True,
                "duration_seconds": 1800
            }
        ]
        
        created_ids = []
        
        # Test 1: Create logs
        print("1. Testing create_usage_log...")
        for i, data in enumerate(test_data):
            log_id = await self.client.create_usage_log(data)
            if log_id:
                created_ids.append(log_id)
                print(f"  ✅ Created log {i+1} with ID: {log_id}")
            else:
                print(f"  ❌ Failed to create log {i+1}")
        
        # Test 2: Get logs
        print("2. Testing get_usage_logs...")
        logs = await self.client.get_usage_logs()
        if logs:
            print(f"  ✅ Retrieved {len(logs)} logs")
        else:
            print("  ❌ Failed to retrieve logs")
        
        # Test 3: Get unique values
        print("3. Testing unique value methods...")
        
        users = await self.client.get_unique_users()
        print(f"  👥 Users: {len(users) if users else 0}")
        
        apps = await self.client.get_unique_applications()
        print(f"  📱 Apps: {len(apps) if apps else 0}")
        
        platforms = await self.client.get_unique_platforms()
        print(f"  💻 Platforms: {len(platforms) if platforms else 0}")
        
        # Test 4: Update a log
        if created_ids:
            print("4. Testing update_usage_log...")
            success = await self.client.update_usage_log(created_ids[0], {
                "duration_seconds": 7200
            })
            if success:
                print("  ✅ Successfully updated log")
            else:
                print("  ❌ Failed to update log")
        
        # Test 5: Duration aggregation
        print("5. Testing duration aggregation...")
        await self.test_duration_aggregation()
        
        print("\n🎉 All automated tests completed!")

    async def run(self):
        """Main interactive loop"""
        if not await self.connect():
            return
        
        try:
            while True:
                self.show_menu()
                choice = input("\n🎯 Enter your choice: ").strip()
                
                if choice == '1':
                    await self.create_usage_log()
                elif choice == '2':
                    await self.get_usage_logs(filtered=False)
                elif choice == '3':
                    await self.get_usage_logs(filtered=True)
                elif choice == '4':
                    await self.update_usage_log()
                elif choice == '5':
                    await self.delete_usage_log()
                elif choice == '6':
                    await self.get_unique_users()
                elif choice == '7':
                    await self.get_unique_applications()
                elif choice == '8':
                    await self.get_unique_platforms()
                elif choice == '9':
                    await self.get_usage_stats()
                elif choice == '10':
                    await self.test_duration_aggregation()
                elif choice.lower() in ['summary', 's', '📊']:
                    await self.show_data_summary()
                elif choice.lower() in ['test', 'auto', '🧪']:
                    await self.run_all_tests()
                elif choice.lower() in ['exit', 'quit', 'q', 'x', '❌']:
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice! Please try again.")
                
                input("\n⏸️ Press Enter to continue...")
                
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Goodbye!")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
        finally:
            await self.disconnect()

async def main():
    """Main entry point"""
    print("🚀 Starting Interactive MCP Client...")
    client = InteractiveMCPClient()
    await client.run()

if __name__ == "__main__":
    asyncio.run(main())
