from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from PyQt5.QtCore import QThread
import pickle

#from pygame.examples.audiocapture import callback


class Client(QThread):
    """
    for communication with server
    """
    # CONSTANTS
    HOST = 'localhost'
    PORT = 5500
    ADDR = (HOST, PORT)
    BUFSIZ = 1024

    def __init__(self, mail, password,  callback=None):
        """
        Init object, connects to server and activate receive thread for
        handling the incoming messages from the server.
        :param password: string
        :param mail: str
        """
        super().__init__()
        self.mail = mail
        self.password = password
        self.callback = callback
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        data = self.connect_to_server()
        receive_thread = Thread(target=self.receive_messages)
        receive_thread.start()

    def connect_to_server(self):
        """
        Connect to server and then send the client mail
        """
        try:
            self.client_socket.connect(self.ADDR)
        except ConnectionError as e:  # This is the correct syntax
            print("No Response -->  ", e)
        try:
            self.client_socket.sendall(pickle.dumps(self.mail))
        except:
            print("Can't Send -->  ")

    def sign_up(self):

        try:
            self.client_socket.connect(self.ADDR)
        except ConnectionError as e:  # This is the correct syntax
            print("No Response -->  ", e)
        try:
            self.client_socket.sendall(pickle.dumps(self.mail))
            self.client_socket.sendall(pickle.dumps(self.password))
        except:
            print("Can't Send -->  ")



    def receive_messages(self):
        """
        receive messages from server
        :return: None
        """
        while True:
            try:
                data = pickle.loads(self.client_socket.recv(self.BUFSIZ*20))
            except Exception as e:
                print("[EXCEPTION]", e)
                break
 
           # -- Complete the instruction
            if self.callback and data:
                self.callback(data)


    def send_message(self,data):
        """
        send messages to server
        :param msg: str
        :return: None
        """
        # Convert Python object to Pickle bytes
        self.client_socket.sendall(pickle.dumps(data))
 


