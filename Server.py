import codecs
import socket
import time
import sys
import scapy.all as s
from threading import Thread
# from SocketServer import ThreadingMixIn
import random

threads = []
teams = {"1":[],"2":[]}
startMessage = None
endMessage = None
TCP_PORT = 2060
hostName = "local" #eth1/eth2

class ClientThread(Thread):

    def __init__(self, ip, port, team,conn):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.teamName = "unknown"
        self.conn = conn
        self.active = True
        self.team = team
        self.startGame = False
        self.score = 0

    def run(self):
        global teams
        try:
            self.teamName = self.conn.recv(2048).decode('utf-8')
            teams[self.team].append(self.teamName)
            while (startMessage == None):
                time.sleep(1)
            self.conn.sendall(bytes(startMessage, 'utf-8'))
            while self.active:
                try:
                    data = self.conn.recv(2048).decode('utf-8')
                    self.score+=len(data)
                except:
                    0
            while (endMessage == None):
                time.sleep(1)
            self.conn.sendall(bytes(endMessage, 'utf-8'))
            self.conn.close()
            exit(0)
        except:
            0

class initClientThreads(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.running = True
        self.ip = None

    def run(self):
        global threads
        tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcpServer.bind((self.ip, TCP_PORT))
        while self.running:
            tcpServer.listen(4)
            (conn, (ip, port)) = tcpServer.accept()
            team = random.choice(["1", "2"])
            newthread = ClientThread(ip, port, team,conn)
            newthread.start()
            threads.append(newthread)
        exit(0)

def main():
    global startMessage
    global threads
    global teams
    global endMessage
    try:
        if(hostName == "local"):
            ip = socket.gethostbyname(socket.gethostname())
        else:
            ip = s.get_if_addr(hostName)
        print ("Server started,listening on IP address {}".format(ip))
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        server.settimeout(0.2)

        while(True):
            threads = []
            teams = {"1": [], "2": []}
            startMessage = None
            #Part 1 - send broadcasts
            port = hex(TCP_PORT)
            # print (str(port)[2:])
            message = codecs.decode('feedbeef02080c', 'hex_codec')
            timePassed = 0
            while timePassed<10:
                server.sendto(message, ('<broadcast>', 13117))
                time.sleep(1)
                timePassed+=1

            #Part 2 - init tcp connections
            initThread = initClientThreads()
            initThread.ip = ip
            initThread.start()
            time.sleep(10)
            initThread.running = False
            startMessage = """"
            Welcome to Keyboard Spamming Battle Royale.
            Group 1:
            ==
            {}
            Group 2:
            ==
            {}
            Start pressing keys on your keyboard as fast as you can!!
            """.format("".join(teams["1"]),"".join(teams["2"]))
            for t in threads:
                t.startGame = True
            time.sleep(10)
            for t in threads:
                t.active = False
            finalScore = {"1":0,"2":0}
            for t in threads:
                finalScore[t.team]+=t.score
            if(finalScore["1"] > finalScore["2"]):
                winners = "1"
            elif(finalScore["1"] < finalScore["2"]):
                winners = "2"
            else:
                winners = "DRAW"
                endMessage = """
                Game over!
                Group 1 typed in {} characters. Group 2 typed in {} characters.
                Its a DRAW!
                """.format(finalScore["1"], finalScore["2"])
            if(winners!="DRAW"):
                endMessage = """
            Game over!
            Group 1 typed in {} characters. Group 2 typed in {} characters.
            Group {} wins!
            Congratulations to the winners:
            ==
            {}
            """.format(finalScore["1"],finalScore["2"],winners,"".join(teams[winners]))
            for t in threads:
                t.join()
            print ("Game over, sending out offer requests...")
    except Exception as e:
        print("Error occured, starting new session")

if __name__ == "__main__":
    # execute only if run as a script
    main()