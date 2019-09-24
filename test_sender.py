import socket
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) #UDP
message = "SUP" #example message

sock.sendto(message.encode('utf-8'),("127.0.0.1",5002))
"""
1st argument: data sent .. in this case it's "SUP" (without apostrophe)
2nd argument: list of address to send
"""
        
