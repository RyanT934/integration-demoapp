import os
import psycopg2
from datetime import datetime
import sys

try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        connect_timeout=5
    )

    cur = conn.cursor()
    now = datetime.now()

    cur.execute(
        "INSERT INTO app_logs (run_date, message) VALUES (%s, %s)",
        (now, "Batch executed successfully")
    )

    conn.commit()
    cur.close()
    conn.close()

except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
