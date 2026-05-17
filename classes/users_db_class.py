import sqlite3
import hashlib

#password is saved as it's hash in SHA256
class UsersDB:
    """ DB class """
    def __init__(self):
        self.conn = sqlite3.connect('users.db', check_same_thread=False)
        self.cursor = self.conn.cursor()

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users_info (
            mail TEXT,
            hashed_pass TEXT,
            auth_mail TEXT
            )""")

        self.conn.commit()

    def insert_new_user(self, mail, password, auth_mail):
        hashed_pass = hashlib.sha256(password.encode()).hexdigest()
        self.cursor.execute("SELECT * FROM users_info where mail = :mail", {'mail': mail})
        fetched_data = self.cursor.fetchall()
        if not(fetched_data == []):
            return False # mail already exists
        with self.conn:
            self.cursor.execute("INSERT INTO users_info VALUES(:mail,:hashed_pass,:auth_mail)",
                      {'mail': mail, 'hashed_pass': hashed_pass, 'auth_mail': auth_mail})
            return True

    def user_check(self, mail, password):
        hashed_pass = hashlib.sha256(password.encode()).hexdigest()
        with self.conn:
            self.cursor.execute("SELECT * FROM users_info where mail = :mail", {'mail': mail})
            fetched_data = self.cursor.fetchall()
            print(fetched_data)
            if fetched_data == []:
                return False, ''
            for mail, db_pass, auth_mail in fetched_data: #checks password
                if hashed_pass == db_pass:
                    return True, auth_mail
                else:
                    return False, ''


#c = UsersDB()
#c.insert_new_user('aaa', '1234')
#c.insert_new_user('aaa', 'dfsg')