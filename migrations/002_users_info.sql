INSERT INTO users (id, email, password_hash, role, is_active, created_at, updated_at, refresh_token,refresh_token_expire ,last_login_at, failed_login_count, locked_until)
VALUES (
    1,
    'admin@gmail.com',
    '$argon2id$v=19$m=64,t=3,p=4$Q1dieExaaVhoRnZ1RUF1NA$HWVkKgvU6Ij+sg9i/UgS1qDfu7aneVFHaCnofS09Rrk', -- hash abcd
    'admin',
    1,
    datetime('now', '-2 days'),
    datetime('now'),
    ' ',
    datetime('now', '-3 days')
    ,
    datetime('now', '-1 hour'),
    0,
    NULL
);

INSERT INTO users (id, email, password_hash, role, is_active, created_at, updated_at, refresh_token, refresh_token_expire,last_login_at, failed_login_count, locked_until)
VALUES (
    2,
    'kaan@gmail.com',
    '$argon2id$v=19$m=64,t=3,p=4$Q1dieExaaVhoRnZ1RUF1NA$HWVkKgvU6Ij+sg9i/UgS1qDfu7aneVFHaCnofS09Rrk', -- hash abcd
    'user',
    1,
    datetime('now', '-3 days'),
    datetime('now', '-2 days'),
    ' ',
    datetime('now', '-5 days')
    ,
    datetime('now', '-3 hours'),
    0,
    NULL
);
