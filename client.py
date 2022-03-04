import pickle
import signal
import socket
import sys, os
import time
from threading import Thread, main_thread

ACK_REQ = 10000000
fSizeInPkts: int
fname: str

is_windows = sys.platform.startswith('win')
serverPort = 50000
serverIp = socket.gethostname()
menu = "what would you like to do?\nTo send a public message: type all: and then your message\n" \
       "To send a private message type person name followed by ':' and write your message\n" \
       "To quit enter quit:\n" \
       "To get a list of online members type online:"


def connectToServer(soc: socket.socket, udp: socket.socket):
    # connecting to the server

    try:  # set connection and user name
        response = b''
        soc.connect((serverIp, serverPort))
        udp.bind((socket.gethostname(), soc.getsockname()[1]))
        while response.decode() != "NAME_OK":
            print(response.decode())
            name = input("Enter your user name: ")
            soc.send(name.encode())
            response = soc.recv(128)

    except Exception as e:
        print(f"Connection failed due to: {e}")
        quit()


def getMessages(soc: socket.socket):
    while True:
        try:
            message = soc.recv(2048).decode()
            if len(message) == 0:
                print("msg len is 0 ~ check why it happened")
                sys.exit()

            print(message)
        except Exception as e:
            print(f"socket error{e}")
            sys.exit()


def sendMessage(soc: socket.socket, fileSoc: socket.socket):
    print(menu)
    while True:
        message = input()

        if message == "quit:":
            return

        if message[:4] == 'file':
            # we open a new tcp socket for system messages between the server and the client
            # try:
            #     controlSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # except socket.error:
            Thread(target=getFile, daemon=True, args=(fileSoc,)).start()

        # if message.split(':')[0] == 'file':

        try:
            soc.send(message.encode())
        except Exception as e:
            print(f"Socket error {e}")
            sys.exit()


def getFile(fileSoc: socket.socket):
    # get file name and the number of incoming packets
    print(fileSoc)
    print("Incoming file")
    filename, _ = fileSoc.recvfrom(128)
    print(filename)
    packetsNum, _ = fileSoc.recvfrom(128)
    packetsNum = int(packetsNum.decode())
    print("size in packets: " + str(packetsNum))

    packets = [b''] * packetsNum  # list to save the received packets

    fileSoc.settimeout(1)  # close thread and socket if no data sent for 5 seconds
    f = open(filename.decode(), 'wb')
    Acks = []
    try:
        while True:

            # get packets from server
            pac, addr = fileSoc.recvfrom(2048)
            # check if the pac is part of the file or it is an ack request
            seqNo = int.from_bytes(pac[:4], byteorder='big')
            if seqNo == ACK_REQ:
                # we send the ACK list to the server
                fileSoc.sendto(pickle.dumps(Acks), addr)
                continue
            # check if we got the package already

            if packets[seqNo] == b'':  # packet haven't buffered before - solves problem of duplicate packets
                packets[seqNo] = pac[4:]
                print(seqNo)
                Acks.append(seqNo)  # mark that we got this package

            if b'' not in packets:
                print("all packets received successfully")
                # read the last ACK_REQ to clear the buffer
                d , _ =fileSoc.recvfrom(128)
                print(f"leftovers {d}")
                break

        for pac in packets:
            f.write(pac)
        f.close()
        # flush remaining data
        fileSoc.settimeout(0.1)
    except socket.error:
        f.close()


if __name__ == '__main__':
    clientSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    fileSoc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    connectToServer(clientSoc, fileSoc)

    print("Connected successfully")
    # initialize a daemon thread to listen for incoming messages
    Thread(target=getMessages, daemon=True, args=(clientSoc,)).start()

    # send messages when user want to
    sendMessage(clientSoc, fileSoc)

    clientSoc.close()
    fileSoc.close()
