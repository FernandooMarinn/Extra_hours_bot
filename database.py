import sqlite3

import table_creation

def check_and_create_tables():
    table_creation.table_creation()

def introduce_daily_user_to_database(telegram_id, user: dict):
    total_per_hour = user["payment_per_hour"]
    connection = sqlite3.connect("database/daily_users.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO daily_users(telegram_id, payment_per_hour)
        VALUES(?, ?)
    """, (telegram_id, total_per_hour))

    connection.commit()

    connection.close()


def introduce_new_user_to_database(telegram_id, user: dict):
    name = user["name"]
    start_hour = user["start_hour"]
    finish_hour = user["finish_hour"]
    payment_per_hour = user["payment_per_hour"]

    connection = sqlite3.connect("database/users.db")
    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO users(telegram_id, name, start_hour, finish_hour, payment_per_hour)
            VALUES(?, ?, ?, ?, ?)
        """, (int(telegram_id), name, start_hour, finish_hour, payment_per_hour))

        connection.commit()
        connection.close()
    except sqlite3.IntegrityError:
        connection.close()
        return False

    introduce_working_days_to_database(telegram_id, user)


def introduce_working_days_to_database(telegram_id, user: dict):
    working_days = user["work_days"]

    connection = sqlite3.connect("database/users.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO working_days(Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday)
        VALUES(?, ?, ?, ?, ?, ?, ?)
    """, (working_days["Monday"], working_days["Tuesday"], working_days["Wednesday"],
          working_days["Thursday"], working_days["Friday"], working_days["Saturday"], working_days["Sunday"]))

    connection.close()
    return True


def delete_user(telegram_id):
    print(telegram_id)
    connection = sqlite3.connect("database/users.db")
    cursor = connection.cursor()
    cursor.execute("DELETE FROM users WHERE telegram_id = ?", (telegram_id,))
    connection.commit()
    connection.close()

def check_and_return_daily_user(telegram_id):
    connection = sqlite3.connect("database/daily_users.db")
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
    connection = sqlite3.connect("database/daily_users.db")
    cursor = connection.cursor()

    cursor.execute("DELETE FROM daily_users WHERE telegram_id = ?", (telegram_id,))
    connection.commit()
    #  To know if we deleted anything
    connection.close()
    return cursor.rowcount