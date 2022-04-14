#!/bin/sh
if test $# -ne 1; then
    echo "Usage: `basename $0` days-before
example: `basename $0` 3" 1>&2    
    exit 1
fi

if test $1 -lt 1; then    
    echo "days-before must bigger than 1."    
    exit 1
fi

#1.1ɾ³ýµÄÎļþÁбí
find /intdata/mdb -maxdepth 1 -type d -iname "*_MDB*" \
    | while read mdb_dir; do \
         cur=`find $mdb_dir/data/mdb -type f -name "mdbinfo.txt" \
          | xargs cat|head -n 1`;
          find $mdb_dir/data/mdb -mtime +$1 -type f -name "mdbinfo.txt.*" \
          | grep -v "mdbinfo.txt.$cur" \
          | awk -F"mdbinfo.txt" '{print $1" "$0}' \
          | while read mdbinfo_path file; do \
                export mdb_path=$mdbinfo_path; \
                cat $file | awk -F "/" 'NF==1 {version=$1}; NR>=2 {print "ls -l "ENVIRON["mdb_path"]"/"$2"-"$3".mdb."version"*"} NR>=2 {print "ls -l "ENVIRON["mdb_path"]"/"$2"-"$3".frm."version}'; \
                done |sh >> ~/users/backup/deleted_mdbfile_`date +%Y%m%d`.txt;
     done
#1.2½øÐÐɾ³ý 
find /intdata/mdb -maxdepth 1 -type d -iname "*_MDB*" \
    | while read mdb_dir; do \
          cur=`find $mdb_dir/data/mdb -type f -name "mdbinfo.txt" \
          | xargs cat|head -n 1`;
          find $mdb_dir/data/mdb -mtime +$1 -type f -name "mdbinfo.txt.*" \
          | grep -v "mdbinfo.txt.$cur" \
          | awk -F"mdbinfo.txt" '{print $1" "$0}' \
          | while read mdbinfo_path file; do \
                export mdb_path=$mdbinfo_path; \
                cat $file | awk -F "/" 'NF==1 {version=$1}; NR>=2 {print "rm "ENVIRON["mdb_path"]"/"$2"-"$3".mdb."version"*"} NR>=2 {print "rm "ENVIRON["mdb_path"]"/"$2"-"$3".frm."version}'; \
                done |sh >> ~/users/backup/deleted_mdbfile_`date +%Y%m%d`.txt;
     done

#2.1 ɾ³ýµÄmdbinfo.txt.*ÎļþÁбí
find /intdata/mdb -maxdepth 1 -type d -iname "*_MDB*" \
    | while read mdb_dir; do \
          cur=`find $mdb_dir/data/mdb -type f -name "mdbinfo.txt" \
          | xargs cat|head -n 1`;
          find $mdb_dir/data/mdb -mtime +$1 -type f -name "mdbinfo.txt.*" \
          | grep -v "mdbinfo.txt.$cur" \
          | awk -F"mdbinfo.txt" '{print $1" "$0}' \
          | while read mdbinfo_path file; do \
              ls -l $file;
              done >> ~/users/backup/deleted_mdbfile_`date +%Y%m%d`.txt;

#2.2 ½øÐÐɾ³ý
find /intdata/mdb -maxdepth 1 -type d -iname "*_MDB*" \
    | while read mdb_dir; do \
          cur=`find $mdb_dir/data/mdb -type f -name "mdbinfo.txt" \
          | xargs cat|head -n 1`;
          find $mdb_dir/data/mdb -mtime +$1 -type f -name "mdbinfo.txt.*" \
          | grep -v "mdbinfo.txt.$cur" \
          | awk -F"mdbinfo.txt" '{print $1" "$0}' \
          | while read mdbinfo_path file; do \
              rm $file;
              done >> ~/users/backup/deleted_mdbfile_`date +%Y%m%d`.txt
     done
     
#2.3½øÐÐbinlog/bakɾ³ý
find /intdata/mdb -maxdepth 1 -type d -iname "*_MDB*" \
    | while read mdb_dir; do \
          find $mdb_dir/data/mdb/binlog/bak -type f -name '*.bin' \
          | while read file; do \
             echo "rm $file;"
              rm $file;
              done >> ~/users/backup/deleted_mdbfile_`date +%Y%m%d`.txt;
     done
 done
 
#3½øÐÐaddup_mdbµÄÎļþɾ³ýÌØÊ⴦À¸öckµİ汾 
for addupType in `echo "YN_ADDUP_MDB_A_M|YN_ADDUP_MDB_A_S|YN_ADDUP_MDB_A_R|YN_ADDUP_MDB_B_M|YN_ADDUP_MDB_B_S|YN_ADDUP_MDB_B_R" |tr '|' ' '`
do
    #echo $addupType
    addupPath='/intdata/mdb/'$addupType'/data/mdb/'
    if [ ! -f $addupPath"mdbinfo.txt" ];then
        echo $addupPath"mdbinfo.txt not exists!" >> ~/users/backup/deleted_mdbfile_`date +%Y%m%d`.txt;
        continue;
    fi
    if [ `ps -ef | grep mysqld | grep $addupType | grep -v grep|wc -l` -lt 1 ];then
        echo "addup mdb $addupType process not exists!" >> ~/users/backup/deleted_mdbfile_`date +%Y%m%d`.txt;
        continue;
    fi
    addupMdbInfoFile=$addupPath"mdbinfo.txt"
    mdbinfoDate="`ls --full-time $addupMdbInfoFile|cut -d' ' -f 6`"
    mdbinfoTime="`ls --full-time $addupMdbInfoFile|cut -d' ' -f 7`"
    mdbinfoSecond="`date -d "$mdbinfoDate $mdbinfoTime" +%s`"
    newfileSecond=`expr $mdbinfoSecond - 18000`
    newfileDateTime="`date -d "@$newfileSecond" +%Y%m%d%H%M`"
    touch -t $newfileDateTime $addupPath"deletefileinfo.txt"
    find $addupPath -type f ! -newer $addupPath"deletefileinfo.txt"|grep -v ADDUP_MDB-CUnifyPaymentSessionInfo|while read file
    do
        echo "rm $file;"
        rm $file
    done >> ~/users/backup/deleted_mdbfile_`date +%Y%m%d`.txt;
    find $addu