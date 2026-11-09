
from config import get_db_connection

try:
    conn = get_db_connection()

    print("MySQL connected successfully!")

    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")

    print("Tables in the database:")

    for table in cursor.fetchall():
        print(table[0])

    cursor.close()
    conn.close()

except Exception as e:
    print("Database connection failed:")
    print(e)
