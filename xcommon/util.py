import os
import pwd
import sys
from xcommon.xconfig import *
import io
import chardet

class XUtil:
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

    @staticmethod
    def sanitised_input(prompt, type_=None, max_=None, min_=None, range_=None):
        prompt += "(q for escape):"
        if min_ is not None and max_ is not None and max_ < min_:
            raise ValueError("min_ must be smaller than max_.")

        while True:
            if type_ is not None:
                try:
                    ui = INPUT_(prompt)

                    if 'q' == ui:
                        break

                    ui = type_(ui)
                except ValueError:
                    print("the type must be:{0}".format(type_.__name__))
                    continue

            if max_ is not None and ui > max_:
                print("input must be smaller than {0}".format(max_))
            elif min_ is not None and ui < min_:
                print("input must be bigger than {0}".format(min_))
            elif range_ is not None and ui not in range_:
                if isinstance(range_, range):
                    template = "input must between:{0.start} and {0.stop}"
                    print(template.format(range_))
                else:
                    template = "input must be:{0}"
                if len(range_) == 1:
                    print(template.format(*range_))
                else:
                    print(
                        template.format(" or ".join(
                            (", ".join(map(str,
                                           range_[:-1])), str(range_[-1])))))
            else:
                return ui

    # decode output, using perline mode for mixed encode.
    @staticmethod
    def decode_msg(in_msg):
        if chardet.detect(in_msg)['encoding'] == 'ascii':
            msg = io.StringIO(in_msg.decode())
        else:
            msg = io.StringIO(in_msg.decode("unicode_escape"))
        output_msg = ""
        while True:
            line = msg.readline().encode('ISO-8859-1')
            if len(line) == 0:  # Zero length indicates EOF
                break
            d = chardet.detect(line)
            if d['encoding'] == 'GB2312':
                output_msg = output_msg + line.decode('gb18030')
            elif d['encoding'] == 'utf-8':
                output_msg = output_msg + line.decode('utf-8')
            elif d['encoding'] == 'ISO-8859-9':
                output_msg = output_msg + line.decode('gb18030')
            elif d['encoding'] == 'ISO-8859-1':
                output_msg = output_msg + line.decode('gb18030')
            elif d['encoding'] == 'TIS-620':
                output_msg = output_msg + line.decode('gb18030')
            elif d['encoding'] == 'ascii':
                output_msg = output_msg + line.decode('ascii')
            else:
                print(line)
                output_msg = output_msg + line.decode('unicode_escape').encode(
                    'ISO-8859-1').decode("utf-8", 'ignore')
        return output_msg
