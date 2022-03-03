import socket

'''
this module adds reliable data transfer attributes to the the unreliable
UDP connection.
'''


def rdtSend(sender: socket.socket, destination: (str, int), msg: str, code: str):
    sender.settimeout(0.5)  # after half second without a response the sender wil retransmit the packet

    while True:
        sender.sendto(msg.encode(), destination)
        try:
            response, addr = sender.recvfrom(128)
        except Exception as e:
            print(e)
            continue
        if response.decode() == code and destination == addr:
            return


def rdtRecv(receiver: socket.socket, code: str):

        msg, addr = receiver.recvfrom(128)
        rdtSend(receiver, addr, code,)