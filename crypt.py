#coding: utf8
import sys
from Crypto.Cipher import AES
from Crypto import Random
from binascii import b2a_hex, a2b_hex

key = 'AsiaInfoAsiaInfo'
iv = key[::-1]

BS = AES.block_size
#iv = Random.new().read(BS)
#原始密文长度补充至AES.block_size的整数倍
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
#去除解密密文中额外添加的补充记录
unpad = lambda s : s[0:-ord(s[-1])]

class aicrypt():
    def __init__(self, key):
        self.key = key
        self.mode = AES.MODE_CBC

    #加密函数，如果text不是16的倍数【加密文本text必须为16的倍数！】，那就补足为16的倍数
    def encrypt(self, text):
        cryptor = AES.new(self.key, self.mode, iv)
        #这里密钥key 长度必须为16（AES-128）、24（AES-192）、或32（AES-256）Bytes 长度.目前AES-128足够用

        self.ciphertext = cryptor.encrypt(pad(text))
        #因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        #所以这里统一把加密后的字符串转化为16进制字符串
        return b2a_hex(self.ciphertext)

    #解密后，使用unpad去除解密密文中额外添加的补充记录
    def decrypt(self, text):
        if len(text) % 32 != 0:
            print text+" might be not an encrypted code, can\'t be decrypted."
            return ''
        else:
            cryptor = AES.new(self.key, self.mode, iv)
            plain_text = cryptor.decrypt(a2b_hex(text))
            return unpad(plain_text)


if __name__ == '__main__':
    pc = aicrypt(key)      #初始化密钥
    usage = """which function are you gonna use?
[E]ncrypt or [D]ecrypt >> """
    choice_dict = {'E':'Encrypt','D':'Decrypt','Q':'Quit'}
    choice = raw_input(usage)
    while True:
        if choice[0].upper() in 'EDQ':
            print "your choice is %s"%choice_dict[choice[0].upper()]
            if choice[0].upper() == 'Q':
                print "Program exit!"
                sys.exit()
            if choice[0].upper() == 'E':
                code = raw_input("Please enter the code for Encrypt:").strip()
                print '*'*30
                print "Code : "+code
                print "Encrypt : "+pc.encrypt(code)
            else:
                code = raw_input("Please enter the code for Decrypt:").strip()
                print '*'*30
                print "Code : "+code
                print "Decrypt : "+pc.decrypt(code)
            print '*'*30
            choice = raw_input(usage)
        else:
            print "Wrong command! E or D is expected! Q for Quit!"
            print '*'*30
            choice = raw_input(usage)