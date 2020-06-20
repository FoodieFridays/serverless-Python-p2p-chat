'''
serverless-Python-p2p-chat
Translated from Russian to English by FoodieFridays
Forked from justcomex's p2p-chat
'''

import os
import socket
import sys
from threading import Thread
import time


# function responsible for receiving and processing UDP packets from peers
def GetUdpChatMessage():
    global name
    global broadcastSocket
    global current_online
    while True:
        recv_message = broadcastSocket.recv(1024)              # we get 1024 bytes from the peer
        recv_string_message = str(recv_message.decode('utf-8'))# translate (decode) the message into a string
        if recv_string_message.find(':') != -1:                
        # if the message contains a colon, that is, messages of the form: 'peer name: message'
            print('\r%s\n' % recv_string_message, end='')      # print a message from the peer to the console
        elif recv_string_message.find('!@#') != -1 and recv_string_message.find(':') == -1 and recv_string_message[3:] in current_online:
        # if in the message we find the service sequence '!@#', and this is not a chat message from any peer, and the name of this peer is contained in the list of current names
            current_online.remove(recv_string_message[3:])     # remove the peer name from the list with names
            print('>> Peers online now: ' + str(len(current_online)))  # display the current number of peers in the network
        elif not(recv_string_message in current_online) and recv_string_message.find(':') == -1:
        # if the name of the new peer is not contained in the list of peers in the network, and this is not a chat message from any peer
            current_online.append(recv_string_message)         # add the name of the new peer to the list
            print('>> Peers online now: ' + str(len(current_online)))  # display the current number of peers in the network

# function responsible for sending messages to all peers
def SendBroadcastMessageForChat():
    global name
    global sendSocket
    sendSocket.setblocking(False)           # do not block the socket from which broadcast messages are sent
    while True:                             # endless loop
        data = input()                      # used to store user input
        if data == 'Exit()':               
        # if one of the peers wants to exit the program
            close_message = '!@#' + name    # we form the closing message 
            sendSocket.sendto(close_message.encode('utf-8'), ('255.255.255.255', 8080)) # send a message to all peers in the subnet
            #time.sleep(2)                  # program timeout - not currently activated
            os._exit(1)                     # exit the program
        elif data != '' and data != 'Exit()':  
        # if the message is not empty and there is no exit message
            send_message = name + ': ' + data   # we put the message into a nice format
            sendSocket.sendto(send_message.encode('utf-8'), ('255.255.255.255', 8080))  # send a message to all peers in the subnet
        else:
        # if the user did not enter a message (tried to send an empty message)
            print('You must write a message first!')        

# function responsible for sending peer names every second, while a particular peer is in the network (implementation of sending status on the network)
def SendBroadcastOnlineStatus():
    global name
    global sendSocket
    sendSocket.setblocking(False)           # do not block the socket from which broadcast messages are sent
    while True:                             # endless loop
        time.sleep(1)                       # only updates every second
        sendSocket.sendto(name.encode('utf-8'), ('255.255.255.255', 8080))  # sending the peer name while it is online

# main function
def main():
    global broadcastSocket
    # socket to implement receiving messages from peers
    broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)      # initializing a socket for working with IPv4 addresses using UDP
    broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   # assign the parameter SO_REUSEADDR at the library level, SO_REUSEADDR - indicates that several applications can listen to the socket at once
    broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)   # assign the parameter SO_BROADCAST at the library level, SO_BROADCAST - indicates that the packets will be broadcast
    broadcastSocket.bind(('0.0.0.0', 8080))                                 # bind to the address '0.0.0.0' to listen to all interfaces
    global sendSocket
    # socket to implement sending messages to peers
    sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)           # initializing a socket for working with IPv4 addresses using UDP
    sendSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)         # assign the parameter SO_BROADCAST at the library level, SO_BROADCAST - indicates that the packets will be broadcast

    # startup greeting
    print('*********************************************************')
    print('*  Welcome to our Python P2P chat!                      *')
    print('*  To exit, send the message: Exit()    		*')
    print('*  After entering your name, you can immediately chat.  *')
    print('*  Have fun!				                *')
    print('*********************************************************')


    global name
    name = ''                                                   # username
    # poor username input
    while True:                                                 
        if not name:
        # if the name is empty
            name = input('Your name: ')
            if not name:
            # if the name is empty
                print('Enter a non-empty name!')
            else:
            # if name is entered correctly exit loop
                break
    print('*********************************************************')  # delimiter between name and chat

    global recvThread
    recvThread = Thread(target=GetUdpChatMessage)               # thread for receiving messages from peers

    global sendMsgThread
    sendMsgThread = Thread(target=SendBroadcastMessageForChat)  # thread for sending messages to peers

    global current_online
    current_online = []                                         # list of peers that are online

    global sendOnlineThread
    sendOnlineThread = Thread(target=SendBroadcastOnlineStatus) # thread to send connection status

    recvThread.start()                                          # start a thread to receive messages from peers
    sendMsgThread.start()                                       # start a thread to send messages to all peers
    sendOnlineThread.start()                                    # start a thread to send connection status

    recvThread.join()                                           # block the thread in which the call is made until recvThread is completed
    sendMsgThread.join()                                        # block the thread in which the call is made until sendMsgThread is completed
    sendOnlineThread.join()                                     # block the thread in which the call is made until sendOnlineThread is completed

if __name__ == '__main__':
    main()
