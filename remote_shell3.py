#!/usr/bin/env python3.10
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

import glob
import sys
import cmd
import subprocess
import os
import base64
import termios
import struct
import fcntl
import socket
from collections import Counter
from collections import defaultdict
import readline
import pexpect
from xcommon.xconfig import *
from xcommon.util import XUtil


# todo add set variable to save domain, check host.cfg is existed while set domain.
# todo add set variable to save host
# todo show domain host


class RemoteShell(cmd.Cmd):
    """
    remote shell
    """

    def __init__(self, host):
        cmd.Cmd.__init__(self)
        # self.intro = '''Enter \"help\" for instructions'''
        self.secs = 1.0
        self.count = 3
        self.his = []
        self.host_name = socket.gethostname()
        self.host = host
        self.config_file = XUtil.get_host("host.cfg")
        # self.config_file = sys.path[0]+'/host.cfg'
        self.domain = "all"
        self.prompt = f"\033[36;1m{self.host_name} \033[32;1m{self.domain} {self.host}\033[36;1m remote shell\033[0m#"
        self.map_domain_host = defaultdict(list)
        self.histfile = os.path.expanduser("~/.remote_shell_history")
        self.histfile_size = 1000

        self.refresh_menu()

    def quit(self):
        """
        quit
        """
        try:
            self.quit()
        except:
            pass

    def do_prompt(self, line):
        '''Set command prompt, eg. \"prompt remote shell\"'''
        self.prompt = f"\033[36;1m{self.host_name} \033[32;1m{self.domain} {self.host}\033[36;1m remote shell\033[0m#"

    def do_EOF(self, line):
        """Exit remote_shell.py with EOF."""
        # print
        return 1

    def preloop(self):
        if os.path.exists(self.histfile):
            readline.read_history_file(self.histfile)

    def postloop(self):
        readline.set_history_length(self.histfile_size)
        readline.write_history_file(self.histfile)

    # 采用按块显示的方式，每个块固定BLOCK_NUM决定块里有多个主机，默认为10条
    def refresh_menu(self):
        """
        refresh menu
        """
        self.cfg = XConfigParser(allow_no_value=True)
        self.cfg.read(self.config_file)

        self.map_domain_host.clear()
        domaintmp = []
        self.map_login = {}
        for i in self.cfg.sections():
            # print self.cfg.options(i)
            if i == "global":
                self.lang = self.cfg.get(i, "LANG")
                continue
            for j in self.cfg.options(i):
                # print self.cfg.get(i,j)
                if j == "domain":
                    domaintmp.append(self.cfg.get(i, j))
                    self.map_domain_host[self.cfg.get(i, j)].append(i)
            #! 支持按IP进行登录跳转
            self.map_login[self.cfg.get(i, "user") + "@" + self.cfg.get(i, "host")] = i
            self.map_login[self.cfg.get(i, "host") + "@" + self.cfg.get(i, "user")] = i
            self.map_login[self.cfg.get(i, "host")] = i

        # print self.map_domain_host
        self.domain_list = Counter(domaintmp)
        # print(self.domain_list)
        # for a,b in self.domain_list.items():
        #    print a, "to", b
        # for c,d in sorted(self.domain_list.iteritems(),key=lambda dict:dict[1],reverse=True):
        #    print c, "to=>", d

        print("*" + "*" * (COLUMN_WIDTH + 1) * COLUMN_NUM)
        # print("*"+"{0: ^{1}}".format("welcome to use scripts for remoting login",
        #       (COLUMN_WIDTH+1)*COLUMN_NUM-1)+"*")  # {}内嵌{}
        print(
            f"*{'welcome to use scripts for remoting login':^{(COLUMN_WIDTH + 1) * COLUMN_NUM - 1}}*"
        )
        print("*" + "*" * (COLUMN_WIDTH + 1) * COLUMN_NUM)

        hostlist = []
        # for d,h in sorted(self.domain_list.iteritems(),key=lambda dict:dict[1],reverse=False):   #domain, 按主机数量增序排列
        # domain, 按主机数量增序排列
        for d, h in sorted(
            self.domain_list.items(), key=lambda dict: dict[0], reverse=False
        ):
            if self.domain != "all" and d != self.domain:
                continue
            i_num = 0

            for i in sorted(self.map_domain_host[d]):
                if i_num % BLOCK_NUM == 0:
                    # {: ^38}, 38宽度补空格对齐
                    hostlist.append(
                        f"*\033[32;1m{d:^{COLUMN_WIDTH-XUtil.str_count(d)}}\033[0m"
                    )
                    hostlist.append(f"*{' -'*(int(COLUMN_WIDTH/2)): ^{COLUMN_WIDTH}}")
                    hostlist.append(
                        "*"
                        + f" {'HOST.NO': <{HOST_WIDTH-1}}{'用户': <{USER_WIDTH-XUtil.str_count('用户')}}{'IP列表': <{IP_WIDTH-XUtil.str_count('IP列表')}}"
                    )
                str1 = (
                    "*"
                    + f" \033[36;1m{i[:HOST_WIDTH-2]: <{HOST_WIDTH-1}}\033[0m{self.cfg.get(i, 'user')[:USER_WIDTH-1]:<{USER_WIDTH}}{self.cfg.get(i, 'host')[:IP_WIDTH-1]: <{IP_WIDTH}}"
                )
                hostlist.append(str1)  # host
                i_num = i_num + 1
                if i_num % BLOCK_NUM == 0:
                    hostlist.append("*" + "*" * COLUMN_WIDTH)

            while (i_num % BLOCK_NUM) != 0:  # 补足BLOCK_NUM
                hostlist.append("*" + f"{' ': ^{COLUMN_WIDTH}}")
                i_num = i_num + 1

            if (
                h % BLOCK_NUM != 0
            ):  # 不是BLOCK_NUM的倍数时，才需要补一行:"*"+"*"*COLUMN_WIDTH
                hostlist.append("*" + "*" * COLUMN_WIDTH)

        # 补足COLUMN_NUM的倍数的数据块, 其中为固定字符的4行
        i_block_num = (len(hostlist) / (BLOCK_NUM + 4)) % COLUMN_NUM
        while i_block_num % COLUMN_NUM != 0:
            # {: ^38}, 38宽度补空格对齐
            hostlist.append("*" + f"{' ': ^{COLUMN_WIDTH}}")
            hostlist.append("*" + f"{' -' *(int(COLUMN_WIDTH/2)): ^{COLUMN_WIDTH}}")
            hostlist.append(
                "*"
                + f" {'HOST.NO': <{HOST_WIDTH-1}}{'用户': ^{USER_WIDTH-XUtil.str_count('用户')}}{'IP列表': ^{IP_WIDTH-XUtil.str_count('IP列表')}}"
            )
            hostlist.append("*" + f"{' ': ^{COLUMN_WIDTH}}")
            i_num1 = 1
            while i_num1 % BLOCK_NUM != 0:  # 补足BLOCK_NUM
                hostlist.append("*" + f"{' ': ^{COLUMN_WIDTH}}")
                i_num1 = i_num1 + 1
            hostlist.append("*" + "*" * COLUMN_WIDTH)
            i_block_num = i_block_num + 1

        #    array1[d] = hostlist
        # print hostlist
        hostlist_size = len(hostlist)
        for layer in range(int(hostlist_size / COLUMN_NUM / (BLOCK_NUM + 4))):  # 层
            for i in range(BLOCK_NUM + 4):  # 列
                line = ""
                for j in range(COLUMN_NUM):  # 行
                    line = (
                        line
                        + hostlist[
                            layer * COLUMN_NUM * (BLOCK_NUM + 4)
                            + (BLOCK_NUM + 4) * j
                            + i
                        ]
                    )
                # if(line != ("*"+"{0: ^{1}}".format(" ", COLUMN_WIDTH))*COLUMN_NUM):  # 空行
                if line != ("*" + f"{' ': ^{COLUMN_WIDTH}}") * COLUMN_NUM:  # 空行
                    print(line + "*")
        help_txt = []
        temp_hint = " 帮  助 $  输入HOST.NO,登录对应主机"
        # 10为里面包含了10个汉字
        help_txt.append(f"{temp_hint: <{COLUMN_WIDTH -XUtil.str_count(temp_hint)}}")
        temp_hint = " exit: 退出 | set domain: 切换主机域"
        # 7为里面包含了7个汉字
        help_txt.append(f"{temp_hint: <{COLUMN_WIDTH -XUtil.str_count(temp_hint)}}")
        for i in range(COLUMN_NUM - 3):  # 前面的两行help
            help_txt.append(" " * COLUMN_WIDTH)
            i = i + 1
        help_line = "*"
        # n = 0
        for l in help_txt:
            help_line = help_line + f"{l: <{COLUMN_WIDTH-20}}"
            help_line = help_line + "|"
        help_line += f" 当前域：\033[31;1m{self.domain: <10} {self.host: >15}\033[0m"
        help_line += " " * (COLUMN_WIDTH - 35 - XUtil.str_count(self.domain)) + "*"
        print(help_line)

        print("*" + "*" * (COLUMN_WIDTH + 1) * COLUMN_NUM)
        self.prompt = f"\033[33;1m{self.host_name} \033[32;1m{self.domain} {self.host}\033[36;1m remote shell\033[0m#"

    def emptyline(self):
        self.refresh_menu()
        self.quit()
        # pass

    def do_exit(self, line):
        """Exit remote_shell.py."""
        self.quit()
        return True

    def do_bye(self, line):
        """Exit remote_shell.py."""
        self.quit()
        return True

    def do_vl(self, line):
        """Edit config file."""
        os.system("vi " + self.config_file)
        self.quit()
        return True

    # add_cfg
    def do_set(self, line):
        """add config."""
        return self.config_host(ENCRYPT_PASSWORD_MODE)

    # add_cfg
    def do_enset(self, line):
        """add encrypted config."""
        return self.config_host(DECRYPT_PASSWORD_MODE)

    # add_cfg
    def do_rmhost(self, line):
        """rm host."""
        return self.rm_host()

    # excute command for special domain
    def do_domain(self, line):
        """excute command for special domain.\neg. domain mdb\n    domain all\n    domain"""
        parse_temp = line.split()
        if len(parse_temp) == 0:
            self.domain = "all"
            self.host = ""
            self.refresh_menu()
            return False
        else:
            if parse_temp[0].lower() == "all":
                self.domain = "all"
                self.host = ""
                self.refresh_menu()
                return False
            for d, _ in sorted(
                self.domain_list.items(), key=lambda dict: dict[1], reverse=False
            ):
                if parse_temp[0].lower() == d.lower():
                    self.domain = d
                    self.host = ""
                    self.refresh_menu()
                    return False
            print(f"domain \033[31;1m{parse_temp[0]}\033[0m is not exists.")

        return False

    def complete_domain(self, text, line, begidx, endidx):
        completions_set = ["all"]

        mline = line.partition(" ")[-1]
        # domain, 按主机数量增序排列
        for d, _ in sorted(
            self.domain_list.items(), key=lambda dict: dict[1], reverse=False
        ):
            if self.domain != "all" and d != self.domain:
                completions_set.append(d)
                continue
            # i_num = 0
            completions_set.append(d)

        offs = len(mline) - len(text)
        return [s[offs:] for s in completions_set if s.startswith(mline)]

    # ----------------------------------------------------------------------
    # 新增：add 命令（一行添加完整主机信息）
    # 用法示例：
    # add mdb_benchmark benchmark01 10.21.15.100 22 aidb 123456 /data/aidb "-o MACs=hmac-sha2-256"
    # ----------------------------------------------------------------------
    def do_add(self, line):
        """Add a new host entry quickly.
        Usage: add <domain> <host_no> <ip> <port> <user> <password> <workdir> [ssh_param]
        """
        args = line.strip().split()
        if len(args) < 7:
            print(
                "Error: 参数不足，至少需要 7 个参数（domain host_no ip port user password workdir）"
            )
            return

        domain, host_no, ip, port, user, password, workdir = args[:7]
        ssh_param = " ".join(args[7:]) if len(args) > 7 else ""

        # 读取最新配置（防止在交互过程中被其他方式修改）
        self.cfg = XConfigParser(allow_no_value=True)
        self.cfg.read(self.config_file)

        if self.cfg.has_section(host_no):
            print(f"Error: host_no [{host_no}] 已存在！")
            return

        # 加密密码（保持原来加密方式）
        enpassword = base64.b64encode(password.encode("utf-8")).decode("utf-8")

        # 添加 section
        self.cfg.add_section(host_no)
        self.cfg.set(host_no, "domain", domain)
        self.cfg.set(host_no, "host", ip)
        self.cfg.set(host_no, "port", port)
        self.cfg.set(host_no, "user", user)
        self.cfg.set(host_no, "password", enpassword)
        self.cfg.set(host_no, "workdir", workdir)
        if ssh_param:
            self.cfg.set(host_no, "ssh_param", ssh_param)
        self.cfg.set(host_no, "serveraliveinterval", "0")  # 默认不开启 keepalive

        # 写回文件
        with open(self.config_file, "w", encoding="utf-8") as f:
            self.cfg.write(f)

        print(f"Success: 已成功添加主机 [{host_no}]（{ip}）")
        self.refresh_menu()  # 刷新菜单显示最新内容

    def help_add(self):
        print("快速添加主机")
        print(
            "add <domain> <host_no> <ip> <port> <user> <password> <workdir> [ssh_param]"
        )

    # ----------------------------------------------------------------------
    # delete 命令 + Tab 自动补全（完整版）
    # 用法：
    #   delete <host_no>                     # 直接删
    #   delete <domain> <host_no>            # 更安全，防止跨域误删
    # ----------------------------------------------------------------------
    def do_delete(self, line):
        """Delete a host entry.\nUsage:\n  delete <host_no>\n  delete <domain> <host_no>"""
        args = line.strip().split()
        if not args:
            print("Error: 请提供要删除的 host_no")
            return

        # 每次操作前都重新读取最新配置文件
        self.cfg = XConfigParser(allow_no_value=True)
        self.cfg.read(self.config_file)

        target = None

        if len(args) == 1:
            # 只提供 host_no，直接按 section 名删除（兼容老习惯）
            host_no = args[0]
            if not self.cfg.has_section(host_no):
                print(f"Error: 未找到 host_no [{host_no}]")
                return
            target = host_no

        else:
            # 提供 domain + host_no，精准匹配
            domain, host_no = args[0], args[1]
            found = False
            for sec in self.cfg.sections():
                if (
                    self.cfg.has_option(sec, "domain")
                    and self.cfg.get(sec, "domain") == domain
                    and sec == host_no
                ):
                    target = sec
                    found = True
                    break
            if not found:
                print(f"Error: 在 domain [{domain}] 中未找到 host_no [{host_no}]")
                return

        if input(f"Confirm: 确认删除主机 [{target}] ? (y/N): ").lower() != "y":
            print("已取消删除")
            return

        self.cfg.remove_section(target)
        with open(self.config_file, "w", encoding="utf-8") as f:
            self.cfg.write(f)

        print(f"Success: 已成功删除主机 [{target}]")
        self.refresh_menu()

    def help_delete(self):
        print("删除主机配置")
        print("delete <host_no>")
        print("delete <domain> <host_no>   # 推荐，更安全")

    # ----------------------------------------------------------------------
    # delete 命令的 Tab 补全（完全参考 complete_domain 的写法）
    # ----------------------------------------------------------------------
    def complete_delete(self, text, line, begidx, endidx):
        """
        Tab completion for delete command
        - delete <TAB>          → list all domains
        - delete mdb<TAB>       → list host_no under domain "mdb..."
        - delete mdb_benchmark <TAB> → list host_no in this domain
        - delete bench<TAB>     → also list matching host_no directly (single-arg mode)
        """
        args = line.split()
        completions = []

        # 还没输入任何参数 → 补全 domain（和 domain 命令完全一致）
        if len(args) == 1 or (len(args) == 2 and not line.endswith(" ")):
            # 第一个参数：补全 domain
            for d in self.domain_list.keys():
                if d.startswith(text):
                    completions.append(d)
            # 同时也支持直接输入 host_no（单参数模式）
            if not text.startswith("all"):
                for sec in self.cfg.sections():
                    if sec.startswith(text):
                        completions.append(sec)
            return completions

        # 已经输入了 domain（两个参数的情况）
        if len(args) >= 2:
            domain = args[1]  # delete <domain> ...
            if domain in self.map_domain_host:
                for host_no in self.map_domain_host[domain]:
                    if host_no.startswith(text):
                        completions.append(host_no)

        # 当用户在第一参数已经敲了一部分 host_no 时，也要能补全（单参数写法）
        if len(args) == 2 and not line.endswith(" "):
            for sec in self.cfg.sections():
                if sec.startswith(text):
                    completions.append(sec)

        return completions

    # ----------------------------------------------------------------------
    # modify 命令 + Tab 自动补全
    # 用法：
    #   modify <host_no>                    # 交互式修改所有字段
    #   modify <host_no> <field> <value>    # 直接修改指定字段
    # 支持字段: domain, host, port, user, password, workdir, ssh_param, serveraliveinterval
    # ----------------------------------------------------------------------
    def do_modify(self, line):
        """Modify a host entry.
        Usage:
          modify <host_no>                      # 交互式修改
          modify <host_no> <field> <value>      # 直接修改指定字段

        支持的字段: domain, host, port, user, password, workdir, ssh_param, serveraliveinterval
        """
        args = line.strip().split(maxsplit=2)  # 最多分3段
        if not args:
            print("Error: 请提供要修改的 host_no")
            return

        # 重新读取最新配置
        self.cfg = XConfigParser(allow_no_value=True)
        self.cfg.read(self.config_file)

        host_no = args[0]
        if not self.cfg.has_section(host_no):
            print(f"Error: 未找到 host_no [{host_no}]")
            return

        # 支持的字段列表
        valid_fields = [
            "domain",
            "host",
            "port",
            "user",
            "password",
            "workdir",
            "ssh_param",
            "serveraliveinterval",
        ]

        # 模式1: modify <host_no> <field> <value> - 直接修改
        if len(args) == 3:
            field = args[1].lower()
            value = args[2]

            if field not in valid_fields:
                print(f"Error: 不支持的字段 [{field}]")
                print(f"支持的字段: {', '.join(valid_fields)}")
                return

            # 如果是密码字段,需要加密
            if field == "password":
                value = base64.b64encode(value.encode("utf-8")).decode("utf-8")

            self.cfg.set(host_no, field, value)
            with open(self.config_file, "w", encoding="utf-8") as f:
                self.cfg.write(f)

            print(f"Success: 已成功修改 [{host_no}] 的 {field} 字段")
            self.refresh_menu()
            return

        # 模式2: modify <host_no> - 交互式修改
        print(f"修改主机配置: [{host_no}]")
        print("提示: 直接按回车保持原值不变")
        print("-" * 50)

        # 显示当前值并获取新值
        new_values = {}
        for field in valid_fields:
            if self.cfg.has_option(host_no, field):
                current_value = self.cfg.get(host_no, field)
                # 密码字段显示为 ***
                display_value = "***" if field == "password" else current_value
            else:
                current_value = ""
                display_value = "(未设置)"

            new_value = input(f"{field} [{display_value}]: ").strip()

            # 如果用户输入了新值,则记录
            if new_value:
                # 密码需要加密
                if field == "password":
                    new_value = base64.b64encode(new_value.encode("utf-8")).decode(
                        "utf-8"
                    )
                new_values[field] = new_value

        # 确认修改
        if not new_values:
            print("未做任何修改")
            return

        print("\n将要修改的字段:")
        for field, value in new_values.items():
            display_value = "***" if field == "password" else value
            print(f"  {field}: {display_value}")

        if input("\n确认修改? (y/N): ").lower() != "y":
            print("已取消修改")
            return

        # 应用修改
        for field, value in new_values.items():
            self.cfg.set(host_no, field, value)

        with open(self.config_file, "w", encoding="utf-8") as f:
            self.cfg.write(f)

        print(f"Success: 已成功修改主机 [{host_no}]")
        self.refresh_menu()

    def help_modify(self):
        print("修改主机配置")
        print("modify <host_no>                      # 交互式修改")
        print("modify <host_no> <field> <value>      # 直接修改指定字段")
        print(
            f"支持的字段: domain, host, port, user, password, workdir, ssh_param, serveraliveinterval"
        )

    # ----------------------------------------------------------------------
    # modify 命令的 Tab 补全
    # ----------------------------------------------------------------------
    def complete_modify(self, text, line, begidx, endidx):
        """
        Tab completion for modify command
        - modify <TAB>                → list all host_no
        - modify host01 <TAB>         → list all fields
        - modify host01 domain <TAB>  → list all domains
        """
        args = line.split()
        completions = []

        # 第一个参数: 补全 host_no
        if len(args) == 1 or (len(args) == 2 and not line.endswith(" ")):
            for sec in self.cfg.sections():
                if sec != "global" and sec.startswith(text):
                    completions.append(sec)
            return completions

        # 第二个参数: 补全字段名
        if len(args) == 2 or (len(args) == 3 and not line.endswith(" ")):
            valid_fields = [
                "domain",
                "host",
                "port",
                "user",
                "password",
                "workdir",
                "ssh_param",
                "serveraliveinterval",
            ]
            for field in valid_fields:
                if field.startswith(text):
                    completions.append(field)
            return completions

        # 第三个参数: 如果是 domain 字段,补全已有的 domain
        if len(args) >= 3:
            field = args[2]
            if field == "domain":
                for d in self.domain_list.keys():
                    if d.startswith(text):
                        completions.append(d)

        return completions

    # 重写cmd类的completedefault
    def completedefault(self, text, line, begidx, endidx):
        return self.completenames(text, line, begidx, endidx)

    # 重写cmd类的completenames
    def completenames(self, path, line, begidx, endidx):
        # print("path={0}, line={1}, begidx={2}, endidx={3}".format(path, line, begidx, endidx))
        # if path == "":
        #    dotext = 'do_'+ path
        #    return [a[3:] for a in self.get_names() if a.startswith(dotext)]
        completions = []
        commands = [
            "prompt",
            "EOF",
            "exit",
            "bye",
            "vl",
            "set",
            "enset",
            "rmhost",
            "domain",
            "add",
            "delete",
            "modify",
            "show",
            "showpass",
            "refresh",
            "quit",
            "by",
            "q",
            "shell",
            "run",
            "help",
        ]
        if line == "":
            completions = commands
            return completions

        if path.partition(" ")[-1] == "" and len(line.split(" ")) == 1:
            # domain, 按主机数量增序排列
            for d, _ in sorted(
                self.domain_list.items(), key=lambda dict: dict[1], reverse=False
            ):
                if self.domain != "all" and d != self.domain:
                    continue
                # i_num = 0
                # completions.append("domain "+d)
                for i in self.map_domain_host[d]:
                    if i.startswith(path):
                        completions.append(i)

                for k, _ in self.map_login.items():
                    if k.startswith(path):
                        completions.append(k)

            for i in commands:
                if i.startswith(path):
                    completions.append(i)

        if path[0] == "~":
            path = os.path.expanduser("~") + path[1:]
        if os.path.isdir(path):
            return glob.glob(os.path.join(path, "*"))
        completions = completions + glob.glob(path + "*")

        if len(completions) == 0:  # 不是目录文件的情况下，返回候选命令
            bin_path = os.environ.get("PATH").split(":")
            for i in bin_path:
                completions = completions + [
                    (s.split("/"))[-1] for s in glob.glob(i + "/" + path + "*")
                ]
        return completions

    # def _complete_path(self, path, line, start_idx, end_idx):
    def _complete_path(self, path, start_idx, end_idx):
        if path[0] == "~":
            path = os.path.expanduser("~") + path[1:]
        if os.path.isdir(path):
            return glob.glob(os.path.join(path, "*"))
        completions = glob.glob(path + "*")

        if len(completions) == 0:  # 不是目录文件的情况下，返回候选命令
            bin_path = os.environ.get("PATH").split(":")
            for i in bin_path:
                completions = completions + [
                    (s.split("/"))[-1] for s in glob.glob(i + "/" + path + "*")
                ]
        return completions

    def do_show(self, line):
        """show the domain and host information, eg. show."""
        print(f"domain={self.domain}, host={self.host}\n")
        return False

    # ----------------------------------------------------------------------
    # showpass 命令 - 显示主机密码
    # 用法：
    #   showpass <host_no>              # 显示指定主机的密码
    #   showpass <host_no> --all        # 显示主机的所有配置信息(包括密码)
    # ----------------------------------------------------------------------
    def do_showpass(self, line):
        """Show host password.
        Usage:
          showpass <host_no>              # 显示指定主机的密码
          showpass <host_no> --all        # 显示主机的所有配置信息"""
        args = line.strip().split()
        if not args:
            print("Error: 请提供要查看的 host_no")
            print("用法: showpass <host_no> [--all]")
            return

        # 重新读取最新配置
        self.cfg = XConfigParser(allow_no_value=True)
        self.cfg.read(self.config_file)

        host_no = args[0]
        if not self.cfg.has_section(host_no):
            print(f"Error: 未找到 host_no [{host_no}]")
            return

        show_all = len(args) > 1 and args[1] == "--all"

        # 获取密码并解密
        if self.cfg.has_option(host_no, "password"):
            password_encrypted = self.cfg.get(host_no, "password")

            # 判断是否是文件路径(pem文件)
            if os.path.isfile(password_encrypted):
                password_display = f"[PEM文件] {password_encrypted}"
            else:
                # base64解密
                try:
                    password_decrypted = base64.b64decode(password_encrypted).decode(
                        "utf-8"
                    )
                    password_display = password_decrypted
                except Exception as e:
                    password_display = f"[解密失败] {str(e)}"
        else:
            password_display = "(未设置)"

        if show_all:
            # 显示所有配置信息
            print(f"\n{'='*60}")
            print(f"主机配置信息: [{host_no}]")
            print(f"{'='*60}")

            fields = [
                "domain",
                "host",
                "port",
                "user",
                "password",
                "workdir",
                "ssh_param",
                "serveraliveinterval",
            ]
            for field in fields:
                if self.cfg.has_option(host_no, field):
                    value = self.cfg.get(host_no, field)
                    if field == "password":
                        # 显示解密后的密码
                        if os.path.isfile(value):
                            display_value = f"[PEM文件] {value}"
                        else:
                            try:
                                display_value = base64.b64decode(value).decode("utf-8")
                            except:
                                display_value = "[解密失败]"
                    else:
                        display_value = value
                    print(f"  {field:20s}: {display_value}")
                else:
                    print(f"  {field:20s}: (未设置)")
            print(f"{'='*60}\n")
        else:
            # 只显示密码
            print(f"\n主机: [{host_no}]")
            print(f"密码: {password_display}\n")

        return False

    def help_showpass(self):
        print("显示主机密码")
        print("showpass <host_no>              # 显示指定主机的密码")
        print("showpass <host_no> --all        # 显示主机的所有配置信息")

    # ----------------------------------------------------------------------
    # showpass 命令的 Tab 补全
    # ----------------------------------------------------------------------
    def complete_showpass(self, text, line, begidx, endidx):
        """
        Tab completion for showpass command
        - showpass <TAB>          → list all host_no
        - showpass host01 <TAB>   → suggest --all option
        """
        args = line.split()
        completions = []

        # 第一个参数: 补全 host_no
        if len(args) == 1 or (len(args) == 2 and not line.endswith(" ")):
            for sec in self.cfg.sections():
                if sec != "global" and sec.startswith(text):
                    completions.append(sec)
            return completions

        # 第二个参数: 补全 --all 选项
        if len(args) == 2 or (len(args) == 3 and not line.endswith(" ")):
            if "--all".startswith(text):
                completions.append("--all")
            return completions

        return completions

    def do_quit(self, line):
        """Exit remote_shell.py."""
        self.quit()
        return True

    def do_by(self, line):
        """Exit remote_shell.py."""
        self.quit()
        return True

    def do_q(self, line):
        """Exit remote_shell.py."""
        self.quit()
        return True

    # ----------------------------------------------------------------------
    # refresh 命令 - 刷新菜单
    # 用法：
    #   refresh                         # 重新加载配置文件并刷新菜单显示
    # ----------------------------------------------------------------------
    def do_refresh(self, line):
        """Refresh menu and reload host.cfg.
        Usage:
          refresh                           # 重新加载配置文件并刷新菜单"""
        print("正在刷新菜单,重新加载配置文件...")
        try:
            self.refresh_menu()
            print("\n✓ 菜单刷新成功!")
        except Exception as e:
            print(f"\n✗ 菜单刷新失败: {str(e)}")
        return False

    def help_refresh(self):
        print("刷新菜单并重新加载配置文件")
        print("refresh                           # 重新加载 host.cfg 并刷新菜单显示")

    def onecmd(self, line):
        """Execute the rest of the line as a shell command, eg. \'!ls\', \'shell pwd\'."""
        if (
            line == ""
            or line == "bye"
            or line == "exit"
            or line == "by"
            or line == "quit"
            or line.startswith("help")
            or line == "EOF"
            or line.startswith("shell")
            or line.startswith("run")
            or line.startswith("show")
            or line == "q"
            or line == "set"
            or line == "enset"
            or line == "vl"
            or line == "rmhost"
            or line.startswith("domain")
            or line.startswith("add")
            or line.startswith("delete")
            or line.startswith("modify")
            or line.startswith("showpass")
            or line.startswith("refresh")
        ):
            return cmd.Cmd.onecmd(self, line)
        line = line.strip()
        if line in self.cfg.sections():
            self.remote_interactive(line)
            return
        if line in self.map_login:
            self.remote_interactive(self.map_login[line])
            return
        if line != "" and line[0] == "!":
            if len(line) > 2 and line[1:3] == "vi":
                print("can't support !vi or !vim")
                return False
            command = subprocess.Popen(line[1:], shell=True, stdout=subprocess.PIPE)
            print(command.communicate()[0], end=" ")
            return False

        if len(line) > 1 and line[0:2] == "vi":
            print("can't support vi or vim. Interactive command is so on.")
            return False
        self.remote_cmd(line)
        # pass

    def do_shell(self, line):
        """Execute the rest of the line as a shell command, eg. \'!ls\', \'shell pwd\'.
        ! for localhost, shell or none for remote host."""
        # 判断输入是非为HOST.NO
        if line in self.cfg.sections():
            self.remote_interactive(line)
            return
        self.remote_cmd(line)

    # tab自动补齐shell命令的参数
    def complete_shell(self, text, line, start_idx, end_idx):
        """
        complete shell
        """
        return self._complete_path(text, line, start_idx, end_idx)

    def do_run(self, line):
        """Execute the rest of the line as a shell command, eg. \'run ls\', \'run pwd\'."""
        self.remote_cmd(line)

    # def sigwinch_passthrough (sig, data):
    #    winsize = self.getwinsize()
    #    global child
    #    child.setwinsize(winsize[0],winsize[1])

    def getwinsize(self):
        """This returns the window size of the child tty.
        The return value is a tuple of (rows, cols).
        """
        # if 'TIOCGWINSZ' in dir(termios):
        #     TIOCGWINSZ = termios.TIOCGWINSZ
        # else:
        #     # TIOCGWINSZ = 1074295912L # Assume
        #     TIOCGWINSZ = 1074295912  # Assume
        s = struct.pack("HHHH", 0, 0, 0, 0)
        x = fcntl.ioctl(
            sys.stdout.fileno(),
            termios.TIOCGWINSZ if "TIOCGWINSZ" in dir(termios) else 1074295912,
            s,
        )
        return struct.unpack("HHHH", x)[0:2]

    def remote_interactive(self, host):
        """remote interactive"""
        if os.path.isfile(self.cfg.get(host, "password")):
            self.remote_interactive_pem(host)
        else:
            self.remote_interactive_passwd(host)

    def remote_interactive_passwd(self, host):
        """remote interactive by password"""
        user = self.cfg.get(host, "user")
        password = self.cfg.get(host, "password")
        ip = self.cfg.get(host, "host")
        port = self.cfg.get(host, "port")
        ssh_param = self.cfg.get(host, "ssh_param")
        if ssh_param is None:
            ssh_param = ""
        serveraliveinterval = self.cfg.get(host, "serveraliveinterval")
        serveraliveinterval_opt = (
            ""
            if serveraliveinterval == "0" or serveraliveinterval is None
            else " -o TCPKeepAlive=yes -o ServerAliveInterval=" + serveraliveinterval
        )
        str_cmd = (
            f"ssh {serveraliveinterval_opt} -o PubkeyAuthentication=no "
            f"{ssh_param} "
            f"-o StrictHostKeyChecking=no -p {port} {user}@{ip}"
        )
        print(str_cmd)
        child = pexpect.spawn(str_cmd)
        # signal.signal(signal.SIGWINCH, self.sigwinch_passthrough)
        winsize = self.getwinsize()
        child.setwinsize(winsize[0], winsize[1])
        try:
            child.expect("(!*)(P|p)assword:(!*)")
            # base64解码后多一个回车键符，需要剪掉一位
            _ = child.sendline(base64.b64decode(password))
        except pexpect.EOF:
            print(f"can not connect to {host}")
            if child.isalive():
                child.close(force=True)
            return
        except pexpect.TIMEOUT:
            print(f"connect timeout {host}")
            if child.isalive():
                child.close(force=True)
            return

        child.interact()
        child.expect(pexpect.EOF)
        child.close(force=True)

    def remote_interactive_pem(self, host):
        """remote interactive by pem file"""
        user = self.cfg.get(host, "user")
        password = self.cfg.get(host, "password")
        ip = self.cfg.get(host, "host")
        # port = self.cfg.get(host, "port")
        serveraliveinterval = self.cfg.get(host, "serveraliveinterval")
        serveraliveinterval_opt = (
            " "
            if serveraliveinterval == "0" or serveraliveinterval is None
            else " -o TCPKeepAlive=yes -o ServerAliveInterval=" + serveraliveinterval
        )
        str_cmd = f"ssh {serveraliveinterval_opt} -o PubkeyAuthentication=yes -o StrictHostKeyChecking=no -i {password} {user}@{ip}"
        print(str_cmd)
        child = pexpect.spawn(str_cmd)
        # signal.signal(signal.SIGWINCH, self.sigwinch_passthrough)
        winsize = self.getwinsize()
        child.setwinsize(winsize[0], winsize[1])
        # try:
        #     child.expect('(!*)(P|p)assword:(!*)')
        #     # base64解码后多一个回车键符，需要剪掉一位
        #     _ = child.sendline(base64.b64decode(password))
        # except pexpect.EOF:
        #     print("can not connect to {}".format(host))
        #     if child.isalive():
        #         child.close(force=True)
        #     return
        # except pexpect.TIMEOUT:
        #     print("connect timeout {}".format(host))
        #     if child.isalive():
        #         child.close(force=True)
        #     return

        child.interact()
        child.expect(pexpect.EOF)
        child.close(force=True)

    def remote_cmd(self, line):
        """
        remote command
        """
        line = (
            line.replace('"', '\\"')
            .replace("$", "\\$")
            .replace("'", "\\'")
            .replace("`", "\\`")
        )
        line = '"' + line + '"'
        # print "line:{0}".format(line)
        if self.host != "":
            sz_cmd = (
                f"{os.path.dirname(os.path.realpath(__file__))}/remote_cmd3.py "
                f"--domain {self.domain} --ip {self.host} {line}"
            )
        else:
            sz_cmd = (
                f"{os.path.dirname(os.path.realpath(__file__))}/remote_cmd3.py "
                f"--domain {self.domain} {line}"
            )
        # print(szCmd)
        command = subprocess.Popen(
            sz_cmd, shell=True, stdout=subprocess.PIPE, universal_newlines=True
        )
        while 1:
            out = command.stdout.readline()
            if out == "":
                break
            print(out.strip())
        command.stdout.close()

    def config_host(self, opt):
        """Config the host file"""
        print("Config the host file:" + self.config_file)
        host_no = input("Input your host_no: ")
        # section already exists return
        if self.cfg.has_section(host_no):
            print("host_no:" + host_no + " already exists!")
            return

        # get userinput
        domain = input("Input your domain: ")
        host = input("Input your host: ")
        port = input("Input your port: ")
        user = input("Input your user: ")
        password = input("Input your password: ")
        serveraliveinterval = input("keep server alive second: ")

        # encrypt password
        if ENCRYPT_PASSWORD_MODE == opt:
            # enpassword = subprocess.getoutput("echo " + password + "|base64")
            enpassword = base64.b64encode(password.encode("utf-8")).decode("utf-8")
        else:
            enpassword = password
        workdir = input("Input your workdir: ")

        print(
            "[" + host_no + "]"
            "\r\ndomain = "
            + domain
            + "\r\nhost = "
            + host
            + "\r\nport = "
            + port
            + "\r\nuser = "
            + user
            + "\r\npassword = "
            + enpassword
            + "\r\nserveraliveinterval = "
            + serveraliveinterval
            + "\r\nworkdir = "
            + workdir
        )
        if "y" == input("confirm the config to be saved.(y/n):"):
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
            with open(self.config_file, "w+", encoding="utf-8") as f:
                self.cfg.write(f)
            self.emptyline()

    def rm_host(self):
        """rm the host_no cofig"""
        host_no = input("Input the host_no you want to rm: ")
        # section not exists return
        if not self.cfg.has_section(host_no):
            print("host_no:" + host_no + " not exists!")
            return
        self.cfg.remove_section(host_no)
        # write to file
        with open(self.config_file, "w+", encoding="utf-8") as f:
            self.cfg.write(f)
        self.emptyline()


if __name__ == "__main__":
    #! for add current dir to LD_LIBRARY_PATH environment
    import platform

    # * 这里有一个问题用#!/usr/bin/env python3时，macos操作系统下环境变量变更os.execve会不生效
    if platform.system() == "Linux":
        if os.path.dirname(os.path.realpath(__file__)) not in os.environ.get(
            "LD_LIBRARY_PATH"
        ):
            os.environ["LD_LIBRARY_PATH"] = (
                os.environ.get("LD_LIBRARY_PATH")
                + ":"
                + os.path.dirname(os.path.realpath(__file__))
            )
            os.execve(os.path.realpath(__file__), sys.argv, os.environ)  # * rerun

    readline.set_completer_delims(" \t\n")

    if len(sys.argv) > 2:
        print("usage:", sys.argv[0])
        print("usage:", sys.argv[0], "host")
    else:
        if len(sys.argv) == 2:
            client = RemoteShell(sys.argv[1])
        else:
            client = RemoteShell("")
        try:
            client.cmdloop()
        finally:
            client.quit()
