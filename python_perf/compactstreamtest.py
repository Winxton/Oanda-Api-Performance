import time
import socket

class CompactStreamTest():
    # Retreive a symbol list as reference
    # Host: localhost
    # Port: 9600
    def __init__(self, *args, **kw):
        TCP_PORT = 9600

        self.TCP_IP = "localhost"
        self.TCP_PORT = TCP_PORT
        self.BUFFER_SIZE = 1024
        self.TIMEOUT = 60
        # The size of the whole symbol list is 15730
        self.SYMBOL_BUFFER_SIZE = 16384
        self.RATES_TXT = "/oanda/torridsim/etc/rates.txt"
        tick_socket = self.connect_to_stream()
        try:
            tick_socket.send("s\r\n")
        except Exception as e:
            self.assertTrue(False, "Caught exception with send symbol list request\n" + str(e))
        self.symbol_list = tick_socket.recv(self.SYMBOL_BUFFER_SIZE)
        tick_socket.close()

    # Open a socket
    def connect_to_stream(self, skip_header = True):
        tick_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            tick_socket.connect((self.TCP_IP, self.TCP_PORT))
        except Exception as e:
            print ("Caught exception when connecting to stream via TCP socket\n" + str(e))
        tick_socket.settimeout(self.TIMEOUT)
        
        # Return the socket without header message
        if skip_header:
            tick_socket.recv(self.BUFFER_SIZE)
            return tick_socket
        else:
            header = tick_socket.recv(self.BUFFER_SIZE)
            return (tick_socket, header)

test = CompactStreamTest()