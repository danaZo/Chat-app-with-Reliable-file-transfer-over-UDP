import socket
from threading import Thread
import sys, os
import pickle
import binascii
import time
import random
# global variables
serverPort = 50000
serverIP = '0.0.0.0'
clients: {socket.socket}
clients = dict()
clientAddr = dict()
forbbidenNames = ["all", "quit", "online", "file", "getfiles"] # list of forbidden user names
ACK_REQ = 10000000
STOP_REQ = 20000000
WIN_SIZE = 10
serverSocket: socket.socket
fileSoc: socket.socket

packetLossPrct = float(input("insert packet loss percentage, (0 for normal use, more for loss simulation):\n")) / 100
corruptionPrct = float(input("insert packet corruption percentage, (0 for normal use, more for simulation):\n")) / 100

def setUpServer():
    '''
    a function that set the server up, safely connect the sockets
    and define the socket settings
    '''
    global serverSocket, fileSoc
    # socket creations
    try:
        # server TCP socket
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverSocket.bind((serverIP, serverPort))
        serverSocket.listen(5)

        # server UDP socket
        fileSoc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        fileSoc.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 4096)
        fileSoc.bind((socket.gethostname(), 50000))

    except socket.error as e:
        print(f"Socket error: {e}")
        sys.exit()

    print("Server is up and listening.")


def shutDown():
    """
    Gracefully shut down the server and the clients connections
    """
    for soc in clients:
        soc.close()
        sys.exit()
    fileSoc.close()
    serverSocket.close()


def getOnlineUsers(client: socket.socket):
    '''
    :param client: the requesting socket
    send list of the online members to the requesting client
    '''
    res = ""
    for name in clients.keys():
        res = res + name + ', '
    client.send(f"Users Online: {res[:-2]}".encode())


def getFilesOnserver( name: str):
    '''
    send a list of available files to the requesting client
    :param name: requesting client
    '''
    directMessage("Available files: ", name, str(os.listdir('Files')))


def sendPkstByNums(indices: list, packetList: list, fileSoc: socket.socket, addr):
    """
    :param indices: list of packet indexes to send
    :param packetList: the packet array we send from
    :param fileSoc: sender socket
    :param addr: receiver address
    """
    global WIN_SIZE
    # send the number of packets to send
    fileSoc.settimeout(1)
    print(f"Sending {len(indices)} packets")

    while indices:
        sent = len(indices)  # number of sent packets
        for i in indices:
            pkt = packetList[i]
            if i == 427:
                print(f"len ={len(pkt)}" )
                print(pkt)
            if packetLossPrct > 0:
                rand = random.uniform(0,1)
                if rand < packetLossPrct:
                    print(f"packet #{i} lost - simulation")
                    continue
            if corruptionPrct > 0:
                rand = random.uniform(0, 1)
                if rand < corruptionPrct:
                    pkt = corruptPacket(pkt)
                    print(f"Packet #{i} corrupted for testing purposes")
            fileSoc.sendto(pkt, addr)  # sending the packet to the receiver
        time.sleep(0.02)
        # requesting an acknowledge status from the receiver
        fileSoc.sendto(ACK_REQ.to_bytes(4, 'big'), addr)
        data, _ = fileSoc.recvfrom(1024)
        acked = pickle.loads(data)  # contain the Acked packets
        indices = [x for x in indices if x not in acked]  # leaving only the lost packets
        if len(indices) == 0:  # exit the function in case that all of the packets ACK'ed
            WIN_SIZE += 1
            print("all packets received successfully")
            break
        lost = len(indices)  # decrease the window size
        if lost / sent > 0.07:
            WIN_SIZE = max(10, int(WIN_SIZE / 2))

        print("retransmiting packets: " + str(indices))


def sendFile(client: socket.socket, filename: str):
    """
    Function that transfer a file to the requesting client
    :param client: receiver's socket
    :param filename: file to send
    """
    global fileSoc

    # open the requested file if it exits
    packetList = []
    pacNo = 0

    filename = 'Files/' + filename  # access to the server's files area
    try:
        f = open(filename, 'rb')

    except IOError:
        client.send("File does not exits".encode())
        return

    # split the file into packets of 500 Bytes - to avoid fragmentation
    while True:
        segment = f.read(500)
        if segment == b'':
            break
        segment = pacNo.to_bytes(4, 'big') + segment  # add the serial number of the packet
        segment = segment + (binascii.crc32(segment) & 0xffffffff).to_bytes(32, 'big')
        packetList.append(segment)  # store the file as list of ordered packets
        pacNo += 1
    f.close()

    try:
        # send the name of the file
        addr = (socket.gethostname(), clientAddr[clientSoc][1])
        fileSoc.sendto(filename[6:].encode(), addr)
        # send the number of packets that were extracted from the file
        fileSoc.sendto(str(pacNo).encode(), addr)

        # send the packets
        base = 0  # window base
        while base < pacNo / 2:
            upperBound = min(base + WIN_SIZE, pacNo)  # Window end
            sendPkstByNums(list(range(base, upperBound)), packetList, fileSoc, addr)
            base = upperBound # sliding the window
        fileSoc.settimeout(120)  # waiting for user to chose whether to download the res or not
        if pacNo > 1:
            fileSoc.sendto(STOP_REQ.to_bytes(4, 'big'), addr)
            msg, _ = fileSoc.recvfrom(128)
            print(msg)
            if str.lower(msg.decode()) == 'no':
                return
        # sending the second half of the file
        while base < pacNo:
            upperBound = min(base + WIN_SIZE, pacNo)
            sendPkstByNums(list(range(base, upperBound)), packetList, fileSoc, addr)
            base = upperBound

    except Exception as e:
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
    Safely connect and get name from new users
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
    """
    safely disconnect clients from the server
    :param clientSoc:
    :param name:
    :return:
    """
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
                sendFile(clientSoc, msg[1])
                continue

            if msg[0] == 'online':
                getOnlineUsers(clientSoc)
                continue
            if msg[0] == 'getfiles':
                getFilesOnserver(name)
            else:
                clientSoc.send("Unknown user or command ".encode())

        # connection closed or some other  error occured
        except Exception as e:
            print(f"Error {e}")
            del clients[name]

def corruptPacket(data):
    """
    a simple function that corrupts packet for testing purposes
    :return: the corrupted data
    """
    d = list(data)
    for i in range(0, random.randint(1, 4)):
        pos = random.randint(0, len(d) - 33) # to avoid corrupting the crc bits
        d[pos] = random.randint(0, 255)
    return bytes(d)

setUpServer()
while True:
    clientSoc, caddr = serverSocket.accept()
    clientAddr[clientSoc] = caddr
    print(f"{caddr[1]} connected to the server")
    client_name = connectNewClient(clientSoc)
    # assign the client its own thread and send him off
    # we make it a daemon thread so it wont stop the server from closing when it want to
    Thread(target=listenToClient, args=(clientSoc, client_name), daemon=True).start()


