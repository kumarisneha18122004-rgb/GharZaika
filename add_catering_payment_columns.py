
from main import get_db_connection

conn = None
cur = None

try:
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        ALTER TABLE catering_bookings
        ADD COLUMN IF NOT EXISTS advance_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
        ADD COLUMN IF NOT EXISTS balance_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
        ADD COLUMN IF NOT EXISTS payment_status VARCHAR(30) NOT NULL DEFAULT 'pending',
        ADD COLUMN IF NOT EXISTS payment_id VARCHAR(150);
    """)

    cur.execute("""
        UPDATE catering_bookings
        SET advance_amount = ROUND(estimated_amount * 0.25, 2),
            balance_amount = ROUND(estimated_amount * 0.75, 2)
        WHERE advance_amount = 0
          AND balance_amount = 0
          AND estimated_amount > 0;
    """)

    conn.commit()
    print("Success! Payment columns add ho gaye.")
    print("Existing bookings safe hain.")

except Exception as e:
    if conn:
        conn.rollback()
    print("Error:", e)

finally:
    if cur:
        cur.close()
    if conn:
        conn.close()
