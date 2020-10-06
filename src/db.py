import os
import sqlite3
from helper import *

# From: https://goo.gl/YzypOI
def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance


class DatabaseDriver(object):
    """
    Database driver for the User app.
    Handles with reading and writing data with the database.
    """

    def __init__(self):
        self.conn = sqlite3.connect("venmo.db", check_same_thread=False)
        self.create_user_table()
        # self.create_send_table()

    def create_user_table(self):
        try:
            self.conn.execute("""
                CREATE TABLE user (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    NAME TEXT NOT NULL,
                    USERNAME TEXT NOT NULL,
                    BALANCE INT NOT NULL,
                    PASSWORD TEXT,
                    EMAIL TEXT
                );
            """)
        except Exception as e:
            print(e)

    def get_all_users(self):
        cursor = self.conn.execute("SELECT * FROM user;")
        users = []

        for row in cursor:
            users.append({"id": row[0], "name": row[1], "username": row[2]})

        return users

    def insert_user_table(self, name, username, balance, password="", email =""):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO user (NAME, USERNAME, BALANCE, PASSWORD,EMAIL) VALUES (?, ?, ?, ?, ?);", (name, username, balance, hash_password(password),email))
        self.conn.commit()
        return cur.lastrowid


    def get_user_by_id(self, id):
        cursor = self.conn.execute("SELECT * FROM user WHERE ID = ?", (id,))

        for row in cursor:
            return {"id": row[0], "name": row[1], "username": row[2], "balance": row[3], "password": row[4], "email": row[5]}

        return None


    
    def update_user_by_id(self, id, name, username, balance, password="",email = ""):
        self.conn.execute("""
            UPDATE user 
            SET name = ?, username = ?, balance = ?, password = ?, email = ?
            WHERE id = ?;
        """, (name, username, balance, hash_password(password), email, id))
        self.conn.commit()


    def delete_user_by_id(self, id):
        self.conn.execute("""
            DELETE FROM user
            WHERE id = ?;        
        """, (id,))
        self.conn.commit()
# Only <=1 instance of the database driver
# exists within the app at all times
DatabaseDriver = singleton(DatabaseDriver)
