import os, sys, json
from pathlib import Path
this_dir = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(str(Path(this_dir).parent.parent))
import asyncio
from typing import Dict, Callable
from functools import partial
from base64 import b64decode
from poco.proxy import UIObjectProxy
from airtest.core.helper import log
from Ninja.Utils.linker import get_link
from Ninja.Utils.UagesCase import StorePict, store, FloderInstance, MakeFloader
from Ninja.Utils.NinjaMethods import storefunc, StorePict
from Ninja.Utils.NinjaMethods import Ninja
from Ninja.profile import DeviceInfo, LinkInfo, PocoInfo


class runCase(object):
    CHAPTERS:Dict[str, Callable]={"Chapter1":Ninja.ChapterOne}
    def __init__(self, info: DeviceInfo):
        if info.link.temp_logdir is None:
            MakeFloader(info.BasePth)
            info.link.temp_logdir = os.path.join(info.BasePth,FloderInstance())
            self.temp_logdir = info.link.temp_logdir
        self.retry = info.CaseRetry
        storefunc(store, path=info.link.temp_logdir)
        storefunc(StorePict, path= info.link.temp_logdir)
        self.poco = get_link(info.link, info.poco, restart=True) # restart whether restart Application on this Device
        self.GaminPath =MakeFloader(os.path.join(self.temp_logdir,'GameinSnapshots'))
    
    async def __call__(self, GoScenario: int):
        
        await self.setup(GoScenario)

        try:
            flag = self.poco("Img_Hand").exists()
        except:
            flag = False
        snaps = 1
        while not flag:

            self.snapshots(snaps)
            try:
                flag = self.poco("Img_Hand").exists()
            
            finally:
                snaps+=1
                await Ninja.Goon(self.poco) # resume Gaming
        

    async def setup(self, GoScenario:int):
        await self.CHAPTERS["Chapter{:1}".format(GoScenario)](self.poco)
        log('Arrived at the Scenario named Chapter{:1}'.format(GoScenario))
        

    def snapshots(self, snaps):
        
        with self.poco.freeze() as frozenTree:
            hitree = frozenTree.agent.hierarchy.dump()
        b64img, fmt = self.poco.snapshot()
        Ninja.HangUp(self.poco)
        with open(os.path.join(self.GaminPath,"picture{}.{}".format(snaps, fmt)),
            'wb') as fx:
            fx.write(b64decode(b64img))
        with open(os.path.join(self.GaminPath,'hitree{}.json'.format(snaps)),'wt')as f:
            hitree = hitree['children'][16]
            json.dump(hitree,f,ensure_ascii=False,indent=2)
    
        
def run_coroutine_in_thread(coro):
    """
    accepted coroutine Object
    """
    loop = asyncio.new_event_loop()
    try: 
        return  loop.run_until_complete(coro)
    finally:
        loop.close()
import  concurrent 
async def main():
    '''
    multiprocess 
    '''
    deviceinfo = DeviceInfo(
        link=LinkInfo(connect_url=['android://127.0.0.1:5037/35b1a832?cap_method=MINICAP&touch_method=MAXTOUCH'], 
                    temp_logdir = None, 
                    package_name='com.oceangames.ninja.gp'),
        poco=PocoInfo(android_poco_retry_cnt=3, android_poco_sleep_time=3, use_airtest_input=True, poco="UnityPoco"), 
        BasePth='C:\\Users\\happyelements\\workstation\\UnityPocoProject\\Storage',
        CaseRetry=1
        )
    
    Ninjarun = runCase(deviceinfo)
    await Ninjarun(1)
    
if __name__=="__main__":
    asyncio.run(main())