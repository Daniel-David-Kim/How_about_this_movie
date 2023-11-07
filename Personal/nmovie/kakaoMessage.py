# 만들었던 kakao02, naver_movies를 모듈로 불러옵니다.
import os
from . import kakao02 as k2
import json, requests

main_url = "https://movie.naver.com/"
tokens = k2.load_tokens('tokens.json')
url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
headers = {"Authorization":"Bearer " + tokens['access_token']}

def execute_msg(msg, link):
    template = {
         "object_type":"text",
         "text":msg,
         "link":{
             "web_url":main_url
         }
    }

    data = {
        "template_object":json.dumps(template, ensure_ascii=False)
    }

    res = requests.post(url, headers=headers, data=data)
    if res.status_code != 200:
        print('Error! because ', res.json())
        return 404
    else:
        print('메세지 전송 완료!')
        return 200

