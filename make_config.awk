#!/usr/bin/awk -f
# 用于生成host.cfg文件，初始化文件格式如下:
# 主机名 域名 用户名 IP 密码 端口
# [host123]
# domain = mdb
# host = 10.232.29.198
# port = 22
# user = billapp
# password = QXNpYUAxMjMK
# workdir = /home/billapp
BEGIN{
}
{
    if(FNR==1 && ($1=="help" || $1==""))
    {
        print "# 用于生成host.cfg文件，请先初始化文件init.txt格式如下:"
        print "主机名    域名 用户名    IP           密码   端口"
        print "centos01 mdb billmdb 192.168.1.2 temp123 22022"
        print "运行./make_config.awk init.txt > host.cfg"
        print "cat host.cfg,内容示例如下："
        print "[host123]"
        print "domain = mdb"
        print "host = 10.232.29.198"
        print "port = 22"
        print "user = billapp"
        print "password = QXNpYUAxMjMK"
        print "workdir = /home/billapp"
        exit
    }
    print "["$1"]"
    print "domain = "$2
    print "host = "$4
    print "port = "$6
    print "user = "$3
    password_cmd = "echo  " $5 "|base64";
    password_cmd | getline password;
    close(password_cmd);
    print "password = "password;
    print "workdir = /home/"$3;
}
END{
}
