from bs4 import BeautifulSoup
import pandas as pd
import requests, lxml, re
from functools import reduce

# 가장 기본이 되는 네이버 영화 사이트입니다.
root = 'https://movie.naver.com'
# 평점 사이트에 접속할 때 필요한 url입니다.
comment_root = 'https://movie.naver.com/movie/bi/mi'

# 네이버 영화에 연결합니다. 검색어를 가지고 검색하는 방법, url로 목표한 사이트에 접속하는 것 두가지 방법이 있습니다.
def getConnection(query=None, ipUrl=None):
    url = 'https://movie.naver.com/movie/search/result.naver?query=%s' % (query)
    if ipUrl == None: ipUrl = url
    data = {'User-Agent':'Mozilla/5.0'}
    res = requests.get(ipUrl, data=data)
    if res.status_code == 200: 
        html = res.text
        soup = BeautifulSoup(html, 'lxml')
        return html, soup

# 검색 결과로 나온 영화 목록들이 더보기 항목이 있는지 확인합니다. (더보기가 있으면 그 주소로 이동해 있는 모든 영화들을 리스트로 가져옵니다.)
def find_more_list(soup):
    more_list = soup.find('a', class_='more_list')
    if more_list.get_text() == '더 많은 영화 보기': return True, root + more_list.attrs['href']
    else: return False, None

# 네이버 영화 사이트에 들어가서 키워드로 검색하여 결과로 나온 영화 목록들을 리스트로 반환합니다.
def get_search_list(soup, *moreTupl):
    search_links = []
    search_titles = []
    if moreTupl[0] == True:
        html2, soup2 = getConnection(ipUrl=moreTupl[1])
        soup = soup2
    while True:
        pages = soup.find('div', class_='pagenavigation')
        if pages is not None: 
            pages_table = pages.select('table tr td a')
            next_page = pages_table[-1] if pages_table[-1].get_text() == '다음' else None
        
        search_list = soup.find('ul', class_='search_list_1').select('li > dl > dt > a')
        search_links += [root + a['href'] for a in search_list]
        search_titles += [a.get_text() for a in search_list]
        
        if (pages == None) or (next_page == None): break
        else: 
            next_page_url = root + next_page['href']
            html3, soup3 = getConnection(ipUrl=next_page_url)
            soup = soup3
        
    df = pd.DataFrame([search_titles, search_links], index=['title', 'link']).T
    return df

# 검색한 영화들을 보여주고, 어떤 영화릐 리뷰를 수집할지 선택하게 합니다.
def select_from_lists(lists):
    print('*'*30, '총 %d건의 결과가 검색되었습니다.' % (len(lists)), '*'*30, end='\n\n')
    while True:
        try:
            print('='*25, '다음 중에서 원하시는 영화의 번호를 입력해주세요.', '='*25)
            for idx, movie in enumerate(lists.values): print(idx+1, '  :  ', movie[0])
            sel = int(input('===> '))
            break
        except Exception as e:
            print('정수만 입력해주세요')
            continue
    return lists.iloc[sel-1]


def collect_comments1(target):
    # 선택한 영화의 페이지로 이동합니다.
    html, soup = getConnection(ipUrl=target['link'])
    
    # 별점이 있으면 추출합니다.
    actualPoint = soup.find('a', id='actualPointPersentWide')
    if actualPoint != None: 
        actualPoint = actualPoint.findAll('em')
        actualPoint = [ele.get_text() for ele in actualPoint]
        actualPoint = '관람객 평점 : ' + ''.join(actualPoint) if ''.join(actualPoint).strip() != '' else '관람객 평점 없음'
    else: actualPoint = '관람객 평점 없음'
    netizenPoint = soup.find('a', id='pointNetizenPersentWide')
    if netizenPoint != None: 
        netizenPoint = netizenPoint.findAll('em')
        netizenPoint = [ele.get_text() for ele in netizenPoint]
        netizenPoint = '네티즌 평점 : ' + ''.join(netizenPoint) if ''.join(netizenPoint).strip() != '' else '네티즌 평점 없음'
    else: netizenPoint = '네티즌 평점 없음'
    ratings = [actualPoint, netizenPoint]
    
    #result_list = [['rank', 'content', 'score']] # rank : 공감 순위 / content : 리뷰 내용 / score : 별점
    
    # tab5가 (다섯번째 탭) 평점입니다. 그 탭을 선택합니다.(평점 탭 번호는 5번으로 고정입니다. 다른 탭들이 없어도 5번입니다.)
    tab05_review = soup.find('a', class_='tab05')
    if tab05_review is not None: 
        tab05_url = comment_root + tab05_review.attrs['href'][1:]
        html2, soup2 = getConnection(ipUrl=tab05_url)
       
        # 평점은 iframe에 담겨 있습니다. 그 iframe을 찾습니다. (리뷰가 없어도 이 프레임은 있습니다.)
        iframe = soup2.find('iframe', id='pointAfterListIframe')
        if iframe != None:                                                                        # 1
            ifr_link = root + iframe.attrs['src'] # iframe의 링크 추출 && root주소와의 조합
            #print(ifr_link) 
            # 추출한 iframe의 주소에 접속합니다.
            html3, soup3 = getConnection(ipUrl=ifr_link)
            
            # iframe에 리뷰가 있는지 확인합니다. 정렬 체크박스조차 없으면 리뷰가 없는 것입니다.
            checked = soup3.find('div', id='orderCheckbox')
            if checked is not None:                                                             # 2
                # 관람객의 공감을 가장 많이 받은 순위대로 정렬했는지 확인합니다. 
                checked = checked.find('ul', class_='sorting_list').find('li', class_='on').find('a')
                if checked.get_text() == '공감순':                                               # 3
                    total = soup3.find('div', class_='score_total')
                    
                    if total != None:                                                           # 4
                        total = total.find('strong').find('em').get_text()
                        total = re.sub(',', '', total)
                        total = int(total)
                        
                        return [total, soup3, ratings]
                    
                    else: 
                        print('관람객 총 리뷰 건수를 찾을 수 없습니다.')  # 4
                else: 
                    print('공감 순이 아닙니다. 다시 확인해주세요.')  # 3
            else: 
                #print('이 영화는 리뷰가 없습니다.')  # 2
                return [0, '이 영화는 리뷰가 없습니다.', ratings]
        else: 
            print('평점을 찾지 못했습니다 : cannot find iframe')    # 1    
                        
                                             
