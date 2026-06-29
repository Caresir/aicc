import os
import time
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/aicc")
MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), "memory", "migrations")


def wait_for_postgres(max_retries=30):
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(DATABASE_URL)
            conn.close()
            print("Postgres is ready.")
            return
        except Exception as e:
            print(f"Waiting for postgres ({i+1}/{max_retries})... {e}")
            time.sleep(2)
    raise RuntimeError("Postgres not available after waiting.")


def run_migrations():
    wait_for_postgres()
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cursor = conn.cursor()
    for filename in sorted(os.listdir(MIGRATIONS_DIR)):
        if not filename.endswith(".sql"):
            continue
        path = os.path.join(MIGRATIONS_DIR, filename)
        with open(path) as f:
            sql = f.read()
        try:
            cursor.execute(sql)
            print(f"Migration applied: {filename}")
        except Exception as e:
            print(f"Migration {filename} skipped (already applied or error): {e}")
    cursor.close()
    conn.close()


if __name__ == "__main__":
    run_migrations()
