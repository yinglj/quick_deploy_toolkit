#!/usr/bin/env bash

pid=$$
interval=300
run_days=-1
result_path="${HOME}/backup/mdb_monitor"
mdb_user="billmdb"
mdb_passwd="billmdb"

exit_flag=0
function signal_handle()
{
    exit_flag=1;
    echo "catch process exit signal."
}

function check_usage()
{
    if [ $# -ne 1 ] && [ $# -ne 2 ] && [ $# -ne 3 ]
    then
        echo "Usage: $0 mdb_cnf_name_list [interval(minute)] [run_days]"
        exit 1
    fi

    if [ $# -eq 2 ]
    then
        interval=`expr $2 \* 60`
    fi

    if [ $# -eq 3 ]
    then
        run_days=$3
    fi

    local cnf_names="$1"
    local v_idx=0
    local v_mdb_cnf_name=""
    mdb_cnf_name_list=(${cnf_names//,/ })
    for v_mdb_cnf_name in ${mdb_cnf_name_list[@]}
    do
        if [ "A${v_mdb_cnf_name:0-4:4}" == "A.cnf" ]
        then
            mdb_cnf_name_list[$v_idx]="${v_mdb_cnf_name%.cnf}"
        fi
        v_idx=`expr $v_idx + 1`
    done
}

function check_process_exist()
{
    local process_name="$1"
    local process_base_name="`basename $process_name`"
    local ps_results="`ps --no-headers -A -opid,ppid,cmd | grep $process_name |grep -v grep`"
    while read -r ps_result
    do
        local ps_result_array=($ps_result)
        local result_array_len=${#ps_result_array[@]}
        if   [ ${ps_result_array[0]} -eq ${pid} ] || [ ${ps_result_array[1]} -eq ${pid} ]
        then
            continue
        fi

        if   [ "`basename ${ps_result_array[2]}`" = "$process_base_name" ] \
          || ([ ${result_array_len} -gt 3 ] && [ "`basename ${ps_result_array[3]}`" == "$process_base_name" ])
        then
            echo "process($process_name) has started."
            exit 1
        fi
    done <<< "${ps_results}"
}

function check_path_exist()
{
    for v_mdb_cnf_name in ${mdb_cnf_name_list[@]}
    do
        local file_path="${result_path}/${v_mdb_cnf_name}"
        if [ ! -d ${file_path} ]
        then
            mkdir -p ${file_path}
        fi
    done
}

collect_sql_list="thread_group_stat:select * from information_schema.thread_group_stat
mdb_stat:select * from information_schema.mdb_stat where name='tps'
process_list:select * from information_schema.processlist"

declare -a socket_port_list
function get_port()
{
    local v_mdb_cnf_name=""
    local v_idx=0
    for v_mdb_cnf_name in ${mdb_cnf_name_list[@]}
    do
        v_mdb_cnf_name="${v_mdb_cnf_name}.cnf"
        local proc_num=`ps --no-header -A -o cmd | grep mysqld | grep -v grep | grep ${v_mdb_cnf_name}|wc -l`
        if [ ${proc_num} -ge 1 ]
        then
            socket_port_list[$v_idx]=`ps --no-header -A -o cmd | grep mysqld | grep -v grep | grep ${v_mdb_cnf_name} | awk -F'defaults-file=' '{print $2}' | awk '{print $1}' | xargs grep '^[ \t]*port' | grep -v grep | head -n1|awk -F"=" '{gsub(/^\s+|\s+$/,"",$2);print $2}'`
            echo "${v_mdb_cnf_name}, port:${socket_port_list[$v_idx]}"
        else
            echo "mysqld ${v_mdb_cnf_name} process not found."
            exit 1
        fi
        v_idx=`expr $v_idx + 1`
    done
}

function collect_sql_data()
{
    local v_idx=0
    for v_socket_port in ${socket_port_list[@]}
    do
        local sql=""
        local time_suffix="`date +'%Y%m%d%H%M%S'`"
        local file_list=""
        while read -r line
        do
            local table_name="${line%%:*}"
            local select_sql="${line#*:}"
            local file_name="${result_path}/${mdb_cnf_name_list[$v_idx]}/${table_name}.${time_suffix}.txt"
            file_list="${file_list} ${table_name}.${time_suffix}.txt"
            sql="${sql}${select_sql} into outfile '${file_name}' fields terminated by ',' optionally enclosed by '\"';"
        done <<< "$collect_sql_list"
        mysql --connect-timeout=4 -u${mdb_user} -p${mdb_passwd} -h127.0.0.1 -P${v_socket_port} <<-EOF
            $sql
                EOF
        if [ $? -ne 0 ]
        then
            echo "exec sql{${sql}} error."
        else
            local cur_pwd=`pwd`
            cd ${result_path}/${mdb_cnf_name_list[$v_idx]} && tar zcvf ${time_suffix}.tar.gz ${file_list} > /dev/null && rm ${file_list} && cd ${cur_pwd}
        fi
    done
}

trap "signal_handle" SIGHUP SIGINT SIGQUIT SIGKILL SIGTERM SIGTRAP

check_usage "$@"
check_path_exist
check_process_exist $0
get_port

run_stop_sec=`expr ${run_days} \* 24 \* 60 \* 60`
echo "interval=${interval}s, run_days=${run_days}, run_stop_sec=${run_stop_sec}"

run_sec=0
while [ $exit_flag -eq 0 ] && ([ $run_stop_sec -lt 0 ] || ([ $run_stop_sec -gt 0 ] && [ $run_sec -le $run_stop_sec ]))
do
    collect_sql_data
    sleep $interval
    run_sec=`expr $run_sec + $interval`
done
