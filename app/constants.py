import os
#Paths
PATH_AUTH_LOGIN = "/auth/login"
PATH_AUTH_REFRESH = "/auth/refresh"
PATH_AUTH_LOGOUT = "/auth/logout"
PATH_AUTH_ME = "/auth/me"
PATH_HEALTH = "/health"
#DB / Env
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////app/data/database.db")
TEST_DATABASE_URL = "sqlite:///test_database.db"
ENV_SECRET_KEY = os.getenv("SECRET_KEY")

#SQL queries
INSERT_USER_QUERY = """
        INSERT INTO users (email, password_hash, role, is_active)
        VALUES (:email, :password_hash, :role, :is_active)
    """
SQL_SELECT_USER_BY_EMAIL = "SELECT * FROM users WHERE email = :email"
SQL_SELECT_USER_BY_ID = "SELECT * FROM users WHERE id = :id"
SQL_UPDATE_REFRESH_BY_EMAIL = "UPDATE users SET refresh_token = :refresh WHERE email = :email"
SQL_UPDATE_REFRESH_NULL_BY_EMAIL = "UPDATE users SET refresh_token = :refresh WHERE email = :email"
SQL_UPDATE_SET_USER_ACTIVE ="UPDATE users SET is_active = 1 WHERE email = :email"
SQL_UPDATE_SET_USER_INACTIVE ="UPDATE users SET is_active = 0 WHERE email = :email"
SQL_UPDATE_LAST_LOGIN="UPDATE users SET last_login_at = :date WHERE email = :email"
SQL_SELECT_HEALTH="SELECT 1"
REFRESH_TOKEN_CREATION_QUERY="UPDATE users SET refresh_token = :refresh, refresh_token_expire = :expire WHERE email = :email"
SQL_UPDATE_LOGIN_ATTEMPT="""INSERT INTO login_attempts (ip_address, email, attempt_count, first_attempt, last_attempt)
VALUES (:ip_address, :email, 1, datetime('now'), datetime('now'))
ON CONFLICT(ip_address) DO UPDATE SET
  email = excluded.email,
  attempt_count =
    CASE
      WHEN login_attempts.first_attempt < datetime('now','-5 minutes') THEN 1
      ELSE login_attempts.attempt_count + 1
    END,
  first_attempt =
    CASE
      WHEN login_attempts.first_attempt < datetime('now','-5 minutes') THEN datetime('now')
      ELSE login_attempts.first_attempt
    END,
  last_attempt = datetime('now');
 """
SQL_COUNT_LOGINS_LAST_FIVE_MINUTES="""SELECT attempt_count
FROM login_attempts
WHERE ip_address = :ip_address;
"""
SQL_VALIDATE_REFRESH="SELECT 1 FROM users  WHERE id = :id AND refresh_token = :token AND refresh_token_expire > datetime('NOW')"
INSERT_TEST_USER = """
    INSERT INTO users (email, password_hash, role, is_active, created_at, updated_at, refresh_token, refresh_token_expire, last_login_at, failed_login_count, locked_until)
    VALUES (:email, :password_hash, :role, 1, datetime('now'), datetime('now'), '', NULL, NULL, 0, NULL)
"""


#Token Creation
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

