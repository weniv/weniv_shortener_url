from django.urls import path

from . import views

app_name = 'shortener'
urlpatterns = [
    path('', views.index, name='index'),
    path('<str:shorten_url_code>/', views.redirect_original_url, name='redirect_original_url'),

]
