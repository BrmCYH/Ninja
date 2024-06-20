import os, sys, json
import time
from pathlib import Path
this_dir = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(str(Path(this_dir).parent))
sys.path.append(str(Path(this_dir).parent.parent))

from airtest.core.api import log
from poco.drivers.unity3d import UnityPoco
from poco.proxy import UIObjectProxy
from poco.exceptions import PocoTargetTimeout
from functools import wraps, partial
import asyncio
from base64 import b64decode
from typing import Dict, Callable

from Ninja.profile import *
from Ninja.Utils import get_link
from Utils.UagesCase import FloderInstance, MakeFloader, store, StorePict

PATH_DICT={
     "Gamein_Windows":[13, 2, 0, 1, 3],
     "Skip1_UINinjaHome":[13, 2, 0, 1, 5, 0, 0],
     "Skip2_UINinjaHome":[13, 2, 0, 1, 5, 0, 0],
     "ExploreTime_Chapter":[[13, 2, 0, 1, 4, 0, 0, 0],[14, 2, 0, 1, 4, 2, 0, 0, 6, 2, 0]],
     "ChapterPage_Choice":[14, 2, 0, 1, 3, 1, 0],
     "ChapterIn_battle":[14, 2, 0, 1, 3, 2, 0],
     "Scenario_Pick_01":[[16, 2, 0, 1],[18, 2, 0, 1]],
     "Skill_Pick_chip":[18, 2, 0, 1, 3, 5, 0],
     "Skill_Confirm_chip":[18, 2, 0, 1, 3, 5, 0],
     "Scenario_Pick_03":[23, 2, 0, 1, 3, 1, 0]
}
STORAGE: Dict[str, Callable] = {}
NodeNames={
    "ConfirmSkill":["Common","Btn_Cancel","Btn_Confirm"]
}

def storefunc(func, path) -> Dict[str,Callable]:

    BFunc = partial(func, path= path)
    STORAGE[func.__name__] = BFunc
    
def GetStoreFunc(name):
    return STORAGE.get(name, None)

async def find_node(nodename, result:Dict):
    
    if isinstance(result,dict):
        hitree = result
    else:
        hitree = json.loads(result)
    routeall = PATH_DICT.get(nodename,None)
    

    if routeall is None:
        print(nodename)
        raise f"PATH_DICT not incloud nodename path: {nodename}"
    else:
        signal = True if isinstance(routeall[0],list)else False
        if not signal:
            try:

                find = lambda i,hitree: hitree['children'][i]

                for path in routeall:
                    hitree = find(path,hitree)
            except IndexError as e:
                log("hitree can not find in the {}".format(routeall))
                hitree = {}
            
        while signal:
            try:
                routeall = iter(routeall)
                route=next(routeall)
            except StopIteration as e:
                hitree = {}
                log("hitree can not find in the {}".format(routeall))
                break
                
            try:
                find = lambda i,hitree: hitree['children'][i]
            
                for path in route:
                    hitree = find(path,hitree)
                signal = False
            except IndexError as e:
                signal = True
                continue
        
    return hitree
def store_to(filename):
    def run(fun):
        @wraps(fun)
        async def wrapper(*args, **kw):

            result = await fun(*args, **kw)
            if result is None:
                raise "function running error"
            File = fun.__name__
            Nodename = '_'.join([File,filename])
            cus_store =  GetStoreFunc("store")
            hitree = await find_node(Nodename, result)
            await cus_store(hitree=hitree,Node_Name=Nodename)

        return wrapper
    return run
