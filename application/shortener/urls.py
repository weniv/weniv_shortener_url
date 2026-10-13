from django.urls import path, re_path

from . import views

app_name = 'shortener'
urlpatterns = [
    path('', views.index, name='index'),
    # 숫자(·하이픈)로만 된 코드는 위니버시티 교재 단축 주소 (weniv.link/482913 → weniversity.co.kr/b/482913/)
    re_path(r'^(?P<code>[0-9]+(?:-[0-9]+)*)/?$', views.redirect_book_short_code, name='redirect_book_short_code'),
    path('<str:shorten_url_code>/', views.redirect_original_url, name='redirect_original_url'),
    # 직원 전용 url 줄이기 기능
    path('staff/shorten_url', views.staff_index, name='staff_index'),
    path('api/generate', views.api_generate_shorten_url, name='generate_shorten_url'),

]
