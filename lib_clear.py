#!/usr/bin/env python
# coding=utf-8

'''
name:
lib_clear.py
email:
yinglj@asiainfo.com
title:
这个Python用于删除ob_rel/lib下库文件有多个历史版本,减少lib目录的大小
1.判断.so文件是否链接文件,并记录下当前链接的原始lib库文件
2.执行删除操作,将不在库链接列表中的历史版本的文件进行删除,文件名称必须为*.so.*
'''

import cmd
import os
import re
import subprocess
import sys
import time


class lib_clear(cmd.Cmd):

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.intro = '''Enter \"help\" for instructions'''
        self.tablelist = []
        self.prompt = '>> '
        self.secs = 1.0
        self.count = 3
        self.his = []
        self.child = subprocess.Popen('ls -l', shell=True,
                                      stdin=subprocess.PIPE, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        self.listLibLink = []
        self.listLibLinked = []
        self.listAllLib = []
        self.listToDelete = []
        self.input = self.child.stdin
        self.output = self.child.stdout
        self.read_all()
        self.delete_lib()

    def quit(self):
        try:
            self.child.communicate('5')
            # print 'exit 5'
        except:
            pass

    def readline(self):
        line = ''
        while True:
            s = self.output.read(1)
            if len(s) == 0:
                break
            line += s
            if (s == '\n') or (line == '>> '):
                break

        return line

    def regexFileName(self, strPrefix, strFile, strRegex):
        strPattern = r"" + strPrefix + strRegex
        pattern = re.compile(strPattern)
        # if pattern.match(strFile) != None:
        if pattern.search(strFile) != None:  # 这里改成search匹配
            return True
        else:
            return False

    def read_all(self):
        while True:
            line = self.readline()
            if len(line) == 0:
                break
            elif line.count('>>') != 0:
                return True
            else:
                # print line,
                self.filterLib(line)
        return False

    def delete_lib(self):
        for strLib in self.listAllLib:
            del_command = ''
            if strLib not in self.listLibLinked:
                del_command = "mkdir -p ./backup;mv %s ./backup" % (strLib)
                print del_command

                if os.system(del_command) == 0:
                    print '%s is successful' % (del_command)
                else:
                    print '%s is failed' % (del_command)
        return False

    def filterLib(self, line):
        strPrefix = ''
        # strRegex = '(\.so\.){1}';
        strRegex = r'(\.so\.)[1]\.[0-9]\.[0-9]\.[0-9]{6}' #fixed by hanzw

        strLinkRegex = r'(\ ->\ ){1}'
        strLinkSoRegex = r'(\.so){1}$'
        if self.regexFileName(strPrefix, line, strLinkRegex):
            for strSplit in line.split(" "):
                if self.regexFileName(strPrefix, strSplit, strLinkSoRegex):
                    self.listLibLink.append(strSplit.strip())
                if self.regexFileName(strPrefix, strSplit, strRegex):
                    self.listLibLinked.append(strSplit.strip())
        else:
            if self.regexFileName(strPrefix, line, strRegex):
                for strSplit in line.split(" "):
                    if self.regexFileName(strPrefix, strSplit, strRegex):
                        self.listAllLib.append(strSplit.strip())

    def post(self, statements):
        self.input.write(statements)
        self.input.flush()
        return self.read_all()

    def do_prompt(self, line):
        '''Set command prompt, eg. \'prompt daemon\' '''
        if line == '':
            self.prompt = '>> '
        else:
            self.prompt = line

    def do_EOF(self, line):
        '''Exit lib_clear.py with EOF.'''
        print
        return 1

    def emptyline(self):
        pass

    def do_exit(self, line):
        '''Exit lib_clear.py.'''
        self.quit()
        return True

    def do_bye(self, line):
        '''Exit lib_clear.py.'''
        self.quit()
        return True

    def do_quit(self, line):
        '''Exit lib_clear.py.'''
        self.quit()
        return True

    def do_by(self, line):
        '''Exit lib_clear.py.'''
        self.quit()
        return True

    def do_shell(self, line):
        '''Execute the rest of the line as a shell command, eg. \'!ls\', \'shell pwd\'.'''
        command = subprocess.Popen(line, shell=True, stdout=subprocess.PIPE)
        print command.communicate()[0],

    def do_list(self, line):
        '''Display the history list.'''
        num = 1
        for command in self.his:
            print num, command
            num = num + 1


if __name__ == '__main__':
    if len(sys.argv) != 1:
        print sys.argv[0], "server_ip server_port"
    else:
        client = lib_clear()
        try:
            # client.check_lock();
            time.sleep(1)
        except KeyboardInterrupt as e:
            print e
        except IOError as e:
            print e
        except ValueError as e:
            print e
        finally:
            client.quit()
