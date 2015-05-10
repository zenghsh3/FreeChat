# tcp_server.py
import sys
import socket
import select
import json
import struct

HOST = '' 
SOCKET_LIST = [] # socket
SOCKET_DICT = {} # name:socket
MESSAGE_DICT = {} # socket:message
LENGTH_DICT = {} # socket:the length of the rest message
RECV_BUFFER = 4096 
PORT = 10000
tag_unpacker = struct.Struct('!1sI')
name_unpacker = struct.Struct('!100s')

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(1024)

# add server socket object to the list of readable connections
SOCKET_LIST.append(server_socket)

def chat_server():
    print "Chat server started on port" + str(PORT)

    while 1:
        # get the list sockets which are ready to be read through select
        # 4th arg, time_out  = 0 : poll and never block
        ready_to_read,ready_to_write,in_error = select.select(SOCKET_LIST,[],[],0)

        for sock in ready_to_read:
            # a new connection request recieved
            if sock == server_socket: 
                sockfd, addr = server_socket.accept()
                print "Client (%s, %s) connected" % addr
                SOCKET_LIST.append(sockfd)
            # a message from a client, not a new connection
            else:
            # process data recieved from client, 
                try:
                    # receiving data from the socket.
                    package = sock.recv(RECV_BUFFER)
                    if package:
                        # there is something in the socket
                        print package
                        # There is a incomplete package in the sock 
                        if sock in MESSAGE_DICT:
                            # this package length >= the rest length
                            if len(package) >= LENGTH_DICT[sock]:
                                MESSAGE_DICT[sock] += package[:LENGTH_DICT[sock]]
                                handle_complete_package(sock, MESSAGE_DICT[sock])
                                del LENGTH_DICT[sock]
                                del MESSAGE_DICT[sock]
                            else:
                                MESSAGE_DICT[sock] += package
                                LENGTH_DICT[sock] -= len(package)
                        else:
                            unpacked_data = tag_unpacker.unpack(package[0:tag_unpacker.size])
                            print unpacked_data
                            tag = unpacked_data[0]
                            length = unpacked_data[1]
                            if tag == 'a':
                                if length + tag_unpacker.size > RECV_BUFFER:
                                    LENGTH_DICT[sock] = length - RECV_BUFFER + tag_unpacker.size
                                    MESSAGE_DICT[sock] = package
                                else:
                                    handle_complete_package(sock, package)
                            else:
                                if length + tag_unpacker.size + 2 * name_unpacker.size > RECV_BUFFER:
                                    LENGTH_DICT[sock] = length - RECV_BUFFER + tag_unpacker.size + 2 * name_unpacker.size
                                    MESSAGE_DICT[sock] = package
                                else:
                                    handle_complete_package(sock, package)
                except:
                    print 'Receive package exception.'
                    continue
    server_socket.close()

def handle_complete_package(sock, package):
    message_tag = tag_unpacker.unpack(package[0:tag_unpacker.size])
    # handle text message
    if message_tag[0] == 'a':
        try:
            decoded = json.loads(package[tag_unpacker.size:])
            tag = decoded[0]
        except:
            print 'Error format'
        # upload name and return online names
        if tag == 'upload_name':
            SOCKET_DICT[decoded[1]] = sock
            online_list = ['online_names']
            for key in SOCKET_DICT.keys():
                online_list.append(key)
            forward(sock, json.dumps(online_list))  
            broadcast(server_socket, json.dumps(["online_notification", decoded[1]]))
        # [send_message, from_name, to_name, message]
        elif tag == 'send_message': 
            forward_message = ["chat_message", decoded[1], decoded[3]]
            forward(SOCKET_DICT[decoded[2]], json.dumps(forward_message))
        # [offline_request, name]
        elif tag == 'offline_request':
            # remove in SOCKET_LIST and SOCKET_DICT
            SOCKET_LIST.remove(sock)
            del SOCKET_DICT[decoded[1]]
            # broadcast offline notification
            broadcast(server_socket, json.dumps(["offline_notification", decoded[1]]))
        else:
            print 'Error tag from client!'

    # handle media message
    else:
        tag = message_tag[0]
        l1 = tag_unpacker.size
        l2 = name_unpacker.size 
        to_name = name_unpacker.unpack(package[l1 + l2 : l1 + 2 * l2])
        pos = to_name[0].find('\x00')
        to_name = to_name[0][:pos]
        forward_message = package[: l1 + l2] + package[l1 + 2 * l2:] 
        forward_sock = SOCKET_DICT[to_name]
        forward_sock.send(forward_message)

# forward chat text messages to specified client
def forward(sock, message):
    packed_tag = tag_unpacker.pack('a', len(message))
    sock.send(packed_tag + message)
    
               
# broadcast message to all connected clients
def broadcast(server_socket, message):
    for sock in SOCKET_LIST:
        if sock != server_socket:
            try:
                packed_tag = tag_unpacker.pack('a', len(message))
                sock.send(packed_tag + message)
            except:
                # broken socket connection
                sock.close()
                # broken socket, remove it
                if sock in SOCKET_LIST:
                    SOCKET_LIST.remove(sock)

if __name__ == "__main__":
    sys.exit(chat_server())
