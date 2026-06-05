import time
from logging import exception
from mailbox import NoSuchMailboxError

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import datetime
import threading
import queue
from threading import Thread
from classes.client import Client
from classes.msg_class import Message
import file_explorer

client = Client("", "")


# Build sync thread for message display
class DisplayMessageSyncThread(QThread):
    update_signal = pyqtSignal()

    def __init__(self,event):
        super().__init__()
        self.event = event

    def run(self):
        # Emit a signal to update the GUI
        while True:
            self.event.wait()  # Blocks until the event is set
            self.update_signal.emit()
            self.event.clear()  # Clear the event


class ChatMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.qu = queue.Queue()  # Create a queue with a maximum size
        self.event = threading.Event() # Create thread event

        # Create client
        print(client.password)
        client.callback = self.receive_new_message

        # for new message
        self.send_win = NewMessageWindow()

        self.msg_wins = []
        self.index = 0

        # Create the Display Message synchronizer thread
        self.DisplayMessageSyncThread = DisplayMessageSyncThread(self.event)
        self.DisplayMessageSyncThread.update_signal.connect(self.display_message)  # Connect the signal to display message
        self.DisplayMessageSyncThread.start()

        # Title
        self.title_label = QLabel("Mail - Incoming Messages")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 36px;
            font-weight: bold;
            color: orange;
        """)

        # Chat Label
        self.chat_label = QLabel("")

        # Chat message input box with vertical scroll bar
        #self.message_edit = QTextEdit()
        #self.message_edit.setPlaceholderText("Type your message...")
        #self.message_edit.setFixedHeight(70)

        # Submit message button
        self.send_button = QPushButton("New message")
        self.send_button.clicked.connect(self.send_window)

        # Chat messages trace label
        self.messages_trace = QVBoxLayout()
        self.messages_trace.setAlignment(Qt.AlignTop)

        # Scroll area for messages trace with vertical scroll bar
        self.scroll_widget = QWidget()
        self.scroll_widget.setLayout(self.messages_trace)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)

        # Save chat info button
        self.save_button = QPushButton("Save Chat Info")
        self.save_button.clicked.connect(self.save_chat_history)

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create the Window Layout
        self.layout = QVBoxLayout(central_widget)

        self.layout.addWidget(self.title_label)
        #self.layout.addWidget(self.message_edit)
        self.layout.addWidget(self.send_button)
        self.layout.addWidget(self.scroll_area)
        #self.layout.addWidget(self.save_button)

        container = QWidget()
        container.setLayout(self.layout)

        # Set the central widget of the Window.
        self.setCentralWidget(container)

        client.ready()


    def send_window(self):
        self.send_win.resize(750, 1000)
        self.send_win.show()

    def open_msg_win(self,msg_win):
        msg_win.show()

    def display_message(self):
        """
        The function is triggerd by the DisplayMessageSyncThread upon receiving
        a new message from the server. The function removes the message from the queue
        and adds it to the messages trace scroll area widget.
        """
        while not self.qu.empty():
            print("loading")
            new_message = self.qu.get()
            print(1)
            msg_win = MSGWindow(new_message)
            print(2)
            self.msg_wins.append(msg_win)
            print(3)
            block = QPushButton(f'{new_message.msg_date}.\nFrom: {new_message.name}')
            print(4)
            # '_' catches PyQt's default 'checked' boolean parameter.
            # 'current_win=msg_win' freezes the loop's current window instance in time.
            block.clicked.connect(lambda _,x=msg_win: self.open_msg_win(x)) #throwaway variable to catch an unwanted argument - indicating the button's toggle state
            print(5)
            block.setFixedHeight(70)
            print(6)

            block.setStyleSheet("""
                                                       background-color: #9ec1cf;
                                                        padding: 15px;
                                                      font-size: 14px;
                                                        border-radius: 5px;
                                                """)
            self.messages_trace.addWidget(block)
            print("finished")

    def save_chat_history(self):
        """
        The function is called upon pressing the save_chat button.
        The function calls get_all_widgets_from_layout function for capturing
        all widgets from layout, finally it and saves the chat history in a file
        """
        
        #-- Complete the function
        filename = f"chat_history_{self.name}.txt"

        with open(filename, "w", encoding="utf-8") as f:
            for i in range(self.messages_trace.count()):
                f.write(self.messages_trace.itemAt(i).widget().text() + "\n")

        print("chat info has been successfully saved")
   
    def receive_new_message(self, new_message):
        """
        This is the callback function.
        The function is called by the client object upon receiving a new message.
        The function stores the new message in python's queue element
        and raises an event by utilizing queue put and event set operations.
        The event will trigger the activation of the display_message function thru 
        a synchronization thread that symchronizes between the receive messages thread
        and the GUI thread.        
        """
        if type(new_message) is list:
            print(new_message)
            for message in new_message:
                self.qu.put(message)
                self.event.set()  # Set the event, which unblocks the listener
                print(message)
        else:
            self.qu.put(new_message)
            self.event.set()  # Set the event, which unblocks the listener
            print(new_message)
        #-- Complete the function

class MSGWindow(QWidget): #TODO:add copy text option
    """
    after clicking on incoming message this window will appear
    """
    def __init__(self, message):
        super().__init__()

        self.message = message

        # Chat messages trace label
        self.message_trace = QVBoxLayout()
        self.message_trace.setAlignment(Qt.AlignTop)

        # Scroll area for messages trace with vertical scroll bar
        self.scroll_widget = QWidget()
        self.scroll_widget.setLayout(self.message_trace)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)

        self.setFixedHeight(500)
        self.setFixedWidth(760)

        self.txt = message.__repr__()

        self.msg_block = QLabel(self.txt)
        self.msg_block.setAlignment(Qt.AlignCenter)
        self.msg_block.setStyleSheet("""
                           background-color: #9ec1cf;
                            padding: 15px;
                          font-size: 14px;
                            border-radius: 5px;
                    """)

        self.msg_block.setFixedWidth(750)
        self.msg_block.setWordWrap(True)
        #self.msg_label.setFixedHeight(350)
        #self.msg_label.setFixedWidth(350)

        self.file_block = QPushButton("Download file")
        self.file_block.clicked.connect(self.save_file)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.scroll_area)
        self.setLayout(self.layout)

        self.message_trace.addWidget(self.msg_block)
        print(message.data)
        if message.data is not None:
            print(8)
            self.message_trace.addWidget(self.file_block)

    def save_file(self):
        file_explorer.saveFile(self.message.data, self.message.file_type)


class NewMessageWindow(QWidget):
    """
    This is the GUI window for sending a new message.
    """
    def __init__(self):
        super().__init__()
        #self.name = name

        self.setFixedHeight(600)

        # Create client
        self.client = client

        # Title
        self.title_label = QLabel("New Message")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 36px;
            font-weight: bold;
            color: orange;
        """)
        self.title_label.setFixedHeight(50)

        # Chat Label
        self.chat_label = QLabel("")

        # Chat message input box with vertical scroll bar
        self.message_edit = QTextEdit()
        self.message_edit.setPlaceholderText("Type your message...")
        self.message_edit.setFixedHeight(400)


        self.To_edit = QTextEdit()
        self.To_edit.setPlaceholderText("To: (e.g.: {e1@mb.com,e2@mb.com}... comas between, no spaces!)")
        self.To_edit.setFixedHeight(50)

        self.file_button = QPushButton("Add file")
        self.file_button.clicked.connect(self.toggle_file)
        self.file_data = None
        self.file_type = ""



        # Submit message button
        self.send_button = QPushButton("> Submit message")
        self.send_button.clicked.connect(self.send_message)



        # Create a central widget
        #central_widget = QWidget()
        #self.setCentralWidget(central_widget)

        # Create the Window Layout
        self.layout = QVBoxLayout()

        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.To_edit)
        self.layout.addWidget(self.file_button)
        self.layout.addWidget(self.message_edit)
        self.layout.addWidget(self.send_button)

        self.setLayout(self.layout)

        # Set the central widget of the Window.
        #self.setCentralWidget(container)

    def toggle_file(self):
        """
        after the button is clicked, the function will navigate to the required secondary-function
        :return:
        """
        if self.file_data is None:
            print("adding file")
            self.add_file()
            return
        else:
            print("remove")
            self.remove_file()
            return

    def add_file(self):
        """
        adds the required file
        :return:
        """
        self.file_data, self.file_type = file_explorer.openFile()
        print("data taken:")
        print(self.file_data)
        self.file_button.setText("Remove the added file")

    def remove_file(self):
        """
        removing the uploaded file
        :return:
        """
        print("Removing file")
        self.file_data = None
        self.file_type = ""
        self.file_button.setText("Add file")

    def send_message(self):
        """
        after send button is clicked, it sends the data through the client.
        :return:
        """
        to = self.To_edit.toPlainText() + "," + client.mail
        text = self.message_edit.toPlainText()
        if to.strip() == "" : #or text.strip() == ""
            return
        self.To_edit.clear()
        self.message_edit.clear()

        print(text)
        msg_object = Message((datetime.datetime.now()).strftime("%Y %b %H:%M"), client.mail, text, to, self.file_data, self.file_type)
        self.remove_file()
        try:
            self.client.send_message(msg_object)
            print("chat message has been successfully sent")
        except:
            print("chat message could not be sent")


        if text == 'EXIT':
            exit(0)
        # -- Complete the function

