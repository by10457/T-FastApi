-- 初始化数据库（如果还没建库，先手动执行这里）
-- CREATE DATABASE IF NOT EXISTS your_database CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE your_database;

-- 以下表结构由 aerich 迁移管理，此文件可放一些初始化数据
-- 例如：插入默认管理员账号、基础配置数据等

-- 示例：初始化超级管理员（密码 admin123，需替换为 bcrypt 哈希值）
-- INSERT IGNORE INTO users (username, email, hashed_password, is_active, is_superuser)
-- VALUES ('admin', 'admin@example.com', '$2b$12$...', 1, 1);
