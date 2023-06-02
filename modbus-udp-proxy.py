# SPDX-License-Identifier: MIT

import sys, socket, binascii

def printErrorAndExit(reason):
    print(reason)
    sys.exit(1)

def checkPort(portStr, portName):
    portNum = 0
    try:
        portNum = int(portStr)
        assert (portNum > 0) and (portNum < 65536)
    except:
        printErrorAndExit('Illegal ' + portName + ' number')
    return portNum

numArg = len(sys.argv)
if not (numArg == 4 or numArg == 5):
    printErrorAndExit('Run with ' + sys.argv[0] + ' <localPort> <remoteHost> <remotePort> <verbose on|off, optional>')

localPort =  checkPort(sys.argv[1],  'localPort')
remoteHost = sys.argv[2]
remotePort = checkPort(sys.argv[3], 'remotePort')

# display some debug data
verbose=False
if numArg == 5:
    if sys.argv[4] in ["on", "true", "1"]:
        verbose = True
try:
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sockaddr = socket.getaddrinfo('0.0.0.0', localPort)[0][-1]
    mySocket.bind(sockaddr)
	
except Exception as e:
	printErrorAndExit('Failed to bind on port ' + str(localPort) + ' ' + str(e))

clientAddr = None
serverAddr = socket.getaddrinfo(remoteHost, remotePort)[0][-1]
print('Listening on 0.0.0.0:' + str(localPort))

while True:
    recvPacket, addr = mySocket.recvfrom(1024)
    if clientAddr is None or addr != serverAddr:
	clientAddr = addr

    if verbose:
	print("Packet received from " + str(addr))

    if addr == clientAddr:
        if verbose:
            print("forwarding to " + str(serverAddr))
	# check if this is a Modbus Read request
	if recvPacket[0] == 0xf7 and recvPacket[1]==0x03:
            if verbose:
                print("valid request")
	    mySocket.sendto(recvPacket, serverAddr)
	else:
	    if verbose:
		print("skip: ", binascii.hexlify(recvPacket,","))
    else:
	if verbose:
	    print("forwarding to " + str(clientAddr))
	# check if this is a Modbus Read response
	if recvPacket[0]==0xaa and recvPacket[1]==0x55 and recvPacket[2] == 0xf7 and recvPacket[3]==0x03:
	    if verbose:
                print("valid response packet")
	    mySocket.sendto(recvPacket, clientAddr)
	else:
	    if verbose:
		print("skip: ", binascii.hexlify(recvPacket,","))  
                
