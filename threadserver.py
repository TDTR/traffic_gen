#!/usr/bin/env python
# -*- coding:utf-8 -*-

import socket
import threading
import time

host = ''
port = 15000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
s.bind((host,port))
s.listen(1)

def threadfunc(sock):
    print '%s is created!' % (threading.currentThread().getName())
    while 1:
        rcvmsg = sock.recv(1024)
        time.sleep(1)
        if rcvmsg =='':
            break
        else:
            #print '%s received -> %s' %(threading.currentThread().getName(), rcvmsg)
            continue
    sock.close()
    print '%s is terminated!' % (threading.currentThread().getName())

while 1:
    try:
        clientsock, clientaddr = s.accept()
    except:
        break
    t = threading.Thread(target = threadfunc, args = [clientsock])
    t.setDaemon(1)
    t.start()

                         
