import socket
from _thread import *
import pickle

from game import Card, Trick, Player, Game
from settings import *

# this is the(a) server script, it always has to be running, need to first run this server
# script, and we can try to connect clients to it

server = "192.168.0.11"  # this is a local network, so on the same wifi
# to get the local ip address, type ipconfig to the command prompt
port = 5555  # this is a port that's typically open
# this is for an IPV4 address socket.AF_INET is the type we'll use and SOCK_STREAM is how the server string comes in
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# will do a try/catch statement here in case the server and port fail to bind to the socket
try:
    s.bind((SERVER_ADDRESS, PORT))  # bind the ip address (server) to this given port
except socket.error as e:
    print(e)

# the parameter is the number of clients to be able to connect to the server
s.listen(4)
print("Waiting for a connection, Server Started")

game = Game([0, 0, 0, 0])
player_points = [0, 0, 0, 0]


# defining a threaded function
def threaded_client(conn, player):
    # send a message to the client containing its player number
    global game
    conn.send(str.encode(str(player)))

    while True:
        try:
            # we're putting in 2048 bits, the amount of info we're receiving
            data = pickle.loads(conn.recv(2048))

            # we need to decode the information received, as it is encoded over a client server system
            # utf-8 is the format'''
            # reply = data.decode("utf-8")

            if not data:
                print("Disconnected")
                break
            else:
                if data == 'ping':
                    reply = game
                else:
                    game.add_card(data)
                    print('gets here')
                    if game.end_of_round:
                        print('gets here 2')
                        current_scores = [game.players[i].score for i in range(4)]
                        game = Game(current_scores)
                    reply = game

                # print("Received: ", data)
                # print("Sending:", reply)
                    print(f'The current trick is {game.current_trick}')
            # this is just encoding it into a bites object
            conn.sendall(pickle.dumps(reply))
        except:
            break

    print("Lost connection")
    conn.close()


current_player = 0
while True:
    # s.accept() accepts any incoming connections and it will store the connection and the address
    connection, address = s.accept()
    print("Connected to:", address)
    # A thread is just another process that's running in the background
    # we don't want to end the previous threaded_client when we run another one
    # we want threaded_client to run in the background'''
    start_new_thread(threaded_client, (connection, current_player))
    current_player += 1
