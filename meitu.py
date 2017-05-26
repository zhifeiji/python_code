# -*- coding: utf-8 -*-
# create by hudengqi
# 2017-05-26 14:08
# decode www.meipai.com  data-video to video-url

import base64

def getHex(agr1):
    _str = agr1[4:]
    _hex = agr1[0:4][::-1]
    return {"_str":_str,"_hex":_hex}

def subSplit(arg1):
    ret = []
    for i, ch in enumerate(arg1):
        ret.append(int(ch))
    return ret

def getDec(agr1):
    loc1 = str(int(agr1,16))
    _pre = subSplit(loc1[0:2])
    _tail = subSplit(loc1[2:])
    return {"_pre":_pre,"_tail":_tail}

def substr(arg1,arg2):
    loc1 = arg1[0:arg2[0]]
    loc2 = arg1[arg2[0]:arg2[0]+arg2[1]]
    loc3 = arg1[arg2[0]:].replace(loc2,"")
    return loc1 + loc3

def getPos(arg1,arg2):
    arg2[0] = len(arg1) - arg2[0] - arg2[1]
    return arg2

def decode(agr1):
    loc1 = getHex(agr1)
    loc2 = getDec(loc1["_hex"])
    loc3 = substr(loc1['_str'],loc2['_pre'])
    return base64.decodestring(substr(loc3,getPos(loc3,loc2['_tail'])))

if __name__ == '__main__':
    agr1 = "3c62aHR0cDovLo5WXIPwSn212dmlkZW8xLm1laXR1ZGF0YS5jb20vNTkyNTMwOTRmMDg5ZDc1NjQubXJsJA0"
    url = decode(agr1)
    print(url)