class SignWindow(QMainWindow):  # need to be transferred to a new script
    """
    GUI for signing in
    """
    def __init__(self):
        super().__init__()

        # Title
        self.title_label = QLabel("Mail - Sign In")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 30px;
            font-weight: bold;
            color: red;
        """)

        # Notes Label
        self.notes_label = QLabel("")
        self.notes_label.setStyleSheet("""
                    font-size: 10px;
                    font-weight: bold;
                    color: orange;
                """)


        self.TFA_win = TFAWindow()

        self.new_user_win = NewUserWindow()

        self.mail_edit = QTextEdit()
        self.mail_edit.setPlaceholderText("Type your mail...(e.g. {mymail}@mb.com)")
        self.mail_edit.setFixedHeight(40)

        self.password_edit = QTextEdit()
        self.password_edit.setPlaceholderText("Type your password...") #(at least 8 characters is recommended)
        self.password_edit.setFixedHeight(40)

        # Submit message button
        self.sign_in_button = QPushButton("Sign In")
        self.sign_in_button.clicked.connect(self.check_user)

        # Save chat info button
        self.sign_up_button = QPushButton("New user?")
        self.sign_up_button.clicked.connect(self.new_user_process)

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create the Window Layout
        self.layout = QVBoxLayout(central_widget)

        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.notes_label)
        self.layout.addWidget(self.mail_edit)
        self.layout.addWidget(self.password_edit)
        self.layout.addWidget(self.sign_in_button)
        self.layout.addWidget(self.sign_up_button)

        container = QWidget()
        container.setLayout(self.layout)

        # Set the central widget of the Window.
        self.setCentralWidget(container)




    def TFA_process(self):
        """activates the 2FA GUI"""
        self.TFA_win.resize(300, 300)
        self.TFA_win.show()


    def check_user(self):
        """checking with the server if the mail and password are valid"""
        client.mail = self.mail_edit.toPlainText()
        client.password = self.password_edit.toPlainText()
        print(1)
        response = client.log_in()
        print(response)
        if type(response) == str and response == 'WRONG PASSWORD OR MAIL':
            self.notes_label.setText(response)
        elif type(response) == str and response.split(' ')[0] == 'OK':
            print(response)
            self.hide()
            self.TFA_process()
            #client.logged_in = True
            #self.close()

    def new_user_process(self):
        """displays the new user GUI"""
        self.new_user_win.resize(450, 550)
        self.new_user_win.show()

class TFAWindow(QWidget):
    """the GUI window for the second step in the log-in process.(2FA)"""
    def __init__(self):
        super().__init__()
        # self.name = name



        # Title
        self.title_label = QLabel("Authentication")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: green;
        """)
        self.title_label.setFixedHeight(40)

        # Notes Label
        self.notes_label = QLabel("")
        self.notes_label.setStyleSheet("""
                            font-size: 10px;
                            font-weight: bold;
                            color: orange;
                        """)
        self.notes_label.setFixedHeight(40)

        # Chat message input box with vertical scroll bar
        self.code_edit = QTextEdit()
        self.code_edit.setPlaceholderText("Type here the code you got...")
        self.code_edit.setFixedHeight(30)


        # Submit message button
        self.send_button = QPushButton("> Submit code")
        self.send_button.clicked.connect(self.check_code)

        # Create a central widget
        # central_widget = QWidget()
        # self.setCentralWidget(central_widget)

        # Create the Window Layout
        self.layout = QVBoxLayout()

        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.notes_label)
        self.layout.addWidget(self.code_edit)
        self.layout.addWidget(self.send_button)

        self.setLayout(self.layout)


    def check_code(self):
        """checking the 2FA auth code with the server and displays the response"""
        code = self.code_edit.toPlainText()
        print(1)
        response = client.TFA_send(code)
        print(response)
        if type(response) == str and response == 'WRONG - Sending new code':
            self.notes_label.setText(response)
        elif type(response) == str and response == 'CORRECT':
            self.hide()
            client.logged_in = True
            self.close()


