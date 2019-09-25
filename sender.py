import socket
import multiprocessing

ReceiverIP = '127.0.0.1'
ReceiverPort = 5005
AVAILABLE_PORTS = range(5007, 5500, 2)

def sendFile(portToSend, queue, fileRequest, packetId):
    #Bind socket
    sockReceiveFile = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sockReceiveFile.bind((ReceiverIP, ReceiverPort))
    sockReceiveFile.settimeout(5)
    print(fileRequest)

    fileOpen = open(fileRequest, 'wb')
    packetData, packetAddress = sockReceiveFile.recvfrom(32768)
    packetToSend = Packet(parsedBytes = bytearray(data))
    while(packetToSend.packetData < 2):
        if (packetToSend.isGeneratedChecksumEqualToActualChecksum and packetToSend.packetSequenceNumber == i):
            print(i)
            fileOutput.write(bytes(packetToSend.packetData))
            res = Packet(1, packetToSend.packetId) #temp change var
            sockReceiveFile.sendto(res.parsePacketInByteArrays(), (receiverIP, receiverPort))
            packetData, packetAddress = sockReceiveFile.recvfrom(32768)
            packetToSend = Packet(packetParsedBytes = bytearray(packetData))
            i+=1
            if (i == 256):
                i = 0
    print('Sent File : ',fileRequest)
    fileOpen.close()
    queue.put(portToSend)

def receiver(packetData, packetAddress, queue, sock):
    packet = Packet(packetParsedBytes = bytearray(data))
    firstRequest = bytes(packet.packetData).decode().split(':') #Change var
    fileRequest = firstRequest[0] 
    primarySendPort = int(firstRequest[1]) #change var
    print("File Request:", fileRequest)
    if (packet.isGeneratedChecksumEqualToActualChecksum()):
        port = queue.get()
        print("Starting transfer from port: ", receiverPort)
        fileRequest = PATH + fileRequest
        packetId = packet.packetId
        packet = Packet(parsedData = bytearray(str(receiverPort).encode()), packetId = packetId)
        print(primarySendPort)
        sock.sendto(packet.parsePacketInByteArrays(),(receiverIP, receiverPort))
        sendFile(portToSend, queue, fileRequest, packetId)
    else:
        if(not packet.isGeneratedChecksumEqualToActualChecksum()):
            print('Checksum Failed')
        print("Packet sending has failed")
        packet = Packet(3,0) #temp packetType (?)
        sock.sendto(packet.parsePacketInByteArrays(), (receiverIP, primarySendPort))

    return 0
            

if __name__ == '__main__':
    #Bind socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ReceiverIP, ReceiverPort))
    #sock.settimeout(5)
    #set multiprocessing
    pool = multiprocessing.Pool(10)
    manager = multiprocessing.Manager()
    queue = multiprocessing.Queue()
    for x in AVAILABLE_PORTS:
        queue.put(x)
    while True:
        packetData, packetAddr = sock.recvfrom(1024)

        results = pool.apply_async(receiver, (packetData, packetAddr, q, sock))
    
