CREATE TABLE IF NOT EXISTS usage_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    monitor_app_version TEXT NOT NULL,
    platform TEXT NOT NULL,
    "user" TEXT NOT NULL,
    application_name TEXT NOT NULL,
    application_version TEXT NOT NULL,
    log_date TEXT NOT NULL,
    legacy_app BOOLEAN NOT NULL,
    duration_seconds INTEGER NOT NULL
);
