import sqlite3

def table_creation():
    connection = sqlite3.connect("database/daily_users.db")
    cursor = connection.cursor()
    try:
        cursor.execute("""
            CREATE TABLE daily_users(
                telegram_id INTEGER PRIMARY KEY,
                payment_per_hour FLOAT
                )
        """)
        connection.commit()
        connection.close()
        print("Daily users database successfully created.")

        connection = sqlite3.connect("database/users.db")
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE users(
                telegram_id INTEGER PRIMARY KEY,
                name TEXT,
                start_hour TEXT,
                finish_hour TEXT,
                payment_per_hour FLOAT
                )
        """)

        cursor.execute("""
            CREATE TABLE working_days(
                telegram_id INTEGER PRIMARY KEY,
                Monday INTEGER,
                Tuesday INTEGER,
                Wednesday INTEGER,
                Thursday INTEGER,
                Friday INTEGER,
                Saturday INTEGER,
                Sunday INTEGER,
                FOREIGN KEY (telegram_id) REFERENCES users(telegram_id)
                )
        """)

        cursor.execute("""
            CREATE TABLE days(
                telegram_id KEY,
                day TEXT,
                start_hour TEXT,
                finish_hour TEXT,
                extra_hours TEXT,
                FOREIGN KEY (telegram_id) REFERENCES users(telegram_id),
                UNIQUE(telegram_id, day)
                )
        """)


        connection.commit()
        print("Database users successfully created.")
    except sqlite3.OperationalError:
        print("Database is already created.")
    connection.close()

