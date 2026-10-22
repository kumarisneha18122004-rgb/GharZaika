
import psycopg2
from getpass import getpass

try:
    password = getpass("PostgreSQL password: ")

    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="gharzaika_db",
        user="postgres",
        password="Vidisha@123",
         connect_timeout=10
    )

    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS catering_bookings (
                    id SERIAL PRIMARY KEY,
                    full_name VARCHAR(150) NOT NULL,
                    mobile VARCHAR(20) NOT NULL,
                    event_type VARCHAR(80) NOT NULL,
                    package_name VARCHAR(100) NOT NULL,
                    guest_count INTEGER NOT NULL CHECK (guest_count > 0),
                    event_date DATE NOT NULL,
                    event_location TEXT NOT NULL,
                    requirements TEXT,
                    estimated_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
                    booking_status VARCHAR(30) NOT NULL DEFAULT 'pending',
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """)

    conn.close()
    print("Success: catering_bookings table ready.")

except Exception as e:
    print("Error:", e)
