
import psycopg2
from getpass import getpass

try:
    password = getpass("PostgreSQL password: ")

    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="gharzaika_db",
        user="postgres",
        password=password,
        connect_timeout=10
    )

    cur = conn.cursor()

    cur.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'food_items'
        ORDER BY ordinal_position;
    """)

    columns = cur.fetchall()

    print("\nDatabase connection successful!")
    print("Food_items table ke columns:")

    for column in columns:
        print(column[0])

    cur.close()
    conn.close()

except Exception as e:
    print("Error:", e)
