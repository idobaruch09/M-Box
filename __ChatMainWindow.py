import time
from logging import exception

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

client = Client("a", "")


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
        self.w = NewMessageWindow()

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
        self.layout.addWidget(self.save_button)

        container = QWidget()
        container.setLayout(self.layout)

        # Set the central widget of the Window.
        self.setCentralWidget(container)

        client.ready()




    def send_window(self):
        self.w.resize(750, 1000)
        self.w.show()


    def display_message(self):
        """
        The function is triggerd by the DisplayMessageSyncThread upon receiving
        a new message from the server. The function removes the message from the queue
        and adds it to the messages trace scroll area widget.
        """
        while not self.qu.empty():
            new_message = self.qu.get()
            #-- Complete the function
            block = QLabel(new_message.__repr__())
            block.setWordWrap(True)

            block.setStyleSheet("""
                   background-color: #9ec1cf;
                    padding: 15px;
                  font-size: 14px;
                    border-radius: 5px;
            """)

            self.messages_trace.addWidget(block)

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


class NewMessageWindow(QWidget):
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
        self.To_edit.setPlaceholderText("To:")
        self.To_edit.setFixedHeight(50)




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
        self.layout.addWidget(self.message_edit)
        self.layout.addWidget(self.send_button)

        self.setLayout(self.layout)

        # Set the central widget of the Window.
        #self.setCentralWidget(container)

    def send_message(self):
        """
        This function is activated upon clicking the submit_message button.
        it extracts the chat message data from the chat message input box,
        creates a message object and calls the client's send_message function
        that finally sends the message to the server
        """
        to = self.To_edit.toPlainText()
        self.To_edit.clear()
        text = self.message_edit.toPlainText()
        self.message_edit.clear()
        print(text)
        msg_object = Message((datetime.datetime.now()).strftime("%Y %b %H:%M"), client.mail, text, to)
        try:
            self.client.send_message(msg_object)
            print("chat message has been successfully sent")
        except:
            print("chat message could not be sent")


        if text == 'EXIT':
            exit(0)
        # -- Complete the function

def sign_in():
    app_sign = QApplication(sys.argv)
    window = SignWindow()
    window.resize(500, 300)
    window.show()
    app_sign.exec()
    app_sign.closeAllWindows()
    return



class SignWindow(QMainWindow):  # need to be transferred to a new script
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

        self.mail_edit = QTextEdit()
        self.mail_edit.setPlaceholderText("Type your mail...(e.g. {mymail}@mb.com)")
        self.mail_edit.setFixedHeight(40)

        self.password_edit = QTextEdit()
        self.password_edit.setPlaceholderText("Type your password...(at least 8 characters is recommended)")
        self.password_edit.setFixedHeight(40)

        # Submit message button
        self.sign_in_button = QPushButton("Sign In")
        self.sign_in_button.clicked.connect(self.check_user)

        # Save chat info button
        self.sign_up_button = QPushButton("New user?")
        self.sign_up_button.clicked.connect(self.save_chat_history)

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

    def check_user(self):
        client.mail = self.mail_edit.toPlainText()
        client.password = self.password_edit.toPlainText()
        print(1)
        response = client.log_in()
        print(response)
        if type(response) == str and response == 'WRONG PASSWORD OR MAIL':
            self.notes_label.setText(response)
        elif type(response) == str and response == 'OK':
            client.logged_in = True
            print(response)
            self.close()


    def save_chat_history(self):
        pass

def GUI():
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

