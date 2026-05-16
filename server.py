import pickle
import threading
from socket import AF_INET, socket, SOCK_STREAM
from threading import Lock
from threading import Thread

from classes.chat_db_class import ChatDB
from classes.person import Person
from classes.msg_class import Message

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
        if p.mail == msg.get_to():
            client = p.client_socket
            lock.acquire()
            client.sendall(pickle.dumps(msg))
            lock.release()


def client_communication(person):
    """
    Thread to handle all messages from client
    :param person: Person
    :return: None
    """
    global chat_db

    client = person.client_socket

    # First message received is always the person's addr
    # Convert Pickle string back to Python object
    name = pickle.loads(client.recv(BUFSIZ))
    person.set_name(name)
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
        except:
            pass
        if client_socket:
            p = Person(address, client_socket)
            threading.Thread(target=client_communication, args=(p,)).start()

 

if __name__ == "__main__":
    global chat_db
    chat_db = ChatDB()
    SERVER.listen(MAX_CONNECTIONS) # open server to listen for connections
    print("[STARTED] waiting for connections...")
    ACCEPT_THREAD = Thread(target=wait_for_connection)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
