-- Initialize database extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable pg_trgm for text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;
