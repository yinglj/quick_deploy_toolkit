#!/bin/sh
gdb -p $1<<EOF
handle SIGPIPE nostop

break mmap
break brk
break munmap
continue
shell cat /dev/null > ./gdb.output
set logging file ./gdb.output
set logging on
where
set logging off
#shell cat ./gdb.output|grep 'obb_stream::operator'|cut -d' ' -f1|sed 's/#//'|xargs -i echo -e 'frame {}\nprint *this' > ./print.frame
shell grep 'SeriesSampler::take_sample' ./gdb.output|awk '{print \$1"\nprint *this"}' |sed 's/#/frame /g' > ./print.frame
#shell grep 'CRasBase::query_pay_bill_inside' ./gdb.output|awk '{print \$1"\nprint cUp\nprint cRet"}' |sed 's/#/frame /g' >> ./print.frame
#shell grep 'CRasBase::query_pay_bill_ext' ./gdb.output|awk '{print \$1"\nprint cUp\nprint cRet"}' |sed 's/#/frame /g' >> ./print.frame
#shell grep 'CMdbFrameImp::deal_client2' ./gdb.output|awk '{print \$1"\nprint *this\nprint *pEvent\nprint *pThreadInfo"}' |sed 's/#/frame /g' >> ./print.frame
###转化结果 frame 32 print *this，根据实际需要
source ./print.frame
detach
EOF
