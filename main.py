import os
import socket
import sys
from threading import Thread
import time


# функция, отвечающая за получение и обработку UDP-пакетов от пиров
def GetUdpChatMessage():
    global name
    global broadcastSocket
    global current_online
    while True:
        recv_message = broadcastSocket.recv(1024)              # получаем 1024 байта от пира
        recv_string_message = str(recv_message.decode('utf-8'))# переводим сообщение в строку
        if recv_string_message.find(':') != -1:                
        # если в сообщении есть двоеточие, то есть сообщения вида: 'имя пира: сообщение'
            print('\r%s\n' % recv_string_message, end='')      # выводим в консоль сообщение от пира
        elif recv_string_message.find('!@#') != -1 and recv_string_message.find(':') == -1 and recv_string_message[3:] in current_online:
        # если в сообщении находим служебную последовательность '!@#', и это не сообщение чата от любого пира, и имя этого пира содержится в списке текущих имён
            current_online.remove(recv_string_message[3:])     # удаляем имя пира из списка с именами
            print('>> Сейчас в сети: ' + str(len(current_online)))  # выводим текущее количество пиров в сети 
        elif not(recv_string_message in current_online) and recv_string_message.find(':') == -1:
        # если имя нового пира не содержится в списке пиров в сети, и это не сообщение чата от любого пира
            current_online.append(recv_string_message)         # добавляем в список имя нового пира
            print('>> Сейчас в сети: ' + str(len(current_online)))  # выводим текущее количество пиров в сети

# функция, отвечающая за отправку сообщений всем пирам
def SendBroadcastMessageForChat():
    global name
    global sendSocket
    sendSocket.setblocking(False)           # не блокируем сокет, с которого происходит отправка широковещательных сообщений
    while True:                             # бесконечный цикл
        data = input()                      # ввод сообщения пиром
        if data == 'Выход()':               
        # если кто-то из пиров захотел выйти из программы
            close_message = '!@#' + name    # формируем сообщение, регламентирующее закрытие
            sendSocket.sendto(close_message.encode('utf-8'), ('255.255.255.255', 8080)) # отправляем сообщение всем пирам в подсети
            #time.sleep(2)                  # таймаут выход из программы
            os._exit(1)                     # выходим из программы
        elif data != '' and data != 'Выход()':  
        # если сообщение не пустое и нет сообщения-признака выхода
            send_message = name + ': ' + data   # формируем сообщение в удобочитаемом формате
            sendSocket.sendto(send_message.encode('utf-8'), ('255.255.255.255', 8080))  # отправляем сообщение всем пирам в подсети
        else:
        # если пользователь не ввёл сообщение (попытался отправить пустое сообщение)
            print('Напишите сначала сообщение!')        

# функция, отвечающая за отправку имён пиров каждую секунду, пока конкретный пир в сети (реализация отправки статуса в сети)
def SendBroadcastOnlineStatus():
    global name
    global sendSocket
    sendSocket.setblocking(False)           # не блокируем сокет, с которого происходит отправка широковещательных соообщений
    while True:                             # бесконечный цикл
        time.sleep(1)                       # таймаут отправки статуса, что пир онлайн
        sendSocket.sendto(name.encode('utf-8'), ('255.255.255.255', 8080))  # отправка имени пира, пока он в сети

# главная функция
def main():
    global broadcastSocket
    # сокет для реализации получения сообщений от пиров
    broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)      # инициализация сокета для работы с IPv4-адресами, используя протокол UDP
    broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   # присваиваем параметр SO_REUSEADDR на уровне библиотеки, SO_REUSEADDR - указывает на то, что сразу несколько приложений могут слушать сокет
    broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)   # присваиваем параметр SO_BROADCAST на уровне библиотеки, SO_BROADCAST - указывает на то, что пакеты будут широковещательные
    broadcastSocket.bind(('0.0.0.0', 8080))                                 # биндимся к адресу '0.0.0.0', чтобы прослушивать все интерфейсы
    global sendSocket
    # сокет для реализации отправки сообщений пирам
    sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)           # инициализация сокета для работы с IPv4-адресами, используя протокол UDP
    sendSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)         # присваиваем параметр SO_BROADCAST на уровне библиотеки, SO_BROADCAST - указывает на то, что пакеты будут широковещательные

    # делаем красивое приветствие
    print('*************************************************')
    print('*  Добро пожаловать в наш P2P-чат!              *')
    print('*  Чтобы выйти, отправьте сообщение: Выход()    *')
    print('*  После ввода имени сразу можно писать в чат.  *')
    print('*  Хорошего времяпрепровождения!                *')
    print('*************************************************')


    global name
    name = ''                                                   # имя пользователя
    # точный, но убогий в реализации ввод имени пользователя
    while True:                                                 
        if not name:
        # если имя пустое
            name = input('Ваше имя: ')
            if not name:
            # если имя пустое
                print('Введите непустое имя!')
            else:
            # если имя введено, то выйти из цикла
                break
    print('*************************************************')  # красивый разграничитель между именем и чатом

    global recvThread
    recvThread = Thread(target=GetUdpChatMessage)               # поток для получения сообщений от пиров

    global sendMsgThread
    sendMsgThread = Thread(target=SendBroadcastMessageForChat)  # поток для отправки сообщений от пиров

    global current_online
    current_online = []                                         # список имя пиров, которые находятся в сети

    global sendOnlineThread
    sendOnlineThread = Thread(target=SendBroadcastOnlineStatus) # поток для отправки статусов, что пир в сети

    recvThread.start()                                          # запуск потока для получения сообщений от пиров
    sendMsgThread.start()                                       # запуск потока для отправки сообщений всем пирам
    sendOnlineThread.start()                                    # запуск поток для отправки статусов, что пир в сети

    recvThread.join()                                           # блокируем поток, в котором осуществляется вызов до тех пор, пока recvThread не будет завершён
    sendMsgThread.join()                                        # блокируем поток, в котором осуществляется вызов до тех пор, пока sendMsgThread не будет завершён
    sendOnlineThread.join()                                     # блокируем поток, в котором осуществляется вызов до тех пор, пока sendOnlineThread не будет завершён

if __name__ == '__main__':
    main()
