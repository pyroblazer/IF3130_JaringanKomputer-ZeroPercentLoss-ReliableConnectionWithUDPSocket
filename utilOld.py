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
        

    def packet_type(self):
        packet_type = ""
        #FIN-ACK
        if self.flag_ack == 1 and self.flag_fin == 1:
            packet_type = 0x3
        #FIN
        elif self.flag_fin == 1:
            packet_type = 0x2
        #ACK
        elif self.flag_ack == 1:
            packet_type = 0x1
        #DATA
        elif self.data != "":
            packet_type = 0x0
        return packet_type

    def set_flags(self, ack=False, syn=False, fin=False):
        if ack:
            self.flag_ack = 1
        else:
            self.flag_ack = 0
        if syn:
            self.flag_syn = 1
        else:
            self.flag_syn = 0
        if fin:
            self.flag_fin = 1
        else:
            self.flag_fin = 0

     @staticmethod
    def gen_starting_seq_num():
        return random.randint(TCPPacket.SMALLEST_STARTING_SEQ, TCPPacket.HIGHEST_STARTING_SEQ)


class TCP(object):

    def __init__(self, timeout=5):
        self.status = 1  # socket open or closed
        #seq will have the last     packet send and ack will have the next packet waiting to receive
        self.own_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP socket used for communication.
        self.own_socket.settimeout(timeout)
        self.connections = {}
        self.connection_queue = []
        self.connection_lock = threading.Lock()
        self.queue_lock = threading.Lock()
        # each condition will have a dictionary of an address and it's corresponding packet.
        self.packets_received = {"SYN": {}, "ACK": {}, "SYN-ACK": {}, "DATA or FIN": {}, "FIN-ACK": {}}

        self.central_receive()


    def __repr__(self):
        return "TCP()"

    def __str__(self):
        return "Connections: %s" \
               % str(self.connections)

    def send(self, data, connection=None):
        try:
            if connection not in list(self.connections.keys()):
                if connection is None:
                    connection = list(self.connections.keys())[0]
                else:
                    return "Connection not in connected devices"
            data_parts = TCP.data_divider(data)
            for data_part in data_parts:
                data_not_received = True
                checksum_of_data = TCP.checksum(data_part)
                self.connections[connection].checksum = checksum_of_data
                self.connections[connection].data = data_part
                self.connections[connection].set_flags()
                packet_to_send = pickle.dumps(self.connections[connection])
                while data_not_received:
                    data_not_received = False
                    try:
                        self.own_socket.sendto(packet_to_send, connection)
                        answer = self.find_correct_packet("ACK", connection)

                    except socket.timeout:
                        print("timeout")
                        data_not_received = True
                self.connections[connection].seq += len(data_part)
        except socket.error as error:
            print(("Socket was closed before executing command. Error is: %s." % error))

    @staticmethod
    def data_divider(data):
        """Divides the data into a list where each element's length is 1024"""
        data = [data[i:i + DATA_DIVIDE_LENGTH] for i in range(0, len(data), DATA_DIVIDE_LENGTH)]
        data.append("END")
        return data


if __name__ == "__main__":
    main()
