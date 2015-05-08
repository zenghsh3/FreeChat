# tcp_server.py
import sys
import socket
import select
import json

HOST = '' 
SOCKET_LIST = [] # socket
SOCKET_DICT = {} # name:socket
RECV_BUFFER = 4096 
PORT = 10000

def chat_server():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1024)
 
    # add server socket object to the list of readable connections
    SOCKET_LIST.append(server_socket)
 
    print "Tcp server started on port" + str(PORT)
 
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
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        # there is something in the socket
                        print data
                        try:
                            decoded = json.loads(data);
                            tag = decoded[0]
                        except:
                            print 'Error format'
                        # upload name and return online names
                        if tag == 'upload_name':
                            SOCKET_DICT[decoded[1]] = sock
                            online_list = ['online_names']
                            for key in SOCKET_DICT.keys():
                                online_list.append(key)
                            sock.send(json.dumps(online_list))
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
                    else:
                        # remove the socket that's broken    
                        if sock in SOCKET_LIST:
                            SOCKET_LIST.remove(sock)
                #exception 
                except:
                    print 'Exception!'
                    continue
    server_socket.close()
    
# forward chat messages to specified client
def forward(sock, message):
        try :
            sock.send(message)
        except :
            # broken socket connection
            sock.close()
            # broken socket, remove it
            if sock in SOCKET_LIST:
                    SOCKET_LIST.remove(sock)

# broadcast message to all connected clients
def broadcast(server_socket, message):
    for sock in SOCKET_LIST:
        if sock != server_socket:
            try:
                sock.send(message)
            except:
                # broken socket connection
                sock.close()
                # broken socket, remove it
                if sock in SOCKET_LIST:
                    SOCKET_LIST.remove(sock)

if __name__ == "__main__":
    sys.exit(chat_server())
