#!/usr/bin/awk -f
#command: cat i.awk

BEGIN {
ignores[1] = "mdb_client";
ignores[2] = "TableName";
ignores[3] = "RecordNum";
ignores[4] = "RecordExt";
ignores[5] = "HashBuf";
ignores[6] = "RealNum";
ignores[7] = "UsedNum";

count       = 0;
IP          = "";
PORT        = "";
TableName   = "";
RecordNum   = "";
RecordExt   = "";
HashBuf     = "";
RealNum     = "";
UsedNum     = "";
HOSTINFO[0,0,0]="";
}
{
    bFound =0;
    if( match($0,"mdb_client") > 0 )
    {
        IP=$2;
        PORT=$3;

    }
    else if( match($0,"TableName") > 0 )
    {
        split($0, a, ": ")
        TableName = a[2]
    }
    else if( match($0,"RecordNum") > 0 )
    {
        split($0, a, ": ")
        RecordNum=a[2]
        HOSTINFO[PORT, TableName, "RecordNum"]=RecordNum;
        #print PORT, TableName, "RecordNum", RecordNum, HOSTINFO[PORT, TableName, "RecordNum"]
    }else if( match($0,"RecordExt") > 0 )
    {
        split($0, a, ": ")
        RecordExt=a[2]
        HOSTINFO[PORT, TableName, "RecordExt"]=RecordExt;
        #print PORT, TableName, "RecordExt", RecordExt, HOSTINFO[PORT, TableName, "RecordExt"]
    }else if( match($0,"HashBuf") > 0 )
    {
        split($0, a, ": ")
        HashBuf=a[2]
        HOSTINFO[PORT, TableName, "HashBuf"]=HashBuf;
        #print PORT, TableName, "HashBuf", HashBuf, HOSTINFO[PORT, TableName, "HashBuf"]
    }
    else if( match($0,"RealNum") > 0 )
    {
        split($0, a, ": ")
        RealNum=a[2]
        HOSTINFO[PORT, TableName, "RealNum"]=RealNum;
        #print PORT, TableName, "RealNum", RealNum, HOSTINFO[PORT, TableName, "RealNum"]
    }else if( match($0,"UsedNum") > 0 )
    {
        split($0, a, ": ")
        UsedNum=a[2]
        HOSTINFO[PORT, TableName, "UsedNum"]=UsedNum;
        #print PORT, TableName, "UsedNum", UsedNum, HOSTINFO[PORT, TableName, "UsedNum"]
        if(int(RecordNum) > 10 * int(RecordExt))
        {
            if(count == 0)
            {
                printf("%-16s%-7s%-32s\t%-12s%-12s%-12s%-12s%-12s\n",
                       "IP", "PORT", "TableName", "RecordNum", "RecordExt", "HashBuf", "RealNum", "UsedNum")
                count = 1
            }
                printf("%-16s%-7s%-32s\t%-12s%-12s%-12s%-12s%-12s\n",
                  IP, PORT, TableName, RecordNum, RecordExt, HashBuf, RealNum, UsedNum)
        }
    }
}
END {
    #for(i in HOSTINFO)
    #    print i;
    #printf "========================================================\n"
    for (subscript in HOSTINFO) {
        split(subscript, a, SUBSEP);
        #printf "%s\t%s\t%s\t%s\n", a[1], a[2], a[3], HOSTINFO[a[1], a[2], a[3]]
    }
}
#i.awk C.txt