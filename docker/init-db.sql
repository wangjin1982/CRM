-- 初始化数据库脚本
-- 设置时区
SET timezone = 'Asia/Shanghai';

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- 用于模糊搜索

-- 授予权限
GRANT ALL PRIVILEGES ON DATABASE crm_db TO crm_user;
