-- Database initialization script for callback-listener
-- This script will be executed when the PostgreSQL container starts for the first time

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set timezone
SET timezone = 'UTC';

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE callback_listener TO callback_user;

-- Create any additional schemas if needed
-- CREATE SCHEMA IF NOT EXISTS callback_data;
