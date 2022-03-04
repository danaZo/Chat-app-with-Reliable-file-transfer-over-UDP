import socket
from threading import Thread
import sys, os
import pickle

import time

MSG_HDR = 10
serverPort = 50000
serverIP = socket.gethostname()
clients: {socket.socket}
clients = dict()
clientAddr = dict()
clientFileSoc = dict()
forbbidenNames = ["all", "quit", "online", "file"]
ACK_REQ = 10000000
STOP_REQ = 20000000
serverSocket: socket.socket
fileSoc: socket.socket


def setUpServer():
    global serverSocket, fileSoc
    # server initialization
    try:
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        fileSoc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        fileSoc.bind((socket.gethostname(), 50000))

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
    for soc in clients:
        soc.close()
        sys.exit()
    fileSoc.close()
    serverSocket.close()


def getOnlineUsers(client: socket.socket):
    res = ""
    for name in clients.keys():
        res = res + name + ', '
    client.send(f"Users Online: {res[:-2]}".encode())


def getFilesOnserver(client: socket.socket, name: str):
    directMessage("Available files: ", name, str(os.listdir('Files')))


def sendPkstByNums(indices: list, packetList: list, fileSoc: socket.socket, addr):
    # send the number of packets to send
    fileSoc.settimeout(1)
    print(f"Sending {len(indices)} packets")

    boolVal = True
    packetToLoose = [1, 3, 5, 8]

    while indices:
        for i in indices:
            if i == 10 and boolVal:
                boolVal = False
                continue
            fileSoc.sendto(packetList[i], addr)
        # eliminate the Ack'ed packets from the list
        time.sleep(0.15)


        fileSoc.sendto(ACK_REQ.to_bytes(4, 'big'), addr)
        data, _ = fileSoc.recvfrom(1024)
        acked = pickle.loads(data)  # contain the Acked packets
        indices = [x for x in indices if x not in acked]
        if len(indices) == 0:
            print("all packets received successfully")
            break


        print("retransmiting packets: " + str(indices))

    print(f"all {len(indices)} packets ACK'ed")


def sendFile(client: socket.socket, filename: str, client_name: str):
    global fileSoc

    # open the requested file if it exits
    packetList = []
    pacNo = 0

    filename = 'Files/' + filename

    try:

        f = open(filename, 'rb')


    except IOError:
        client.send("File does not exits".encode())
        return

    # split the file into packets of 1350 Bytes

    while True:
        segment = f.read(1350)
        if segment == b'':
            break
        segment = pacNo.to_bytes(4, 'big') + segment  # add the serial number of the packet
        packetList.append(segment)  # store the file as list of ordered packets
        pacNo += 1
    f.close()
    # open UDP socket for the server
    try:
        # send the name of the file
        fileSoc.sendto(filename[6:].encode(), (socket.gethostname(), clientAddr[clientSoc][1]))
        # send the number of packets that were extracted from the file
        fileSoc.sendto(str(pacNo).encode(), (socket.gethostname(), clientAddr[clientSoc][1]))

        # send the packets
        addr = (socket.gethostname(), clientAddr[clientSoc][1])
        # sendPkstByNums(list(range(pacNo)), packetList, fileSoc, addr)
        sendPkstByNums(list(range(int(pacNo/2))), packetList, fileSoc,addr )
        #fileSoc.sendto(STOP_REQ.to_bytes(4, byteorder="big"), addr)
        sendPkstByNums(list(range(int(pacNo / 2), pacNo)), packetList, fileSoc,addr)




    except socket.error as e:
        print(f"Could not send the file {e}")
        return


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
        while name in clients.keys() or name in forbbidenNames:
            clientSoc.send("<Username taken or forbidden, please pick another>".encode())
            name = clientSoc.recv(128).decode()
        clientSoc.send("NAME_OK".encode())

    except socket.error as e:
        print(f"Receiving Error {e} ")
        sys.exit()

    broadcast("", f"> {name} joined the conversation")
    # print(f"{name} joined the conversation")
    clients[name] = clientSoc

    return name


def disconnectClient(clientSoc: socket.socket, name: str):
    del clients[name]
    clientSoc.close()
    broadcast("", f"> {name} disconnected")


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
            print("command: " + msg)
            if len(msg) == 0:
                disconnectClient(clientSoc, name)
                return

            msg = msg.split(":")
            if msg[0] == "all":
                broadcast(name, ''.join(msg[1:]))
                continue

            if msg[0] == "quit":
                disconnectClient(clientSoc, name)
                return

            if msg[0] in clients.keys():
                directMessage(name, msg[0], ''.join(msg[1:]))
                continue

            if msg[0] == 'file':
                sendFile(clientSoc, msg[1], name)
                continue

            if msg[0] == 'online':
                getOnlineUsers(clientSoc)
                continue
            if msg[0] == 'getfiles':
                getFilesOnserver(clientSoc, name)
            else:
                clientSoc.send("Unknown user or command ".encode())

        # connection closed or some other  error occured
        except Exception as e:
            print(f"Error {e}")
            del clients[name]


setUpServer()
while True:
    clientSoc, caddr = serverSocket.accept()
    clientAddr[clientSoc] = caddr
    print(f"{caddr[1]} connected to the server")
    client_name = connectNewClient(clientSoc)
    # assign the client its own thread and send him off
    # we make it a daemon thread so it wont stop the server from closing when it want to
    Thread(target=listenToClient, args=(clientSoc, client_name), daemon=True).start()