import socket
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) #UDP sock
address = ("127.0.0.1",5002)
sock.bind(address)
while True:
    data,addr = sock.recvfrom(32768) #32768 byte
    print(data)
    print(addr)

    
