import time
import psycopg2
from psycopg2 import OperationalError


def wait_for_db():
    """Пробует подключиться к Postgres, пока тот не станет доступен."""
    while True:
        try:
            conn = psycopg2.connect(
                dbname="hotel_db",
                user="hotel_user",
                password="hotel_password",
                host="db",
                port="5432"
            )
            conn.close()
            print("✅ Database is ready!")
            break
        except OperationalError:
            print("⏳ Waiting for database to be ready...")
            time.sleep(2)


if __name__ == "__main__":
    wait_for_db()
