#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ---------------------------------------------------------------------------------------
# Copyright (c) 2016 project AutomicDeploy
# This script is licensed under GNU GPL version 2.0 or above
# author: yinglj@gmail.com
# ---------------------------------------------------------------------------------------
# Expect script to supply root/admin password for remote ssh server and execute command.
# user = User Name of remote Linux/UNIX server, no hostname
# password = Password of remote Linux/UNIX server, for root user.
# host = IP Addreess of remote Linux/UNIX server, no hostname
# ---------------------------------------------------------------------------------------

import sys
import cmd
import subprocess
import time
import os
import pexpect
import ConfigParser
from collections import Counter
from collections import defaultdict
import base64
import signal
import termios
import struct
import fcntl
import socket
#todo add set variable to save domain, check host.cfg is existed while set domain.
#todo add set variable to save host
#todo show domain host
cfg = ConfigParser.ConfigParser()
COLUMN_NUM = 3
BLOCK_NUM = 10

class remote_shell(cmd.Cmd):

    def __init__(self, host):
        cmd.Cmd.__init__(self)
        #self.intro = '''Enter \"help\" for instructions'''
        self.secs = 1.0
        self.count = 3
        self.his = []
        self.hostName = socket.gethostname()
        self.host = host
        self.config_file = sys.path[0]+'/host.cfg'
        self.domain = "all"
        self.prompt = '\033[36;1m{} {} {} remote shell\033[0m#'.format(self.hostName, self.domain, self.host)
        self.mapDomainHost = defaultdict(list)
        cfg.read(self.config_file)
        
        domaintmp=[]
        hostlist=[]
        for i in cfg.sections():
            #print cfg.options(i)
            for j in cfg.options(i):
                #print cfg.get(i,j)
                if j == "domain":
                    domaintmp.append(cfg.get(i,j))
                    self.mapDomainHost[cfg.get(i,j)].append(i)
        #print self.mapDomainHost
        self.domain_list = Counter(domaintmp)
        #print(self.domain_list)
        #for a,b in self.domain_list.items():
        #    print a, "to", b
        #for c,d in sorted(self.domain_list.iteritems(),key=lambda dict:dict[1],reverse=True):
        #    print c, "to=>", d
        self.refresh_menu()

    def quit(self):
        try:
            self.quit()
        except:
            pass

    def do_prompt(self, line):
        '''Set command prompt, eg. \"prompt remote shell\"'''
        self.prompt = '\033[36;1m{} {} {} remote shell\033[0m#'.format(self.hostName, self.domain, self.host)

    def do_EOF(self, line):
        '''Exit remote_shell.py with EOF.'''
        print
        return 1

    # 采用按块显示的方式，每个块固定BLOCK_NUM决定块里有多个主机，默认为10台
    def refresh_menu(self):
        print("**********************************************************************************************************************")
        print("*                                     Welcome to using scripts for remoting login                                    *")
        print("**********************************************************************************************************************")
        #array1 = {}
        hostlist = []
        for d,h in sorted(self.domain_list.iteritems(),key=lambda dict:dict[1],reverse=False):   #domain
            if(self.domain != "all" and d != self.domain):
                continue
            #hostlist = []
            iNum=0
            hostlist.append("*"+"\033[32;1m{: ^38}\033[0m".format(d))     #{: ^38}, 38宽度补空格对齐
            hostlist.append("*"+" - - - - - - - - - - - - - - - - - - -")
            hostlist.append("*"+" HOST.NO    用户        IP列表        ")
            for i in self.mapDomainHost[d]:
                str1 = "*"+"\033[36;1m{: ^9}\033[0m{: ^9}{: ^20}".format(i, cfg.get(i,"user") , cfg.get(i,"host"))
                hostlist.append(str1) #host
                iNum = iNum + 1
                if(iNum % BLOCK_NUM == 0):
                    hostlist.append("*"+"*"*38)
                    hostlist.append("*"+"\033[32;1m{: ^38}\033[0m".format(d))     #{: ^38}, 38宽度补空格对齐
                    hostlist.append("*"+" - - - - - - - - - - - - - - - - - - -")
                    hostlist.append("*"+" HOST.NO    用户        IP列表        ")
            while( (iNum % BLOCK_NUM) <> 0):    #补足BLOCK_NUM
                hostlist.append("*"+"{: ^38}".format(" "))
                iNum = iNum + 1
            hostlist.append("*"+"*"*38)

        #补足COLUMN_NUM的倍数的数据块, 其中为固定字符的4行
        iBlockNum = (len(hostlist)/(BLOCK_NUM+4))%COLUMN_NUM
        while(iBlockNum % COLUMN_NUM <> 0):
            hostlist.append("*"+"{: ^38}".format(" "))     #{: ^38}, 38宽度补空格对齐
            hostlist.append("*"+" - - - - - - - - - - - - - - - - - - -")
            hostlist.append("*"+" HOST.NO    用户        IP列表        ")
            hostlist.append("*"+"{: ^38}".format(" "))
            iNum1 = 1
            while( iNum1 % BLOCK_NUM <> 0):    #补足BLOCK_NUM
                hostlist.append("*"+"{: ^38}".format(" "))
                iNum1 = iNum1 + 1
            hostlist.append("*"+"*"*38)
            iBlockNum = iBlockNum + 1

        #    array1[d] = hostlist
        #print hostlist
        hostlist_size = len(hostlist)
        for layer in range(hostlist_size/COLUMN_NUM/(BLOCK_NUM+4)): #层
            for i in range(BLOCK_NUM+4):     #列
                line=""
                for j in range(COLUMN_NUM): #行
                    line = line + hostlist[layer*COLUMN_NUM*(BLOCK_NUM+4)+(BLOCK_NUM+4)*j+i]
                if(line != ("*"+"{: ^38}".format(" "))*COLUMN_NUM):  #空行
                    print line+"*"
        #print("*====================================================================================================================*")
        print("* 帮  助 $  输入HOST.NO,登录对应主机   | exit: 退出 | set domain: 切换主机域  | 当前域：\033[31;1m{: <10} {: >15}\033[0m   *".format(self.domain, self.host))
        print("*====================================================================================================================*")
        self.prompt = '\033[36;1m{} {} {} remote shell\033[0m#'.format(self.hostName, self.domain, self.host)
    
    def emptyline(self):
        self.refresh_menu()
        self.quit()
        pass

    def do_exit(self, line):
        '''Exit remote_shell.py.'''
        self.quit()
        return True

    def do_bye(self, line):
        '''Exit remote_shell.py.'''
        self.quit()
        return True

    def do_set(self, line):
        '''set the special domain or set the host or set the ip.\neg. set domain mdb\n    set host host158\n    set ip 10.10.13.158'''
        parse_temp = line.split()
        if len(parse_temp) < 1:
            print("domain={}, host={}".format(self.domain, self.host))
            print("Please input set domain|host|ip")
        else:
            if parse_temp[0]=='host' or parse_temp[0]=='ip':
                if len(parse_temp) == 1:
                    self.host = ""
                else:
                    self.host = parse_temp[1]
                self.refresh_menu()
            elif parse_temp[0]=='domain':
                if len(parse_temp) == 1:
                    self.domain = "all"
                    self.host = ""
                    #return False
                else:
                    if(parse_temp[1] == 'all' or parse_temp[1] == 'ALL'):
                        self.domain = "all"
                        self.host = ""
                    else:
                        self.domain = parse_temp[1]
                        self.host = ""
                    #if not os.path.exists(parse_temp[1]):
                    #    print("file {} is not exist.".format(parse_temp[1]))
                self.refresh_menu()
            else:
                print("set host host123\nset host 10.10.13.158\nset domain mdb")
        return False

    def do_show(self, line):
        '''show the domain and host information, eg. show.'''
        print("domain={}, host={}\n".format(self.domain, self.host))
        return False

    def do_quit(self, line):
        '''Exit remote_shell.py.'''
        self.quit()
        return True

    def do_by(self, line):
        '''Exit remote_shell.py.'''
        self.quit()
        return True

    def do_q(self, line):
        '''Exit remote_shell.py.'''
        self.quit()
        return True

    def onecmd(self, line):
        '''Execute the rest of the line as a shell command, eg. \'!ls\', \'shell pwd\'.'''
        if line == "" or line == "bye" or line == "exit" or line == "by" or line == "quit" \
            or "help" in line or line == "EOF" or "shell" in line or "run" in line \
            or "set" in line or "show" in line or line == "q":
            return cmd.Cmd.onecmd(self, line)
        if line in cfg.sections():
            self.remote_interactive(line)
            return
        if line != "" and line[0] == '!':
            if len(line)>2 and line[1:3] == "vi":
                print "can't support !vi or !vim"
                return False
            command = subprocess.Popen(line[1:], shell=True, stdout=subprocess.PIPE)
            print command.communicate()[0],
            return False

        if len(line)>1 and line[0:2] == "vi":
            print "can't support vi or vim. Interactive command is so on."
            return False
        self.remote_cmd(self.host, line)
        pass

    def do_shell(self, line):
        '''Execute the rest of the line as a shell command, eg. \'!ls\', \'shell pwd\'.
        ! for localhost, shell or none for remote host.'''
        #判断输入是非为HOST.NO
        if line in cfg.sections():
            self.remote_interactive(line)
            return
        self.remote_cmd(self.host, line)

    def do_run(self, line):
        '''Execute the rest of the line as a shell command, eg. \'run ls\', \'run pwd\'.'''
        self.remote_cmd(self.host, line)

    #def sigwinch_passthrough (sig, data):
    #    winsize = self.getwinsize()
    #    global child
    #    child.setwinsize(winsize[0],winsize[1])

    def getwinsize(self):
        """This returns the window size of the child tty.
        The return value is a tuple of (rows, cols).
        """
        if 'TIOCGWINSZ' in dir(termios):
            TIOCGWINSZ = termios.TIOCGWINSZ
        else:
            TIOCGWINSZ = 1074295912L # Assume
        s = struct.pack('HHHH', 0, 0, 0, 0)
        x = fcntl.ioctl(sys.stdout.fileno(), TIOCGWINSZ, s)
        return struct.unpack('HHHH', x)[0:2]

    def remote_interactive(self, host):
        user = cfg.get(host, "user")
        password = cfg.get(host, "password")
        ip = cfg.get(host, "host")
        port = cfg.get(host, "port")
        cmd = "ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no -o StrictHostKeyChecking=no -p {} {}@{}".format(port, user, ip)
        print cmd
        child = pexpect.spawn(cmd)
        #signal.signal(signal.SIGWINCH, self.sigwinch_passthrough)
        winsize = self.getwinsize()
        child.setwinsize(winsize[0], winsize[1])
        try:
            child.expect('(!*)password:(!*)')
            _ = child.sendline(base64.b64decode(password)[:-1]) #base64解码后多一个回车键符，需要剪掉一位
        except pexpect.EOF:
            print("pexpect.EOF")
            child.close(force=True)
            return
        except pexpect.TIMEOUT:
            print("pexpect.TIMEOUT")
            child.close(force=True)
            return

        child.interact()
        child.expect(pexpect.EOF)
        child.close(force=True)

    def remote_cmd(self, host, line):
        line = line.replace("\"", "\\\"").replace("$", "\\$").replace("\'", "\\'").replace("`", "\\`")
        line = "\""+line+"\""
        #print "line:{}".format(line)
        if self.host != "":
            szCmd = "{}/remote_cmd.py --domain {} --ip {} {}".format(os.path.dirname(os.path.realpath(__file__)), 
                self.domain, self.host, line)
        else:
            szCmd = "{}/remote_cmd.py --domain {} {}".format(os.path.dirname(os.path.realpath(__file__)), 
                self.domain, line)
        #print szCmd
        command = subprocess.Popen(szCmd, shell=True, stdout=subprocess.PIPE)
        while 1:
            out = command.stdout.readline()
            if out == '':
                break
            print out,
        #print command.communicate()[0],

if __name__ == '__main__':
        if len(sys.argv) > 2:
            print "usage:",sys.argv[0]
            print "usage:",sys.argv[0],"host"
        else:
            if len(sys.argv) == 2:
                client = remote_shell(sys.argv[1])
            else:
                client = remote_shell("")
            try:
                client.cmdloop()
            except KeyboardInterrupt as e:
                print e
            except IOError as e:
                print e
            except ValueError as e:
                print e
            finally:
                client.quit()
