
import os
import psycopg2

try:
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("ERROR: DATABASE_URL set nahi hai.")
        print("Pehle Render connection setup karna hoga.")
    else:
        conn = psycopg2.connect(database_url)

        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, available
                FROM public.food_items
                ORDER BY id;
            """)

            print("\nLIVE DATABASE KE FOOD ITEMS:")
            for food in cur.fetchall():
                print(food)

            cur.execute("""
                SELECT COUNT(*)
                FROM public.order_items;
            """)

            print(
                "\nEXISTING ORDER ITEMS:",
                cur.fetchone()[0]
            )

        conn.close()
        print("\nCheck complete. Koi data change nahi kiya.")

except Exception as e:
    print("ERROR:", e)
