#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
name:
static_core.py
email:
yinglj@asiainfo.com
title:
pstack.py for Linux
'''

import os
import cPickle
import time
import ConfigParser
import re
import string
import logging
import sys
import cmd
import subprocess


class CPStack:
    def __init__(self):
        self.listPstackFiles = []
        self.listStat = []
        self.totalThreads = 0
        self.listIgnores = {"billing billing": 0, "exe =": 0}
        self.backtrace = ""
        self.mapStatic = {}

    def analyseAllFiles(self):
        for i in range(1, len(sys.argv)):
            self.listPstackFiles.append(sys.argv[i])
            # print "listPstackFiles", self.listPstackFiles;
        for v in self.listPstackFiles:
            self.analyseOneFile(v)
        self.showResult()

    def analyseOneFile(self, pstack_file):
        if not os.path.exists(pstack_file):
            return True
        f = file(pstack_file, 'r')
        # if no mode is specified, 'r'ead mode is assumed by default
        stat = 0
        lines = ""
        self.totalThreads = 0
        self.backtrace = ""
        while True:
            line = f.readline()
            if len(line) == 0:  # Zero length indicates EOF
                break
            if line.find("(Thread ") != -1:
                self.totalThreads += 1
                stat = 1
                lines = ""
                continue
            ignore = False
            for v in self.listIgnores:
                if line.find(v) != -1:
                    stat = 2
                    self.listIgnores[v] += 1
                    ignore = True
                continue
            if ignore == True:
                continue
            if line.find("----------------") != -1:
                if self.backtrace != "":
                    if self.mapStatic.get(self.backtrace) != None:
                        self.mapStatic[self.backtrace] += 1
                    else:
                        self.mapStatic[self.backtrace] = 1
                self.backtrace = ""
                continue
            self.staticLine(line)
            lines = lines + line
            if line.find("in clone") != -1 and stat == 1:
                print lines

                # print line, # Notice comma to avoid automatic newline added by Python
        f.close()  # close the file
        return True

    def staticLine(self, line):
        funcName = ""
        line1 = ""
        #0  sdl::SdlSession::SetAttrib (this=this@entry=0x2ae87c4dcab0, iAttrId=iAttrId@entry=3, pObject=pObject@entry=0x2ae881464210) at src/sdl_session.cpp:174
        #1  0x00002ae85ded36c0 in kpi::KpiStatBegin (iKpiId=60305, pSession=0x2ae87c4dcab0) at kpi2.cpp:304
        split1 = line.split(" in ")
        if len(split1) > 1:
            split2 = split1[0].split(" ")
            left = split2[0]
            line1 = "{} {}".format(left,split1[1])
        else:
            line1 = split1[0]
        split3 = line1.split(" ")
        split3 = [x for x in split3 if x]   #删除空串
        if len(split3) > 3:
            funcName = "{:0>3} {} @ {}".format(split3[0][1:], split3[1], split3[-1])
            self.backtrace =  self.backtrace + funcName
        else:
            funcName = "{:0>3} {} @ {}".format(split3[0][1:], split3[1], split3[-1])
            self.backtrace =  self.backtrace + funcName
        #if self.mapStatic.get(funcName) != None:
        #    self.mapStatic[funcName] += 1
        #else:
        #    self.mapStatic[funcName] = 1

    def showResult(self):

        # print self.mapStatic;
        mapStatic = sorted(self.mapStatic.items(), key=lambda d: d[1])  #
        mapStatic = sorted(mapStatic, key=lambda d: d[0])  #
        mapStatic = sorted(mapStatic, key=lambda d: d[1])  #
        line = "-"*128
        i = ""
        for v in mapStatic:
            #if i != v[1]:
            #    print("="*128)
            i = v[1]
            print "{}{:-^128}".format(v[0], "此类core总计: {} 个".format(v[1]))
        print "="*128
        for v in self.listIgnores:
            print self.listIgnores[v], "\t", v
        print self.totalThreads, "\t", "total threads"


def Usage(command):
    print "usage:" + command + " [file]"
    print "example: " + command + " *.pstack.*"
    print "example: " + command + " 12345.pstack.1 12345.pstack.2"


if __name__ == '__main__':
    if len(sys.argv) == 1:
        Usage(sys.argv[0])
    else:
        try:
            client = CPStack()
            client.analyseAllFiles()
            time.sleep(0)
        except KeyboardInterrupt as e:
            print e
        except IOError as e:
            print e
        except ValueError as e:
            print e
        finally:
            pass