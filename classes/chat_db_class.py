import sqlite3
from .msg_class import Message
class ChatDB:
    """ DB class """
    def __init__(self):
        self.conn = sqlite3.connect('chat.db', check_same_thread=False)
        self.cursor = self.conn.cursor()

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS chat_info (
            date TEXT,
            from_mail TEXT,
            msg_text TEXT,
            to_mail TEXT
            )""")

        self.conn.commit()

    def insert_msg(self, msg):
        with self.conn:
            self.cursor.execute("INSERT INTO chat_info VALUES(:date,:from_mail,:msg_text, :to_mail)",
                      {'date': msg.get_date(), 'from_mail': msg.get_name(), 'msg_text': msg.get_info(), 'to_mail': msg.get_to()})

    def get_history(self, to):
        print(to)
        msgs =[]
        with self.conn:
            self.cursor.execute("SELECT * FROM chat_info where to_mail = :to", {'to': to})
            fetched_data = self.cursor.fetchall()
            for d, name, msg_text, t in fetched_data:
                m = Message(d, name, msg_text, to)
                msgs.append(m)
        return msgs


