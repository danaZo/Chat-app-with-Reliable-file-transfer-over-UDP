import signal
import socket
import sys, os
from threading import Thread, main_thread

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
            print("f")
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
    print(packetsNum)
    packetsNum = int(packetsNum.decode())

    packets = [b''] * packetsNum # list to save the received packets
    receivedPkts = 0

    f = open(filename.decode(), 'wb')

    while True:

        data, _ = fileSoc.recvfrom(2048)
        receivedPkts += 1
        print(int.from_bytes(data[:4], byteorder='big'))
        packets[int.from_bytes(data[:4], byteorder='big')] = data[4:]
        if receivedPkts == packetsNum:
            break

    for pac in packets:
        f.write(pac)
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
