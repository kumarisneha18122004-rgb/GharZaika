
import os
import psycopg2
from getpass import getpass

LIVE_URL = os.environ.get("DATABASE_URL")

if not LIVE_URL:
    raise SystemExit(
        "DATABASE_URL set nahi hai. Pehle wahi terminal use karein "
        "jisme live database connection set kiya tha."
    )

local_password = getpass("Local PostgreSQL password: ")

local_conn = None
live_conn = None

try:
    # Local database se 48 food records read karein
    local_conn = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="gharzaika_db",
        user="postgres",
        password=local_password,
        connect_timeout=15,
    )

    with local_conn.cursor() as cur:
        cur.execute("""
            SELECT id, name, description, price, category,
                   TRUE AS available, created_at,
                   half_price, full_price
            FROM public.food_items
            ORDER BY id;
        """)
        local_foods = cur.fetchall()

    if len(local_foods) != 48:
        raise RuntimeError(
            f"Local database mein 48 ki jagah {len(local_foods)} foods mile. "
            "Koi live change nahi kiya gaya."
        )

    live_conn = psycopg2.connect(
        LIVE_URL,
        connect_timeout=15,
    )
    live_conn.autocommit = False

    with live_conn.cursor() as cur:
        cur.execute("""
            SELECT id, name
            FROM public.food_items
            ORDER BY id;
        """)
        live_foods = cur.fetchall()

        live_by_id = {row[0]: row[1] for row in live_foods}

        # Existing IDs ke names alag hue to stop karein
        conflicts = [
            (food[0], live_by_id[food[0]], food[1])
            for food in local_foods
            if food[0] in live_by_id
            and live_by_id[food[0]] != food[1]
        ]

        if conflicts:
            raise RuntimeError(
                f"Food ID/name conflict mila: {conflicts}. "
                "Live database mein koi change nahi kiya gaya."
            )

        missing_foods = [
            food for food in local_foods
            if food[0] not in live_by_id
        ]

        print("\n========== SYNC PREVIEW ==========")
        print("Local foods:", len(local_foods))
        print("Live foods before sync:", len(live_foods))
        print("Naye foods add honge:", len(missing_foods))
        print("Sabhi 48 foods available rakhe jayenge.")
        print("Existing food details ko overwrite nahi kiya jayega.")
        print("Orders, customers aur order_items change nahi honge.")

        for food in missing_foods:
            print(f"ADD ID {food[0]}: {food[1]}")

        if len(live_foods) > 48:
            raise RuntimeError(
                "Live database mein 48 se zyada food rows hain. "
                "Manual check zaroori hai."
            )

        confirm = input(
            "\nAgar aap live database update karna chahti hain, "
            "to SYNC type karein: "
        ).strip()

        if confirm != "SYNC":
            live_conn.rollback()
            print("Cancelled. Koi live change nahi kiya gaya.")
        else:
            # Sirf missing foods insert karein.
            # Existing IDs, prices aur names untouched rahenge.
            for food in missing_foods:
                cur.execute("""
                    INSERT INTO public.food_items (
                        id, name, description, price, category,
                        available, created_at, half_price, full_price
                    )
                    VALUES (%s, %s, %s, %s, %s, TRUE, %s, %s, %s);
                """, (
                    food[0], food[1], food[2], food[3],
                    food[4], food[6], food[7], food[8]
                ))

            # Existing five foods ko bhi available karein.
            # Kisi aur column ko change nahi karein.
            cur.execute("""
                UPDATE public.food_items
                SET available = TRUE
                WHERE id BETWEEN 1 AND 48;
            """)

            # Future auto-generated IDs ko maximum ID ke baad rakhein.
            cur.execute("""
                SELECT pg_get_serial_sequence(
                    'public.food_items', 'id'
                );
            """)
            sequence_name = cur.fetchone()[0]

            if sequence_name:
                cur.execute("""
                    SELECT setval(
                        %s::regclass,
                        (SELECT MAX(id) FROM public.food_items),
                        TRUE
                    );
                """, (sequence_name,))

            cur.execute("""
                SELECT COUNT(*)
                FROM public.food_items
                WHERE id BETWEEN 1 AND 48
                  AND available = TRUE;
            """)
            available_count = cur.fetchone()[0]

            if available_count != 48:
                raise RuntimeError(
                    f"Verification failed: {available_count} foods available."
                )

            live_conn.commit()

            print("\nSUCCESS!")
            print("Sync complete.")
            print("Available foods:", available_count)
            print("Purane orders/customers/order_items untouched rahe.")

except Exception as error:
    if live_conn is not None:
        live_conn.rollback()
    print("\nERROR:", error)
    print("Transaction rollback ki gayi; changes commit nahi hue.")

finally:
    if local_conn is not None:
        local_conn.close()
    if live_conn is not None:
        live_conn.close()
