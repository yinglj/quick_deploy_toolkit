import os
import pwd
import sys


class CUtil:
    @staticmethod
    def get_username():
        return pwd.getpwuid(os.getuid())[0]

    @staticmethod
    def str_count(str):
        import string
        '''Find out the number of Chinese and English, spaces, numbers, and punctuation marks in the string'''
        count_en = count_dg = count_sp = count_zh = count_pu = 0

        if 2 == sys.version_info.major:
            for s in str.decode('utf-8'):
                # English
                if s in string.ascii_letters:
                    count_en += 1
                # digital
                elif s.isdigit():
                    count_dg += 1
                # space
                elif s.isspace():
                    count_sp += 1
                # Chinese
                elif s.isalpha():
                    count_zh += 1
                # Special Character
                else:
                    count_pu += 1
        else:
            for s in str:
                # English
                if s in string.ascii_letters:
                    count_en += 1
                # digital
                elif s.isdigit():
                    count_dg += 1
                # space
                elif s.isspace():
                    count_sp += 1
                # Chinese
                elif s.isalpha():
                    count_zh += 1
                # Special Character
                else:
                    count_pu += 1

        return count_zh
