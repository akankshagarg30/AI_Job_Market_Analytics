from connection import get_connection


try:

    connection = get_connection()

    print("PostgreSQL connection successful!")

    cursor = connection.cursor()

    cursor.execute(
        "SELECT current_database(), current_user;"
    )

    result = cursor.fetchone()

    print("Database:", result[0])
    print("User:", result[1])

    cursor.close()
    connection.close()

    print("Connection closed successfully.")

except Exception as error:

    print("Database connection failed.")
    print("Error:", error)