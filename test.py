import sqlite3

# Устанавливаем соединение с базой данных
con = sqlite3.connect('db/main.db')
cur = con.cursor()

# # Создаем таблицу Users
# cur.execute('''
#     CREATE TABLE users (
#     id         INTEGER PRIMARY KEY,
#     user_id    INTEGER NOT NULL
#                        UNIQUE,
#     username   TEXT,
#     balance    REAL,
#     money_time TEXT,
#     ref_id     INTEGER,
#     reg_time   TEXT
#     )
# ''')

a = cur.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';''')

# Сохраняем изменения и закрываем соединение
con.commit()
con.close()