
#initialize port
port = 0
#check port input
try:
    port = int(input("Enter a port number: "))
    if 1 <= port <= 65535:
        print("This is a VALID port number.")
    else:
        raise ValueError
except ValueError:
    print("This is NOT a VALID port number.")
