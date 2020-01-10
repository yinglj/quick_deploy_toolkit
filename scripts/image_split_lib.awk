#!/usr/bin/awk -f
#command: cat i.awk
#run with cmd.sh
BEGIN {
    row = 0
    map["A"] = 1
    map["B"] = 2
    map["C"] = 3
    map["D"] = 4
    map["E"] = 5
    map["F"] = 6
    map["G"] = 7
    map["H"] = 8
    map["I"] = 9
    map["J"] = 10
    map["K"] = 11
    map["L"] = 12
    map["M"] = 13
    map["N"] = 14
    map["O"] = 15
    map["P"] = 16
    map["Q"] = 17
    map["R"] = 18
    map["S"] = 19
    map["T"] = 20
    map["U"] = 21
    map["V"] = 22
    map["W"] = 23
    map["X"] = 24
    map["Y"] = 25
    map["Z"] = 26
    map["AA"] = 27
    map["AB"] = 28
    map["AC"] = 29
    map["AD"] = 30
    map["AE"] = 31
    map["AF"] = 32
    map["AG"] = 33
    map["AH"] = 34
    map["AI"] = 35
    map["AJ"] = 36
    map["AK"] = 37
    map["AL"] = 38
    map["AM"] = 39
    map["AN"] = 40
    map["AO"] = 41
    map["AP"] = 42
    map["AQ"] = 43
    map["AR"] = 44
    map["AS"] = 45
    map["AT"] = 46
    map["AU"] = 47
    map["AV"] = 48
    map["AW"] = 49
    map["AX"] = 50
    map["AY"] = 51
    map["AZ"] = 52
    image["frame"]   = "B:B";        #框架库镜像对应《浙江电信lib清单-全库.xlsx》中的B列
    image["decode"]  = "C:C";        #解码镜像对应《浙江电信lib清单-全库.xlsx》中的C列
    image["xfer"]    = "D:D";        #xfer镜像对应《浙江电信lib清单-全库.xlsx》中的D列
    image["billing"] = "E:Y";        #长流程镜像对应《浙江电信lib清单-全库.xlsx》中的E-Y列
    image["detect"]  = "Z:AE";       #侦测镜像对应《浙江电信lib清单-全库.xlsx》中的Z-AE列
    for (i in image) {
            print "cat /dev/null > "i".txt"
    }
}
{
    if(NR > 2)
    {
        for(i=1; i<=NF; i++)
        {
            for (d in image) {
                split(image[d], tmp, ":");
                if(i>=map[tmp[1]] && i<=map[tmp[2]] )
                {
                    lib_count[d] += $i
                }
            }
        }
        for(j in lib_count)
        {
            if(lib_count[j] > 0)
            {
                print "echo "$1" >> "j".txt"
                lib_count[j] = 0
            }
        }
        
    }
}
END {
}
#image_split_lib.awk C.txt