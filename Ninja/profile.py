from pydantic import BaseModel, Field
from typing import Literal, List, Union
# formatting defination
class LinkInfo(BaseModel):
    connect_url: List[str]
    temp_logdir: Union[str,bool,None]=Field(default=None, description='The Path to store Log, pictures and Ui infos within executing task  Model is running temperory storage folder')
    package_name: str
    
class PocoInfo(BaseModel):
    android_poco_retry_cnt:int=3
    android_poco_sleep_time: int=2
    use_airtest_input:bool=True
    Poco:Literal["UnityPoco","AndroidPoco"]= 'UnityPoco'

class PocoUIInfo(BaseModel):
    type: Union[str,None] = None
    name: Union[str,None] = None
    text: Union[str,None] = None
    

class SourceMetric(BaseModel):
    retry_times: int =1
    signal: bool =False
    interval: int =2
    start_time: float =0.0

class DeviceInfo(BaseModel):
    link:LinkInfo
    poco:PocoInfo
    BasePth: str
    CaseRetry: int = 2
