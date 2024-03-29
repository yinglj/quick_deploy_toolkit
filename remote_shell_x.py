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

from __future__ import print_function
import glob
import sys
import cmd
import subprocess
import time
import os
import pexpect
import base64
import signal
import termios
import struct
import fcntl
import socket
from xcommon.xconfig import *
from collections import Counter
from collections import defaultdict
from xcommon.util import XUtil

# todo add set variable to save domain, check host.cfg is existed while set domain.
# todo add set variable to save host
# todo show domain host

# The interface displays the configuration definition, which can be adjusted as needed


class remote_shell(cmd.Cmd):

    def __init__(self, host):
        cmd.Cmd.__init__(self)
        #self.intro = '''Enter \"help\" for instructions'''
        self.secs = 1.0
        self.count = 3
        self.lang = '1'
        self.his = []
        self.hostName = socket.gethostname()
        self.host = host
        self.config_file = XUtil.get_host('host.cfg')
        # self.config_file = sys.path[0]+'/host.cfg'
        self.domain = "all"
        self.prompt = '\033[36;1m{0} \033[32;1m{1} {2}\033[36;1m remote shell\033[0m#'.format(
            self.hostName, self.domain, self.host)
        self.mapDomainHost = defaultdict(list)
        self.refresh_menu()

    def quit(self):
        try:
            self.quit()
        except:
            pass

    def do_prompt(self, line):
        '''Set command prompt, eg. \"prompt remote shell\"'''
        self.prompt = '\033[36;1m{0} \033[32;1m{1} {2}\033[36;1m remote shell\033[0m#'.format(
            self.hostName, self.domain, self.host)

    def do_EOF(self, line):
        '''Exit remote_shell.py with EOF.'''
        print
        return 1

    # Display by block, each block fixed BLOCK_NUM determines that there are multiple hosts in the block, default is 10
    def refresh_menu(self):
        self.cfg = XConfigParser(allow_no_value=True)
        self.cfg.read(self.config_file)

        self.mapDomainHost.clear()
        domaintmp = []
        self.mapLogin = {}
        for i in self.cfg.sections():
            # print self.cfg.options(i)
            if i == "global":
                self.lang = self.cfg.get(i, "LANG")
                continue
            for j in self.cfg.options(i):
                # print self.cfg.get(i,j)
                if j == "domain":
                    domaintmp.append(self.cfg.get(i, j))
                    self.mapDomainHost[self.cfg.get(i, j)].append(i)
            #! support useing ip to login
            self.mapLogin[self.cfg.get(
                i, 'user')+"@"+self.cfg.get(i, 'host')] = i
            self.mapLogin[self.cfg.get(
                i, 'host')+"@"+self.cfg.get(i, 'user')] = i
            self.mapLogin[self.cfg.get(i, 'host')] = i

        # print self.mapDomainHost
        self.domain_list = Counter(domaintmp)
        # print(self.domain_list)
        # for a,b in self.domain_list.items():
        #    print a, "to", b
        # for c,d in sorted(self.domain_list.iteritems(),key=lambda dict:dict[1],reverse=True):
        #    print c, "to=>", d

        print("*"+"*"*(COLUMN_WIDTH+1)*COLUMN_NUM)
        if 3 == sys.version_info.major and LANGUAGE_CHINESE == self.lang:
            welcome_hint_length = (COLUMN_WIDTH+1)*COLUMN_NUM-11
        elif LANGUAGE_ENGLISH == self.lang:
            welcome_hint_length = (COLUMN_WIDTH+1)*COLUMN_NUM-1
        else:
            welcome_hint_length = (COLUMN_WIDTH+1)*COLUMN_NUM+9

        print("*"+"{0: ^{1}}".format(XLangHelper.get_hint(self.lang, "welcome_hint"),
                                     welcome_hint_length)+"*")  # {}inline{}
        print("*"+"*"*(COLUMN_WIDTH+1)*COLUMN_NUM)

        hostlist = []
        hostno_hint = XLangHelper.get_hint(self.lang, "hostno_hint")
        user_hint = XLangHelper.get_hint(self.lang, "user_hint")
        iplist_hint = XLangHelper.get_hint(self.lang, "iplist_hint")
        # for d,h in sorted(self.domain_list.iteritems(),key=lambda dict:dict[1],reverse=False):   #domain, sorted by increasing number of hosts
        # domain, sorted by increasing number of hosts
        for d, h in sorted(self.domain_list.items(), key=lambda dict: dict[1], reverse=False):
            if(self.domain != "all" and d != self.domain):
                continue
            iNum = 0

            for i in sorted(self.mapDomainHost[d]):
                if(iNum % BLOCK_NUM == 0):
                    # {: ^38}, 38 width fill space alignment
                    hostlist.append(
                        "*"+"\033[32;1m{0: ^{1}}\033[0m".format(d, COLUMN_WIDTH+XUtil.str_count(d)))
                    hostlist.append(
                        "*"+"{0: ^{1}}".format(" -"*(int(COLUMN_WIDTH/2)), COLUMN_WIDTH))
                    if 3 == sys.version_info.major and LANGUAGE_CHINESE == self.lang:
                        hostlist.append("*"+" {0: <{1}}{2: <{3}}{4: <{5}}".format(
                            hostno_hint, HOST_WIDTH-1, user_hint, USER_WIDTH-XUtil.str_count(user_hint), iplist_hint, IP_WIDTH-XUtil.str_count(iplist_hint)))
                    else:
                        hostlist.append("*"+" {0: <{1}}{2: <{3}}{4: <{5}}".format(
                            hostno_hint, HOST_WIDTH-1, user_hint, USER_WIDTH+XUtil.str_count(user_hint), iplist_hint, IP_WIDTH+XUtil.str_count(iplist_hint)))

                str1 = "*"+" \033[36;1m{0: <{1}}\033[0m{2: <{3}}{4: <{5}}".format(
                    i, HOST_WIDTH-1, self.cfg.get(i, "user"), USER_WIDTH, self.cfg.get(i, "host"), IP_WIDTH)
                hostlist.append(str1)  # host
                iNum = iNum + 1
                if(iNum % BLOCK_NUM == 0):
                    hostlist.append("*"+"*"*COLUMN_WIDTH)

            while((iNum % BLOCK_NUM) != 0):  # Complement BLOCK_NUM
                hostlist.append("*"+"{0: ^{1}}".format(" ", COLUMN_WIDTH))
                iNum = iNum + 1

            if h % BLOCK_NUM != 0:  # When it is not a multiple of BLOCK_NUM, you only need to add a line: "*"+"*"*COLUMN_WIDTH
                hostlist.append("*"+"*"*COLUMN_WIDTH)

        # Complement the data block that is a multiple of COLUMN_NUM, where 4 lines of fixed characters
        iBlockNum = (len(hostlist)/(BLOCK_NUM+4)) % COLUMN_NUM
        while(iBlockNum % COLUMN_NUM != 0):
            # {: ^38}, 38 width fill space alignment
            hostlist.append("*"+"{0: ^{1}}".format(" ", COLUMN_WIDTH))
            hostlist.append("*"+"{0: ^{1}}".format(" -" *
                                                   (int(COLUMN_WIDTH/2)), COLUMN_WIDTH))
            if 3 == sys.version_info.major and LANGUAGE_CHINESE == self.lang:
                hostlist.append("*"+" {0: <{1}}{2: ^{3}}{4: ^{5}}".format(
                    hostno_hint, HOST_WIDTH-1, user_hint, USER_WIDTH-XUtil.str_count(user_hint), iplist_hint, IP_WIDTH-XUtil.str_count(iplist_hint)))
            else:
                hostlist.append("*"+" {0: <{1}}{2: ^{3}}{4: ^{5}}".format(
                    hostno_hint, HOST_WIDTH-1, user_hint, USER_WIDTH+XUtil.str_count(user_hint), iplist_hint, IP_WIDTH+XUtil.str_count(iplist_hint)))
            hostlist.append("*"+"{0: ^{1}}".format(" ", COLUMN_WIDTH))
            iNum1 = 1
            while(iNum1 % BLOCK_NUM != 0):  # Complement BLOCK_NUM
                hostlist.append("*"+"{0: ^{1}}".format(" ", COLUMN_WIDTH))
                iNum1 = iNum1 + 1
            hostlist.append("*"+"*"*COLUMN_WIDTH)
            iBlockNum = iBlockNum + 1

        #    array1[d] = hostlist
        # print hostlist
        hostlist_size = len(hostlist)
        for layer in range(int(hostlist_size/COLUMN_NUM/(BLOCK_NUM+4))):  # Layer
            for i in range(BLOCK_NUM+4):  # Column
                line = ""
                for j in range(COLUMN_NUM):  # row
                    line = line + \
                        hostlist[layer*COLUMN_NUM *
                                 (BLOCK_NUM+4)+(BLOCK_NUM+4)*j+i]
                if(line != ("*"+"{0: ^{1}}".format(" ", COLUMN_WIDTH))*COLUMN_NUM):  # blank line
                    print(line+"*")
        help = []
        temp_hint = XLangHelper.get_hint(self.lang, "login_hint")
        temp_hint = XLangHelper.get_hint(self.lang, "domain_hint")
        if 3 == sys.version_info.major and LANGUAGE_CHINESE == self.lang:
            help.append("{0: <{1}}".format(
                temp_hint, COLUMN_WIDTH-XUtil.str_count(temp_hint)))
            help.append("{0: <{1}}".format(
                temp_hint, COLUMN_WIDTH-XUtil.str_count(temp_hint)))
        else:
            help.append("{0: <{1}}".format(
                temp_hint, COLUMN_WIDTH+XUtil.str_count(temp_hint)))
            help.append("{0: <{1}}".format(
                temp_hint, COLUMN_WIDTH+XUtil.str_count(temp_hint)))
        for i in range(COLUMN_NUM - 3):  # The first two lines "help"
            help.append(" "*COLUMN_WIDTH)
            i = i+1
        help_line = "*"
        #n = 0
        for l in help:
            help_line = help_line + "{0: <{1}}".format(l, COLUMN_WIDTH-20)
            help_line = help_line + "|"
        if LANGUAGE_ENGLISH == self.lang:
            help_line = help_line + \
                "{0} \033[31;1m{1: <10} {2: >12}\033[0m".format(
                    XLangHelper.get_hint(self.lang, "cur_domain_hint"), self.domain, self.host) + "*"
        else:
            help_line = help_line + "{0} \033[31;1m{1: <10} {2: >14}\033[0m".format(
                XLangHelper.get_hint(self.lang, "cur_domain_hint"), self.domain, self.host) + " "*(COLUMN_WIDTH-35) + "*"

        print(help_line)

        print("*"+"*"*(COLUMN_WIDTH+1)*COLUMN_NUM)
        self.prompt = '\033[36;1m{0} \033[32;1m{1} {2}\033[36;1m remote shell\033[0m#'.format(
            self.hostName, self.domain, self.host)

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

    def do_vl(self, line):
        '''Edit config file.'''
        os.system("vi " + self.config_file)
        self.quit()
        return True

    # add_cfg
    def do_set(self, line):
        '''add config.'''
        return self.config_host(ENCRYPT_PASSWORD_MODE)

    # add_cfg
    def do_enset(self, line):
        '''add encrypted config.'''
        return self.config_host(DECRYPT_PASSWORD_MODE)

    # add_cfg
    def do_rmhost(self, line):
        '''rm host.'''
        return self.rm_host()

    # set lang
    def do_lang(self, line):
        lang = XUtil.sanitised_input(
            prompt="set language:0 for chinese,1 for English", type_=int, min_=0, max_=1, defaultvalue=self.lang)

        if not self.cfg.has_section("global"):
            self.cfg.add_section("global")

        self.cfg.set("global", "lang", lang)

        # write to file
        with open(self.config_file, "w+") as f:
            self.cfg.write(f)
        self.emptyline()

    # excute command for special domain
    def do_domain(self, line):
        '''excute command for special domain.\neg. domain mdb\n    domain all\n    domain'''
        parse_temp = line.split()
        if len(parse_temp) == 0:
            self.domain = "all"
            self.host = ""
            self.refresh_menu()
            return False
        else:
            if parse_temp[0].lower() == 'all':
                self.domain = "all"
                self.host = ""
                self.refresh_menu()
                return False
            for d, h in sorted(self.domain_list.items(), key=lambda dict: dict[1], reverse=False):
                if(parse_temp[0].lower() == d.lower()):
                    self.domain = d
                    self.host = ""
                    self.refresh_menu()
                    return False
            print('domain \033[31;1m{}\033[0m is not exists.'.format(
                parse_temp[0]))

        return False

    def complete_domain(self, text, line, begidx, endidx):
        completions_set = [
            'all'
        ]

        mline = line.partition(' ')[-1]
        # domain, sorted by host's count
        for d, h in sorted(self.domain_list.items(), key=lambda dict: dict[1], reverse=False):
            if(self.domain != "all" and d != self.domain):
                completions_set.append(d)
                continue
            iNum = 0
            completions_set.append(d)

        offs = len(mline) - len(text)
        return [s[offs:] for s in completions_set if s.startswith(mline)]

    # 重写cmd类的completedefault
    def completedefault(self, text, line, begidx, endidx):
        return self.completenames(text, line, begidx, endidx)

    # 重写cmd类的completenames
    def completenames(self, path, line, begidx, endidx):
        #print("path={0}, line={1}, begidx={2}, endidx={3}".format(path, line, begidx, endidx))
        # if path == "":
        #    dotext = 'do_'+ path
        #    return [a[3:] for a in self.get_names() if a.startswith(dotext)]
        completions = []
        commands = [
            'prompt',
            'EOF',
            'exit',
            'bye',
            'vl',
            'set',
            'enset',
            'rmhost',
            'domain',
            'show',
            'quit',
            'by',
            'q',
            'shell',
            'run',
            'lang',
            'help'
        ]
        if line == '':
            completions = commands
            return completions

        if path.partition(' ')[-1] == "" and len(line.split(" ")) == 1:
            # domain, 按主机数量增序排列
            for d, h in sorted(self.domain_list.items(), key=lambda dict: dict[1], reverse=False):
                if(self.domain != "all" and d != self.domain):
                    continue
                iNum = 0
                # completions.append("domain "+d)
                for i in self.mapDomainHost[d]:
                    if i.startswith(path):
                        completions.append(i)

                for k, v in self.mapLogin.items():
                    if k.startswith(path):
                        completions.append(k)

            for i in commands:
                if i.startswith(path):
                    completions.append(i)

        if path[0] == '~':
            path = os.path.expanduser('~')+path[1:]
        if os.path.isdir(path):
            return glob.glob(os.path.join(path, '*'))
        completions = completions + glob.glob(path+'*')

        if len(completions) == 0:  # 不是目录文件的情况下，返回候选命令
            bin_path = os.environ.get("PATH").split(":")
            for i in bin_path:
                completions = completions + \
                    [(s.split('/'))[-1] for s in glob.glob(i+"/"+path+"*")]
        return completions

    def _complete_path(self, path, line, start_idx, end_idx):
        if path[0] == '~':
            path = os.path.expanduser('~')+path[1:]
        if os.path.isdir(path):
            return glob.glob(os.path.join(path, '*'))
        completions = glob.glob(path+'*')

        if len(completions) == 0:  # 不是目录文件的情况下，返回候选命令
            bin_path = os.environ.get("PATH").split(":")
            for i in bin_path:
                completions = completions + \
                    [(s.split('/'))[-1] for s in glob.glob(i+"/"+path+"*")]
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
                or line.startswith("help") or line == "EOF" or line.startswith("shell") \
                or line.startswith("run") or line.startswith("show") or line == "q" \
                or line == "set" or line == "enset" or line == "vl" or line == "rmhost" \
                or line.startswith("lang") or line.startswith("domain"):
            return cmd.Cmd.onecmd(self, line)
        line = line.strip()
        if line in self.cfg.sections():
            self.remote_interactive(line)
            return
        if line in self.mapLogin.keys():
            self.remote_interactive(self.mapLogin[line])
            return
        if line != "" and line[0] == '!':
            if len(line) > 2 and line[1:3] == "vi":
                print("can't support !vi or !vim")
                return False
            command = subprocess.Popen(
                line[1:], shell=True, stdout=subprocess.PIPE)
            print(command.communicate()[0], end=' ')
            return False

        if len(line) > 1 and line[0:2] == "vi":
            print("can't support vi or vim. Interactive command is so on.")
            return False
        self.remote_cmd(self.host, line)
        pass

    def do_shell(self, line):
        '''Execute the rest of the line as a shell command, eg. \'!ls\', \'shell pwd\'.
        ! for localhost, shell or none for remote host.'''
        # check HOST.NO
        if line in self.cfg.sections():
            self.remote_interactive(line)
            return
        self.remote_cmd(self.host, line)

    # tab自动补齐shell命令的参数
    def complete_shell(self, text, line, start_idx, end_idx):
        return self._complete_path(text, line, start_idx, end_idx)

    def do_run(self, line):
        '''Execute the rest of the line as a shell command, eg. \'run ls\', \'run pwd\'.'''
        self.remote_cmd(self.host, line)

    # def sigwinch_passthrough (sig, data):
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
            # TIOCGWINSZ = 1074295912L # Assume
            TIOCGWINSZ = 1074295912  # Assume
        s = struct.pack('HHHH', 0, 0, 0, 0)
        x = fcntl.ioctl(sys.stdout.fileno(), TIOCGWINSZ, s)
        return struct.unpack('HHHH', x)[0:2]

    def remote_interactive(self, host):
        user = self.cfg.get(host, "user")
        password = self.cfg.get(host, "password")
        ip = self.cfg.get(host, "host")
        port = self.cfg.get(host, "port")
        serveraliveinterval = self.cfg.get(host, "serveraliveinterval")
        serveraliveinterval_opt = " " if serveraliveinterval == '0' or serveraliveinterval is None else " -o TCPKeepAlive=yes -o ServerAliveInterval=" + serveraliveinterval
        cmd = "ssh {0} -o PreferredAuthentications=password -o PubkeyAuthentication=no -o StrictHostKeyChecking=no -p {1} {2}@{3}".format(
            serveraliveinterval_opt, port, user, ip)
        # print(cmd)
        child = pexpect.spawn(cmd)
        # signal.signal(signal.SIGWINCH, self.sigwinch_passthrough)
        winsize = self.getwinsize()
        child.setwinsize(winsize[0], winsize[1])
        try:
            child.expect('(!*)password:(!*)')
            # base64解码后多一个回车键符，需要剪掉一位
            _ = child.sendline(base64.b64decode(password))
        except pexpect.EOF:
            print("can not connect to {}".format(host))
            if child.isalive():
                child.close(force=True)
            return
        except pexpect.TIMEOUT:
            print("connect timeout {}".format(host))
            if child.isalive():
                child.close(force=True)
            return

        child.interact()
        child.expect(pexpect.EOF)
        child.close(force=True)

    def remote_cmd(self, host, line):
        line = line.replace("\"", "\\\"").replace(
            "$", "\\$").replace("\'", "\\'").replace("`", "\\`")
        line = "\""+line+"\""
        # print "line:{0}".format(line)
        if self.host != "":
            szCmd = "{0}/remote_cmd3.py --domain {1} --ip {2} {3}".format(os.path.dirname(os.path.realpath(__file__)),
                                                                          self.domain, self.host, line)
        else:
            szCmd = "{0}/remote_cmd3.py --domain {1} {2}".format(os.path.dirname(os.path.realpath(__file__)),
                                                                 self.domain, line)
        # print(szCmd)
        command = subprocess.Popen(
            szCmd, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
        while 1:
            if 2 == sys.version_info.major:
                out = command.stdout.readline()
                if out.decode('unicode_escape') == '':
                    break
                print(out.decode('unicode_escape'), end='')
            else:
                out = command.stdout.readline()
                if out == '':
                    break
                print(out.strip())
        command.stdout.close()

    def config_host(self, opt):
        '''Config the host file'''
        print("Config the host file:" + self.config_file)
        host_no = INPUT_("input your host_no: ")
        # section already exists return
        if True == self.cfg.has_section(host_no):
            print("host_no:" + host_no + " already exists!")
            return

        # get userinput
        domain = INPUT_("input your domain: ")
        host = INPUT_("input your host: ")
        port = INPUT_("input your port: ")
        user = INPUT_("input your user: ")
        password = INPUT_("input your password: ")
        serveraliveinterval = INPUT_("keep server alive second: ")

        # encrypt password
        if ENCRYPT_PASSWORD_MODE == opt:
            # enpassword = subprocess.getoutput("echo " + password + "|base64")
            enpassword = base64.b64encode(
                password.encode('utf-8')).decode('utf-8')
        else:
            enpassword = password
        workdir = INPUT_("input your workdir: ")

        print("[" + host_no + "]"
              "\r\ndomain = " + domain +
              "\r\nhost = " + host +
              "\r\nport = " + port +
              "\r\nuser = " + user +
              "\r\npassword = " + enpassword +
              "\r\nserveraliveinterval = " + serveraliveinterval +
              "\r\nworkdir = " + workdir)
        if "y" == INPUT_("confirm the config to be saved.(y/n):"):
            # add section / set option & key
            self.cfg.add_section(host_no)
            self.cfg.set(host_no, "domain", domain)
            self.cfg.set(host_no, "host", host)
            self.cfg.set(host_no, "port", port)
            self.cfg.set(host_no, "user", user)
            self.cfg.set(host_no, "password", enpassword)
            self.cfg.set(host_no, "serveraliveinterval", serveraliveinterval)
            self.cfg.set(host_no, "workdir", workdir)

            # write to file
            with open(self.config_file, "w+") as f:
                self.cfg.write(f)
            self.emptyline()

    def rm_host(self):
        '''rm the host_no cofig'''
        host_no = INPUT_("input the host_no you want to rm: ")
        # section not exists return
        if False == self.cfg.has_section(host_no):
            print("host_no:" + host_no + " not exists!")
            return
        self.cfg.remove_section(host_no)
        # write to file
        with open(self.config_file, "w+") as f:
            self.cfg.write(f)
        self.emptyline()


if __name__ == '__main__':
    #! for add current dir to LD_LIBRARY_PATH environment
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
        print("usage:", sys.argv[0])
        print("usage:", sys.argv[0], "host")
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