def Img64WithTree(chapter, mission):
    
    def wrap(func):
        @wraps(func)
        async def wrapped(*args, **kwargs):
            results = await func(*args, **kwargs)
            resultdict = {name:value for name, value in results.items()}
            missions=mission
            # print(type(resultdict['Now']),mission)
            if func.__name__ == "PickGoods":
                Num = resultdict.get('Now')
                missions = "{}_{}".format(mission,Num)
            if func.__name__ == "ChoiceSkill" or func.__name__=="ConfirmSkill":
                stage = resultdict.get('stage')
                missions = "{}_{}".format(mission,stage)

            if resultdict.get("b64img",None):
                fmt = resultdict.get(
                    'fmt','jpg'
                )
                await GetStoreFunc('StorePict')(b64BasePic=resultdict['b64img'],Node_Name="{}_{}-Snapshot.{}".format(missions, chapter, fmt))

            if resultdict.get("hitree",None):
        
                hitree = await find_node("{}_{}".format(chapter,missions), resultdict['hitree'])
                await GetStoreFunc('store')(hitree=hitree, Node_Name='{}_{}-Hitree'.format(missions, chapter))
                
            log("Store image&Tree | Task:{:-<15},Chapter:{:-<60}".format(mission, chapter))    
        return wrapped
    
    
    return wrap

async def wait_source(poco: UnityPoco, Info: PocoUIInfo):
    retry_maxtimes = 5
    SourceUseInfo = SourceMetric(start_time=time.time())
    while not SourceUseInfo.signal:
        
        try:
            log("{:<30}第{:}/{}次尝试{}".format("Trying to connect",SourceUseInfo.retry_times,retry_maxtimes,"..."))
            poco(name=Info.name).exists()
            btn = poco(name=Info.name)
            SourceUseInfo.signal = True
        except:
            SourceUseInfo.interval+=1
            await asyncio.sleep(SourceUseInfo.interval)

        finally:
            SourceUseInfo.retry_times+=1
        if SourceUseInfo.retry_times>retry_maxtimes:
            break
    if SourceUseInfo.signal:
        log("{:<30}总耗时：{:}'{:}ms".format("successed!",int(time.time()-SourceUseInfo.start_time),int((time.time()-SourceUseInfo.start_time)*1000)))
    else:
        raise "the target Source which name is {name} have not init".format(name=Info.name)
    return btn
class Ninja:
    def __init__(self, ):
        pass
    def __call__(self):
        pass

    @staticmethod
    @store_to("Windows")
    async def Gamein(poco):
        
        log("{:-<50}{}".format("INIT GAME","login....."))
        NodeInfo = PocoUIInfo(type='Button', name = 'BtnLogin')
        with poco.freeze() as frozen_tree:
            hitree = frozen_tree.agent.hierarchy.dump()
        btn = poco(name=NodeInfo.name)
        btn.click()
        return hitree

    
    @staticmethod
    @store_to("UINinjaHome")
    async def Skip1(poco):
        log("{:-^100}".format("Skip scenario"))
        NodeInfo = PocoUIInfo(type='Butten',name= "ButtonSkipAll")
        
        with poco.freeze() as frozen_tree:
            hitree = frozen_tree.agent.hierarchy.dump()
        btn = poco(name=NodeInfo.name)
        btn.click()
        return hitree
        
    
    @staticmethod
    @store_to("UINinjaHome")
    async def Skip2(poco):
        log("{:-^100}".format("Skip scenario"))
        NodeInfo = PocoUIInfo(type='Butten',name= "BtnSkip")
        
        with poco.freeze() as frozen_tree:
            hitree = frozen_tree.agent.hierarchy.dump()
        btn = poco(name=NodeInfo.name)
        btn.click()
        return hitree

