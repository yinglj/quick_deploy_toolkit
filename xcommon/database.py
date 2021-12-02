# -*- coding:utf-8 -*-
import json
import platform
import cx_Oracle as orcl
import pymysql
import os
import sys

if 2 == sys.version_info.major:
    defaultencoding = 'utf-8'
    if sys.getdefaultencoding() != defaultencoding:
        reload(sys)
        sys.setdefaultencoding(defaultencoding)


class XOracleHandle(object):
    def __init__(self, user, pwd, ip, port, sid):
        # print ("cx_Oracle.version:", orcl.version)
        dsn = orcl.makedsn(ip, port, sid)
        self.connect = orcl.connect(user, pwd, dsn)
        self.cursor = self.connect.cursor()

    def __del__(self):
        print("finally")
        self.cursor.close()
        self.connect.close()

    def select(self, sql):
        try:
            list = []
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            col_name = self.cursor.description
            for row in result:
                dict = {}
                for col in range(len(col_name)):
                    key = col_name[col][0]
                    value = row[col]
                    dict[key] = value
                list.append(dict)
            js = json.dumps(list, ensure_ascii=False,
                            indent=2, separators=(',', ':'))
            return js
        except Exception as e:
            print(e)
        # finally:
        #     self.disconnect()

    def insert(self, sql, list_param):
        try:
            self.cursor.executemany(sql, list_param)
            self.connect.commit()
        except Exception as e:
            print(e)

    def update(self, sql):
        try:
            self.cursor.execute(sql)
            self.connect.commit()

        except Exception as e:
            print(e)

    def delete(self, sql):
        try:
            self.cursor.execute(sql)
            self.connect.commit()
        except Exception as e:
            print(e)

    def executeSQL(self, sql):
        try:
            r = self.cursor.execute(sql)
            sqlRes = r.fetchall()
        except Exception as e:
            print("Excute sql error![MSG=%s,SQL=%s]" % (str(e), sql))
            return None
        return sqlRes


class XMysqlHandle(object):
    ''' 定义一个 MySQL 操作类'''

    def __init__(self, host, username, password, database, port):
        '''初始化数据库信息并创建数据库连接'''
        # 下面的赋值其实可以省略，connect 时 直接使用形参即可
        self.host = host
        self.username = username
        self.password = password
        self.database = database
        self.port = port
        self.db = pymysql.connect(
            self.host, self.username, self.password, self.database, self.port, charset='utf8')

    def __del__(self):
        ''' 数据库连接关闭 '''
        self.db.close()

    def insertDB(self, sql):
        ''' 插入数据库操作 '''
        self.cursor = self.db.cursor()
        try:
            # 执行sql
            self.cursor.execute(sql)
            # tt = self.cursor.execute(sql)  # 返回 插入数据 条数 可以根据 返回值 判定处理结果
            # print(tt)
            self.db.commit()
        except:
            # 发生错误时回滚
            self.db.rollback()
        finally:
            self.cursor.close()

    def deleteDB(self, sql):
        ''' 操作数据库数据删除 '''
        self.cursor = self.db.cursor()
        try:
            # 执行sql
            self.cursor.execute(sql)
            # tt = self.cursor.execute(sql) # 返回 删除数据 条数 可以根据 返回值 判定处理结果
            # print(tt)
            self.db.commit()
        except:
            # 发生错误时回滚
            self.db.rollback()
        finally:
            self.cursor.close()

    def updateDb(self, sql):
        ''' 更新数据库操作 '''
        self.cursor = self.db.cursor()
        try:
            # 执行sql
            self.cursor.execute(sql)
            # tt = self.cursor.execute(sql) # 返回 更新数据 条数 可以根据 返回值 判定处理结果
            # print(tt)
            self.db.commit()
        except:
            # 发生错误时回滚
            self.db.rollback()
        finally:
            self.cursor.close()

    def selectDb(self, sql):
        ''' 数据库查询 '''
        self.cursor = self.db.cursor()
        try:
            self.cursor.execute(sql)  # 返回 查询数据 条数 可以根据 返回值 判定处理结果
            data = self.cursor.fetchall()  # 返回所有记录列表
            print(data)

            # 结果遍历
            for row in data:
                sid = row[0]
                name = row[1]
                # 遍历打印结果
                print('sid = %s, name = %s' % (sid, name))
        except:
            print('Error: unable to fecth data')
        finally:
            self.cursor.close()

    def executeSQL(self, sql):
        self.cursor = self.db.cursor()
        try:
            self.cursor.execute(sql)  # 返回 查询数据 条数 可以根据 返回值 判定处理结果
            data = self.cursor.fetchall()  # 返回所有记录列表
        except:
            print('Error: unable to fecth data')
        finally:
            self.cursor.close()
        return data
