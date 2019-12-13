from django.urls import path
from . import views

app_name = 'usermatch'

urlpatterns = [
    path('', views.home_view, name='home'), # 검색 화면
    # path('usersearch', views.usersearchresult_view, name='usersearch'), # 검색 결과 화면
    path('recentmatch_summary', views.recentmatch_summary, name='recentmatch_summary'), # 검색 결과 화면
    path('bymatch', views.match_detail, name='bymatch'),
]