# @store_to('Chapter')
    @staticmethod
    async def ExploreTime(poco):
        log("{:-^100}".format("Choice Chapter"))
        NodeInfo = PocoUIInfo(type='Butten',name= "BtnStartChapter")
        
        with poco.freeze() as frozen_tree:
            hitree = frozen_tree.agent.hierarchy.dump()
        btn = poco(name=NodeInfo.name)
        btn.click()
        return hitree
    
    @staticmethod
    @store_to("Choice")
    async def ChapterPage(poco):
        log("{:-^100}".format("Choice Chapter"))
        NodeInfo = PocoUIInfo(type='Image',name= "Ani_Square")
        
        with poco.freeze() as frozen_tree:
            hitree = frozen_tree.agent.hierarchy.dump()
        btn = poco(name=NodeInfo.name)
        btn.click()
        return hitree
    
    @staticmethod
    @store_to("battle")
    async def ChapterIn(poco):
        log("{:-^100}".format("Battle-in"))
        NodeInfo = PocoUIInfo(type='TMPROUGUI', name= 'Txt', text = '战斗')
        with poco.freeze() as frozen_tree:
            hitree = frozen_tree.agent.hierarchy.dump()
        btn = poco(name=NodeInfo.name,text=NodeInfo.text)
        btn.click()
        return hitree
    
    
    @staticmethod
    @Img64WithTree("Scenario","Pick")
    async def PickGoods(poco, NodeInfo: PocoUIInfo, ScreenSize: float):
        scenario = poco(name='Txt_NumNow', type= 'TMPROUGUI')
        allscenario = poco(name='Txt_Num', type= 'TMPROUGUI')

        Now = scenario.attr("text")
        all = allscenario.attr("text").lstrip('/')

        log("scenario:{:<3}/{:<3}".format(Now,all))

        with poco.freeze() as frozen_tree:
            hitree = frozen_tree.agent.hierarchy.dump()
        print(NodeInfo.type)
        b64img, fmt = poco.snapshot(width=ScreenSize)
        btn = poco(name=NodeInfo.name, type=NodeInfo.type)
        
        btn.click()
        return {"hitree":hitree, "b64img":b64img, "fmt":fmt, "Now":Now}
    @staticmethod
    def ChoiceNum(poco):
            # Random Choice --> Model inference Choice
            Skills = len(poco("Layout_Overall").child("Layout").child("Item(Clone)"))
            import random
            pick = random.randint(0,Skills)
            return pick
    
    
    @staticmethod
    @Img64WithTree("Skill","Pick")
    async def ChoiceSkill(poco, ScreenSize):
        skillsinf = poco("Txt_Under").wait(2)
        if skillsinf.attr("text") == "获得芯片":
            stage = "chip"
            log("Stage: {}".format(poco('Txt_Under').attr("text")))
        No = Ninja.ChoiceNum(poco)
        with poco.freeze() as frozen_tree:
            hitree = frozen_tree.agent.hierarchy.dump()
        try:

            btn = poco("SkillIcon")
        except PocoTargetTimeout as e:

            btn = poco("Layout_Overall").child("Layout").child("Item(Clone)")[No].offspring("Img_SkillIcon")

        btn.click()
        b64img, fmt = poco.snapshot(width=ScreenSize)
        return {"hitree":hitree, "b64img":b64img, "fmt":fmt, "stage":stage}
    
    
    @staticmethod
    @Img64WithTree("Skill","Confirm")
    async def ConfirmSkill(poco, ScreenSize):
        if poco("Txt_Under").attr("text") == "获得芯片":
            stage = "chip"
            log("Stage: {}".format(poco('Txt_Under').attr("text")))
        with poco.freeze() as frozen_tree:
            hitree = frozen_tree.agent.hierarchy.dump()

        btnnames = iter(NodeNames['ConfirmSkill'])
        btn = None
        while not isinstance(btn,UIObjectProxy):
            try:
                btn = poco(next(btnnames))
            except StopIteration as e:
                raise 'In this chapter,named: ConfirmSkill,the name of btn is not included by Variable NodeNames!'
            

        btn.click() if btn else False
        b64img, fmt = poco.snapshot(width=ScreenSize)
        return {"hitree":hitree, "b64img":b64img, "fmt":fmt, "stage":stage}
    @staticmethod
    def HangUp(poco):
        btn = None
        while not isinstance(btn, UIObjectProxy):
            try:
                btn = poco("BtnPause")
            except:
                time.sleep(1)
        btn.click()
    @staticmethod
    async def Goon(poco):
        btn = None
        while not isinstance(btn, UIObjectProxy):
            try:
                btn = poco("Btn_Confirm")
            except:
                time.sleep(1)
        btn.click()
    @staticmethod
    async def ChapterOne(poco):
        screensize=poco.get_screen_size()
        await Ninja.Gamein(poco)
        time.sleep(5)
        # add assert 
        print("Button exist?")
        if poco(name="Img_Logo").wait(5).exists():
            poco(name='Img_Logo').click()
            time.sleep(1)
            if poco(name='Btn_Exit').wait(1).exists():

                poco(name='Btn_Exit').click()
        time.sleep(3)
        await Ninja.Skip1(poco)
        time.sleep(3)
        await Ninja.Skip2(poco)
        time.sleep(3)
        await Ninja.ExploreTime(poco)
        time.sleep(2)
        await Ninja.ChapterPage(poco)
        time.sleep(1)
        await Ninja.ChapterIn(poco)
        time.sleep(6)
        NodeInfo= PocoUIInfo(type='Image',name='Img_Hand') 
        await Ninja.PickGoods(poco,NodeInfo=NodeInfo,ScreenSize=screensize)
        log("Game in First  {:-^30}".format("chatper one"))
        await Ninja.ChoiceSkill(poco,screensize)
        await Ninja.ConfirmSkill(poco,screensize)
        return True
