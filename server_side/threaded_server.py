# coding=utf-8
__author__ = 'smallfly'

import socket
import threading
from PyQt4.QtCore import QObject, SIGNAL

socket.socket

class TextHandler(QObject):

    def __init__(self):
        super(TextHandler, self).__init__()

    def handleText(self, client, address):
        size = 1024
        print("->client @{} connected".format(address))
        while True:
            try:
                data = client.recv(size)
                if data:
                    data = data.decode("UTF-8")
                    print("->received: ", data)
                    self.emit(SIGNAL("newText"), data)
                else:
                    print("->client @{} disconnected".format(address))
                    return
            except Exception as e:
                print(e)
                client.close()
                return



class ThreadedServer(object):

    def __init__(self, host, port, backlog=5):
        self.host = host
        self.port = port
        self.backlog = backlog
        self.__stop = False
        self.clients = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.sock.bind((self.host, self.port))

    def listen(self,target=None, new_thread=False, daemon=True):
        if target is None:
            raise TypeError("target requires callable")
        self.sock.listen(self.backlog)
        if not new_thread:
            self.__listen()
        else:
            print("->server running in another thread")
            thread = threading.Thread(target=self.__listen, args=(target, ))
            thread.setDaemon(daemon)
            thread.start()
            return thread


    def __listen(self, target):

        while not self.__stop:
            client, address = self.sock.accept()
            self.clients.append(client)
            client.settimeout(60 * 10)
            threading.Thread(target=target, args=(client, address)).start()


    def stop(self):
        # 停止接受新的请求
        self.__stop = True
        for client in self.clients:
            client.close()



    def just_test(self, client, address):
        size = 1024
        print("->client @{} connected".format(address))
        while True:
            try:
                data = client.recv(size)
                if data:
                    data = data.decode("UTF-8")
                    print("->received: ", data)
                else:
                    print("->client @{} disconnected".format(address))
                    return
            except Exception as e:
                print(e)
                client.close()
                return

if __name__ == "__main__":
    server = ThreadedServer("", 50000)
    textHandler = TextHandler()
    server.listen(target=textHandler.handleText, new_thread=True)