#!/usr/bin/env python2
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
#import string
import os
import pexpect
import ConfigParser
#import configparser
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

#界面显示配置定义，这块可以根据需要调整
COLUMN_NUM = 3
HOST_WIDTH = 12
USER_WIDTH = 12
IP_WIDTH = 16
COLUMN_WIDTH = HOST_WIDTH + USER_WIDTH + IP_WIDTH
BLOCK_NUM = 10
#界面显示配置

import glob

def str_count(str):
    import string
    '''找出字符串中的中英文、空格、数字、标点符号个数'''
    count_en = count_dg = count_sp = count_zh = count_pu = 0
    for s in str.decode( 'utf-8' ):
        # 英文
        if s in string.ascii_letters:
            count_en += 1
        # 数字 
        elif s.isdigit():
            count_dg += 1
        # 空格
        elif s.isspace():
            count_sp += 1
        # 中文，除了英文之外，剩下的字符认为就是中文
        elif s.isalpha():
            count_zh += 1
        # 特殊字符
        else:
            count_pu += 1
    return count_zh

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
        self.prompt = '\033[36;1m{0} \033[32;1m{1} {2}\033[36;1m remote shell\033[0m#'.format(self.hostName, self.domain, self.host)
        self.mapDomainHost = defaultdict(list)
        self.histfile = os.path.expanduser('~/.remote_shell_history')
        self.histfile_size = 1000
        cfg.read(self.config_file)
        
        domaintmp=[]
        self.mapLogin={}
        for i in cfg.sections():
            #print cfg.options(i)
            for j in cfg.options(i):
                #print cfg.get(i,j)
                if j == "domain":
                    domaintmp.append(cfg.get(i,j))
                    self.mapDomainHost[cfg.get(i,j)].append(i)
            self.mapLogin[cfg.get(i,'user')+"@"+cfg.get(i,'host')] = i
            self.mapLogin[cfg.get(i,'host')+"@"+cfg.get(i,'user')] = i
            self.mapLogin[cfg.get(i,'host')] = i
            
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
        self.prompt = '\033[36;1m{0} \033[32;1m{1} {2}\033[36;1m remote shell\033[0m#'.format(self.hostName, self.domain, self.host)

    def do_EOF(self, line):
        '''Exit remote_shell.py with EOF.'''
        print
        return 1

    # 采用按块显示的方式，每个块固定BLOCK_NUM决定块里有多个主机，默认为10条
    def refresh_menu(self):
        print("*"+"*"*(COLUMN_WIDTH+1)*COLUMN_NUM)
        print("*"+"{0: ^{1}}".format("Welcome to using scripts for remoting login",(COLUMN_WIDTH+1)*COLUMN_NUM-1)+"*")  #{}内嵌{}
        print("*"+"*"*(COLUMN_WIDTH+1)*COLUMN_NUM)

        hostlist = []
        #for d,h in sorted(self.domain_list.iteritems(),key=lambda dict:dict[1],reverse=False):   #domain, 按主机数量增序排列
        for d,h in sorted(self.domain_list.items(),key=lambda dict:dict[1],reverse=False):   #domain, 按主机数量增序排列
            if(self.domain != "all" and d != self.domain):
                continue
            iNum=0
                
            for i in sorted(self.mapDomainHost[d]):
                if(iNum % BLOCK_NUM == 0):
                    hostlist.append("*"+"\033[32;1m{0: ^{1}}\033[0m".format(d, COLUMN_WIDTH+str_count(d)))     #{: ^38}, 38宽度补空格对齐
                    hostlist.append("*"+"{0: ^{1}}".format(" -"*(int(COLUMN_WIDTH/2)), COLUMN_WIDTH))
                    hostlist.append("*"+" {0: <{1}}{2: ^{3}}{4: ^{5}}".format("HOST.NO", HOST_WIDTH-1, "用户", USER_WIDTH+str_count("用户"), "IP列表", IP_WIDTH+str_count("IP列表")))
                str1 = "*"+" \033[36;1m{0: <{1}}\033[0m{2: ^{3}}{4: ^{5}}".format(i, HOST_WIDTH-1, cfg.get(i,"user"), USER_WIDTH, cfg.get(i,"host"), IP_WIDTH)
                hostlist.append(str1) #host
                iNum = iNum + 1
                if(iNum % BLOCK_NUM == 0):
                    hostlist.append("*"+"*"*COLUMN_WIDTH)
  
            while( (iNum % BLOCK_NUM) != 0):    #补足BLOCK_NUM
                hostlist.append("*"+"{0: ^{1}}".format(" ", COLUMN_WIDTH))
                iNum = iNum + 1

            if h % BLOCK_NUM != 0:  #不是BLOCK_NUM的倍数时，才需要补一行:"*"+"*"*COLUMN_WIDTH
                hostlist.append("*"+"*"*COLUMN_WIDTH)
        
        #补足COLUMN_NUM的倍数的数据块, 其中为固定字符的4行
        iBlockNum = (len(hostlist)/(BLOCK_NUM+4))%COLUMN_NUM
        while(iBlockNum % COLUMN_NUM != 0):
            hostlist.append("*"+"{0: ^{1}}".format(" ", COLUMN_WIDTH))     #{: ^38}, 38宽度补空格对齐
            hostlist.append("*"+"{0: ^{1}}".format(" -"*(int(COLUMN_WIDTH/2)), COLUMN_WIDTH))
            hostlist.append("*"+" {0: <{1}}{2: ^{3}}{4: ^{5}}".format("HOST.NO", HOST_WIDTH-1, "用户", USER_WIDTH+str_count("用户"), "IP列表", IP_WIDTH+str_count("IP列表")))
            hostlist.append("*"+"{0: ^{1}}".format(" ", COLUMN_WIDTH))
            iNum1 = 1
            while( iNum1 % BLOCK_NUM != 0):    #补足BLOCK_NUM
                hostlist.append("*"+"{0: ^{1}}".format(" ", COLUMN_WIDTH))
                iNum1 = iNum1 + 1
            hostlist.append("*"+"*"*COLUMN_WIDTH)
            iBlockNum = iBlockNum + 1
        
        #    array1[d] = hostlist
        #print hostlist
        hostlist_size = len(hostlist)
        for layer in range(int(hostlist_size/COLUMN_NUM/(BLOCK_NUM+4))): #层
            for i in range(BLOCK_NUM+4):     #列
                line=""
                for j in range(COLUMN_NUM): #行
                    line = line + hostlist[layer*COLUMN_NUM*(BLOCK_NUM+4)+(BLOCK_NUM+4)*j+i]
                if(line != ("*"+"{0: ^{1}}".format(" ", COLUMN_WIDTH))*COLUMN_NUM):  #空行
                    print(line+"*")
        help = []
        #help.append("{0: <{1}}".format(" 帮  助 $  输入HOST.NO,登录对应主机",COLUMN_WIDTH+10))   #10为里面包含了10个汉字
        #help.append("{0: <{1}}".format(" exit: 退出 | set domain: 切换主机域",COLUMN_WIDTH+7))  #7为里面包含了7个汉字
        temp_hint = " 帮  助 $  输入HOST.NO,登录对应主机"
        help.append("{0: <{1}}".format(temp_hint,COLUMN_WIDTH+str_count(temp_hint)))   #10为里面包含了10个汉字
        temp_hint = " exit: 退出 | set domain: 切换主机域"
        help.append("{0: <{1}}".format(temp_hint,COLUMN_WIDTH+str_count(temp_hint)))  #7为里面包含了7个汉字
        for i in range(COLUMN_NUM - 3): #前面的两行help
            help.append(" "*COLUMN_WIDTH)
            i= i+1
        help_line = "*"
        #n = 0
        for l in help:
            help_line = help_line + "{0: <{1}}".format(l, COLUMN_WIDTH-20);
            help_line = help_line + "|"
        help_line = help_line + " 当前域：\033[31;1m{0: <10} {1: >15}\033[0m".format(self.domain, self.host) + " "*(COLUMN_WIDTH-35) + "*"
        print(help_line)
    
        print("*"+"*"*(COLUMN_WIDTH+1)*COLUMN_NUM)
        self.prompt = '\033[36;1m{0} \033[32;1m{1} {2}\033[36;1m remote shell\033[0m#'.format(self.hostName, self.domain, self.host)
    
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
            print("domain={0}, host={1}".format(self.domain, self.host))
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
                    #    print("file {0} is not exist.".format(parse_temp[1]))
                self.refresh_menu()
            else:
                print("set host host123\nset host 10.10.13.158\nset domain mdb")
        return False

    def complete_set(self, text, line, begidx, endidx):
        completions_set = [
            'host',
            'domain'
        ]
        
        mline = line.partition(' ')[-1]
        if mline != "":
            for d,h in sorted(self.domain_list.iteritems(),key=lambda dict:dict[1],reverse=False):   #domain, 按主机数量增序排列
                if(self.domain != "all" and d != self.domain):
                    completions_set.append("domain "+d)
                    continue
                iNum=0
                completions_set.append("domain "+d)
                for i in self.mapDomainHost[d]:
                    completions_set.append("host "+i)
                    
        offs = len(mline) - len(text)
        return [s[offs:] for s in completions_set if s.startswith(mline)]
    
    #重写cmd类的completedefault
    def completedefault(self, text, line, begidx, endidx):
        return self.completenames(text, line, begidx, endidx)
    
    #重写cmd类的completenames
    def completenames(self, path, line, begidx, endidx):
        #print("path={0}, line={1}, begidx={2}, endidx={3}".format(path, line, begidx, endidx))
        #if path == "":
        #    dotext = 'do_'+ path
        #    return [a[3:] for a in self.get_names() if a.startswith(dotext)]
        completions = []
        if path.partition(' ')[-1] == "" and len(line.split(" ")) == 1:
            for d,h in sorted(self.domain_list.iteritems(),key=lambda dict:dict[1],reverse=False):   #domain, 按主机数量增序排列
                if(self.domain != "all" and d != self.domain):
                    continue
                iNum=0
                #completions.append("domain "+d)
                for i in self.mapDomainHost[d]:
                    if i.startswith(path):
                        completions.append(i)

                for k,v in self.mapLogin.items():
                    if k.startswith(path):
                        completions.append(k)
                
        if path[0]=='~':
            path = os.path.expanduser('~')+path[1:]
        if os.path.isdir(path):
            return glob.glob(os.path.join(path, '*'))
        completions = completions + glob.glob(path+'*')

        if len(completions) == 0: #不是目录文件的情况下，返回候选命令
            bin_path = os.environ.get("PATH").split(":")
            for i in bin_path:
                completions = completions + [(s.split('/'))[-1] for s in glob.glob(i+"/"+path+"*")]
        return completions

    def _complete_path(self, path, line, start_idx, end_idx):
        if path[0]=='~':
            path = os.path.expanduser('~')+path[1:]
        if os.path.isdir(path):
            return glob.glob(os.path.join(path, '*'))
        completions = glob.glob(path+'*')

        if len(completions) == 0: #不是目录文件的情况下，返回候选命令
            bin_path = os.environ.get("PATH").split(":")
            for i in bin_path:
                completions = completions + [(s.split('/'))[-1] for s in glob.glob(i+"/"+path+"*")]
        return completions

    def do_show(self, line):
        '''show the domain and host information, eg. show.'''
        print("domain={0}, host={1}\n".format(self.domain, self.host))
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
            or line.startswith("help") or line == "EOF" or line.startswith("shell") or line.startswith("run") \
            or line.startswith("set") or line.startswith("show") or line == "q":
            return cmd.Cmd.onecmd(self, line)
        if line in cfg.sections():
            self.remote_interactive(line)
            return
        if line in self.mapLogin.keys():
            self.remote_interactive(self.mapLogin[line])
            return
        if line != "" and line[0] == '!':
            if len(line)>2 and line[1:3] == "vi":
                print("can't support !vi or !vim")
                return False
            command = subprocess.Popen(line[1:], shell=True, stdout=subprocess.PIPE)
            print command.communicate()[0],
            return False

        if len(line)>1 and line[0:2] == "vi":
            print("can't support vi or vim. Interactive command is so on.")
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
    
    #tab自动补齐shell命令的参数
    def complete_shell(self, text, line, start_idx, end_idx):
        return self._complete_path(text, line, start_idx, end_idx)

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
            #TIOCGWINSZ = 1074295912L # Assume
            TIOCGWINSZ = 1074295912 # Assume
        s = struct.pack('HHHH', 0, 0, 0, 0)
        x = fcntl.ioctl(sys.stdout.fileno(), TIOCGWINSZ, s)
        return struct.unpack('HHHH', x)[0:2]

    def remote_interactive(self, host):
        user = cfg.get(host, "user")
        password = cfg.get(host, "password")
        ip = cfg.get(host, "host")
        port = cfg.get(host, "port")
        cmd = "ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no -o StrictHostKeyChecking=no -p {0} {1}@{2}".format(port, user, ip)
        print(cmd)
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
        #print "line:{0}".format(line)
        if self.host != "":
            szCmd = "{0}/remote_cmd.py --domain {1} --ip {2} {3}".format(os.path.dirname(os.path.realpath(__file__)), 
                self.domain, self.host, line)
        else:
            szCmd = "{0}/remote_cmd.py --domain {1} {2}".format(os.path.dirname(os.path.realpath(__file__)), 
                self.domain, line)
        #print(szCmd)
        command = subprocess.Popen(szCmd, shell=True, stdout=subprocess.PIPE)
        while 1:
            out = command.stdout.readline()
            if out.decode() == '':
                break
            print out.decode(),
        #print command.communicate()[0],

if __name__ == '__main__':
        #* for add current dir to LD_LIBRARY_PATH environment
        import platform
        # * 这里有一个问题用#!/usr/bin/env python3时，macos操作系统下环境变量变更os.execve会不生效
        if platform.system() == 'Linux':
            if os.path.dirname(os.path.realpath(__file__)) not in os.environ.get('LD_LIBRARY_PATH'):
                os.environ['LD_LIBRARY_PATH'] = os.environ.get(
                    'LD_LIBRARY_PATH')+":"+os.path.dirname(os.path.realpath(__file__))
                os.execve(os.path.realpath(__file__),
                        sys.argv, os.environ)  # * rerun
        import readline
        readline.set_completer_delims(' \t\n')

        if len(sys.argv) > 2:
            print("usage:",sys.argv[0])
            print("usage:",sys.argv[0],"host")
        else:
            if len(sys.argv) == 2:
                client = remote_shell(sys.argv[1])
            else:
                client = remote_shell("")
            try:
                client.cmdloop()
            except KeyboardInterrupt as e:
                print(e)
            except IOError as e:
                print(e)
            except ValueError as e:
                print(e)
            finally:
                client.quit()