async def HomePage(poco):
    await Ninja.Gamein(poco)
    time.sleep(5)
    # add assert 
    print("Button exist?")
    if poco(name="Img_Logo").wait(5).exists():
        poco(name='Img_Logo').click()
        time.sleep(1)
        if poco(name='Btn_Exit').wait(1).exists():

            poco(name='Btn_Exit').click()
    time.sleep(3)
    await Ninja.Skip1(poco)
    time.sleep(3)
    await Ninja.Skip2(poco)
    time.sleep(3)
    await Ninja.ExploreTime(poco)
    time.sleep(2)
    await Ninja.ChapterPage(poco)
    time.sleep(1)
    await Ninja.ChapterIn(poco)
    time.sleep(2)
    log("Game in First  {:-^30}".format("chatper one"))
    # time.sleep(2)
    asyncio.run(Ninja.ChoiceSkill(poco,screensize))
    asyncio.run(Ninja.ConfirmSkill(poco,screensize))
if __name__=="__main__":
    StorePath = 'C:\\Users\\happyelements\\workstation\\UnityPocoProject\\Storage'
    path = MakeFloader(StorePath)
    floder = FloderInstance()
    logpath = MakeFloader(os.path.join(StorePath, floder))
    print(logpath)
    linkinfo = LinkInfo(connect_url=['android://127.0.0.1:5037/35b1a832?cap_method=MINICAP&touch_method=MAXTOUCH'], temp_logdir = logpath, package_name='com.oceangames.ninja.gp')
    pocoinfo = PocoInfo(android_poco_retry_cnt=3, android_poco_sleep_time=3, use_airtest_input=True, poco="UnityPoco")
    storefunc(func=StorePict,path=logpath)
    storefunc(func=store, path=logpath)

    poco = get_link(linkinfo, pocoinfo, restart=True)
    screensize=poco.get_screen_size()
    asyncio.run(HomePage(poco))
    NodeInfo= PocoUIInfo(type='Image',name='Img_Hand')
    # try:
    #     poco('Img_Hand',type='Image').wait_for_appearance()
    # except PocoTargetTimeout:
    #     # bugs here as the panel not shown
    #     raise
    poco('Img_Hand',type='Image').wait(1)
    asyncio.run(Ninja.PickGoods(poco,NodeInfo=NodeInfo,ScreenSize=screensize))
    log("Game in First  {:-^30}".format("chatper one"))
    # time.sleep(2)
    asyncio.run(Ninja.ChoiceSkill(poco,screensize))
    asyncio.run(Ninja.ConfirmSkill(poco,screensize))
    
    

    

