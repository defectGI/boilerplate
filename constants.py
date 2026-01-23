#Paths
PATH_AUTH_LOGIN = "/AUTH/LOGIN"
PATH_AUTH_REFRESH = "/AUTH/REFRESH"
PATH_AUTH_LOGOUT = "/AUTH/LOGOUT"
PATH_AUTH_ME = "/AUTH/ME"

#DB / Env
DATABASE_URL = "sqlite:///./datalocal/database.db"
ENV_SECRET_KEY = "SECRET_KEY"

#SQL queries
SQL_SELECT_USER_BY_EMAIL = "SELECT * FROM users WHERE email = :email"
SQL_SELECT_USER_BY_ID = "SELECT * FROM users WHERE id = :id"
SQL_UPDATE_REFRESH_BY_EMAIL = "UPDATE users SET refresh_token = :refresh WHERE email = :email"
SQL_UPDATE_REFRESH_NULL_BY_EMAIL = "UPDATE users SET refresh_token = :refresh WHERE email = :email"
SQL_UPDATE_SET_USER_ACTIVE ="UPDATE users SET is_active = 1 WHERE email = :email"
SQL_UPDATE_SET_USER_INACTIVE ="UPDATE users SET is_active = 0 WHERE email = :email"
SQL_UPDATE_LAST_LOGIN="UPDATE users SET last_login_at = :date WHERE email = :email"


#Token Creation
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
refresh_token_creation_query="UPDATE users SET refresh_token= :refresh WHERE email = :email"
