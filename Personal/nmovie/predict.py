import joblib, re
from konlpy.tag import Okt as okt
import konlpy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
#from NaverMovie import execute
from functools import reduce
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import matplotlib.image as img
from collections import Counter as counter
#from kakaoMessage import execute_msg

# 영화 예측 -> 0 : 부정 / 1 : 긍정
# 이 메서드 없으면 벡터라이저 파일을 업로드 못함! 
# 장고에서는 manage.py에다가 넣어주어야 함!
def divide_morphs(txt):
    nlp = okt()
    return nlp.morphs(txt)

def pre_ready(text, tfidfVec):
    temp = text
    temp = re.compile(r'[ㄱ-ㅣ가-힣]+').findall(temp)
    temp = [' '.join(temp)]
    return tfidfVec.transform(temp)

def draw_wc(worddict):
    font_path = './resources/font/ibmplexsanskr_regular.ttf'
    wc = WordCloud(font_path, background_color='beige', width=700, height=500)
    c = wc.generate_from_frequencies(worddict)
    c.to_file('./static/img/result_wordcloud.jpg')
    #plt.figure(figsize=(8, 8))
    #plt.imshow(c)
    #plt.axis('off')
    #plt.show()

def entire_predict(ratingStar, result_data):
    # gridSearch version : 미리 훈련된 모델과 벡터라이저를 가져옵니다.
    model = joblib.load('./resources/model/rand/best_review_classifier.pkl')
    tfidfVec = joblib.load('./resources/model/rand/tfidfVectorizer_rand.pkl')

    # 영화 제목을 검색하여 원하는 영화를 선택한 후, 그 영화에서 원하는 만큼의 리뷰 데이터를 가져옵니다.
    #ratingStar, result_data = execute()
    result_data = result_data[1][1:]

    print('\n\n분석이 끝날 때까지 잠시만 기다려주세요......')
    pos = []
    neg = []
    posCount = 0
    negCount = 0
    entire = len(result_data)

    for i in result_data:
        ready = pre_ready(i, tfidfVec)
        res = model.predict(ready)
        if res == 0: # 0은 부정
            neg.append(i)
            negCount += 1
        else:
            pos.append(i)
            posCount += 1

    collect = ''
    tree = ''
    resStr = ''
    print('='*50, '결과', '='*50, end='\n\n')
    plt.figure(figsize=(8, 8))
    posPercent = (posCount/entire) * 100
    tree = '긍정적인 의견 : {}%     /     부정적인 의견 : {}%'.format(posPercent, 100-posPercent)
    print(tree)
    if 0 <= posPercent < 25:
        resStr += '노잼!\n으헝헝 노잼! 이걸 보느니 차라리 아무것도 안하고 말지...!!!!'
        #render = img.imread('./resources/imgs/jo.jpg')
    elif 25 <= posPercent < 75:
        resStr += '볼까? 말까?\n'
        #render = img.imread('./resources/imgs/gomin.png')
        if 25 <= posPercent < 50:
            resStr += '관람객의 의견은 {} 부정적인 편입니다.....'.format('대체로' if 25 <= posPercent < 35 else '')
        else:
            resStr += '관람객의 의견은 {} 긍정적인 편입니다~'.format('대체로' if 65 <= posPercent < 75 else '')
    elif 75<= posPercent <= 100:
        #render = img.imread('./resources/imgs/wow.jpg')
        resStr += '어머! 이건 꼭 사야 해!\n꼭 보세요! 무조건 보세요!'
    print(resStr)
   # plt.imshow(render)
    #plt.axis('off')
    #plt.show()
    #print('\n')
    collect += resStr + '\n\n' + tree + '\n\n' 

    if 0 <= posPercent < 50:
        longline = reduce(lambda x, y : x + ' ' + y, neg)
    else:
        longline = reduce(lambda x, y : x + ' ' + y, pos)
    longline = re.sub('[^가-힣ㄱ-ㅎㅏ-ㅣ]', ' ', longline)
    nlp = okt()
    nouns = nlp.nouns(longline)

    vcount = counter(nouns)
    worddict = dict()
    mc100 = vcount.most_common(100)
    for group in mc100:
        if group[1] > 2:
            worddict[group[0]] = group[1]

    starStr = ''
    #print('이 영화를 시청한 사람들의 평점입니다.')
    for star in ratingStar: starStr += star
    #print('관람객들의 리뷰에 가장 많이 등장한 단어들입니다.')
    print(starStr)
    draw_wc(worddict)
    collect += starStr
    return [posCount, posPercent, ratingStar, collect]
