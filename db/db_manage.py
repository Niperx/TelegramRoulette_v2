import sqlite3
from datetime import datetime, date


async def check_db():  # Проверка на ДБ, при отсутствии - создание
    con = sqlite3.connect('db/main.db')
    cur = con.cursor()

    list_of_tables = cur.execute('''
        SELECT name FROM sqlite_master WHERE type='table' AND name='{users}';
        ''')

    if not list_of_tables:
        print('DB Created')
        cur.execute('''
               CREATE TABLE users (
               id         INTEGER PRIMARY KEY,
               user_id    INTEGER NOT NULL
                                  UNIQUE,
               username   TEXT,
               balance    INTEGER,
               money_time TEXT,
               ref_id     INTEGER,
               reg_time   TEXT
               )
           ''')
        con.commit()
    else:
        print('DB Loaded')

    con.close()


async def create_user(user_id, username=None, balance=0, ref_id=None):  # создание нового пользователя
    con = sqlite3.connect('db/main.db')
    cur = con.cursor()
    cur.execute(f'SELECT id FROM users ORDER BY id desc')
    check = cur.fetchall()
    if check:
        cur.execute(f'SELECT id FROM users ORDER BY id desc')
        old_id = cur.fetchall()[0][0]
        new_id = old_id + 1
    else:
        new_id = 1

    user_info = (new_id, user_id, username, balance, datetime.now(), ref_id, datetime.now())
    cur.execute("INSERT INTO users VALUES(?,?,?,?,?,?,?);", user_info)
    con.commit()


async def check_user_id(user_id):
    con = sqlite3.connect('db/main.db')
    cur = con.cursor()

    cur.execute(f'SELECT COUNT(*) FROM users WHERE user_id = {user_id}')
    check = cur.fetchall()[0][0]
    if check:
        return True
    else:
        return False


async def load_user(user_id):  # загрузка всей инфы о юзере
    con = sqlite3.connect('db/main.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    result = cur.fetchone()
    return result


async def get_balance(user_id):
    con = sqlite3.connect('db/main.db')
    cur = con.cursor()
    cur.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    result = cur.fetchone()[0]
    return result


async def add_money(user_id, money):
    con = sqlite3.connect('db/main.db')
    cur = con.cursor()

    # Пополнение у пользователя
    cur.execute(f'SELECT wallet FROM users WHERE id = {user_id}')
    old_balance = cur.fetchall()[0][0]
    new_balance = old_balance + money
    cur.execute(F'UPDATE users SET wallet = {new_balance} WHERE id = {user_id}')

    # Пополнение у реферала
    cur.execute(f'SELECT ref_id FROM users WHERE id = {user_id}')

    ref = cur.fetchall()[0][0]

    if ref:
        cur.execute(f'SELECT wallet FROM users WHERE id = {ref}')
        old_balance = cur.fetchall()[0][0]
        new_balance = old_balance + money * 0.05
        cur.execute(F'UPDATE users SET wallet = {new_balance} WHERE id = {ref}')

    con.commit()
