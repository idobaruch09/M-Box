from http.client import responses
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from PyQt5.QtCore import QThread
import pickle
from threading import Lock

from websockets import connect

lock = Lock()
from requests.utils import dotted_netmask
import time
import sys
import ssl



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

        self.logged_in = False
        #data = self.connect_to_server()
        self.receive_thread = Thread(target=self.receive_messages)
        self.stop_thread = False
        self.stopped = False


    def connect(self):
        context = ssl.create_default_context()
        # 2. בגלל שזו תעודה עצמית (Self-signed), נגיד ללקוח לסמוך עליה ספציפית
        context.load_verify_locations(cafile="server.crt")
        # אם ה-IP של השרת הוא לא 'localhost' (למשל 192.168.1.50), והתעודה יוצרה עבור localhost,
        # נצטרך לבטל זמנית את בדיקת תאימות השם כדי שלא ייזרק error (לצרכי פיתוח בלבד):
        #context.check_hostname = False
        c_socket = socket(AF_INET, SOCK_STREAM)

        # 4. עטיפת הסוקט ב-TLS
        self.client_socket = context.wrap_socket(c_socket, server_hostname='localhost')

    def new_user(self, mail, password, auth_mail): #TODO: finish this func, close connection after creating
        try:
            self.connect()
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
                print("a")
            else:
                return 'SERVER ERROR'
            response = pickle.loads(self.client_socket.recv(1024))
            if not response == 'WAITING':
                return 'SERVER ERROR'
            self.client_socket.sendall(pickle.dumps(mail))
            print("b")
            response = pickle.loads(self.client_socket.recv(1024))
            if not response == 'ACK':
                return response
            self.client_socket.sendall(pickle.dumps(password))
            print("c")
            response = pickle.loads(self.client_socket.recv(1024))
            if not response == 'ACK':
                return 'ERROR'
            self.client_socket.sendall(pickle.dumps(auth_mail))
            print("d")
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
            self.connect()
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

    def ask_new_messages(self):
        try: #NOTE: may send array of msg objects
            self.client_socket.sendall(pickle.dumps('NEWMSG?'))
            response = pickle.loads(self.client_socket.recv(1024))
            print(response)
            if response == 'NONE':
                return
            elif response == 'SENDING':
                self.client_socket.sendall(pickle.dumps('OK'))
                data_size = pickle.loads(self.client_socket.recv(1024))  # first the size
                self.client_socket.sendall(pickle.dumps('ACK'))
                print(data_size)

                raw = self.client_socket.recv(data_size)
                print(len(raw))
                while not len(raw) == data_size:
                    print(len(raw))
                    raw += self.client_socket.recv(data_size)
                data = pickle.loads(raw)
                self.client_socket.sendall(pickle.dumps('ACK'))
                print(data)
                if self.callback and data:
                    self.callback(data)


        except Exception as e:
            print("Can't Send -->  ", e)

    def receive_messages(self):
        """
        receive messages from server
        :return: None
        """
        while True:
            self.stopped = True
            #print(self.stop_thread)
            while not self.stop_thread:
                self.stopped = False
                try:
                    print(11111)
                    self.ask_new_messages()
                    time.sleep(1)
                except Exception as e:
                    print("[EXCEPTION]", e)
                    break

                # -- Complete the instruction


    def ready(self):
        """
        sends the server that he can send history
        :return:
        """
        try:
            self.client_socket.sendall(pickle.dumps('READY'))
            self.receive_thread.start()
        except Exception as e:
            print("[EXCEPTION]", e)

    def send_message(self,msg): #TODO: add FTP logic (remember sending msg obj without the data), also add note for too long msg
        """
        send messages to server
        :param msg: str
        :return: None
        """
        self.stop_thread = True
        while not self.stopped:
            print(666)
            time.sleep(2)
            pass

        self.client_socket.sendall(pickle.dumps('SENDMSG'))
        print("sent1")
        response = pickle.loads(self.client_socket.recv(1024))
        print(response)
        if not response == 'START':
            return
        # Convert Python object to Pickle bytes
        data = pickle.dumps(msg)
        #self.client_socket.sendall()
        size = len(data)

        response = ""
        while not response == 'ACK':
            print("sending ", size)
            self.client_socket.sendall(pickle.dumps(size))
            print("sent2")
            response = pickle.loads(self.client_socket.recv(1024))

        response = ""
        while not response == 'ACK':
            self.client_socket.sendall(data)
            response = pickle.loads(self.client_socket.recv(1024))

        self.stop_thread = False


