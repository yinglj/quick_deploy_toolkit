#!/bin/sh

OUR_LIB_PATH=/app/billing/docker-make/zhaojj


cd $OUR_LIB_PATH

for so_file in lib/*.so.[0-9].[0-9].[0-9].[0-9][0-9][0-9][0-9][0-9][0-9] ; do
  so_org_name=${so_file//.[0-9].[0-9].[0-9].[0-9][0-9][0-9][0-9][0-9][0-9]/}
  so_link_name=`readlink $so_org_name`
  so_base_link_name=`basename $so_link_name`
  if [ $so_base_link_name  != `basename $so_file` ] ;then
     echo $so_file
  fi
done


for bin_file in bin/*.[0-9].[0-9].[0-9].[0-9][0-9][0-9][0-9][0-9][0-9] ; do
  org_name=${bin_file//.[0-9].[0-9].[0-9].[0-9][0-9][0-9][0-9][0-9][0-9]/}
  link_name=`readlink $org_name`
  base_org_name=`basename $org_name`
  base_link_name=`basename $link_name`
  if [ $base_link_name  != `basename $bin_file` ] ;then
     echo $bin_file
  fi
done
