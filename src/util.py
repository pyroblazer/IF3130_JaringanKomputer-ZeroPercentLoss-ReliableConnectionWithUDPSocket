import socket
import random
import threading
import time
import pickle


class Packet(object):
    
    def __init__(self, packetType=0, packetId=0, packetSequenceNumber=0, packetLength=0, packetChecksum=0, packetData=bytearray(), packetParsedBytes=0, packetParsedData=0):
        #initialize when data is present
        if (packetParsedData != 0):
            self.packetDataofPacket(packetType, packetId, packetSequenceNumber, packetParsedData)
        #initialize when data isn't present, but bytes isn't present
        elif (packetParsedBytes == 0):
            self.packetType = packetType # Hex number (0x0 - 0x3) -> 4 bit
            self.packetId = packetId # Hex number (0x0-0x3) -> 4 bit
            self.packetSequenceNumber = packetSequenceNumber #integer
            self.packetLength = packetLength # Integer -> 0-32768 2^16/2
            self.packetChecksum = packetChecksum # CRC, e.g. if check = 0xFFFF = 65535 -> 16 bit
            # print("init Checksum 1 : ",self.packetChecksum)
            self.packetData = packetData # 32 KB/ 32768 byte 2^16/2
        #initialize when parsed bytes is present, fits according to packet structure that is required
        else:
            self.packetType = packetParsedBytes[0] % (1 << 4) # Hex number (0x0 - 0x3) -> 4 bit
            self.packetId = packetParsedBytes[0] // (1 << 4) # Hex number (0x0-0x3) -> 4 bit
            self.packetSequenceNumber = (packetParsedBytes[1]<<8) + packetParsedBytes[2] #integer
            self.packetLength = (packetParsedBytes[3]<<8) + packetParsedBytes[4] # Integer -> 0-32768 2^16/2
            self.packetChecksum = (packetParsedBytes[5]<<8) + packetParsedBytes[6] 
            self.packetData = packetParsedBytes[7:] #

    def generateChecksum(self):
        
        packetArray = bytearray(self.parsePacketInBytes())
        length = len(packetArray)
        int_values = [x for x in packetArray]
        packetLengthFilledTwoBytes = len(int_values) // 2
        packetLengthNotFilledTwoBytes = len(int_values) % 2
        #Checksum XOR per two bytes
        i=0
        tempChecksum = 0
        for i in range(packetLengthFilledTwoBytes):
            tempChecksum = tempChecksum ^ ((packetArray[i*2]<<8) + packetArray[i*2+1])
            #print("i: " + str(i) + " | " + "buffer: " + str(tempChecksum) + " buffer in binary: " + str(bin(tempChecksum)) + " hex: " + str(hex(tempChecksum)))
            # i+=1
        if (packetLengthNotFilledTwoBytes >0):
            tempChecksum = tempChecksum ^ packetArray[i*2]
        checksum = tempChecksum
        return checksum

    def parsePacketInBytes(self):
        packetInByteArraysWithoutData = bytearray(7) #will include Packet Type, Id, Sequence Number, Length & Checksum, divided every 8 bits
                                                                                    # Packet Structure
                                                                                    # 8 bits
        packetInByteArraysWithoutData[0] = self.packetType + (self.packetId << 4)   # Packet type + packet id
        packetInByteArraysWithoutData[1] = (self.packetSequenceNumber >> 8)           # Packet Sequence Number
        packetInByteArraysWithoutData[2] = self.packetSequenceNumber % (1<<8)        # Packet Sequence Number next 8 bytes
        packetInByteArraysWithoutData[3] = (self.packetLength >> 8)                   # Packet Length
        packetInByteArraysWithoutData[4] = self.packetLength % (1<<8)
        packetInByteArraysWithoutData[5] = (self.packetChecksum >> 8)                 # Packet Checksum
        packetInByteArraysWithoutData[6] = self.packetChecksum % (1<<8)

        packetInByteArrays = packetInByteArraysWithoutData + self.packetData        #Append data
        return bytes(packetInByteArrays)

    def isGeneratedChecksumEqualToActualChecksum(self):
        tempChecksum = self.packetChecksum #preserve checksum
        self.packetChecksum = 0 #initialize checksum
        self.packetChecksum = self.generateChecksum()  #generate checksum

        generatedChecksumEqualToActualChecksum = (self.packetChecksum == tempChecksum) #check if generated checksum is equal to actual checksum

        self.checksum = tempChecksum #deinitialize checksum

        return generatedChecksumEqualToActualChecksum

    def packetDataofPacket(self, packetType, packetId, packetSequenceNumber, packetParsedData):
        self.packetType = packetType
        self.packetId = packetId
        self.packetSequenceNumber = packetSequenceNumber
        self.packetLength = len(packetParsedData)
        self.packetData = packetParsedData
        self.packetChecksum = 0
        self.packetChecksum = self.generateChecksum()
