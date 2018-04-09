import random
import sys
import traceback
from select import *
from socket import *

import re
import params

switchesVarDefaults = (
    (('-s', '--server'), 'server', "127.0.0.1:50000"),
    (('-n', '--numClients'), 'numClients', "2"),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '-h', '--usage'), "usage", False), # boolean (set if present)
    (('-r', '-request'), "clientRequests", "PUT|testFileFromClient.txt GET|testFileFromServer.txt"), # boolean (set if present)
    )

paramMap = params.parseParams(switchesVarDefaults)
server, usage, debug = paramMap["server"], paramMap["usage"], paramMap["debug"]
numClients = int(paramMap["numClients"])
clientRequests = paramMap["clientRequests"]
clientRequests = clientRequests.split(" ")


if usage:
    params.usage()

try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)
except:
    print "Can't parse server:port from '%s'" % server
    sys.exit(1)


sockNames = {}               # from socket to name
nextClientNumber = 0     # each client is assigned a unique id

            
    
liveClients, deadClients = set(), set()

class Client:
    def __init__(self, af, socktype, saddr, request):
        global nextClientNumber
        global liveClients, deadClients
        self.saddr = saddr # addresses
        self.numSent, self.numRecv = 0,0
        self.allSent = 0
        self.error = 0
        self.isDone = 0
        self.clientIndex = clientIndex = nextClientNumber
        nextClientNumber += 1
        self.request = request
        self.protocol = ""
        self.fileName = ""
        self.ssock = ssock = socket(af, socktype)
        self.message = ""
        print "New client #%d to %s" % (clientIndex, repr(saddr))
        sockNames[ssock] = "C%d:ToServer" % clientIndex
        ssock.setblocking(False)
        ssock.connect_ex(saddr)
        liveClients.add(self)

    def parseClientRequest(self):
        self.request = re.split('\|', self.request)

        if 1 < len(self.request):
            self.protocol = self.request[0].lower()
            self.fileName = self.request[1]

        self.message = self.protocol + "|" + self.fileName + "|"

    def doSend(self):
        try:
            self.parseClientRequest()
            if self.protocol == "put":
                with open("client/" + self.fileName, 'rb') as file:
                    for line in file:
                        self.message += line
            self.message += "<EOM>"
            self.numSent += self.ssock.send(self.message)

        except Exception as e:
            self.errorAbort("can't send: %s" % e)
            return
        self.allSent = 1
        self.ssock.shutdown(SHUT_WR)
    def doRecv(self):
        try:
            messageFromServer = self.ssock.recv(1024)
            n = len(messageFromServer)
            if self.protocol == "get" and messageFromServer != None:
                 with open("client/testFileFromServer.txt", 'a') as file:
                        file.write(messageFromServer)
        except Exception as e:
            print "doRecv on dead socket"
            print e
            self.done()
            return
        self.numRecv += n
        if self.numRecv > self.numSent and self.protocol == "put": 
            self.errorAbort("sent=%d < recd=%d" %  (self.numSent, self.numRecv))
        if n != 0:
            return
        if debug: print "client %d: zero length read" % self.clientIndex
        if self.numRecv == self.numSent:
            self.done()
        else:
            if self.protocol == "put":
                self.errorAbort("sent=%d but recd=%d" %  (self.numSent, self.numRecv))
            elif self.protocol == "get":
                self.done()
    def doErr(self, msg=""):
        error("socket error")
    def checkWrite(self):
        if self.allSent:
            return None
        else:
            return self.ssock
    def checkRead(self):
        if self.isDone:
            return None
        else:
            return self.ssock
    def done(self):
        self.isDone = 1
        self.allSent =1
        if self.numSent != self.numRecv and self.protocol == "put": 
            self.error = 1
        elif self.protocol == "get":
            pass
        try:
            self.ssock(close)
        except:
            pass
        print "client %d done (error=%d)" % (self.clientIndex, self.error)
        deadClients.add(self)
        try: liveClients.remove(self)
        except: pass
            
    def errorAbort(self, msg):
        self.allSent =1
        self.error = 1
        print "FAILURE client %d: %s" % (self.clientIndex, msg)
        self.done()
        
                  
def lookupSocknames(socks):
    return [ sockName(s) for s in socks ]

for i, clientRequest in zip(range(numClients), clientRequests):
    liveClients.add(Client(AF_INET, SOCK_STREAM, (serverHost, serverPort), clientRequest))

while len(liveClients):
    rmap,wmap,xmap = {},{},{}   # socket:object mappings for select
    for client in liveClients:
        sock = client.checkRead()
        if (sock): rmap[sock] = client
        sock = client.checkWrite()
        if (sock): wmap[sock] = client
        xmap[client.ssock] = client
    if debug: print "select params (r,w,x):", [ repr([ sockNames[s] for s in sset] ) for sset in [rmap.keys(), wmap.keys(), xmap.keys()] ]
    rset, wset, xset = select(rmap.keys(), wmap.keys(), xmap.keys(),60)
    #print "select r=%s, w=%s, x=%s" %
    if debug: print "select returned (r,w,x):", [ repr([ sockNames[s] for s in sset] ) for sset in [rset,wset,xset] ]
    for sock in xset:
        xmap[sock].doErr()
    for sock in rset:
        rmap[sock].doRecv()
    for sock in wset:
        wmap[sock].doSend()


numFailed = 0
print("")
for client in deadClients:
    err = client.error
    print "Client %d Succeeded=%s, Bytes sent=%d, rec'd=%d" % (client.clientIndex, not err, client.numSent, client.numRecv)
    print "Protocol: " + client.protocol
    print "File: " + client.fileName
    print("")
    if err:
        numFailed += 1
print "%d Clients failed." % numFailed