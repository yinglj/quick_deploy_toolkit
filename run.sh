#!/bin/bash
host_ip=$1
pwd_root=$2
newuser=$3
newuser_pwd=$4
echo "Start create user "$3",on host:"$1
expect ./useradd.exp $host_ip root $pwd_root $newuser $newuser_pwd
