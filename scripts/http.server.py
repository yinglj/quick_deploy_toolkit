#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os, socket
from socketserver import ThreadingMixIn
from http.server import SimpleHTTPRequestHandler, HTTPServer

HOST = socket.gethostname()

class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass

'''
这里设置监听端口
'''
if sys.argv[1:]:
    PORT = int(sys.argv[1])
else:
    PORT = 8000

'''
这里设置工作目录，如果不设置则使用脚本文件所在目录
'''
if sys.argv[2:]:
    os.chdir(sys.argv[2])
    CWD = sys.argv[2]
else:
    CWD = os.getcwd()

server = ThreadingSimpleServer(('0.0.0.0', PORT), SimpleHTTPRequestHandler)
print("目录：", CWD, "地址：", HOST, "端口", PORT)
try:
    while 1:
        sys.stdout.flush()
        server.handle_request()
except KeyboardInterrupt:
    print("\n用户终止运行.")