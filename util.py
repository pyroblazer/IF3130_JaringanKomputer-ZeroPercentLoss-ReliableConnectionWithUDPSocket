import random
import socket
import pickle
import threading
import time

#NOTE: PACKET STRUCTURENYA SEPERTINYA BELOM BENER... DI SINI MASIH ADA FLAG, SEPERTINYA GA BOLEH ADA :(
DATA_DIVIDE_LENGTH = 1024

class TCPPacket(object):
    """
    Doc
    """
    SMALLEST_STARTING_SEQ = 0
    HIGHEST_STARTING_SEQ = 65535
    
    def __init__(self, packetType=0, packetId=0, packetSequenceNumber=0, packetLength=0, packetChecksum=0, packetData=bytearray(), packetParsedBytes=0, packetParsedData=0):
        #initialize when data is present
        if (parsed_data != 0):
            self.packet
        #initialize when data isn't present, but bytes isn't present
        elif (packetParsedBytes == 0):
            self.packetType = packetType # Hex number (0x0 - 0x3) -> 4 bit
            self.packetId = packetId # Hex number (0x0-0x3) -> 4 bit
            self.packetSequenceNumber = packetSequenceNumber #integer
            self.packetLength = packetLength # Integer -> 0-32768 2^16/2
            self.packetChecksum = packetChecksum # CRC, e.g. if check = 0xFFFF = 65535 -> 16 bit
            self.packetData = packetData # 32 KB/ 32768 byte 2^16/2
        #initialize when data isn't present, but bytes is present, fits according to packet structure that is required
            self.packetType = parsed_bytes[0]^4 # Hex number (0x0 - 0x3) -> 4 bit
            self.packetId = parsed_bytes[0] >> 4 # Hex number (0x0-0x3) -> 4 bit
            self.packetSequenceNumber = TCPPacket.gen_starting_seq_num() #integer
            self.length = 0 # Integer -> 0-32768 2^16/2
            self.checksum = 0 # CRC, e.g. if check = 0xFFFF = 65535 -> 16 bit
            self.data = "" # 32 KB/ 32768 byte 2^16/2
    

    def checksum():
        packetArray = self.parsePacketInByteArrays() #1,2,3,4,5,6,7]
        #byteArrayOfPacket = bytearray([1,2,3,4,5,6,7]) #might not be needed, gotta check later
        #print(byteArrayOfPacket)
        length = len(array)
        tempChecksum = 0
        #int_values = [x for x in array]
        packetLengthFilledTwoBytes =len(array) >> 1 
        packetLengthNotFilledTwoBytes = len(array) ^ 1
        #Checksum XOR per two bytes
        i=0
        while i< packetLengthFilledTwoBytes:
            tempChecksum = tempChecksum ^ ((packetArray[i*2]<<8) + packetArray[i*2+1])
            print("i: " + str(i) + " | " + "buffer: " + str(tempChecksum) + "buffer in binary: " + str(bin(tempChecksum)))
            i+=1
        if (packetLengthNotFilledTwoBytes >0):
            tempChecksum = tempChecksum ^ packetArray[i*2]
        checksum = tempChecksum
        print(checksum)

    def parsePacketInByteArrays():
        data_type = 1
        data_id = 2
        sequence_number = 1
        length = 7
        checksum = 1799
        data = bytes(1)
        packetInByteArraysWithoutData = bytearray(7) #will include Packet Type, Id, Sequence Number, Length & Checksum, divided every 8 bits
                                                                            # Packet Structure
                                                                            # 8 bits
        packetInByteArraysWithoutData[0] = packetType + (packetId << 4)     # Packet type + packet id
        packetInByteArraysWithoutData[1] = packetSequenceNumber >> 8             # Packet Sequence Number
        packetInByteArraysWithoutData[2] = packetSequenceNumber & (8-1)          # Packet Sequence Number next 8 bytes
        packetInByteArraysWithoutData[3] = packetLength >> 8                      # Packet Length
        packetInByteArraysWithoutData[4] = packetLength & (8-1)
        packetInByteArraysWithoutData[5] = packetChecksum >> 8                    # Packet Checksum
        packetInByteArraysWithoutData[6] = packetChecksum & (8-1)

        packetInByteArrays = packetInByteArraysWithoutData + data #Append data
        return packetInByteArrays

if __name__ == "__main__":
    main()
