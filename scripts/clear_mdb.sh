#!/bin/sh

if test $# -ne 1; then
    echo "Usage: `basename $0` days-before
example: `basename $0` 3" 1>&2
    exit 1
fi

#限制只能删除两天前的文件，防止误操作
if test $1 -lt 2; then
    echo "days-before must bigger than 2."
    exit 1
fi

#取最新的mdbinfo.txt文件信息,这份文件不能删除
#cur=`find $1/data/mdb -mtime +$2 -type f -name "mdbinfo.txt" \
    #| xargs cat|head -n 1`

#find $HOME/mdb /data -maxdepth 1 -type d -name "*_mdb" \
    #| while read mdb; do \
        #echo "$mdb"; \
        #done
#exit 1

#1.1删除的文件列表
find $HOME/mdb /data -maxdepth 1 -type d -name "*_mdb" \
    | while read mdb_dir; do \
          cur=`find $mdb_dir/data/mdb -type f -name "mdbinfo.txt" \
          | xargs cat|head -n 1`;
          find $mdb_dir/data/mdb -mtime +$1 -type f -name "mdbinfo.txt.*" \
          | grep -v "mdbinfo.txt.$cur" \
          | awk -F"mdbinfo.txt" '{print $1" "$0}' \
          | while read mdbinfo_path file; do \
                export mdb_path=$mdbinfo_path; \
                cat $file | awk -F "/" 'NF==1 {version=$1}; NR>=2 {print "ls -l "ENVIRON["mdb_path"]"/"$2"-"$3".mdb."version} NR>=2 {print "ls -l "ENVIRON["mdb_path"]"/"$2"-"$3".mdb."version".*"} NR>=2 {print "ls -l "ENVIRON["mdb_path"]"/"$2"-"$3".frm."version}'; \
                done |sh >> ~/backup/deleted_mdbfile_`date +%Y%m%d`.txt;
     done

#1.2进行删除
find $HOME/mdb /data -maxdepth 1 -type d -name "*_mdb" \
    | while read mdb_dir; do \
          cur=`find $mdb_dir/data/mdb -type f -name "mdbinfo.txt" \
          | xargs cat|head -n 1`;
          find $mdb_dir/data/mdb -mtime +$1 -type f -name "mdbinfo.txt.*" \
          | grep -v "mdbinfo.txt.$cur" \
          | awk -F"mdbinfo.txt" '{print $1" "$0}' \
          | while read mdbinfo_path file; do \
                export mdb_path=$mdbinfo_path; \
                cat $file | awk -F "/" 'NF==1 {version=$1}; NR>=2 {print "rm "ENVIRON["mdb_path"]"/"$2"-"$3".mdb."version} NR>=2 {print "rm "ENVIRON["mdb_path"]"/"$2"-"$3".mdb."version".*"} NR>=2 {print "rm "ENVIRON["mdb_path"]"/"$2"-"$3".frm."version}'; \
                done |sh >> ~/backup/deleted_mdbfile_`date +%Y%m%d`.txt;
     done

#2.1删除的mdbinfo.txt.*文件列表
find $HOME/mdb /data -maxdepth 1 -type d -name "*_mdb" \
    | while read mdb_dir; do \
          cur=`find $mdb_dir/data/mdb -type f -name "mdbinfo.txt" \
          | xargs cat|head -n 1`;
          find $mdb_dir/data/mdb -mtime +$1 -type f -name "mdbinfo.txt.*" \
          | grep -v "mdbinfo.txt.$cur" \
          | awk -F"mdbinfo.txt" '{print $1" "$0}' \
          | while read mdbinfo_path file; do \
              ls -l $file;
              done >> ~/backup/deleted_mdbfile_`date +%Y%m%d`.txt
    done

#2.2进行删除
find $HOME/mdb /data -maxdepth 1 -type d -name "*_mdb" \
    | while read mdb_dir; do \
          cur=`find $mdb_dir/data/mdb -type f -name "mdbinfo.txt" \
          | xargs cat|head -n 1`;
          find $mdb_dir/data/mdb -mtime +$1 -type f -name "mdbinfo.txt.*" \
          | grep -v "mdbinfo.txt.$cur" \
          | awk -F"mdbinfo.txt" '{print $1" "$0}' \
          | while read mdbinfo_path file; do \
              rm $file;
              done >> ~/backup/deleted_mdbfile_`date +%Y%m%d`.txt
     done
     
#2.3进行binlog/bak删除
find $HOME/mdb /data -maxdepth 1 -type d -name "*_mdb" \
    | while read mdb_dir; do \
          find $mdb_dir/data/mdb/binlog/bak -mtime +$1 -type f -name '*.bin' \
          | awk -F"aimdb-" '{print $1" "$0}' \
          | while read mdbinfo_path file; do \
              echo "rm $file;"
              rm $file;
              done >> ~/backup/deleted_mdbfile_`date +%Y%m%d`.txt
     done