import os, json, datetime
from . import kakao01 as k1

# 토큰을 갱신하는 코드는 교안에서 설명한 로직이랑 같습니다. 다만, 다른 파일에서 모듈로 가져가 사용할 것이기 때문에 맨 아래의 함수 실행 코드들은 주석 처리했습니다.

def load_tokens(filename):
    #os.chdir('E:/Mark12/testArchive/json_Archive')
    #os.chdir('./resources/json/')
    with open('./resources/json/' + filename, 'r') as fs:
        return json.load(fs)

def save_tokens(filename, tokens):
    with open('./resources/json/' + filename, 'w') as fs:
        json.dump(tokens, fs)
        print('saved!')

def refresh_tokens(app_key, filename):
    tokens = load_tokens(filename)
    print(tokens)
    data = {
        "grant_type":"refresh_token",
        "client_id":app_key,
        "refresh_token":tokens['refresh_token']
    }
    url = 'https://kauth.kakao.com/oauth/token'
    
    res = requests.post(url, data=data)
    now = datetime.datetime.now().strftime('%Y%m%dd_%H%M%S')
    new_filename = filename + '.' + now
    if res.status_code != 200:
        print('Error because ', res.json())
    else:    
        os.rename('./resources/json/' + filename, new_filename)
        print('백업 파일 생성 완료')
        tokens['access_token'] = res.json()['access_token']
        save_tokens(filename, tokens)
        print('업데이트 완료')

#codes = load_codes('initCode.json')
#print(load_tokens('tokens.json'))
#refresh_tokens(codes['client_id'], 'tokens.json')
#print(load_tokens('tokens.json'))