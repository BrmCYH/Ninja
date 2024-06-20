import os, json
import time, random
from base64 import b64decode
from typing import Dict, Callable

from airtest.core.api import log
from poco.drivers.unity3d import UnityPoco
from poco.exceptions import PocoTargetTimeout
from functools import wraps, partial

def MakeFloader(floder:str):
    if not os.path.exists(floder):
        try:
            os.mkdir(floder)
        except:
            return None
    return floder
def FloderInstance():
    current_time = int(time.time() * 1e6)
    
    unique_value = f"Info_{current_time}"
    return unique_value

async def store(path:str, hitree:Dict, Node_Name:str):
    if os.path.exists(path):
        with open(os.path.join(path,Node_Name+'.json'),'wt',encoding='utf-8')as f:
            
            json.dump(hitree,f,ensure_ascii=False,indent=2)
        log("Hitree expressing Windows UI infos of {} , has been stored to Disk: {},fileName: {}".format(
            Node_Name.split("_")[0],
            path,
            Node_Name+'.json')
            )
    else:
        raise('path not found')
async def StorePict(path:str, b64BasePic:str, Node_Name:str):
    if os.path.exists(path):
        with open(os.path.join(path,Node_Name),'wb')as f:
            f.write(b64decode(b64BasePic))
        log("Snapshot expressing status of {} , has been stored to Disk:{},fileName:{}".format(
            Node_Name.split("_")[0],
            path,
            Node_Name)
            )
    else:
        raise('path not found')


