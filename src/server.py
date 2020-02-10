import multiprocessing
import socket
import time
import os
import select
from util import Packet

PATH = 'receivedFiles/'
allocatedPorts = range(6001, 6999, 2)
sizeLimit = 32000 # bytes
maxBufferSize = 1 << 8 #1024
maxSequenceNumber = 1 << 16 #16 bits
UdpIp = "127.0.0.1"
UdpPort = 6000

def sendFile(UdpTargetIp, UdpTargetPort, queue, requestedFile, packetId):
    sockSendFile = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sockSendFile.bind((UdpIp, UdpTargetPort))
    sockSendFile.settimeout(500)
  
    f = open(requestedFile,'wb')

    data, addr = sockSendFile.recvfrom(32678)
    packet = Packet(packetParsedBytes=bytearray(data))
    
    countSequenceNumber = 0 #Sequence Number
    countMaxSequenceNumber = 0 #number of Max Sequnce Numbers
    while(packet.packetType < 2):
        if (packet.isGeneratedChecksumEqualToActualChecksum() and packet.packetSequenceNumber==countSequenceNumber):
            #print(countSequenceNumber + maxSequenceNumber*countMaxSequenceNumber) 
            f.write(bytes(packet.packetData))
            response = Packet(1,packet.packetId,packetSequenceNumber=countSequenceNumber)
            #print('Sequence Number of sent file: ',response.packetSequenceNumber)
            sockSendFile.sendto(response.parsePacketInBytes(), (UdpTargetIp, UdpTargetPort+1))
            try:
                data, addr = sockSendFile.recvfrom(32678)
                packet = Packet(packetParsedBytes=bytearray(data))
                #print('Sequence Number of Received File: ',packet.packetSequenceNumber)
                countSequenceNumber+=1
                if (countSequenceNumber==maxSequenceNumber):
                    countSequenceNumber=0
                    countMaxSequenceNumber+=1
            except(Exception):
                print('Packet Transfer NOT ACKNOWLEDGED, resending packet')
                f.seek((countSequenceNumber + maxSequenceNumber*countMaxSequenceNumber)*sizeLimit,0)
        else:
            print('There is a mismatch on actual file Sequence Number: ',packet.packetSequenceNumber,'and Sequence Number to be sent: ',countSequenceNumber)
            response = Packet(1,packet.packetId,packetSequenceNumber=countSequenceNumber)
            #print('Sequence Number of Sent File:',response.packetSequenceNumber)
            sockSendFile.sendto(response.parsePacketInBytes(), (UdpTargetIp, UdpTargetPort+1))
            try:
                data, addr = sockSendFile.recvfrom(32678)
                packet = Packet(packetParsedBytes=bytearray(data))
                #print('Sequence Number of Received File: ',packet.packetSequenceNumber)
            except(Exception):
                print('Packet Transfer NOT ACKNOWLEDGED, resending packet')
                f.seek((countSequenceNumber + maxSequenceNumber*countMaxSequenceNumber)*sizeLimit,0)
    print('Finished sending file: ',requestedFile)
    f.close()
    queue.put(UdpTargetPort)

def receiver(packetData, packetAddress, queue, sock):
    UdpTargetIp = packetAddress[0]
    packet = Packet(packetParsedBytes=bytearray(packetData)) 
    requestedFileAndUdpTargetPort = bytes(packet.packetData).decode().split(':')
    requestedFile = requestedFileAndUdpTargetPort[0]
    UdpTargetPort = int(requestedFileAndUdpTargetPort[1])
    print("Requested File: ", requestedFile)
    if (packet.isGeneratedChecksumEqualToActualChecksum()):
        transferPort = queue.get()
        print("Initialize File Transfer From Port: ", transferPort)
        requestedFile = PATH + requestedFile
        packetId = packet.packetId
        packet = Packet(packetParsedData=bytearray(str(transferPort).encode()), packetId=packetId)
        sock.sendto(packet.parsePacketInBytes(), (UdpTargetIp, UdpTargetPort))
        sendFile(UdpTargetIp, transferPort, queue, requestedFile, packetId)
    else:
        if(not packet.isGeneratedChecksumEqualToActualChecksum()):
            print("Generated Checksum NOT EQUAL to Actual Checksum")
        print("File Transfer Failed")
        packet = Packet(3,0)
        sock.sendto(packet.parsePacketInBytes(), (UdpTargetIp, UdpTargetPort))
    return False

if __name__ == '__main__':

    print("--- EMI GROUP SIMPLE TCP OVER UDP SERVER ---")

    #Socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UdpIp, UdpPort))

    #Multiprocessing
    pool = multiprocessing.Pool()
    multiprocessingManager = multiprocessing.Manager()
    managerQueue = multiprocessingManager.Queue()
    for port in allocatedPorts:
        managerQueue.put(port)

    #Receiver
    while True:
        data, addr = sock.recvfrom(maxBufferSize) # buffer size is 1024 bytes
        results = pool.apply_async(receiver, (data, addr, managerQueue, sock))
        