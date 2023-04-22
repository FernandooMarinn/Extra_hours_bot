import sqlite3

from Table_creation import table_creation


def check_and_create_tables():
    """
    Used to call table creation script. It should only work one time.
    :return:
    """
    table_creation.table_creation()


def introduce_daily_user_to_database(telegram_id, user: dict):
    """
    Introduces daily user data to the daily user database.
    :param telegram_id:
    :param user:
    :return:
    """
    total_per_hour = user["payment_per_hour"]
    connection = sqlite3.connect("../database/daily_users.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO daily_users(telegram_id, payment_per_hour)
        VALUES(?, ?)
    """, (telegram_id, total_per_hour))

    connection.commit()

    connection.close()


def introduce_new_user_to_database(telegram_id, user: dict):
    """
    Introduces new user to users database.
    :param telegram_id:
    :param user:
    :return:
    """
    name = user["name"]
    start_hour = user["start_hour"]
    finish_hour = user["finish_hour"]
    payment_per_hour = user["payment_per_hour"]

    connection = sqlite3.connect("../database/users.db")
    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO users(telegram_id, name, start_hour, finish_hour, payment_per_hour)
            VALUES(?, ?, ?, ?, ?)
        """, (int(telegram_id), name, start_hour, finish_hour, payment_per_hour))

        connection.commit()
        connection.close()
        introduce_working_days_to_database(telegram_id, user)
    except sqlite3.IntegrityError:
        connection.close()
        return False


