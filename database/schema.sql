-- Application Usage Data Schema
-- Updated schema for monitoring application usage across platforms

CREATE TABLE IF NOT EXISTS usage_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    monitor_app_version TEXT NOT NULL,        -- Version of the monitoring tool that logged the data
    platform TEXT NOT NULL,                  -- Operating system (e.g., Windows, macOS, Android)
    user TEXT NOT NULL,                       -- Username or device ID
    application_name TEXT NOT NULL,           -- Name of the application (e.g., chrome.exe)
    application_version TEXT NOT NULL,        -- Application version number
    log_date TEXT NOT NULL,                   -- ISO 8601 timestamp (YYYY-MM-DDTHH:MM:SSZ)
    legacy_app BOOLEAN NOT NULL,              -- Indicates if the application is legacy (true/false)
    duration_seconds INTEGER NOT NULL        -- Usage time in seconds
);

-- Create index for common queries
CREATE INDEX IF NOT EXISTS idx_usage_app ON usage_data(application_name);
CREATE INDEX IF NOT EXISTS idx_usage_user ON usage_data(user);
CREATE INDEX IF NOT EXISTS idx_usage_date ON usage_data(log_date);
CREATE INDEX IF NOT EXISTS idx_usage_platform ON usage_data(platform);

-- Migration: If old table exists, migrate data
-- This will be handled by the database manager during initialization
