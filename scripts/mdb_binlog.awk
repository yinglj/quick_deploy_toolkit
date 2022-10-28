#!/usr/bin/awk -f

function help() {
    print "# 用于生成SQL语句文件，命令格式如下:"
    print "mdb_binlog.awk binlog.aimdb-12000000.bin"
    print "binlog解析命令如下:"
    print "mdb_binlog.sh -f /data/yinglj_v8/data/mdb/tc_mdb_1_m/data/mdb/binlog/aimdb-12000000.bin -m /data/yinglj_v8/data/mdb/tc_mdb_1_m/data/mdb -v detail --offset > ~/binlog.txt"
    print "binlog输出格式:"
    print "========================================================================================="
    print "table_name:./TC_MDB/CUserTrailCodeInfo,table_id:3,m_szUserNumber:13605877826,m_szUserNumber-length:11,m_szCityName:31000,32000|208|207|206,m_szCityName-length:23,m_dValidDate:1629475201,m_dExpireDate:1630339201"
    print "========================================================================================="
    print "例子:"
    print "date;mdb_binlog.sh -f /data/yinglj_v8/data/mdb/tc_mdb_1_m/data/mdb/binlog/aimdb-12000000.bin -m /data/yinglj_v8/data/mdb/tc_mdb_1_m/data/mdb -v detail --offset|grep insert -A 2 |mdb_binlog.awk -F',[a-zA-Z]' > ~/binlog.txt ;date"
    return 0
}

function fetch_line() {

}

function do_ddl() {
    
}

function do_insert(line) {


}

BEGIN{
    FS = ",[a-zA-Z]"

    ignores[1] = "filename:"
    ignores[2] = "offset:"

    keywords["ddl"] = "ops_name:ddl,"
    keywords["insert"] = "ops_name:insert,"
    keywords["update"] = "ops_name:update,"
    keywords["remove"] = "ops_name:remove,"
}
{
    for(i in ignores) {
        if(match($0,ignores[i])) {
            next
        }
    }
    if(match($0,"ops_name:insert")>0) next
    if(match($0,"offset:")>0) next
    sql = "insert into "
    for (i=1; i<=NF; i++)
    {
        if(match($i,"table_name:"))
        {
            split($i, tmp, ":|,|/") 
            table_name = tmp[3]"."tmp[4]
            continue
        }
        if(split($i,tmp, ":"))
        {
            #print tmp[1]"|"tmp[2]
            if(p=match(tmp[1],"-length"))
            {
                field_string=substr(tmp[1],0,p-1)
                fs[field_string]=field_string
                #print "string_field_name[1]="field_string
                continue
            }
            fields[tmp[1]] = tmp[2]
        }
    }
    for(i in fs)
    {
        #print i,fs[i]
    }
    #print "fields:"
    for(i in fields)
    {
        #print i,fields[i]
        if(i in fs)
        {
            fields[i]="'"fields[i]"'"
            #print fields[i]
        }
        if(sql_field=="") sql_field=i
        else sql_field = sql_field","i
        if(sql_value=="") sql_value=fields[i]
        else sql_value = sql_value","fields[i]
    }
    sql = sql" "table_name "(" sql_field ") values (" sql_value ");"
    print sql
    table_name=""
    sql_field=""
    sql_value=""
    split( "", tmp)
    split( "", fields)
    split( "", fs)
}
END{
}
