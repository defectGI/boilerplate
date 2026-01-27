    CREATE TABLE users (
        id INTEGER NOT NULL,
        email VARCHAR NOT NULL,
        password_hash VARCHAR NOT NULL,
        role VARCHAR,
        is_active INTEGER,
        created_at DATETIME,
        updated_at DATETIME, refresh_token TEXT, last_login_at DATETIME, failed_login_count INTEGER DEFAULT 0, locked_until DATETIME,
        PRIMARY KEY (id)
    );
    CREATE TABLE login_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip_address TEXT NOT NULL UNIQUE,
        email TEXT,
        attempt_count INTEGER DEFAULT 1,
        first_attempt DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_attempt DATETIME DEFAULT CURRENT_TIMESTAMP,
        locked_until DATETIME
    );