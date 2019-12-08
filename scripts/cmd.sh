#!/bin/bash
localip=`ifconfig -a|grep 'inet '|grep -v -w 192.168|grep -v -w 127.0.0.1|head -1|awk '{print $2}'|awk -F. '{printf("%d.%d.%d.%d",$1,$2,$3,$4)}'`
#echo $localip
ps -ef | grep mdb | grep odframe | awk '{print "grep server_port "$10";"}' | sh | awk -F "<|>" '{print "~/backup/mdb_client_onecmd.py "ip" "$3"  cmpak 123456 \"info all\""}' ip=$localip | sh > a.txt
//g" a.txt/
~/backup/mdb_table_check.awk a.txt