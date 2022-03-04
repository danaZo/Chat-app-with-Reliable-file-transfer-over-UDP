import socket

packetList = []
Nos = []
f = open('Files/b1.pdf', 'rb')
count = 0
while True:
    packet = f.read(1250)

    if packet == b'':
        break
    packet = count.to_bytes(4,'big') + packet
    # print(packet)
    packetList.append(packet)
    count += 1

# no1 = packetList[0][]
# print(packetList[0])
print(int.from_bytes(packetList[3][:4],byteorder='big'))

clientSoc : socket.socket
senderSoc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
senderSoc.sendto("bb.pdf".encode(),("127.0.0.1",1234))
senderSoc.sendto(str(len(packetList)).encode(),("127.0.0.1",1234))

print(len(packetList))
for pac in packetList:
    # print(pac)
    senderSoc.sendto(pac,("127.0.0.1",1234))


