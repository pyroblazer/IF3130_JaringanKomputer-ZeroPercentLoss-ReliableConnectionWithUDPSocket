import socket
import multiprocessing
import os
from util import Packet

#NOTE: IF DONE, DELETE OR CHANGE TEMP FUNCTION AND VARIABLES

PATH = 'receivedFiles/'

#meminta input berupa port yang akan dibind
def initializePortNumber():
    #initialize port
    portNumber = 0
    #check port input
    try:
        portNumber = int(input("Enter a port number for receiver: "))
        if 1 <= portNumber <= 65535:
            print("This is a VALID port number.")
        else:
            raise ValueError
    except ValueError:
        print("This is NOT a VALID port number.")
    return portNumber

#menginput file-file yang ada di direktori asal kirim
def initializeExistingFiles(existingFiles):
    for ROOT, DIRECTORIES, FILES in os.walk(PATH):
        for file in FILES:
            existingFiles.append(file)
    return existingFiles

#fungsi untuk receive file
def receiveFile(packetToSend, fileToSend):
    senderPort = int(bytes(packetToSend.packetData).decode())
    #FOR TESTING PURPOSES 
    receiverPort = senderPort + 1 #e.g. send from port number = 5000, receive from port number = 5001
    #might move processes below to static function
    #Bind socket
    sockReceiveFile = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sockReceiveFile.bind((ReceiverIP, ReceiverPort))
    sockReceiveFile.settimeout(5)
    #might move above processes to static function
    fileOpen = open('receivedFiles/' + fileToSend,'wb')
    res = Packet(1,packetToSend.packetID) #What is res?
    sockReceiveFile.sendto(res.parsePacketInByteArrays(),(receiverIP,receiverPort))
    packetData, packetAddress = sockReceiveFile.recvfrom(32768) #receive Data (?)
    packetToSend = Packet(packetParsedBytes = bytearray(data))
    i = 0
    while(packetToSend.packetDataType < 2):
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
    print('Received File : ',fileToSend)
    fileOpen.close()                     

if __name__ == '__main__':
    #Object Pool for large file fast transfer, might remove later for manual pool
    pool = multiprocessing.Pool(10)
    #meminta input berupa port yang akan dibind
    receiverPort = initializePortNumber()
    #initializeReceiverIP()
    receiverIP = '127.0.0.1' #might need function
    #Notify Users about Receiver IP
    print("Receiver IP: ", receiverIP)
    print("Receiver Port: ", receiverPort)
    #Bind socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((receiverIP, receiverPort))
    sock.settimeout(5)
    #Initialize Existing Files
    existingFiles = []
    existingFiles = initializeExistingFiles(existingFiles)
    #Print existing files
    print('Files that are ready to be sent:\n')
    for file in existingFiles:
          print(file)
    #Input file to send
    #NEED EXCEPTION CHECK
    print('Input file to send:\n')
    fileToSend = input()
    packetToSend = Packet(packetParsedData = bytearray(fileToSend.encode()))
    #Kirim File      
    sock.sendto(packetToSend.parsePacketInByteArrays(), (receiverIP, receiverPort))
    try:
        packetData, packetAddress = sock.recvfrom(1024)
        packetToSend = Packet(packetParsedBytes = bytearray(packetData))
        if (packetToSend.packetType < 2):
            # Setup port
            # file_writer(p, query)
            print('Starting to send file\n')
            result = pool.apply_async(file_writer, (p, query))
            print('Done Sending File\n')
            # result.get()
    except(TimeoutError):
        print("Timeout")
                  
