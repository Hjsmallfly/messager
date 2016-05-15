# coding=utf-8
__author__ = 'smallfly'

import socket
from ctypes import c_int32

class TextClient(object):

    def __init__(self, host="localhost", port=50000):
        self.host = host
        self.port = port
        self.addr = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sizeSent = 0   # 记录已经发送的字节数
        self.totalSize = 0  # 需要发送的字节数

    def connect(self):
        self.sock.connect(self.addr)

    def reset(self):
        self.sizeSent = 0
        self.totalSize = 0

    def sendText(self, messageBody, encoding="utf-8"):

        # 构建字节流
        messageBytes = messageBody.encode(encoding)
        bytesToSend = bytes(c_int32(len(messageBytes))) + messageBytes
        self.totalSize = len(bytesToSend)
        print("->total bytes", self.totalSize)
        # bufSize = 1024
        while self.sizeSent < self.totalSize:
            bytesSent = self.sock.send(bytesToSend[ self.sizeSent:])
            if bytesSent > 0:
                print("bytes send: ", bytesSent)
                self.sizeSent += bytesSent
            else:
                print("->disconnected")
                self.sock.close()
                return
        self.reset()
        print("->all data sent")

    def close(self):
        # flag Shut down one or both halves of the connection. If how is SHUT_RD, further receives are disallowed. If how is SHUT_WR, further sends are disallowed. If how is SHUT_RDWR, further sends and receives are disallowed.

        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

if __name__ == "__main__":
    client = TextClient()
    client.connect()
    while True:
        msg = input("->")
        if msg:
            client.sendText(msg)
        else:
            break
    # client.sendText("HELLO WORLD, 你好世界!")
    # client.sendText("HELLO WORLD AGAIN, 再一次你好!")
    # f = open(__file__)
    # client.sendText(f.read())
    client.close()