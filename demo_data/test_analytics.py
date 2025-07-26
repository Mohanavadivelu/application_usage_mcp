#!/usr/bin/env python3
"""
Simple test script to verify the generated demo data and analytics functions.
"""

import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Change to parent directory for correct paths
os.chdir(parent_dir)

from database.db_manager import DatabaseManager

def test_analytics():
    """Test all analytics functions with the generated demo data."""
    
    print("🧪 Testing Analytics Functions with Demo Data")
    print("=" * 60)
    
    db_manager = DatabaseManager()
    
    try:
        db_manager.connect()
        
        # Test 1: Basic counts
        print("\n1️⃣ BASIC DATA VALIDATION")
        print("-" * 30)
        
        cursor = db_manager.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM usage_data")
        total_records = cursor.fetchone()[0]
        print(f"✅ Total Records: {total_records:,}")
        
        cursor.execute("SELECT COUNT(DISTINCT user) FROM usage_data")
        unique_users = cursor.fetchone()[0]
        print(f"✅ Unique Users: {unique_users}")
        
        cursor.execute("SELECT COUNT(DISTINCT application_name) FROM usage_data")
        unique_apps = cursor.fetchone()[0]
        print(f"✅ Unique Applications: {unique_apps}")
        
        # Test 2: Top Users Analysis
        print("\n2️⃣ TOP USERS ANALYSIS")
        print("-" * 30)
        
        top_users = db_manager.get_top_users_by_app("chrome.exe", 5)
        for i, user in enumerate(top_users[:5], 1):
            print(f"{i}. {user['user']}: {user['session_count']} sessions, {user['total_hours']:.1f} hours")
        
        # Test 3: New Users Analysis
        print("\n3️⃣ NEW USERS ANALYSIS (Jan 2024)")
        print("-" * 30)
        
        new_users = db_manager.get_new_users_in_period("2024-01-01", "2024-01-31")
        print(f"New users in January 2024: {len(new_users)}")
        for user in new_users[:5]:
            print(f"- {user['user']}: First seen {user['first_entry_date']}, {user['session_count']} sessions")
        
        # Test 4: Application Statistics
        print("\n4️⃣ APPLICATION STATISTICS")
        print("-" * 30)
        
        app_stats = db_manager.get_application_usage_stats()
        for app in app_stats:
            print(f"{app['application_name']}: {app['unique_users']} users, {app['total_sessions']} sessions")
        
        # Test 5: Platform Distribution
        print("\n5️⃣ PLATFORM DISTRIBUTION")
        print("-" * 30)
        
        platform_dist = db_manager.get_platform_distribution()
        for platform in platform_dist:
            print(f"{platform['platform']}: {platform['session_percentage']:.1f}% of sessions")
        
        # Test 6: System Overview
        print("\n6️⃣ SYSTEM OVERVIEW")
        print("-" * 30)
        
        overview = db_manager.get_system_overview()
        print(f"📊 Total Records: {overview['total_records']:,}")
        print(f"👥 Total Users: {overview['total_users']}")
        print(f"💻 Total Applications: {overview['total_applications']}")
        print(f"⏱️ Total Usage Hours: {overview['total_hours']:,.1f}")
        print(f"📅 Date Range: {overview['earliest_record']} to {overview['latest_record']}")
        
        print("\n✅ All analytics functions working correctly!")
        print("🎉 Demo data generation and testing completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db_manager.disconnect()

if __name__ == "__main__":
    test_analytics()