class NewUserWindow(QWidget):
    """
    the GUI window for creating a new user
    """
    def __init__(self):
        super().__init__()
        # self.name = name



        # Title
        self.title_label = QLabel("NEW USER")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: blue;
        """)
        self.title_label.setFixedHeight(40)

        # Notes Label
        self.notes_label = QLabel("")
        self.notes_label.setStyleSheet("""
                            font-size: 10px;
                            font-weight: bold;
                            color: orange;
                        """)
        self.notes_label.setFixedHeight(40)

        # Chat message input box with vertical scroll bar
        self.mail_edit = QTextEdit()
        self.mail_edit.setPlaceholderText("Type here mail(e.g: example@mb.com)...")
        self.mail_edit.setFixedHeight(30)

         # Chat message input box with vertical scroll bar
        self.password_edit = QTextEdit()
        self.password_edit.setPlaceholderText("Type here password(at least 8 characters is recommended)...")
        self.password_edit.setFixedHeight(30)

         # Chat message input box with vertical scroll bar
        self.auth_edit = QTextEdit()
        self.auth_edit.setPlaceholderText("Type here authorization gmail(Make sure it's correct!!)...")
        self.auth_edit.setFixedHeight(30)


        # Submit message button
        self.send_button = QPushButton("> Submit")
        self.send_button.clicked.connect(self.create_user)

        # Create a central widget
        # central_widget = QWidget()
        # self.setCentralWidget(central_widget)

        # Create the Window Layout
        self.layout = QVBoxLayout()

        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.notes_label)
        self.layout.addWidget(self.mail_edit)
        self.layout.addWidget(self.password_edit)
        self.layout.addWidget(self.auth_edit)
        self.layout.addWidget(self.send_button)

        self.setLayout(self.layout)


    def create_user(self):
        """
        after the button was clicked, the info that the user filled is sent to the server
        :return: writes in a label on the screen the server's response
        """
        mail = self.mail_edit.toPlainText()
        password = self.password_edit.toPlainText()
        auth = self.auth_edit.toPlainText()
        if auth.strip() == '' or mail.strip() == '' or password.strip() == '':
            self.notes_label.setText('All fields are required.')
            return
        response = client.new_user(mail, password, auth)
        print(response)
        self.notes_label.setText(response)
        if type(response) == str and response == 'CREATED':
            self.notes_label.setText('Account created successfully! You can log-in now!')
            self.notes_label.setStyleSheet("""
                                        font-size: 10px;
                                        font-weight: bold;
                                        color: green;
                                    """)


def sign_in():
    """
    beginning the sign-in process
    :return:
    """
    app_sign = QApplication(sys.argv)
    window = SignWindow()
    window.resize(500, 300)
    window.show()
    app_sign.exec()
    app_sign.closeAllWindows()
    return

def GUI():
    """
    starting up the GUI by the right order
    :return:
    """
    sign_in()
    if not(client.logged_in):
        sys.exit()
    print("signed")
    app = QApplication(sys.argv)
    #name = sys.argv[1]
    window = ChatMainWindow()
    window.resize(750, 1000)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    Thread(target=GUI).start()

