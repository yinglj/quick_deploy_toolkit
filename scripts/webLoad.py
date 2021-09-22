#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import threading
import time
import sys
import os
import random

TIMES = 1
THREAD_NUM = 1
headers = {'Content-Type': 'application/json', 'Connection': 'keep-alive'}
#url = "http://127.0.0.1:20000/hello"
#url = "http://127.0.0.1:8080"
request = '{ "head":{ "requestRefId":"TSREQ_201601010809108632A", "secretId":"KFZQpn74WFkmLPx3gnP", "signature":"p2y/wVHJRmJvsNnQ1SbaJrOWDfb6FIfgwt9uYUlli/Q=" }, "request":"7717143918dff1b9eb7a37fb39f647b7f6a39da6db6e4981b899fcf5443cf9abcd1d5ab2d3c0e93b1e3cf539f9673a67337c4df16a5919f8fd16f04f0cfaee72d134fc16819c0b9af483c139689f510cb6c9f4011d574b8fab504dd3d2643aa2" }'

def postReq(url, request_file, thread_id,request_counts):
    client = requests.session()
    if not os.path.exists(request_file):
        return True
    f = open(request_file, 'r')
    # if no mode is specified, 'r'ead mode is assumed by default
    stat = 0
    lines = []
    while True:
        line = f.readline()
        if len(line) == 0:  # Zero length indicates EOF
            break
        if line == '\n':    #空行忽略
            continue
        lines.append(line)
    f.close()  # close the file
    
    for i in range(request_counts):
        if len(lines) > 0:
            request = lines[random.randint(0,len(lines))]
        _ = client.post(url=url, data=request, headers=headers)
        #res = client.post(url=url, data=request, headers=headers)
        #if res.status_code != 200:
        #    print(res.text,res.status_code)

def multiThreadWebLoad(url, request_file, thread_num, request_counts):
    thread_list = []
    t = time.time()
    for i in range(thread_num):
        my_thread = threading.Thread(target=postReq, args=(url, request_file,  i, request_counts,))
        my_thread.start()
        thread_list.append(my_thread)
    for thread in thread_list:
        thread.join()
    print("speed: {:.0f} requests per second.".format(request_counts * thread_num / (time.time() - t)))


def Usage(command):
    print("usage:" + command + " url datafile thread_num request_count")
    print("example: " + command + " \"http://127.0.0.1:20000/hello\" datafile 1 1 ")
    print("example: " + command + " \"http://127.0.0.1:20000/hello\" datafile 4 10000")


if __name__ == '__main__':
    if len(sys.argv) != 5:
        Usage(sys.argv[0])
    else:
        try:
            start_time = time.time()
            multiThreadWebLoad(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
            print("used time: {:.0f} seconds.".format(time.time()-start_time))
        except KeyboardInterrupt as e:
            print e
        except IOError as e:
            print e
        except ValueError as e:
            print e
        finally:
            pass