def introduce_working_days_to_database(telegram_id, user: dict):
    """
    Introduces working days to users database.
    :param telegram_id:
    :param user:
    :return:
    """
    working_days = user["work_days"]

    connection = sqlite3.connect("../database/users.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO working_days(Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday, telegram_id)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?)
    """, (working_days["Monday"], working_days["Tuesday"], working_days["Wednesday"],
          working_days["Thursday"], working_days["Friday"], working_days["Saturday"], working_days["Sunday"],
          telegram_id))

    connection.commit()
    connection.close()
    return True


def delete_user(telegram_id):
    """
    Deletes an user from the database.
    :param telegram_id:
    :return:
    """
    connection = sqlite3.connect("../database/users.db")
    cursor = connection.cursor()
    cursor.execute("DELETE FROM users WHERE telegram_id = ?", (telegram_id,))
    connection.commit()
    connection.close()
    delete_days(telegram_id)
    delete_work_days(telegram_id)


def check_if_user_exits(telegram_id):
    """
    Checks if an user already exist in the database.
    :param telegram_id:
    :return:
    """
    sql_instruction = """SELECT * FROM users WHERE telegram_id = ?"""

    connection = sqlite3.connect("../database/users.db")
    cursor = connection.cursor()

    cursor.execute(sql_instruction, (telegram_id,))

    result = cursor.fetchone()
    connection.commit()
    connection.close()

    return result


def check_and_return_daily_user(telegram_id):
    """
    Check if a daily user exist in the database, and returns it.
    :param telegram_id:
    :return:
    """
    connection = sqlite3.connect("../database/daily_users.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM daily_users WHERE telegram_id = ?", (telegram_id,))

    result = cursor.fetchone()
    connection.commit()
    connection.close()

    if result is None:
        return False
    else:
        payment_per_hour = result[1]
        return payment_per_hour


def delete_daily_user(telegram_id):
    """
    Deletes a daily user, and returns cursur rowcount, to see if it indeed deleted anything.
    :param telegram_id:
    :return:
    """
    connection = sqlite3.connect("../database/daily_users.db")
    cursor = connection.cursor()

    cursor.execute("DELETE FROM daily_users WHERE telegram_id = ?", (telegram_id,))
    connection.commit()
    #  To know if we deleted anything
    connection.close()
    return cursor.rowcount


def check_if_already_exist_in_days(parameter_to_serch, column_name, value, telegram_id):
    """
    Check if given parameters already exist en day table, in users database.
    :param parameter_to_serch:
    :param column_name:
    :param value:
    :param telegram_id:
    :return:
    """
    sql_instruction = "SELECT {} FROM days WHERE {} = ? AND telegram_id = ?".format(parameter_to_serch, column_name)
    connection = sqlite3.connect("../database/users.db")
    cursor = connection.cursor()

    cursor.execute(sql_instruction, (value, telegram_id))
    result = cursor.fetchone()

    connection.commit()
    connection.close()
    return result


def introduce_one_to_days(column_name, value):
    """
    Introduces one value to days table, in users database.
    :param column_name:
    :param value:
    :return:
    """
    sql_instruction = "INSERT INTO days ({}) VALUES(?)".format(column_name)

    connection = sqlite3.connect("../database/users.db")
    cursor = connection.cursor()

    cursor.execute(sql_instruction, (value,))

    connection.commit()
    connection.close()


def introduce_many_to_days(column_names, values):
    """
    Introduces many registers to the days table, in users database.
    :param column_names:
    :param values:
    :return:
    """
    connection = sqlite3.connect("../database/users.db")
    cursor = connection.cursor()
    sql_values = ",".join(["?" for _ in range(len(values))])
    sql_names = ",".join([name for name in column_names])

    sql_instruction = "INSERT INTO days ({}) VALUES ({})".format(sql_names, sql_values)
    cursor.execute(sql_instruction, (tuple(values)))

    connection.commit()
    connection.close()


def update_one_to_days(column_name, value, where_condition_name, where_condition_value, telegram_id):
    """
    Updates a value in days table, in users database.
    :param column_name:
    :param value:
    :param where_condition_name:
    :param where_condition_value:
    :param telegram_id:
    :return:
    """

    sql_instruction = """
    UPDATE days
    SET {} = ?
    WHERE {} = ? AND telegram_id = ?
    """.format(column_name, where_condition_name)

    connection = sqlite3.connect("../database/users.db")
    cursor = connection.cursor()

    cursor.execute(sql_instruction, (value, where_condition_value, telegram_id))
    connection.commit()
    connection.close()


def get_usual_hour(telegram_id, hour_to_search):
    """
    Returns start or end hour of a certain user in the database.
    :return:
    """
    connection = sqlite3.connect("../database/users.db")
    cursor = connection.cursor()

    sql_instruction = "SELECT {} FROM users WHERE telegram_id = ?".format(hour_to_search)
    cursor.execute(sql_instruction, (telegram_id,))

    result = cursor.fetchone()
    connection.commit()
    connection.close()
    return result


def end_month_get_hours(telegram_id):
    """
    Get all the hours in the database, for a certain telegram id.
    :param telegram_id:
    :return:
    """

    sql_instruction = """
    SELECT * FROM days WHERE telegram_id = ?
    """

    connection = sqlite3.connect("../database/users.db")
    cursor = connection.cursor()

    cursor.execute(sql_instruction, (telegram_id,))
    result = cursor.fetchall()

    connection.commit()
    connection.close()

    return result


def get_work_days(telegram_id):
    """
    Gets work days for a certain telegram id.
    :param telegram_id:
    :return:
    """

    sql_instruction = """
        SELECT * FROM working_days WHERE telegram_id = ?
    """

    connection = sqlite3.connect("../database/users.db")
    cursor = connection.cursor()

    cursor.execute(sql_instruction, (telegram_id,))
    result = cursor.fetchall()

    connection.commit()
    connection.close()

    return result


def get_money_per_hour(telegram_id):
    """
    Gets hourly income for a certain telegram_id.
    :param telegram_id:
    :return:
    """

    sql_instruction = "SELECT payment_per_hour FROM users where telegram_id = {}".format(telegram_id)

    connection = sqlite3.connect("../database/users.db")
    cursor = connection.cursor()

    cursor.execute(sql_instruction)
    result = cursor.fetchone()

    connection.commit()
    connection.close()

    return result


def delete_days(telegram_id):
    """
    Delete every register in days, for a certain telegram id.
    :param telegram_id:
    :return:
    """

    sql_instruction = """
    DELETE FROM days WHERE telegram_id = ?"""

    connection = sqlite3.connect("../database/users.db")
    cursor = connection.cursor()

    cursor.execute(sql_instruction, (telegram_id,))

    connection.commit()
    connection.close()


def delete_work_days(telegram_id):
    """
    Deletes work days, for a certain telegram id.
    :param telegram_id:
    :return:
    """
    sql_instruction = """
        DELETE FROM working_days WHERE telegram_id = ?"""

    connection = sqlite3.connect("../database/users.db")
    cursor = connection.cursor()

    cursor.execute(sql_instruction, (telegram_id,))

    connection.commit()
    connection.close()


def edit_day(telegram_id, day, column, new_value):
    sql_instruction = """
            UPDATE days
            SET {} = ?
            WHERE day = ? AND telegram_id = ?""".format(column)

    connection = sqlite3.connect("../database/users.db")
    cursor = connection.cursor()

    cursor.execute(sql_instruction, (new_value, day, telegram_id,))

    modify_check = cursor.rowcount

    connection.commit()
    connection.close()

    return modify_check
