-- Runs after Supabase migrate.sh (zz sorts after m) — creates AICC application databases
-- postgres superuser is already created by migrate.sh; no GRANT needed for superusers
SELECT 'CREATE DATABASE aicc' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'aicc')\gexec
SELECT 'CREATE DATABASE n8n'  WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'n8n')\gexec

-- Application services connect as the postgres role; grant it full access
-- to their databases (PostgreSQL 15+ restricts public schema CREATE by default)
\c aicc
GRANT ALL ON SCHEMA public TO postgres;
ALTER DATABASE aicc OWNER TO postgres;
\c n8n
GRANT ALL ON SCHEMA public TO postgres;
ALTER DATABASE n8n OWNER TO postgres;
\c postgres

-- Required by supabase/realtime — it sets search_path to _realtime before running its own migrations
CREATE SCHEMA IF NOT EXISTS _realtime;
GRANT ALL ON SCHEMA _realtime TO supabase_admin, postgres;
