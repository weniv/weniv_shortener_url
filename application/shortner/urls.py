from django.urls import path

from . import views

app_name = 'shortner'
urlpatterns = [
    path('', views.index, name='index'),
]
