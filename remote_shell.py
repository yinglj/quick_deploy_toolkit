#!/usr/bin/env python
#code=utf-8

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
#todo add set variable to save domain, check host.cfg is existed while set domain.
#todo add set variable to save host
#todo show domain host

class remote_shell(cmd.Cmd):

    def __init__(self, host):
        cmd.Cmd.__init__(self)
        #self.intro = '''Enter \"help\" for instructions'''
        self.prompt = 'remote shell>'
        self.secs = 1.0
        self.count = 3
        self.his = []
        self.host = host
        self.domain = 'host.cfg'

    def quit(self):
        try:
            self.quit()
        except:
            pass

    def do_prompt(self, line):
        '''Set command prompt, eg. \"prompt remote shell\"'''
        self.prompt = 'remote shell>'

    def do_EOF(self, line):
        '''Exit remote_shell.py with EOF.'''
        print
        return 1

    def emptyline(self):
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
        '''set the domain config or set the host or set the ip.\neg. set domain host.cfg\n    set host host158\n    set ip 10.10.13.158'''
        parse_temp = line.split()
        if len(parse_temp) < 1:
            print("Please input set domain|host|ip\n")
        else:
            if parse_temp[0]=='host' or parse_temp[0]=='ip':
                if len(parse_temp) == 1:
                    self.host = ""
                else:
                    self.host = parse_temp[1]
            elif parse_temp[0]=='domain':
                if len(parse_temp) == 1:
                    self.domain = ""
                else:
                    self.domain = parse_temp[1]
                if not os.path.exists(parse_temp[1]):
                    print("file {} is not exist.".format(parse_temp[1]))
            else:
                print("set host host123\nset host 10.10.13.158\nset domain host.cfg\n")
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

    def onecmd(self, line):
        '''Execute the rest of the line as a shell command, eg. \'!ls\', \'shell pwd\'.'''
        if line == "" or line == "bye" or line == "exit" or line == "by" or line == "quit" \
            or "help" in line or line == "EOF" or "shell" in line or "run" in line \
            or "set" in line or "show" in line :
            return cmd.Cmd.onecmd(self, line)
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
        self.remote_cmd(self.host, line)

    def do_run(self, line):
        '''Execute the rest of the line as a shell command, eg. \'run ls\', \'run pwd\'.'''
        self.remote_cmd(self.host, line)

    def remote_cmd(self, host, line):
        if self.host != "":
            szCmd = "{}/remote_cmd.py --domain {} --ip {} {}".format(os.path.dirname(os.path.realpath(__file__)), 
                self.domain, self.host, line)
        else:
            szCmd = "{}/remote_cmd.py --domain {} {}".format(os.path.dirname(os.path.realpath(__file__)), 
                self.domain, line)
        print szCmd
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
