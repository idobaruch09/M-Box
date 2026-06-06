import pickle
import sqlite3
from .msg_class import Message
class ChatDB:
    """ DB class """
    def __init__(self):
        self.conn = sqlite3.connect('chat.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS table_names (
                            table_name TEXT
                            )""") #for existing tables
        self.conn.commit()

    def insert_name(self, name):
        with self.conn:
            self.cursor.execute(
                f"INSERT INTO table_names VALUES(:table_name)",
                {'table_name': name})

    def check_exist(self, name):
        print("check", name)
        with self.conn:
            self.cursor.execute(f"SELECT table_name FROM table_names")
            fetched_data = self.cursor.fetchall()
            print(fetched_data)
            for table in fetched_data:
                print(table)
                table_name = table[0]
                print(table_name)
                if table_name == name:
                    return True
        return False




    def create_new_table(self, mail):
        """
        :param mail: the mail of the user's table
        :return: if table created successfully
        """
        print("inininininin")
        table_name = mail.split('@')[0]
        print(table_name)
        if self.check_exist(table_name):
            print("Table already exists")
            return False
        with self.conn:
            self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} (
                                date TEXT,
                                from_mail TEXT,
                                msg_text TEXT,
                                to_mail TEXT,
                                file_data TEXT,
                                type TEXT,
                                scan_report TEXT
                                )""")
        self.insert_name(table_name)
        print("added ", table_name)
        return True


    def insert_msg(self, msg): #TODO: add an option for multiple recipients.
        # idea 1: saved message for each and new parameter of recipients
        # idea 2: when taking history(here) and when sending instantly(server) checking each msg and its recipients
        for recipient in msg.to.split(","):
            print("recipient ", recipient)
            table_name = recipient.split('@')[0]
            print("123", table_name)
            if self.check_exist(table_name):
                print("table exists")
                if msg.data is None:
                    file_data = ""
                else:
                    file_data = msg.data
                with self.conn:
                    self.cursor.execute(
                    f"INSERT INTO {table_name} VALUES(:date,:from_mail,:msg_text, :to_mail,:file_data, :type, :scan_report)",
                        {'date': msg.get_date(), 'from_mail': msg.get_name(), 'msg_text': msg.get_info(),
                         'to_mail': msg.get_to(), 'file_data': file_data, 'type': msg.file_type, 'scan_report': msg.scan_report})


    def get_history(self, to):
        print(to)
        msgs =[]
        table_name = to.split('@')[0]
        print(table_name)
        with self.conn:
            if not self.check_exist(table_name):
                print("Table doesn't exist")
                return msgs
            self.cursor.execute(f"SELECT * FROM {table_name}")
            fetched_data = self.cursor.fetchall()
            for date, name, msg_text, recipients, data, file_type, report in fetched_data:
                    m = Message(date, name, msg_text, recipients, data, file_type)
                    if data == '':
                        m.data = None
                    m.scan_report = report
                    msgs.append(m)
        return msgs


