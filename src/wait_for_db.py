import os
import time

import psycopg2
from psycopg2 import OperationalError


def wait_for_db():
    """Ждёт, пока Postgres станет доступен, используя переменные окружения."""

    dbname = os.getenv("POSTGRES_DB")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST", "db")  # fallback
    port = os.getenv("POSTGRES_PORT", "5432")

    while True:
        try:
            conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port,
            )
            conn.close()
            print("✅ Database is ready!")
            break
        except OperationalError as e:
            print(f"⏳ Waiting for database… ({e})")
            time.sleep(2)


if __name__ == "__main__":
    wait_for_db()
