from util import Packet
import sys
import time
import re
import socket
import os
import multiprocessing

os.system('color')
PATH = 'filesToSend/'
IPAddressRegex = '''^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)'''
sizeLimit = 32000
maxBufferSize = 1 << 8 #1024
maxSequenceNumber = 1 << 16 #16 bits
UdpIpAddress = "127.0.0.1"
UdpTargetPort = 6000

def inputIPAddress():
    IPAddressValid = False
    while (not IPAddressValid):
        IPAddress = input('Please enter target IP Address to send file to:\n')
        if (isIPAddressValid(IPAddress)):
            IPAddressValid = True
            return IPAddress
        else:
            print('IP Address not valid! Please re-enter IP Address!\n')

def isIPAddressValid(IPAddress):
    return re.search(IPAddressRegex, IPAddress)

def initializeExistingFiles():
    EXISTINGFILES = []
    for ROOT, DIRECTORIES, FILES in os.walk(PATH):
        for file in FILES:
            EXISTINGFILES.append(file)
    return EXISTINGFILES

def inputPort():
    portValid = False
    while(not portValid):
        UdpReceivingPort = int(input('Please enter a port number to send file to:\n'))
        try:
            sock.bind((UdpIpAddress, UdpReceivingPort))
            portValid = True
            return UdpReceivingPort
        except(Exception):
            print('That Port is NOT available, please enter another port number')
            portValid = False

def inputFilesToSend(numberOfFilesToSend):
    proceed = False
    while(not proceed):
        filesToSendInput = input('Please enter files that are going to be sent, separated by | \n')
        filesToSend = filesToSendInput.split('|')
        if not(int(len(filesToSend)) == int(numberOfFilesToSend)):
            print('Number of files that are entered does NOT equal to the number of files to send! Expected: ',numberOfFilesToSend,', Received: ',len(filesToSend))
        else:
            for file in filesToSend:
                if (EXISTINGFILES.count(file) == 0):
                    proceed = False
                    print('The File ',file,' does NOT exist!')
                else:
                    proceed = True
                    return filesToSend

def inputNumberOfFilesToSend():
    isInt = False
    while (not isInt):
        try:
            numberOfFilesToSend = int(input('Please enter the number of files to send\n'))
            isInt = True
            return numberOfFilesToSend
        except ValueError:
            print("Input isn't an integer! Please input again!")

def printExistingFiles(EXISTINGFILES):
    print('Existing files in directory that can be sent:')
    for file in EXISTINGFILES:
        print(file)

