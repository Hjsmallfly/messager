# coding=utf-8
__author__ = 'smallfly'

import socket
import threading

from PyQt4.QtCore import QObject, SIGNAL

socket.socket

class TextHandler(QObject):

    # 字节流开始的几个字节存放的是消息体的长度
    SIZEOF_META_DATA = 4

    def __init__(self):
        super(TextHandler, self).__init__()
        self.msgSize = -1
        self.sizeReceived = 0   # 已经接收到的数据
        self.receivedBytes = b''

    def reset(self):
        self.msgSize = -1
        self.sizeReceived = 0
        self.receivedBytes = b''

    def handleText(self, client, address):
        # buffer size
        size = 1024
        print("->client @{} connected".format(address))
        while True:
            try:
                if self.sizeReceived < TextHandler.SIZEOF_META_DATA:
                    # 继续接收一开始的SIZEOF_META_DATA字节
                    # 注意不要多接收字节,不然有几条消息的话可能会混乱
                    data = client.recv(TextHandler.SIZEOF_META_DATA - self.sizeReceived)
                    if data:
                        self.receivedBytes += data
                        self.sizeReceived += len(data)
                    else:
                        # 断开了链接
                        print("->client @{} disconnected".format(address))
                        client.close()
                        return
                else:
                    if self.msgSize == -1:
                        # 读取信息大小
                        self.msgSize = int.from_bytes(self.receivedBytes[: TextHandler.SIZEOF_META_DATA], byteorder="little")
                        print('->message body size: ', self.msgSize)

                    if self.sizeReceived < TextHandler.SIZEOF_META_DATA + self.msgSize:
                        # 继续读取信息, 但是注意不能少读也不能多读
                        data = client.recv(min(TextHandler.SIZEOF_META_DATA + self.msgSize - self.sizeReceived, size))
                        if data:
                            self.receivedBytes += data
                            self.sizeReceived += len(data)
                        else:
                            print("->client @{} disconnected".format(address))
                            client.close()
                            return
                    else:
                        # 读取完毕
                        print("->received {} bytes".format(len(self.receivedBytes)))
                        data = self.receivedBytes[TextHandler.SIZEOF_META_DATA: ].decode("UTF-8")
                        print("->msg", data)
                        self.emit(SIGNAL("newText"), data)
                        # 清空状态
                        self.reset()
            except Exception as e:
                print("->error occurred @{}: {}".format(address, str(e)))
                client.close()
                return



class ThreadedTextServer(object):

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
            self.__listen(target=target)
        else:
            print("->server running in another thread")
            thread = threading.Thread(target=self.__listen, args=(target, ))
            thread.setDaemon(daemon)
            thread.start()
            return thread


    def __listen(self, target):
        # print("in __listen")
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
    server = ThreadedTextServer("", 50000)
    textHandler = TextHandler()
    server.listen(target=textHandler.handleText, new_thread=True, daemon=False)