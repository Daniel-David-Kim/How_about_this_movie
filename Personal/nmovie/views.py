from django.shortcuts import render
from django.http import HttpResponse
from . import NaverMovie as nm
from . import NaverMovieNeo as neo
from . import predict as pre
from . import kakaoMessage as kakao

# Create your views here.
mnane = None
entire_var = None
movie_list = None
selected_mid = None
mmsg = None
title = None
link = None

def index(request):
    return render(request, 'nmovie/index.html')

def receiveAndSearch(request):
    global movie_list, mname
    query = request.GET['moviename']
    mname = query
    if query == '' or query == None: 
        context = {'error_msg':'검색어를 입력해주세요.'}
        return render(request, 'nmovie/error.html', context)
    print('query : ', query)
    html, soup = nm.getConnection(query=query)
    lists = nm.get_search_list(soup, *nm.find_more_list(soup))
    movie_list = lists
    print(list(movie_list['title']))
    render_list = list(movie_list['title'])
   
    context = {'movie_list':render_list}
    return render(request, 'nmovie/select.html', context)
    
def selected(request):
    global selected_mid, title, link
    sel = request.GET['select']
    if sel.isdecimal() == False: 
        context = {'error_msg':'숫자를 입력해주세요.'}
        return render(request, 'nmovie/error.html', context)
    sel = int(sel)
    target = movie_list.iloc[sel-1]
    print('target : ', target['title'], target['link'])
    title = target['title']
    link = target['link']
    selected_mid = neo.collect_comments1(target) # total, soup3, ratings
    if selected_mid[0] == 0:
        context = {'error_msg':'리뷰를 찾을 수 없습니다.'}
        return render(request, 'nmovie/error.html', context)
    context = {'total':selected_mid[0]}
    return render(request, 'nmovie/want_number.html', context)

def research(request):
    global mmsg
    nums = request.GET['nums']
    if nums.isdecimal() == False: 
        context = {'error_msg':'숫자를 입력해주세요.'}
        return render(request, 'nmovie/error.html', context)
    nums = int(nums)
    moveTo = int(nums / 10)
    msg1 = '요청하신 %d건을 수집하기 위해 총 %d 페이지를 탐색합니다.' % (nums, moveTo)
    msg2 = '분석이 끝날 때까지 잠시만 기다려주세요......'
    ratingStar, result_data = neo.collect_comments2(nums, moveTo, selected_mid[1], selected_mid[2])
    
    posCount, posPercent, ratingStar, msg_90 = pre.entire_predict(ratingStar, result_data)
    mmsg = title + '\n\n' + msg_90
    contextFinal = {'posCount':posCount, 'posPercent':posPercent, 'ratingStar':ratingStar}
    return render(request, 'nmovie/result.html', contextFinal)

def send_kakao(request):
    resCode = kakao.execute_msg(mmsg, link)
    if resCode == 200: return render(request, 'nmovie/complete.html')
    else: 
        context = {'error_msg':'전송에 실패했습니다.....'}
        return render(request, 'nmovie/error.html', context)
