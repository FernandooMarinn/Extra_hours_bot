import sqlite3


def introduce_daily_user_to_database(telegram_id, user: dict):
    total_per_hour = user["payment_per_hour"]
    connection = sqlite3.connect("daily_users.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO daily_users(telegram_id, total_per_hour)
        VALUES(?, ?)
    """, (telegram_id, total_per_hour))

    connection.commit()

    connection.close()


def check_and_return_daily_user(telegram_id):
    connection = sqlite3.connect("daily_users.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM daily_users WHERE telegram_id = ?", (telegram_id,))

    result = cursor.fetchone()
    connection.close()

    if result is None:
        print("No ha encontrado nada en la base de datos")
        return False
    else:
        print("Ha encontrado algo en la base de datos.")
        print(result)
        print(result[0])
        print(result[1])
        payment_per_hour = result[1]
        return payment_per_hour


def delete_daily_user(telegram_id):
    connection = sqlite3.connect("daily_users.db")
    cursor = connection.cursor()

    cursor.execute("DELETE FROM daily_users WHERE telegram_id = ?", (telegram_id,))
    connection.commit()
    #  To know if we deleted anything
    connection.close()
    return cursor.rowcount