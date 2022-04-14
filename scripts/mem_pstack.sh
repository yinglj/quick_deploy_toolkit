#!/usr/bin/env bash

exit_flag=0
function signal_handle()
{
    exit_flag=1;
    echo "catch process exit signal."
    echo "`date +'%Y%m%d %H:%M:%S'` catch process exit signal." >> ${log_file}
}

if [ $# -ne 2 ] && [ $# -ne 3 ]
then
    echo "Usage: $0 pid incr_mem_size(KB) [interval(S)]"
    exit 1
fi

pid=$1
incr_mem_size=`expr $2`
interval=60
if [ $# -eq 3 ]
then
    interval=$3
fi

log_path="${HOME}/backup/monitor"
log_file="${log_path}/monitor_${pid}_memory.log"

if [ ! -d ${log_path} ]
then
    mkdir -p ${log_path}
fi

function check_pid_exist()
{
    ps -p $1 > /dev/null
    if [ $? -ne 0 ]
    then
        echo "Pid($1) not found."
        echo "`date +'%Y%m%d %H:%M:%S'` Pid($1) not found." >> ${log_file}
        return 1
    else
        return 0
    fi
}

echo "Monitor Pid($pid) Memory Usage."
echo "`date +'%Y%m%d %H:%M:%S'` Monitor Pid($pid) Memory Usage." >> ${log_file}
echo "Interval($interval) second, Incr_mem_size($incr_mem_size) byte"
echo "`date +'%Y%m%d %H:%M:%S'` Interval($interval) second, Incr_mem_size($incr_mem_size) byte." >> ${log_file}

check_pid_exist $pid
if [ $? -ne 0 ]
then
    exit 1
fi

trap "signal_handle" SIGHUP SIGINT SIGQUIT SIGKILL SIGTERM SIGTRAP

last_memory=`ps -o 'rss' $1 | grep -v RSS| grep -v "grep"`

sn=1
while [ $exit_flag -eq 0 ]
do
    sleep $interval
    check_pid_exist $pid
    if [ $? -ne 0 ]
    then
        break
    fi
    cur_memory=`ps -o 'rss' $1 | grep -v RSS| grep -v "grep"`
    diff_mem=`expr $cur_memory - $last_memory`
    if [ $diff_mem -gt $incr_mem_size ]
    then
        echo "`date +'%Y%m%d %H:%M:%S'` pstack ${pid} > ${log_path}/pstack.${pid}.${diff_mem}.${sn}" >> ${log_file}
        sn=`expr $sn + 1`
        pstack ${pid} > ${log_path}/pstack.${pid}.${diff_mem}.${sn}
    fi
    echo "pid:$1, memory size: $cur_memory, diff_mem:$diff_mem"
    last_memory=$cur_memory
done
echo "" >> ${log_file}