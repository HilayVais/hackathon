import codecs
import socket
import time
import sys
from threading import Thread
# from SocketServer import ThreadingMixIn

#you can enter the team name by uncomment the line
teamName = "ClientServer"

#this thread used to menage the connection with the server and send the key pressed
class gameThread(Thread):

    def __init__(self, sock):
        Thread.__init__(self)
        self.sock = sock
        self.running = True

    def run(self):
        try:
            while self.running:
                message = input('')
                if(self.running):
                    self.sock.sendall(message.encode('utf-8'))
            exit(0)
        except Exception as e:
            # print ("Error occured, stop clicking")
            # print (e)
            exit(0)

def main():
    global sock
    # teamName = input('Enter your team name:')
    #set uo udp client
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.bind(("", 13117))
    while True:
        try:
            sock = None
            #Part 1 - looking for a server
            ip = socket.gethostbyname(socket.gethostname())
            print ("Client started, listening for offer requests...")

            data, addr = client.recvfrom(2048)

            #check magic cookie + message type
            magicCookie = data[:4]
            magicCookie = codecs.encode(magicCookie, 'hex_codec').decode("utf-8")
            if (magicCookie != "feedbeef"):
                print("Wrong magic type")
                raise Exception
            magicType = data[4:5]
            if(magicType != b'\x02'):
                print ("Wrong magic type")
                raise Exception

            port = data[-2:]
            message = codecs.encode(port, 'hex_codec').decode("utf-8")
            port = int(message, 16)

            print ("Received offer from {},attempting to connect...".format(addr[0]))

            time.sleep(10)

            #Part 2 - Connecting to a server
            server_address = (addr[0], port)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(server_address)

            #Send my name
            sock.sendall(bytes(teamName+"\n", 'utf-8'))

            #get start message from server
            startMessage = sock.recv(9999999)
            print(startMessage.decode('utf-8'))

            # Part 3 - game mode
            thread = gameThread(sock)
            thread.start()

            endMessage=""
            while "Game over" not in endMessage:
                endMessage = sock.recv(99999999).decode('utf-8')
            thread.running = False
            print(endMessage)
        except Exception as e:
            print ("Error occured, starting new session")

if __name__ == "__main__":
    # execute only if run as a script
    main()