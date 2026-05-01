-- 初始化数据库（如果还没建库，先手动执行这里）
-- CREATE DATABASE IF NOT EXISTS your_database CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE your_database;

-- 以下表结构由 aerich 迁移管理，此文件可放一些初始化数据
-- 例如：插入默认管理员账号、基础配置数据等

-- 当前模板内置用户表结构，对应 models/user.py。
-- 生产环境推荐通过 aerich 迁移生成和维护表结构；此处用于初始化参考或手动建表。
CREATE TABLE IF NOT EXISTS `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `updated_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  `username` varchar(64) NOT NULL COMMENT '用户名',
  `email` varchar(128) NOT NULL COMMENT '邮箱',
  `hashed_password` varchar(256) NOT NULL COMMENT '哈希密码',
  `is_active` tinyint(1) NOT NULL DEFAULT '1' COMMENT '是否激活',
  `is_superuser` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否超级管理员',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 示例：初始化超级管理员（密码 admin123，需替换为 bcrypt 哈希值）
-- INSERT IGNORE INTO users (username, email, hashed_password, is_active, is_superuser)
-- VALUES ('admin', 'admin@example.com', '$2b$12$...', 1, 1);
