from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from PyQt5.QtCore import QThread
import pickle

from requests.utils import dotted_netmask


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
        self.logged_in = False
        #data = self.connect_to_server()
        self.receive_thread = Thread(target=self.receive_messages)

    def new_user(self, mail, password, auth_mail): #TODO: finish this func, close connection after creating
        try:
            self.client_socket = socket(AF_INET, SOCK_STREAM)
            self.client_socket.connect(self.ADDR)
            print("Connected to server")
        except ConnectionError as e:  # This is the correct syntax
            print("No Response -->  ", e)
        except Exception as e:
            print(e)
        try:
            response = pickle.loads(self.client_socket.recv(1024))
            if response == "REQUEST":
                self.client_socket.sendall(pickle.dumps('NEW'))
            else:
                return 'SERVER ERROR'
            response = pickle.loads(self.client_socket.recv(1024))
            if not response == 'WAITING':
                return 'SERVER ERROR'
            self.client_socket.sendall(pickle.dumps(mail))
            response = pickle.loads(self.client_socket.recv(1024))
            if not response == 'ACK':
                return response
            self.client_socket.sendall(pickle.dumps(password))
            response = pickle.loads(self.client_socket.recv(1024))
            if not response == 'ACK':
                return 'ERROR'
            self.client_socket.sendall(pickle.dumps(auth_mail))
            response = pickle.loads(self.client_socket.recv(1024))
            if not response == 'CREATED':
                return 'ERROR'
            try:
                self.client_socket.close()
            except Exception as e:
                print(e)
            return response
        except Exception as e:
            print(e)
            return 'ERROR'



    def log_in(self):
        try:
            self.client_socket = socket(AF_INET, SOCK_STREAM)
            self.client_socket.connect(self.ADDR)
            print("Connected to server")
        except ConnectionError as e:  # This is the correct syntax
            print("No Response -->  ", e)
        except Exception as e:
            print(e)
        try:
            response = pickle.loads(self.client_socket.recv(1024))
            if response == "REQUEST":
                self.client_socket.sendall(pickle.dumps('LOGIN'))
            else:
                return 'SERVER ERROR'
            response = pickle.loads(self.client_socket.recv(1024))
            if response == 'WAITING':
                self.client_socket.sendall(pickle.dumps(self.mail))
                response = pickle.loads(self.client_socket.recv(1024))
                if not response == 'ACK':
                    return 'ERROR'
                self.client_socket.sendall(pickle.dumps(self.password))
                print("Sent mail")
                response = pickle.loads(self.client_socket.recv(1024))
                if response == 'WRONG PASSWORD OR MAIL':
                    self.client_socket.close()
                print(response)
                print("2")
                return response
        except Exception as e:
            print("Can't Send -->  ", e)
            return 'ERROR'

    def TFA_send(self, code):
        try:
            self.client_socket.sendall(pickle.dumps(code))
            print("Sent code")
            response = pickle.loads(self.client_socket.recv(1024))
            return response
        except Exception as e:
            print("Can't Send -->  ", e)



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

    def ready(self):
        """
        sends the server that he can send history
        :return:
        """
        self.client_socket.sendall(pickle.dumps('READY'))
        self.receive_thread.start()

    def send_message(self,data):
        """
        send messages to server
        :param msg: str
        :return: None
        """
        # Convert Python object to Pickle bytes
        self.client_socket.sendall(pickle.dumps(data))
 


