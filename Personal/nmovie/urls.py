from django.urls import path
from . import views

app_name = 'nmovie'

urlpatterns = [
    path('index/', views.index, name="index"),
    path('receive/' , views.receiveAndSearch, name='receive'),
    path('search/', views.selected, name='selected'),
    path('research/', views.research, name='collect'),
    path('kakao/', views.send_kakao, name='kakao'),
]