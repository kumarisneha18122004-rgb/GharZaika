import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="gharzaika_db",
        user="postgres",
        password="Vidisha@123"
    )

    print("✅ PostgreSQL connection successful!")

    conn.close()

except Exception as e:
    print("❌ PostgreSQL connection failed:")
    print(e)
