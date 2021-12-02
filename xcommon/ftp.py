# coding:utf-8
from ctypes import *
import os
import sys
import ftplib

if 2 == sys.version_info.major:
    defaultencoding = 'utf-8'
    if sys.getdefaultencoding() != defaultencoding:
        reload(sys)
        sys.setdefaultencoding(defaultencoding)


class XFtpTransfer:
    ftp = ftplib.FTP()
    bIsDir = False
    path = ""

    def __init__(self, host, port='21'):
        self.ftp.set_debuglevel(2)  # 打开调试级别2，显示详细信息
        # self.ftp.set_pasv(0)      #0主动模式 1 #被动模式
        self.ftp.connect(host, port)
        self.log_file = open('XFtpTransfer.log', 'wb')
        print("1")

    def __del__(self):
        self.ftp.quit()

    def Login(self, user, passwd):
        self.ftp.login(user, passwd)
        print(self.ftp.getwelcome())

    def __CheckSizeEqual(self, remoteFile, localFile):
        try:
            remoteFileSize = self.ftp.size(remoteFile)
            localFileSize = os.path.getsize(localFile)
            if localFileSize == remoteFileSize:
                return True
            else:
                return False
        except Exception:
            return None

    def DownLoadFile(self, LocalFile, RemoteFile):
        try:
            self.ftp.cwd(os.path.dirname(RemoteFile))
            f = open(LocalFile, 'wb')
            remoteFileName = 'RETR ' + os.path.basename(RemoteFile)
            self.ftp.retrbinary(remoteFileName, f.write)

            if self.__CheckSizeEqual(RemoteFile, LocalFile):
                self.log_file.write(
                    'The File is downloaded successfully to %s\n' % LocalFile)
                return True
            else:
                self.log_file.write(
                    'The localFile %s size is not same with the remoteFile\n' % LocalFile)
                return False
        except Exception:
            return False

    def UpLoadFile(self, LocalFile, RemoteFile):
        if os.path.isfile(LocalFile) == False:
            return False
        file_handler = open(LocalFile, "rb")
        self.ftp.storbinary('STOR %s' % RemoteFile, file_handler, 4096)
        file_handler.close()
        return True

    def UpLoadFileTree(self, LocalDir, RemoteDir):
        if os.path.isdir(LocalDir) == False:
            return False
        print("LocalDir:", LocalDir)
        LocalNames = os.listdir(LocalDir)
        print("list:", LocalNames)
        print(RemoteDir)
        self.ftp.cwd(RemoteDir)
        for Local in LocalNames:
            src = os.path.join(LocalDir, Local)
            if os.path.isdir(src):
                self.UpLoadFileTree(src, Local)
            else:
                self.UpLoadFile(src, Local)

        self.ftp.cwd("..")
        return

    def DownLoadFileTree(self, LocalDir, RemoteDir):
        print("remoteDir:", RemoteDir)
        if os.path.isdir(LocalDir) == False:
            os.makedirs(LocalDir)
        self.ftp.cwd(RemoteDir)
        RemoteNames = self.ftp.nlst()
        print("RemoteNames", RemoteNames)
        for file in RemoteNames:
            Local = os.path.join(LocalDir, file)
            if self.isDir(file):
                self.DownLoadFileTree(Local, file)
            else:
                self.DownLoadFile(Local, file)
        self.ftp.cwd("..")
        return

    def isDir(self, path):
        self.bIsDir = False
        self.path = path

        try:
            self.ftp.cwd(path)
            self.ftp.cwd("..")
            self.bIsDir = True
        except:
            self.bIsDir = False
        return self.bIsDir

    # def show(self, list):
    #     result = list.lower().split( " " )
    #     if self.path in result and result[0].startswith("d"):
    #         self.bIsDir = True
    #         return

    # def isDir(self, path):
    #     self.bIsDir = False
    #     self.path = path
    #     #this ues callback function ,that will change bIsDir value
    #     self.ftp.retrlines( 'LIST', self.show )
    #     if self.bIsDir:
    #         return self.bIsDir
    #     return self.bIsDir