def collect_comments2(nums, moveTo, soup3, ratings):
    # 페이지들을 이동할 수 있는 페이지 탭을 찾습니다.
    
    #실험용. 원래 위에 있던 거다.
    result_list = [['rank', 'content', 'score']] # rank : 공감 순위 / content : 리뷰 내용 / score : 별점
    
    paging = soup3.find('div', class_='paging')
    if paging != None:                                                     # 5
        rank = 0
        page = 1
        while True:
            nextPage = False
            paging = paging.find('div').findAll('a')
            # 페이지를 넘기기 위해 '다음' 버튼을 찾습니다.
            if paging[-1].get_text() == '다음':
                nextPage = True
                next_url = root + paging[-1].attrs['href'] 
            # 페이지가 하나밖에 없거나 마지막 페이지일시 처리입니다.
            else: print('이 영화의 리뷰의 마지막 페이지입니다')

            # 공통 처리 로직(리뷰 데이터 수집)
            result = soup3.find('div', class_='score_result')
            if result != None:
                result = result.find('ul').findAll('li')
                for li in result:
                    rank += 1
                    result = [[rank, re.sub('\s', ' ', li.find('div', class_='score_reple').find('span').get_text()).strip(), li.find('div', class_='star_score').find('em').get_text()]]
                    result_list += result
                    if rank == nums: break
            else: print('리뷰를 찾을 수 없습니다.')

            if (page == moveTo) and (rank == nums): # 요청한 갯수가 채워지면 수집을 종료합니다.
                print('요청하신 수의 데이터를 수집했습니다.')
                print('갯수 : ', rank, ', 탐색한 페이지 수 : ', page)
                break
            elif nextPage == True: # 다음 페이지 버튼이 있을 시
                # 현 페이지에서 리뷰를 다 모았으면 다음 페이지로 이동합니다.
                html3, soup3 = getConnection(ipUrl=next_url)
                paging = soup3.find('div', class_='paging')
                page += 1
            else: break

        # 데이터 수집을 정상적으로 완료했으면 데이터프레임으로 반환합니다.
        return [ratings, pd.DataFrame(result_list)]
    else: 
        print('페이지 항목을 찾을 수 없습니다.')  # 5
                   
def inputName():
    return input('검색하실 영화 제목을 입력하세요~! ---> ')

def new_execute():
    query = inputName()
    html, soup = getConnection(query=query)
    lists = get_search_list(soup, *find_more_list(soup))
    target = select_from_lists(lists)
    total, soup3, ratings = collect_comments1(target)
    
    if total != 0:
        print('총 %d건의 리뷰를 찾았습니다.' % total)                                  
        while True:
            try:
                nums = int(input('몇 건의 리뷰를 수집하시겠습니까? (더 많은 리뷰를 수집하실수록 예측 정확도가 향상됩니다.) ===> '))
                if nums > total: 
                    print('%d건보다 큰 값을 입력할 수 없습니다.' % total)
                    continue
                break
            except Exception as e: print('정수만 입력하세요.')

        moveTo = int(nums / 10) # 검색 결과를 찾기 위해 이동할 페이지 갯수
        # 딱 10 단위로 떨어지지 않으면 그 다음 페이지까지 탐색합니다.
        if nums % 10 > 0: moveTo += 1
        print('요청하신 %d건을 수집하기 위해 총 %d 페이지를 탐색합니다.' % (nums, moveTo))

        return collect_comments2(nums, moveTo, soup3, ratings)
    else:
        print(soup3)
        return [ratings, None]
