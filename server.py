import pickle
import threading
from http.cookiejar import request_port
from socket import AF_INET, socket, SOCK_STREAM
from threading import Lock
from threading import Thread

import re
import TFA
import time
from classes.chat_db_class import ChatDB
from classes.person import Person
from classes.msg_class import Message
from classes.users_db_class import UsersDB
import ssl
import Antivirus
import Gemini

# GLOBAL CONSTANTS
HOST = 'localhost'
PORT = 5500
ADDR = (HOST, PORT)
MAX_CONNECTIONS = 10
BUFSIZ = 1024
lock = Lock()

# GLOBAL VARIABLES
persons = []
SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR) # set up server

# 1. הגדרת קונטקסט ה-TLS של השרת וטעינת התעודות
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile="server.crt", keyfile="server.key")



def broadcast(msg):
    """
    send new messages to all clients
    :param msg: bytes["utf8"]
    :param name: str
    :return:
    """
    for p in persons:
        print(p.mail)
        print(msg.get_info())
        client = p.client_socket
        lock.acquire()
        client.sendall(pickle.dumps(msg))
        lock.release()

def save_msg(msg):
    for p in persons:
        print(p.mail)
        print(msg.get_to())
        recipients = msg.get_to()
        recipients = recipients.split(',')
        for recipient in recipients:
            if p.mail == recipient:
                p.waiting_msgs.append(msg)

def send_to(person):
    """
    send new messages to all clients
    :param msg: bytes["utf8"]
    :param name: str
    :return:
    """
    client = person.client_socket

    try:
        print(person.waiting_msgs)
        if person.waiting_msgs == []:
            client.sendall(pickle.dumps("NONE"))
            return
        else:
            client.sendall(pickle.dumps('SENDING'))
            response = pickle.loads(client.recv(BUFSIZ))
            if not response == 'OK':
                return

            data = pickle.dumps(person.waiting_msgs)
            # self.client_socket.sendall()
            size = len(data)

            response = ""
            while not response == 'ACK':
                client.sendall(pickle.dumps(size))
                response = pickle.loads(client.recv(1024))

            response = ""
            while not response == 'ACK':
                client.sendall(data)
                response = pickle.loads(client.recv(1024))

            person.waiting_msgs = []

    except Exception as e:
        print(e)

def get_msg(client):
    client.sendall(pickle.dumps('START'))
    print("Sent message start send")
    msg_size = pickle.loads(client.recv(BUFSIZ)) #first the size
    print(msg_size)
    client.sendall(pickle.dumps('ACK'))
    print(1)
    raw = client.recv(msg_size)
    print(len(raw))
    while not len(raw) == msg_size:
        print(len(raw))
        raw += client.recv(msg_size)
    msg_object = pickle.loads(raw)
    client.sendall(pickle.dumps('ACK'))
    print(msg_object)
    scan_thread = Thread(target=scan_and_save, args=(msg_object,))
    scan_thread.start()

def scan_and_save(msg_object):
    print("Scan thread")
    report = ""

    """links = Gemini.search_links(msg_object.info)
    if not links.strip() == "":
        links = links.split(',')
        for link in links:
            report += Antivirus.scan(link, 'link') + '\n'"""

    if msg_object.data:
        report += Antivirus.scan(msg_object.data, 'file') + '\n'

    print(report)
    if not report.strip() == "":
        msg_object.scan_report = report

    lock.acquire()
    chat_db.insert_msg(msg_object)
    lock.release()
    save_msg(msg_object)


def check_mail(mail):
    global users_db
    pattern = r'([a-z]|[A-Z]|[0-9])+@mb.com'  # required pattern
    result = re.match(pattern, mail)
    checked, auth = users_db.user_check(mail, '')
    if result and not checked and auth == 'DO NOT EXIST':
        return True
    else:
        return False

