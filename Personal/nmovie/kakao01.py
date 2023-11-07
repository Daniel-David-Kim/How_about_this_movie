import json, os, requests

# A. code와 client_id, grant_type, redirect_uri를 json 파일에 담아서 1 경로에 2의 filename으로 넣었습니다. 
def load_codes(filename): 
    #os.chdir('./resources/json') #1
    with open('./resources/json/' + filename, 'r') as fs: #2
        return json.load(fs)

# data는 요청에 같이 넣어서 보낼 데이터입니다. 요청을 해서 토큰을 가져오는 함수입니다.
def get_tokens(data):
    url = "https://kauth.kakao.com/oauth/token"
    res = requests.post(url, data=data)
    if res.status_code != 200:
        print("Error because ", res.json())
    else:
        print(res.json())
        return res.json()

# 이건 가져온 토큰을 저장하는 함수입니다.
def save_tokens(filename, tokens):
    with open('./resources/json/' + filename, 'w') as fs:
        json.dump(tokens, fs)
        print('saved!')
        
# 이 모듈은 url로 코드를 받아왔을 때 딱 한 번만 사용합니다. 사용하고 난 뒤에는 잘못 실행해서 꼬이는 일이 없도록 밑의 실행코드들을 다 주석 처리했습니다.

# A 함수를 불러와서 data 변수로 저장합니다.
#data = load_codes('initCode.json')

# data 변수를 넣어서 요청해 토큰을 가져옵니다.
#tokens = get_tokens(data)

# 가져온 토큰을 저장합니다.
#save_tokens('tokens.json', tokens)

# 토큰이 저장되면 메세지가 출력됩니다.
#print('one!')