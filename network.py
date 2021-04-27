import socket
import pickle
from settings import *


# coded this class so we can re-use this class in the future
# initialising clients
class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = SERVER_ADDRESS
        self.port = PORT
        self.addr = (self.server, self.port)
        self.player_number = self.connect()

    def get_number(self):
        return self.player_number

    def connect(self):
        try:
            self.client.connect(self.addr)
            return int(self.client.recv(2048*8).decode())
        except:
            pass

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(2048*8))
        except socket.error as e:
            str(e)

    def ping_server(self):
        return self.send('ping')
