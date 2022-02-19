import socket
from threading import Thread
import sys

MSG_HDR = 10
serverPort = 50000
serverIP = socket.gethostname()
clients: {socket.socket}
clients = dict()

# server initialization
try:
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as e:
    print(f"Error opening socket: {e}")
    sys.exit()

try:
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
except socket.error as e:
    print(f"Socket setting Error {e}")
    sys.exit()

try:
    serverSocket.bind((serverIP, serverPort))
except socket.error as e:
    print(f"Socket binding Error {e}")
    sys.exit()

try:
    serverSocket.listen(5)
except socket.error as e:
    print(f"Socket listening Error {e}")
    sys.exit()

print("Server is up and listening.")


def shutDown():
    """
    Gracefully shut down the server
    """
    pass


def broadcast(name: str, msg: str):
    """
    sends message to all the connected users
    :param name: sender name
    :param msg: message to send
    """
    msg = name + ':' + msg
    for username in clients:
        if username != name:
            clients[username].send(msg.encode())


def directMessage(senderName: str, receiverName, msg: str):
    """
    Send private message to specific user
    """
    msg = senderName + '[DM]: ' + msg
    clients[receiverName].send(msg.encode())


def connectNewClient(clientSoc: socket.socket) -> str:
    """
    Connect and get name from new users
    :param clientSoc:  The socket that belong to the new client
    """
    # get user name from client
    name: str
    try:  # make sure the name picked by the user is not taken
        name = clientSoc.recv(128).decode()
        while name in clients.keys():
            clientSoc.send("<Username taken, please pick another>".encode())
            name = clientSoc.recv(128).decode()
        clientSoc.send("NAME_OK".encode())

    except socket.error as e:
        print(f"Receiving Error {e} ")
        sys.exit()

    broadcast("", f"> {name} joined the conversation")
    # print(f"{name} joined the conversation")
    clients[name] = clientSoc

    return name


def listenToClient(clientSoc: socket.socket, name: str):
    """
    A function meant to called by a daemon thread.
    used to listen to the requests of a single client
    :param clientSoc: the costumer
    :param name: client's name
    """
    # listening to messages from the client
    while True:
        try:
            msg = clientSoc.recv(1024).decode()

            if len(msg) == 0:
                broadcast("", f"> {name} disconnected")
                clientSoc.close()
                return

            msg = msg.split(":")
            if msg[0] == "all":
                broadcast(name, ''.join(msg[1:]))
                continue

            if msg[0] in clients.keys():
                directMessage(name, msg[0], ''.join(msg[1:]))

            else:
                clientSoc.send("User does not exits".encode())

        # connection closed or some other  error occured
        except Exception as e:
            print(f"Error {e}")
            del clients[name]


while True:
    clientSoc, caddr = serverSocket.accept()
    print(f"{caddr[1]} connected to the server")
    client_name = connectNewClient(clientSoc)
    # assign the client its own thread and send him off
    # we make it a daemon thread so it wont stop the server from closing when it want to
    Thread(target=listenToClient, args=(clientSoc, client_name), daemon=True).start()