def receiveFile(UdpTargetIp, packet, filesToSend, packetId, progressQueue):
    requestedFile = PATH + filesToSend
    UdpTargetPort = int(bytes(packet.packetData).decode())
    UdpReceivingPort = UdpTargetPort+1
    sockReceiveFile = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sockReceiveFile.bind((UdpIpAddress, UdpReceivingPort))
    sockReceiveFile.settimeout(10)

    # Sending file
    # try:
    f = open(requestedFile,'rb')
    bytes_to_send = os.path.getsize(requestedFile)
    packets_to_send = -(-bytes_to_send // sizeLimit)
    percentage =  -(-packets_to_send // 100)
    if (percentage == 0):
        percentage = 1
    
    # Initiate file sending
    countSequenceNumber = 0 #Sequence Number
    countMaxSequenceNumber = 0 #Seeker
    while ((countSequenceNumber+(countMaxSequenceNumber*maxSequenceNumber))<=packets_to_send):
        packetData = bytearray(f.read(sizeLimit))
        packet = Packet(packetParsedData=packetData, packetId=packetId, packetSequenceNumber=countSequenceNumber)
        sockReceiveFile.sendto(packet.parsePacketInBytes(), (UdpTargetIp, UdpTargetPort))
        # try:
        data, addr = sockReceiveFile.recvfrom(maxBufferSize)
        response = Packet(packetParsedBytes=bytearray(data)) # Read packet
        if ((countSequenceNumber+(countMaxSequenceNumber*maxSequenceNumber))%percentage == 0):
            progressQueue.put((filesToSend,(countSequenceNumber+(countMaxSequenceNumber*maxSequenceNumber)) // percentage))
        if (response.packetType>1): 
            break
        if (response.packetType==1 and response.packetSequenceNumber==countSequenceNumber):
            countSequenceNumber += 1
            if (countSequenceNumber==maxSequenceNumber):
                countSequenceNumber=0
                countMaxSequenceNumber+=1
        elif (response.packetSequenceNumber!=countSequenceNumber):
            print('Mismatched sequence number, readjusting...',countSequenceNumber)
            countSequenceNumber = response.packetSequenceNumber
            f.seek((countSequenceNumber + maxSequenceNumber*countMaxSequenceNumber)*sizeLimit,0)
        else:
            f.seek((countSequenceNumber + maxSequenceNumber*countMaxSequenceNumber)*sizeLimit,0)
    
    # Finishing file transfer
    packet = Packet(2,packetId,countSequenceNumber)
    sockReceiveFile.sendto(packet.parsePacketInBytes(), (UdpTargetIp, UdpTargetPort))
    progressQueue.put([filesToSend,100])
    print("ProgressQueue: ", progressQueue)
    f.close()

def displayProgressBar(progressQueue, listOfFilesAndProgress):
    while True:
        if not(progressQueue.empty()):
            file_to_be_updated = progressQueue.get()
            for fileAndProgress in listOfFilesAndProgress:
                if (file_to_be_updated[0] == fileAndProgress[0]):
                    fileAndProgress[1] = file_to_be_updated[1]
            sys.stdout.write(u"\033[2J")
            sys.stdout.flush()
            for fileAndProgress in listOfFilesAndProgress:
                barColor = listOfFilesAndProgress.index(fileAndProgress) % 7 + 40
                print(fileAndProgress[0], ':')
                print(fileAndProgress[1],"% completed")
                sys.stdout.write('[')
                sys.stdout.write(u'\033[' + str(barColor) + u'm')
                progress_i = 0
                while(progress_i < fileAndProgress[1]):
                    #print progress
                    sys.stdout.write('.')
                    progress_i+=1
                sys.stdout.write(u'\033[0m') 
                while(progress_i < 100):
                    #print blank
                    sys.stdout.write(' ')
                    progress_i+=1
                sys.stdout.write(']\n')
                sys.stdout.flush()
        else:
            proceed = True
            for fileAndProgress in listOfFilesAndProgress:
                if (fileAndProgress[1] != 100):
                    proceed = False
            if (proceed):
                print("Finished Receiving File!")
                break

def initializeListOfFilesAndProgress(sock):
    listOfFilesAndProgress = []
    for fileToSend in filesToSend:
        print("fileToSend: ",fileToSend)
        print("list of files", filesToSend)
        if(EXISTINGFILES.count(fileToSend) > 0):
            packetId = EXISTINGFILES.index(fileToSend)
            fileToSendWithPort = fileToSend + ':' + str(UdpReceivingPort)
            packet = Packet(packetParsedData=bytearray(fileToSendWithPort.encode()), packetId=packetId)
            sock.sendto(packet.parsePacketInBytes(), (UdpTargetIp, UdpTargetPort))
            try:
                data, addr = sock.recvfrom(maxBufferSize)
                packet = Packet(packetParsedBytes=bytearray(data))
                if (packet.packetType < 2):
                    # Setup port
                    result = pool.apply_async(receiveFile, (UdpTargetIp, packet, fileToSend, packetId, progressQueue))
                    print('Starting Upload:', fileToSend)
                    listOfFilesAndProgress.append([fileToSend,0])
            except(TimeoutError):
                print('Timeout')
        else:
            print('That file doesn\'t exist')
    return listOfFilesAndProgress

if __name__=='__main__':

    print("--- EMI GROUP SIMPLE TCP OVER UDP CLIENT ---")

    UdpTargetIp = inputIPAddress()

    print ("Target IP:", UdpTargetIp)
    print ("Target port:", UdpTargetPort)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 

    #port setup
    UdpReceivingPort = inputPort()
    
    #Multiprocessing setup
    pool = multiprocessing.Pool()
    manager = multiprocessing.Manager()
    progressQueue = manager.Queue()

    EXISTINGFILES = initializeExistingFiles()
    
    printExistingFiles(EXISTINGFILES)

    numberOfFilesToSend = inputNumberOfFilesToSend()
    
    filesToSend = inputFilesToSend(numberOfFilesToSend)

    listOfFilesAndProgress = []
    for fileToSend in filesToSend:
        print("fileToSend: ",fileToSend)
        print("list of files", filesToSend)
        if(EXISTINGFILES.count(fileToSend) > 0):
            packetId = EXISTINGFILES.index(fileToSend)
            fileToSendWithPort = fileToSend + ':' + str(UdpReceivingPort)
            packet = Packet(packetParsedData=bytearray(fileToSendWithPort.encode()), packetId=packetId)
            sock.sendto(packet.parsePacketInBytes(), (UdpTargetIp, UdpTargetPort))
            try:
                data, addr = sock.recvfrom(maxBufferSize)
                packet = Packet(packetParsedBytes=bytearray(data))
                if (packet.packetType < 2):
                    # Setup port
                    result = pool.apply_async(receiveFile, (UdpTargetIp, packet, fileToSend, packetId, progressQueue))
                    print('Starting Upload:', fileToSend)
                    listOfFilesAndProgress.append([fileToSend,0])
            except(TimeoutError):
                print('Timeout')
        else:
            print('That file doesn\'t exist')

    displayProgressBar(progressQueue, listOfFilesAndProgress)
