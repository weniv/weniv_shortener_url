from django.urls import path

from . import views

app_name = 'shortener'
urlpatterns = [
    path('', views.index, name='index'),
    path('<str:shorten_url_code>/', views.redirect_original_url, name='redirect_original_url'),
    # 직원 전용 url 줄이기 기능
    path('staff/shorten_url', views.staff_index, name='staff_index'),
    path('api/generate', views.api_generate_shorten_url, name='generate_shorten_url'),

]
