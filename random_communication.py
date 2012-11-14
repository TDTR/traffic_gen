#!/usr/bin/env python
# -*- coding:utf-8 -*-

#import numpy.random
#from pylab import *

import random
import logging
import logging.config
import threading
import time,datetime
import random
import socket
import sys

def _choice_destination_host(fanout,src_host = -1):
    dst_host = random.choice(range(fanout))
    #print 'dst_host = ', dst_host
    #dst_host +=1
    # 自分自身を指している場合
    if(src_host == -1):
        return dst_host
    
    if dst_host == src_host % fanout:
        return _choice_destination_host(fanout,src_host=src_host)
    else :
        return dst_host
    
def _choice_destination_router(router_len,src_router=-1):
    dst_router = random.choice(range(router_len))
    #print 'dst_router = ', dst_router
    #dst_router += 1
    if src_router == -1 : return dst_router

    # 自分自身を指している場合
    if dst_router == src_router:
        return _choice_destination_router(router_len,src_router=src_router)
        
    else :
        return dst_router

def _choice_destination_pod(pod_len, src_pod = -1, neighbor = False):
    if neighbor is True and src_pod != -1 :
        if src_pod == 0:
            return 1
        elif src_pod == pod_len:
            return pod_len -1
    
    dst_pod = random.choice(range(pod_len))
    #print 'dst_pod = ', dst_pod
    #dst_pod += 1
    if src_pod == -1 : return dst_pod
    if dst_pod == src_pod:
        return _choice_destination_pod(pod_len,src_pod=src_pod)
    else :
        return dst_pod

def choice_destination(src,k):
    outcome = random.choice(range(0,16))
    
    src_absolute_loc = src-1 #全体でのスイッチ位置
    src_relative_loc = src_absolute_loc % k/2 # スイッチ配下での位置
    #print 'src_absolute_loc,src_relative_loc=', src_absolute_loc,src_relative_loc
    
    router_absolute_loc = src_absolute_loc / (k/2) # 全体でのスイッチ位置
    router_relative_loc = router_absolute_loc % (k/2) # pod配下での位置
    #print 'router_absolute_loc,router_relative_loc', router_absolute_loc,router_relative_loc

    pod_absolute_loc = src_absolute_loc / (k/2)**2 # 全体でのポッド位置
    #print 'pod_loc' , pod_absolute_loc

    if outcome == 15:
        # ポッドの決定
        p = _choice_destination_pod(k,src_pod = pod_absolute_loc,neighbor = False)
        # ルータの決定
        r = _choice_destination_router(k/2)
        # ホストの決定
        h = _choice_destination_host(k/2)

        dst = (p * (k/2) + r ) * k/2
        
        return dst+h+1
    
    elif outcome == 14:
        # ポッドの決定
        p = _choice_destination_pod(k, src_pod = pod_absolute_loc,neighbor = True)
        # ルータの決定
        r = _choice_destination_router(k/2)
        # ホストの決定
        h = _choice_destination_host(k/2)
        dst = (p * (k/2) + r ) * k/2

        return dst + h+1

    elif outcome == 13 or outcome == 12:
        # 同じpod内での通信
        # ルータの決定 (位置と数)
        r = _choice_destination_router(k/2, src_router = router_relative_loc)
        # ホストの決定
        h = _choice_destination_host(k/2)
        dst = pod_absolute_loc * (k/2)
        dst += r
        dst *= k/2
        return dst + h+1
        
    else :
        # 同一エッジルータ配下で通信
        # ホストの決定
        h = _choice_destination_host(k/2, src_host = src_relative_loc) 
        dst = (pod_absolute_loc * (k/2) + router_relative_loc ) * k/2
        return dst + h+1

class socket_thread(threading.Thread):
    def __init__(self,src=0,k=4):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.i = 0
        self.host_ip = int(src)
        self.pod = int(k)

    def run(self):
        logging.debug("%s Start." % self.getName() )
        _sec = random.expovariate(0.1609)
        # select host
        if self.host_ip == 0:
            host = 'localhost'
        else :
            host = '10.0.0.' + str(choice_destination(self.host_ip,self.pod))
            
        port = 15000
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host,port))
        logging.debug('connection of %s will continue %s sec' % (host,_sec))

        d1 = datetime.datetime.now()
        while True:
            msg = "hogehoge"
            #logging.debug('send msg =' + msg)
            time.sleep(0.1)
            s.sendall(msg)
            d2 = datetime.datetime.now()
            dt = d2 - d1
            result = dt.seconds + float(dt.microseconds)/1000000
            #print str(result)
            if( result > _sec):
                s.sendall('')
                s.close()
                break
        self.i += 1
        #s = None

def main():
    argvs = sys.argv
    argc = len(argvs)
    if argc != 4 :
        print 'Oops!'
        print 'Usage: python %s ip_addr num_pod mu' % argvs[0]
        quit()
    
    LOGGING_CONF = 'log.conf'
    logging.config.fileConfig(LOGGING_CONF)
    logger = logging.getLogger("root")
    logging.debug('number of pod ='+str(argvs[2]))
    while True:
        stop_time = random.expovariate(int(argvs[3]))
        # ソケット通信スレッド生成
        t = socket_thread(argvs[1],argvs[2])
        t.start()
        time.sleep(stop_time)
        logging.debug('sleep Zzzz.....%s sec' % stop_time)
        
if __name__ == '__main__':
    main()
