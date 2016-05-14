#!/usr/bin/python3
# coding=utf-8
__author__ = 'smallfly'

import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from server_side import threaded_server

class Form(QDialog):

    HOST = ""
    PORT = 50000

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        self.textHandler = threaded_server.TextHandler()

        self.sock = threaded_server.ThreadedServer(Form.HOST, Form.PORT)
        self.sock_thread = self.sock.listen(target=self.textHandler.handleText, new_thread=True)
        self.connect(self.textHandler, SIGNAL("newText"), self.updateText)

        # 窗口设置
        self.setWindowTitle("手机<-->电脑信息传输")

        # 控件

        addressLabel = QLabel("Host: {} Port: {}".format(self.HOST, self.PORT))

        self.receivedText = QTextEdit(self)
        receivedLabel = QLabel("收到的消息: ")
        receivedLabel.setBuddy(self.receivedText)
        self.copyButton = QPushButton("拷贝到剪贴板(&C)")
        self.clearButton = QPushButton("清空内容(&L)")


        # 设置布局

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.copyButton)
        buttonLayout.addWidget(self.clearButton)


        layout = QVBoxLayout()
        layout.addWidget(addressLabel)
        layout.addWidget(receivedLabel)
        layout.addWidget(self.receivedText)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)

        # 槽
        # self.connect(self.copyButton, SIGNAL("clicked()"), self.copyContent)
        self.copyButton.clicked.connect(self.copyContent)
        self.clearButton.clicked.connect(self.clearText)


    def copyContent(self):
        clipBoard = QApplication.clipboard()
        clipBoard.setText(self.receivedText.toPlainText())
        self.receivedText.setFocus()

    def updateText(self, text):
        self.receivedText.setText(self.receivedText.toPlainText() + text)

    def clearText(self):
        print("->clear text")
        self.receivedText.setText("")
        self.receivedText.setFocus()

    def close(self):
        self.sock.stop()
        super(Form, self).close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    form = Form()
    form.show()
    app.exec_()