def new_user(client):
    global users_db
    mail =''
    password = ''
    auth_mail = ''
    try:
        client.sendall(pickle.dumps('WAITING'))
        while True:
            mail = pickle.loads(client.recv(BUFSIZ))
            if check_mail(mail):
                break
            else:
                client.sendall(pickle.dumps('INVALID MAIL'))
    except Exception as e:
        print(e)
    try:
        client.sendall(pickle.dumps('ACK'))
        password = pickle.loads(client.recv(BUFSIZ))
        client.sendall(pickle.dumps('ACK'))
        auth_mail = pickle.loads(client.recv(BUFSIZ))

        users_db.insert_new_user(mail, password, auth_mail)
        print(chat_db.create_new_table(mail))

        client.sendall(pickle.dumps('CREATED'))
    except Exception as e:
        print(e)

def client_loop(client, person):
    while True:  # wait for any requests from person
        try:
            request = pickle.loads(client.recv(BUFSIZ))
            print(request)
            if request == "NEWMSG?":
                send_to(person)
            elif request == "SENDMSG":
                get_msg(client)
            elif not request:
                continue
            else:
                client.sendall(pickle.dumps('WRONG'))
        except Exception as e:
            print("[EXCEPTION]", e)
            break

def client_setup(person):
    """
    Thread to handle all messages from client
    :param person: Person
    :return: None
    """
    print("Client communication")
    global chat_db
    global users_db

    client = person.client_socket

    client.sendall(pickle.dumps('REQUEST')) #waiting to know if the client wants to create a new user or log-in
    response = pickle.loads(client.recv(BUFSIZ))
    if response == "NEW":
        new_user(client)
        try:
            client.close()
            return
        except Exception as e:
            print(e)

    # First message received is always the person's addr, then the password
    try:
        client.sendall(pickle.dumps('WAITING'))
        print("Sign sent")
        mail = pickle.loads(client.recv(BUFSIZ))#TODO: add ack
        print("Mail received")
        client.sendall(pickle.dumps('ACK'))
        password = pickle.loads(client.recv(BUFSIZ))
        print("Password received")
    except Exception as e:
        print(e)
        return

    checked, auth = users_db.user_check(mail, password)
    if not checked:
        try:
            client.sendall(pickle.dumps('WRONG PASSWORD OR MAIL'))
            return
        except Exception as e:
            print(e)
            return

    sent, code = TFA.send_TFA(auth) #send 2fa mail here(so the client wouldn't be able to change)

    try:
        to_send = 'OK' + ' ' + str(auth)
        client.sendall(pickle.dumps(to_send))
    except Exception as e:
        print(e)
        return

    while True: #checkin 2fa
        try:
            response = pickle.loads(client.recv(BUFSIZ))
            print(response)
            if response == code:
                client.sendall(pickle.dumps('CORRECT'))
                break
            else:
                client.sendall(pickle.dumps('WRONG - Sending new code'))
                sent, code = TFA.send_TFA(auth)  # send 2fa mail again
                print('Sent new code')
        except Exception as e:
            print(e)
            return


    person.set_mail(mail)
    persons.append(person)

    print(person.mail)
    history = chat_db.get_history(person.mail)
    person.waiting_msgs += history

    response = pickle.loads(client.recv(BUFSIZ))  # TODO: add try
    print(response)
    if not (response == "READY"):
        client.close()
        return
    client_loop(client, person)


def wait_for_connection():
    """
    Wait for connection from new clients, start new thread once connected
    :param SERVER:
    :return: None
    """

    while True:
        client_socket = None
        address = None
        try:
            client_socket, address = SERVER.accept()
            print("[CONNECTED]", address)
        except:
            pass
        if client_socket:
            print("[CONNECTED]")
            secure_client_socket = context.wrap_socket(client_socket, server_side=True)
            p = Person(address, secure_client_socket)
            threading.Thread(target=client_setup, args=(p,)).start()



if __name__ == "__main__":
    global chat_db
    chat_db = ChatDB()
    global users_db
    users_db = UsersDB()
    users_db.insert_new_user("a", "a", '2idobaruch@gmail.com')
    #wait_for_connection()
    SERVER.listen(MAX_CONNECTIONS) # open server to listen for connections
    print("[STARTED] waiting for connections...")
    ACCEPT_THREAD = Thread(target=wait_for_connection)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
