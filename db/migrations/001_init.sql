-- 001_init.sql

-- USERS
CREATE TABLE users (
  id INTEGER NOT NULL,
  email VARCHAR NOT NULL,
  password_hash VARCHAR NOT NULL,
  role VARCHAR,
  is_active INTEGER,
  created_at DATETIME,
  updated_at DATETIME,
  refresh_token TEXT,
  last_login_at DATETIME,
  failed_login_count INTEGER DEFAULT 0,
  locked_until DATETIME,
  PRIMARY KEY (id)
);

-- LOGIN ATTEMPTS
CREATE TABLE login_attempts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ip_address TEXT NOT NULL,
  email TEXT,
  attempt_count INTEGER DEFAULT 1,
  first_attempt DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_attempt DATETIME DEFAULT CURRENT_TIMESTAMP,
  locked_until DATETIME
);

-- INDEXES
CREATE UNIQUE INDEX idx_login_attempts_ip
ON login_attempts(ip_address);
