import random
import socket
import pickle
import threading
import time

class TCPPacket(object):
    """
    Doc
    """
    SMALLEST_STARTING_SEQ = 0
    HIGHEST_STARTING_SEQ = 65535
    
    def __init__(self):
        """
        0x0 (DATA), 0x1 (ACK), 0x2 (FIN), dan 0x3 (FIN-ACK)
        """
        
        self.packetId = packetId
        self.sequenceNumber = TCPPacket.gen_starting_seq_num() 
        self.length = 0 # 0-32678 2^16/2
        self.checksum = 0
        self.data = ""
        #FLAGS
        self.flag_ns = 0  # 1bit
        self.flag_cwr = 0  # 1bit
        self.flag_ece = 0  # 1bit
        self.flag_urg = 0  # 1bit
        self.flag_ack = 0  # 1bit
        self.flag_psh = 0  # 1bit
        self.flag_rst = 0  # 1bit
        self.flag_syn = 0  # 1bit
        self.flag_fin = 0  # 1bit

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


if __name__ == "__main__":
    main()
