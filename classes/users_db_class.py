import sqlite3


class UsersDB:
    """ DB class """
    def __init__(self):
        self.conn = sqlite3.connect('.users.db', check_same_thread=False)
        self.cursor = self.conn.cursor()

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users_info (
            mail TEXT,
            hashed_pass TEXT
            )""")

        self.conn.commit()

    def insert_new_user(self, mail, hashed_pass):
        with self.conn:
            self.cursor.execute("INSERT INTO users_info VALUES(:mail,:hashed_pass)",
                      {'mail': mail, 'hashed_pass': hashed_pass})

    def user_check(self, mail, hashed_pass):

        with self.conn:
            self.cursor.execute("SELECT * FROM users_info where mail = :mail", {'mail': mail})
            fetched_data = self.cursor.fetchall()
            print(fetched_data)
            if fetched_data == []:
                return False, "Mail not found"
            for mail, password in fetched_data:
                if hashed_pass == password:
                    return True, ""
                else:
                    return False, "Wrong password"


users = UsersDB()
print(users.user_check("", ""))