import sys, os
import json
import pathlib
import asyncio

import unittest.test
this_path = os.path.split(os.path.realpath(__file__))[0]

sys.path.append(str(pathlib.Path(this_path).parent.parent))
import unittest
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
class NinjaOpt(unittest.TestCase):
    def __init__(self, info:DeviceInfo, NoScenario:int=1):
        if info.link.temp_logdir is None:
            MakeFloader(info.BasePth)
            info.link.temp_logdir = os.path.join(info.BasePth,FloderInstance())
            self.temp_logdir = info.link.temp_logdir
        self.retry = info.CaseRetry
        storefunc(store, path=info.link.temp_logdir)
        storefunc(StorePict, path= info.link.temp_logdir)
        self.poco = get_link(info.link, info.poco, restart=True) # restart whether restart Application on this Device
        self.GoScenario = NoScenario

    
    def set_up(self):
        log('Go to the Scenario with {}'.format(self.GoScenario.__name__))
        times = 0
        
        while times< self.retry:
            # retry
            try:
                btn = self.GoScenario(self.poco)
            except:
                btn = None
            finally:
                times+=1
                if not isinstance(btn, UIObjectProxy):
                    continue
                else:
                    break
    def tear_down(self):
        log("Case has been executed!")
        pass
    async def run_case(self):
        '''
        Choice senario and execute
        '''
        try:
            btn = self.poco("Img_Hand")
        except:
            btn = None
        snaps = 1
        while not isinstance(btn, UIObjectProxy):

            self.snapshots(snaps)
            try:
                btn = self.poco('Img_Hand') if self.poco("Img_Hand") else None
            except:
                btn = None
            finally:
                snaps+=1
                await Ninja.Goon() # resume Gaming 


    async def runTest(self):
        try:
            self.set_up()
            await self.run_case()
            self.tear_down()
        except Exception as e:
            log(e, desc="Raise Error during Execuating", snapshot=True)      

            self.fail("执行失败")
        
        
    def snapshots(self, snaps:int):
        MakeFloader(os.path.join(self.temp_logdir,'GameinSnapshots'))
        with self.poco.freeze() as frozenTree:
            hitree = frozenTree.agent.hierarchy.dump()
        b64img, fmt = self.poco.snapshot()
        asyncio.run(Ninja.HangUp(self.poco))
        with open(os.path.join(self.temp_logdir,"Gamein","picture_{}.{}".format(snaps, fmt)),
            'wb') as fx:
            fx.write(b64decode(b64img))
        with open(os.path.join(self.temp_logdir,"Gamein",'hitree_{}.json'.format(snaps)),'wt')as f:
            
            json.dump(hitree,f,ensure_ascii=False,indent=2)
async def main():
    deviceinfo = DeviceInfo(
        link=LinkInfo(connect_url=['android://127.0.0.1:5037/35b1a832?cap_method=MINICAP&touch_method=MAXTOUCH'], 
                      temp_logdir = None, 
                      package_name='com.oceangames.ninja.gp'),
        poco=PocoInfo(android_poco_retry_cnt=3, android_poco_sleep_time=3, use_airtest_input=True, poco="UnityPoco"), 
        BasePth='C:\\Users\\happyelements\\workstation\\UnityPocoProject\\Storage',CaseRetry=1)
    Ninjarun = NinjaOpt(deviceinfo)
    test_suite = unittest.TestSuite()
    test_suite.addTest(Ninjarun)
    Execuator = unittest.TextTestRunner()
    result = Execuator.run(test_suite)
if __name__=="__main__":
    asyncio.run(main())