'''
    construct the connection from python to device
    |                       **Case**
    |
    | **Poco**  |  **UserInfo** | **CaseInfo** | **logger**
    |
    | **logger**
'''
import sys, os
from pathlib import Path
this_path = os.path.split(os.path.realpath(__file__))[0]

sys.path.append(str(Path(this_path).parent)) # add parent floder
sys.path.append(str(Path(this_path).parent.parent))

from airtest.core.api import auto_setup, stop_app, sleep, start_app
from airtest.core.android import Android
from airtest.core.ios import IOS
from airtest.core.android.adb import ADB
from poco.drivers.unity3d import UnityPoco
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
from airtest.core.helper import log
from retry import retry

from airtest.core.android.adb import AdbError

from typing import Union, Tuple
from functools import wraps
from Ninja.profile import LinkInfo, PocoInfo

def wraplog(text):
    def execute(func):
        def logging(*args, **kw):
            log("{:-^100}".format(text))
            try:
                result = func(*args, **kw)
            except AdbError as e:
                log("AdbError:detail as follow :{}".format(e))
            except RuntimeError as e:
                log("error detail is {}".format(e))
            log("{} has been executed!".format(text))
            if result:
                return result
            
        return logging
    return execute

def get_link(info: LinkInfo, pocoinfo: PocoInfo, restart:bool=True)-> Tuple[str,Union[UnityPoco, AndroidUiautomationPoco]]:
    @wraplog("Init----Device&StorePath")
    def init_app(urls, logdir, app, restart):
        # init_link
        auto_setup(__file__, devices=urls, logdir=logdir)
        if restart:
            stop_app(app)
            sleep(1)
            start_app(app)
            sleep(15)

    @wraplog("init_Android_Poco")
    @retry(tries=pocoinfo.android_poco_retry_cnt, delay= pocoinfo.android_poco_sleep_time)
    def init_android_poco(**kw):
        log("init android poco")
        android_poco = AndroidUiautomationPoco(**kw)
        log("inited android poco")
        return android_poco
    @wraplog('init_Poco')
    def get_poco(pocoinfo: PocoInfo):
        if pocoinfo.Poco.startswith('Android'):
            return init_android_poco(use_airtest_input = pocoinfo.use_airtest_input, screenshot_each_action=False)
        else:
            return UnityPoco()
    
    init_app(info.connect_url,info.temp_logdir,app=info.package_name, restart=restart)
    
    return get_poco(pocoinfo= pocoinfo)


