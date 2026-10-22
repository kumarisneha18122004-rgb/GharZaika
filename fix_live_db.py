
import psycopg2
from getpass import getpass

try:
    password = getpass("Local PostgreSQL password: ")

    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="gharzaika_db",
        user="postgres",
        password="Vidisha@123"
    )

    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)
            FROM public.food_items;
        """)
        print("\nLOCAL DATABASE MEIN TOTAL FOODS:", cur.fetchone()[0])

        cur.execute("""
            SELECT id, name, available
            FROM public.food_items
            ORDER BY id;
        """)

        print("\nFOOD ITEMS KI LIST:")
        for food in cur.fetchall():
            print(food)

    conn.close()
    print("\nDatabase check complete. Koi data change nahi kiya.")

except Exception as e:
    print("ERROR:", e)
