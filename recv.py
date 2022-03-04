import socket

soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
soc.bind(("127.0.0.1",1234))
print()

print("listening...")
filename, _ = soc.recvfrom(128)
packetsNum , _= soc.recvfrom(128)
packetsNum = int(packetsNum.decode())
print(packetsNum)
receivedPkts = 0
packets = [b''] * packetsNum
print(filename.decode())
f = open(filename.decode(), 'wb')


while True:

    data, _ = soc.recvfrom(2048)
    receivedPkts += 1
    # packets[]
    print(int.from_bytes(data[:4],byteorder='big'))
    packets[int.from_bytes(data[:4],byteorder='big')] = data[4:]
    # f.write(data[5:])
    # f.write(data.decode())
    # print(data.decode())
    if receivedPkts == packetsNum:
        break

for pac in packets:
    f.write(pac)