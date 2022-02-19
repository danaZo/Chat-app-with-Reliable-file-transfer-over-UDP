import socket
import sys
from threading import Thread

serverPort = 50000
serverIp = socket.gethostname()
menu = "what would you like to do?\nTo send a public message: insert p followed by new line and your message  \nTo " \
       "send " \
       "a private message :insert r followed by new line and your message\nTo quit: insert q\n "



def connectToserver(soc: socket.socket):
    # connecting to the server

    try:  # set connection and user name
        response = b''
        soc.connect((serverIp, serverPort))
        while response.decode() != "NAME_OK":
            name = input("Enter your user name: ")
            soc.send(name.encode())
            response = soc.recv(128)

            print(f"{response.decode()}")

    except Exception as e:
        print(f"Connection failed due to: {e}")
        quit()


def getMessages(soc: socket.socket):
    while True:
        try:
            message = soc.recv(2048).decode()
            print(message)
        except Exception as e:
            print(f"socket error{e}")
            sys.exit()


def sendMessage(soc: socket.socket):
    print(menu)
    while True:
        message = input()

        if message.lower() == 'q':
            return
        try:
            soc.send(message.encode())
        except Exception as e:
            print(f"Socket error {e}")
            sys.exit()


if __name__ == '__main__':
    clientSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connectToserver(clientSoc)
    print("connection done")
    # initialize a daemon thread to listen for incoming messages
    Thread(target=getMessages, daemon=True, args=(clientSoc,)).start()

    # send messages when user want to
    sendMessage(clientSoc)

    clientSoc.close()
