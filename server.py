import pickle
import threading
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

def send_to(msg):
    """
    send new messages to all clients
    :param msg: bytes["utf8"]
    :param name: str
    :return:
    """
    for p in persons:
        print(p.mail)
        print(msg.get_to())
        recipients = msg.get_to()
        recipients = recipients.split(',')
        for recipient in recipients:
            if p.mail == recipient:
                client = p.client_socket
                try:
                    lock.acquire()
                    client.sendall(pickle.dumps(msg))
                    lock.release()
                    print("sent")
                except Exception as e:
                    print(e)

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

        client.sendall(pickle.dumps('CREATED'))
    except Exception as e:
        print(e)




def client_communication(person):
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


    response = pickle.loads(client.recv(BUFSIZ))
    print(response)
    if not(response == "READY"):
        client.close()
        return

    person.set_mail(mail)
    persons.append(person)

    print(person.mail)
    history = chat_db.get_history(person.mail)

    lock.acquire()
    client.sendall(pickle.dumps(history))
    lock.release()

    #msg_object = Message((datetime.datetime.now()).strftime("%Y %b %H:%M"), addr, f"{addr} has join the chat!")
    #lock.acquire()
    #chat_db.insert_msg(msg_object)
    #lock.release()

    #broadcast(msg_object) # boradcast welcome message

    while True: # wait for any messages from person
        try:
            msg_object=pickle.loads(client.recv(BUFSIZ))
            print(msg_object)
            if msg_object.get_info() == "EXIT":
                exit(9999)
            lock.acquire()
            chat_db.insert_msg(msg_object)
            #-- Complete the instruction (insert to db)
            lock.release()
            send_to(msg_object)
            #broadcast(msg_object)

        except Exception as e:
            print("[EXCEPTION]", e)
            break



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
            p = Person(address, client_socket)
            threading.Thread(target=client_communication, args=(p,)).start()

 

if __name__ == "__main__":
    global chat_db
    chat_db = ChatDB()
    global users_db
    users_db = UsersDB()
    #users_db.insert_new_user("aaa@mb.com", "bbb", '@gmail.com')
    #wait_for_connection()
    SERVER.listen(MAX_CONNECTIONS) # open server to listen for connections
    print("[STARTED] waiting for connections...")
    ACCEPT_THREAD = Thread(target=wait_for_connection)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
