# config/settings.py
import os

# Database Settings
DB_NAME = "usage.db"
# Use absolute path to avoid working directory issues
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(_PROJECT_ROOT, DB_NAME)
SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "database", "schema.sql")

# MCP Settings
MCP_HOST = "127.0.0.1"
MCP_PORT = 58889  # Use a different port to avoid conflicts
