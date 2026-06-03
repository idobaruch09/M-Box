import pickle
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
            to_mail TEXT,
            file_data TEXT,
            type TEXT
            )""")

        self.conn.commit()

    def insert_msg(self, msg): #TODO: add an option for multiple recipients.
        # idea 1: saved message for each and new parameter of recipients
        # idea 2: when taking history(here) and when sending instantly(server) checking each msg and its recipients
        if msg.data is None:
            file_data = ""
        else:
            file_data = msg.data
        with self.conn:
            self.cursor.execute("INSERT INTO chat_info VALUES(:date,:from_mail,:msg_text, :to_mail,:file_data, :type)",
                      {'date': msg.get_date(), 'from_mail': msg.get_name(), 'msg_text': msg.get_info(),
                       'to_mail': msg.get_to(), 'file_data': file_data, 'type': msg.file_type})

    def get_history(self, to):
        print(to)
        msgs =[]
        with self.conn:
            self.cursor.execute("SELECT * FROM chat_info")
            fetched_data = self.cursor.fetchall()
            for d, name, msg_text, recipients,data, file_type in fetched_data:
                recipients = recipients.split(',')
                for recipient in recipients:
                    if recipient == to:
                        m = Message(d, name, msg_text, recipient, data, file_type)
                        if data == '':
                            m.data = None
                        msgs.append(m)
        return msgs


