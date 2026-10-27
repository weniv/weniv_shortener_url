from django.urls import path, re_path

from . import views

app_name = 'shortener'
urlpatterns = [
    path('', views.index, name='index'),
    # 위룸 주소 이름은 위니버시티에서 관리한다. 기존 단축 코드·교재 번호와 겹치지 않는 /r/ 아래로 연결한다.
    re_path(r'^r/(?P<slug>[A-Za-z0-9][A-Za-z0-9-]{1,38}[A-Za-z0-9])(?:/(?P<page_id>[a-z0-9]{6,32}))?/?$',
            views.redirect_weroom_short_link, name='redirect_weroom_short_link'),
    # 스터디 초대 짧은 링크 (30분, 위니버시티가 발급·만료를 관리한다): weniv.link/s/abc234 → 위니버시티 초대 화면
    re_path(r'^s/(?P<code>[0-9A-Za-z]{6})/?$', views.redirect_study_short_link, name='redirect_study_short_link'),
    # 숫자(·하이픈)로만 된 코드는 위니버시티 교재 단축 주소 (weniv.link/482913 → weniversity.co.kr/b/482913/)
    re_path(r'^(?P<code>[0-9]+(?:-[0-9]+)*)/?$', views.redirect_book_short_code, name='redirect_book_short_code'),
    path('<str:shorten_url_code>/', views.redirect_original_url, name='redirect_original_url'),
    # 직원 전용 url 줄이기 기능
    path('staff/shorten_url', views.staff_index, name='staff_index'),
    path('staff/login', views.staff_login, name='staff_login'),
    path('api/generate', views.api_generate_shorten_url, name='generate_shorten_url'),

]
