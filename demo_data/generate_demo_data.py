#!/usr/bin/env python3
"""
Demo Data Generator for Application Usage MCP System

This script generates realistic demo data for testing the MCP system:
- 50,000 usage records
- 150 unique users
- 5 applications across different categories
- All supported platforms
- Data spanning last 2 years (July 27, 2023 to July 27, 2025)
- Realistic usage patterns with seasonal variations
"""

import sys
import os
import random
import sqlite3
from datetime import datetime, timedelta, date
from typing import List, Dict, Tuple
import json

# Add parent directory to path to import our modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Change working directory to parent to fix relative paths
os.chdir(parent_dir)

from database.db_manager import DatabaseManager
from config.settings import DB_PATH


class DemoDataGenerator:
    def __init__(self):
        self.db_manager = DatabaseManager()
        
        # Configuration
        self.total_records = 50000
        self.num_users = 150
        self.start_date = date(2023, 7, 27)  # 2 years ago
        self.end_date = date(2025, 7, 27)    # Today
        
        # Indian names for realistic user generation
        self.indian_boy_names = [
            "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan",
            "Shaurya", "Atharv", "Advik", "Pranav", "Vedant", "Kabir", "Aryan", "Yuvan", "Shreyas", "Arnav",
            "Daksh", "Veer", "Rudra", "Shivansh", "Kian", "Darsh", "Raghav", "Rian", "Kiaan", "Armaan",
            "Samarth", "Agastya", "Aarush", "Krish", "Tanish", "Moksh", "Viraaj", "Aayan", "Aadhya", "Keshav",
            "Dhruv", "Nivaan", "Tejas", "Yash", "Harsh", "Laksh", "Mohammad", "Vihang", "Parth", "Aaryan",
            "Devansh", "Advaith", "Ishaq", "Advay", "Aaditya", "Vivek", "Ansh", "Manan", "Karthik", "Ravi",
            "Surya", "Manav", "Rohan", "Nikhil", "Rahul", "Akash", "Varun", "Abhishek", "Rajesh", "Suresh",
            "Deepak", "Anil", "Ajay", "Pradeep", "Vinod", "Mukesh"
        ]
        
        self.indian_girl_names = [
            "Saanvi", "Ananya", "Diya", "Aadhya", "Kiara", "Anika", "Kavya", "Priya", "Ira", "Myra",
            "Sara", "Pari", "Avni", "Riya", "Siya", "Khushi", "Ishika", "Arya", "Tara", "Zara",
            "Navya", "Pihu", "Aarohi", "Mahika", "Sana", "Vanya", "Nisha", "Charvi", "Shanaya", "Larisa",
            "Aradhya", "Anvi", "Aditi", "Sia", "Mishka", "Mira", "Aarna", "Anya", "Ahana", "Ishita",
            "Tanvi", "Kyra", "Amaira", "Rhea", "Mahi", "Krisha", "Aarya", "Kaia", "Maira", "Samara",
            "Anushka", "Sneha", "Pooja", "Divya", "Shreya", "Meera", "Kavitha", "Lakshmi", "Deepika", "Swathi",
            "Vidya", "Sushma", "Geeta", "Rekha", "Sunita", "Shanti", "Radha", "Usha", "Lata", "Kiran",
            "Seema", "Madhuri", "Ritu", "Neha", "Shilpa"
        ]
        
        # Application definitions with realistic versions and usage patterns
        self.applications = [
            {
                "name": "chrome",
                "category": "browser",
                "versions": ["118.0.5993.117", "119.0.6045.105", "120.0.6099.129", "121.0.6167.139", "122.0.6261.112"],
                "platforms": ["Windows", "macOS", "Linux"],
                "usage_weight": 35,  # 35% of total usage
                "avg_session_minutes": 45,
                "legacy_probability": 0.05
            },
            {
                "name": "vscode",
                "category": "development",
                "versions": ["1.84.2", "1.85.1", "1.86.0", "1.87.2", "1.88.1"],
                "platforms": ["Windows", "macOS", "Linux"],
                "usage_weight": 25,  # 25% of total usage
                "avg_session_minutes": 120,
                "legacy_probability": 0.02
            },
            {
                "name": "firefox",
                "category": "browser", 
                "versions": ["119.0", "120.0.1", "121.0", "122.0.1", "123.0"],
                "platforms": ["Windows", "macOS", "Linux"],
                "usage_weight": 20,  # 20% of total usage
                "avg_session_minutes": 38,
                "legacy_probability": 0.08
            },
            {
                "name": "slack",
                "category": "communication",
                "versions": ["4.34.119", "4.35.126", "4.36.134", "4.37.141", "4.38.125"],
                "platforms": ["Windows", "macOS"],
                "usage_weight": 15,  # 15% of total usage
                "avg_session_minutes": 25,
                "legacy_probability": 0.03
            },
            {
                "name": "notepad",
                "category": "text_editor",
                "versions": ["10.0.19041.1", "10.0.19041.2", "10.0.22000.1", "11.0.22621.1", "11.0.22621.2"],
                "platforms": ["Windows"],
                "usage_weight": 5,   # 5% of total usage
                "avg_session_minutes": 15,
                "legacy_probability": 0.25
            }
        ]
        
        # Platform definitions with usage distribution
        self.platforms = [
            {"name": "Windows", "weight": 60, "monitor_versions": ["1.0.0", "1.0.1", "1.1.0"]},
            {"name": "macOS", "weight": 25, "monitor_versions": ["1.0.0", "1.0.1", "1.1.0"]},
            {"name": "Linux", "weight": 10, "monitor_versions": ["1.0.0", "1.0.1", "1.1.0"]},
            {"name": "Android", "weight": 3, "monitor_versions": ["1.0.0", "1.0.1"]},
            {"name": "iOS", "weight": 2, "monitor_versions": ["1.0.0", "1.0.1"]}
        ]
        
        # Generate user base with realistic patterns
        self.users = self._generate_users()
        
        print(f"🎯 Demo Data Generator Initialized")
        print(f"📊 Target: {self.total_records:,} records")
        print(f"👥 Users: {self.num_users}")
        print(f"💻 Applications: {len(self.applications)}")
        print(f"🖥️  Platforms: {len(self.platforms)}")
        print(f"📅 Date Range: {self.start_date} to {self.end_date}")

    def _generate_users(self) -> List[Dict]:
        """Generate realistic user profiles with Indian names and different usage patterns."""
        user_types = [
            {"count": 30, "activity_level": "high", "app_preference": "development"},
            {"count": 20, "activity_level": "medium", "app_preference": "mixed"},
            {"count": 25, "activity_level": "medium", "app_preference": "creative"},
            {"count": 35, "activity_level": "low", "app_preference": "communication"},
            {"count": 40, "activity_level": "medium", "app_preference": "browser"}
        ]
        
        users = []
        
        # Shuffle names to ensure random distribution
        all_names = self.indian_boy_names + self.indian_girl_names
        random.shuffle(all_names)
        name_index = 0
        
        for user_type in user_types:
            for i in range(user_type["count"]):
                # Get next Indian name, cycling through if needed
                indian_name = all_names[name_index % len(all_names)]
                name_index += 1
                
                user = {
                    "name": indian_name,
                    "activity_level": user_type["activity_level"],
                    "app_preference": user_type["app_preference"],
                    "platform_preference": self._assign_platform_preference(),
                    "start_date": self._random_start_date(),
                    "active_probability": self._get_activity_probability(user_type["activity_level"])
                }
                users.append(user)
        
        return users

    def _assign_platform_preference(self) -> str:
        """Assign platform preference based on realistic distribution."""
        rand = random.random() * 100
        cumulative = 0
        for platform in self.platforms:
            cumulative += platform["weight"]
            if rand <= cumulative:
                return platform["name"]
        return "Windows"  # Fallback

    def _random_start_date(self) -> date:
        """Generate a random start date for user activity."""
        # Users can start using the system at any point in the last 2 years
        days_range = (self.end_date - self.start_date).days
        random_days = random.randint(0, days_range - 30)  # At least 30 days of potential activity
        return self.start_date + timedelta(days=random_days)

    def _get_activity_probability(self, level: str) -> float:
        """Get daily activity probability based on activity level."""
        levels = {
            "high": 0.85,    # Active 85% of days
            "medium": 0.60,  # Active 60% of days
            "low": 0.35      # Active 35% of days
        }
        return levels.get(level, 0.50)

    def _get_weekday_multiplier(self, date_obj: date) -> float:
        """Get usage multiplier based on day of week."""
        weekday = date_obj.weekday()
        if weekday < 5:  # Monday to Friday
            return 1.0
        elif weekday == 5:  # Saturday
            return 0.3
        else:  # Sunday
            return 0.2

    def _get_seasonal_multiplier(self, date_obj: date) -> float:
        """Get usage multiplier based on season/holidays."""
        month = date_obj.month
        day = date_obj.day
        
        # Holiday periods (reduced usage)
        if (month == 12 and day > 20) or (month == 1 and day < 5):  # Christmas/New Year
            return 0.4
        elif month == 7 or month == 8:  # Summer vacation
            return 0.7
        elif month == 11 and 20 <= day <= 30:  # Thanksgiving week
            return 0.6
        else:
            return 1.0

    def _generate_session_duration(self, app: Dict, user: Dict) -> int:
        """Generate realistic session duration based on app and user patterns."""
        base_minutes = app["avg_session_minutes"]
        
        # User activity level affects session length
        activity_multipliers = {"high": 1.3, "medium": 1.0, "low": 0.7}
        multiplier = activity_multipliers[user["activity_level"]]
        
        # Add some randomness (±50%)
        random_factor = random.uniform(0.5, 1.5)
        
        minutes = int(base_minutes * multiplier * random_factor)
        
        # Ensure minimum 1 minute, maximum 8 hours
        minutes = max(1, min(minutes, 480))
        
        return minutes * 60  # Convert to seconds

    def _select_application_for_user(self, user: Dict) -> Dict:
        """Select an application based on user preferences and app weights."""
        
        # Adjust weights based on user preferences
        adjusted_apps = []
        for app in self.applications:
            weight = app["usage_weight"]
            
            # Boost weight for preferred app categories
            if user["app_preference"] == "development" and app["category"] == "development":
                weight *= 2.5
            elif user["app_preference"] == "browser" and app["category"] == "browser":
                weight *= 2.0
            elif user["app_preference"] == "communication" and app["category"] == "communication":
                weight *= 3.0
            elif user["app_preference"] == "creative" and app["name"] in ["code.exe"]:
                weight *= 1.5
            elif user["app_preference"] == "mixed":
                weight *= 1.1  # Slight boost to all apps
                
            adjusted_apps.extend([app] * int(weight))
        
        return random.choice(adjusted_apps)

    def _select_platform_for_app(self, app: Dict, user: Dict) -> str:
        """Select platform based on app compatibility and user preference."""
        available_platforms = app["platforms"]
        
        # If user's preferred platform is available, use it most of the time
        if user["platform_preference"] in available_platforms:
            if random.random() < 0.8:  # 80% chance to use preferred platform
                return user["platform_preference"]
        
        # Otherwise, select randomly from available platforms
        return random.choice(available_platforms)

    def generate_records(self) -> List[Tuple]:
        """Generate all demo records with realistic patterns."""
        records = []
        current_date = self.start_date
        
        print(f"\n🔄 Generating {self.total_records:,} records...")
        
        # Calculate records per day
        total_days = (self.end_date - current_date).days + 1
        base_records_per_day = (self.total_records * 1.5) // total_days  # Increased multiplier to account for weekends/holidays
        
        generated_count = 0
        
        while current_date <= self.end_date and generated_count < self.total_records:
            # Calculate daily record count with multipliers
            weekday_mult = self._get_weekday_multiplier(current_date)
            seasonal_mult = self._get_seasonal_multiplier(current_date)
            daily_records = int(base_records_per_day * weekday_mult * seasonal_mult)
            
            # Ensure minimum records per day to reach target
            min_daily_records = max(1, self.total_records // (total_days * 2))
            daily_records = max(daily_records, min_daily_records)
            
            # Ensure we don't exceed total target
            remaining_records = self.total_records - generated_count
            daily_records = min(daily_records, remaining_records)
            
            # Generate records for this day
            daily_generated = 0
            attempts = 0
            max_attempts = daily_records * 3  # Allow more attempts to reach target
            
            while daily_generated < daily_records and attempts < max_attempts and generated_count < self.total_records:
                attempts += 1
                
                # Select user (only if they were active by this date)
                active_users = [u for u in self.users if u["start_date"] <= current_date]
                if not active_users:
                    continue
                    
                user = random.choice(active_users)
                
                # More lenient activity check - reduce the randomness for low activity users
                activity_threshold = user["active_probability"]
                if user["activity_level"] == "low":
                    activity_threshold = min(0.6, activity_threshold * 1.5)  # Boost low activity users
                
                if random.random() > activity_threshold:
                    continue
                
                # Select application and platform
                app = self._select_application_for_user(user)
                platform = self._select_platform_for_app(app, user)
                
                # Generate record data
                record = (
                    random.choice(self._get_platform_monitor_versions(platform)),  # monitor_app_version
                    platform,                                                      # platform
                    user["name"],                                                 # user
                    app["name"],                                                  # application_name
                    random.choice(app["versions"]),                              # application_version
                    current_date.strftime("%Y-%m-%d"),                          # log_date
                    1 if random.random() < app["legacy_probability"] else 0,    # legacy_app
                    self._generate_session_duration(app, user)                   # duration_seconds
                )
                
                records.append(record)
                generated_count += 1
                daily_generated += 1
                
                # Progress indicator
                if generated_count % 5000 == 0:
                    progress = (generated_count / self.total_records) * 100
                    print(f"  📈 Progress: {generated_count:,}/{self.total_records:,} ({progress:.1f}%)")
            
            current_date += timedelta(days=1)
        
        print(f"✅ Generated {len(records):,} records")
        return records

    def _get_platform_monitor_versions(self, platform_name: str) -> List[str]:
        """Get available monitor versions for a platform."""
        for platform in self.platforms:
            if platform["name"] == platform_name:
                return platform["monitor_versions"]
        return ["1.0.0"]  # Fallback

    def populate_database(self):
        """Generate and insert all demo data into the database."""
        try:
            print(f"\n🔌 Connecting to database...")
            self.db_manager.connect()
            self.db_manager.initialize_database()
            
            # Clear existing data
            print(f"🧹 Clearing existing data...")
            cursor = self.db_manager.conn.cursor()
            cursor.execute("DELETE FROM usage_data")
            self.db_manager.conn.commit()
            
            # Generate records
            records = self.generate_records()
            
            # Insert records in batches for better performance
            print(f"\n💾 Inserting records into database...")
            batch_size = 1000
            total_batches = (len(records) + batch_size - 1) // batch_size
            
            insert_sql = """
                INSERT INTO usage_data 
                (monitor_app_version, platform, user, application_name, application_version, 
                 log_date, legacy_app, duration_seconds)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                cursor.executemany(insert_sql, batch)
                self.db_manager.conn.commit()
                
                batch_num = (i // batch_size) + 1
                print(f"  📦 Batch {batch_num}/{total_batches} completed ({len(batch)} records)")
            
            # Generate summary statistics
            print(f"\n📊 Generating summary statistics...")
            self._print_summary_statistics()
            
            print(f"\n🎉 Demo data generation completed successfully!")
            print(f"📍 Database location: {DB_PATH}")
            
        except Exception as e:
            print(f"❌ Error during data generation: {e}")
            raise
        finally:
            self.db_manager.disconnect()

    def _print_summary_statistics(self):
        """Print summary statistics of generated data."""
        cursor = self.db_manager.conn.cursor()
        
        # Basic counts
        cursor.execute("SELECT COUNT(*) FROM usage_data")
        total_records = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT user) FROM usage_data")
        unique_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT application_name) FROM usage_data")
        unique_apps = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT platform) FROM usage_data")
        unique_platforms = cursor.fetchone()[0]
        
        cursor.execute("SELECT MIN(log_date), MAX(log_date) FROM usage_data")
        date_range = cursor.fetchone()
        
        cursor.execute("SELECT SUM(duration_seconds) FROM usage_data")
        total_duration = cursor.fetchone()[0]
        
        print(f"📋 SUMMARY STATISTICS")
        print(f"  📝 Total Records: {total_records:,}")
        print(f"  👥 Unique Users: {unique_users}")
        print(f"  💻 Applications: {unique_apps}")
        print(f"  🖥️  Platforms: {unique_platforms}")
        print(f"  📅 Date Range: {date_range[0]} to {date_range[1]}")
        print(f"  ⏱️  Total Usage: {total_duration:,} seconds ({total_duration/3600:.1f} hours)")
        
        # Top applications
        cursor.execute("""
            SELECT application_name, COUNT(*) as sessions, SUM(duration_seconds) as total_time
            FROM usage_data 
            GROUP BY application_name 
            ORDER BY sessions DESC
        """)
        
        print(f"\n📊 APPLICATION BREAKDOWN:")
        for app_name, sessions, total_time in cursor.fetchall():
            percentage = (sessions / total_records) * 100
            hours = total_time / 3600
            print(f"  {app_name}: {sessions:,} sessions ({percentage:.1f}%), {hours:.1f} hours")
        
        # Platform distribution
        cursor.execute("""
            SELECT platform, COUNT(*) as sessions
            FROM usage_data 
            GROUP BY platform 
            ORDER BY sessions DESC
        """)
        
        print(f"\n🖥️  PLATFORM DISTRIBUTION:")
        for platform, sessions in cursor.fetchall():
            percentage = (sessions / total_records) * 100
            print(f"  {platform}: {sessions:,} sessions ({percentage:.1f}%)")


def main():
    """Main function to run the demo data generator."""
    print("🚀 Application Usage MCP - Demo Data Generator")
    print("=" * 60)
    
    try:
        generator = DemoDataGenerator()
        generator.populate_database()
        
        print(f"\n✨ Demo data generation completed!")
        print(f"📖 You can now use the interactive client to explore the data:")
        print(f"   cd examples")
        print(f"   python interactive_client.py")
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
