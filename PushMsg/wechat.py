from abc import ABC, abstractmethod
import requests
import os
import time
import re
import json

class LoadConfig:
    
    def __init__(self) -> None:
        pass

    def loadcfg(self, cfg_path):
        with open(file=cfg_path, mode='r', encoding='utf-8') as f:
            origin = f.read()
        result = json.loads(origin)
        return result
    
class AccessToken:

    def __set_name__(self, owner, name):
        self.private_name = '_' + name

    def __get__(self, obj, objType=None):
        return getattr(obj, self.private_name)
    
    def __set__(self, obj, value):
        setattr(obj, self.private_name, value)

class GetAccessToken:
    corpid = AccessToken()
    secret = AccessToken()
    
    def __init__(self, corpid: any, secret: any) -> None:
        self.corpid = corpid
        self.secret = secret

    @property
    def access_token(self) -> str:
        url = f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self._corpid}&corpsecret={self._secret}'
        response = requests.get(url=url).json()
        return response
    
class Validtor(ABC):
    
    @abstractmethod
    def is_valid(self):pass

class TimeValidtor(Validtor):
    def __init__(self) -> None:pass

    def is_valid(self, in_file):
        pre_time_sec = os.stat(in_file).st_mtime
        current_time_sec = time.time()
        if current_time_sec - pre_time_sec > 7000:
            return True
        else:
            return False

class FileValidtor(Validtor):
    def __init__(self) -> None:pass

    def is_valid(self, infile):
        with open(file=infile, mode='r', encoding='utf-8') as f:
            text_content = f.read()
        pattren = re.compile(f'"access_token"')
        if pattren.search(text_content):
            return True
        else:
            return False

class AccessTokenRd:
    def __init__(self) -> None:pass
    
    def writting(self, file_name, content):
        with open(file=file_name, mode='w+', encoding='utf-8') as f:
            f.write(content)
    
    def reading(self, file_name):
        with open(file=file_name, mode='r', encoding='utf-8') as f:
            read_content = f.read()
            return read_content

class Push(ABC):

    @abstractmethod
    def push_message(self, agent_id: int, to_who: str):pass

class TextMessage(Push):

    def __init__(self) -> None:pass

    def push_message(self, access_token: any, agent_id: int, to_who: str, message_content: any):
        url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}&debug=1'
        data_body = {
            "touser" : to_who,
            "msgtype" : "text",
            "agentid" : agent_id,
            "text" : {
                "content" : message_content
            },
            "safe":0
        }
        response = requests.post(url=url, json=data_body).text
        return response

class ImageMessage(Push):pass