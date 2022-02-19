import socket
from select import select

MSG_HDR = 10
serverPort = 50000
serverIP = socket.gethostname()

# server initialization
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind((serverIP, serverPort))
serverSocket.listen(5)

while True:
    active_sockets,_, err_sockets = select()


def broadcast(msg: str, sender: socket.socket) -> bool:
    pass


def privateMessage(msg: str, sender: socket.socket, receiver: socket.socket) -> bool:
    pass
