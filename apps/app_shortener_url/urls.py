from django.urls import path

from apps.app_shortener_url import views

urlpatterns = [
    # path("home/", views.home, name="home"),
    path("shortener/", views.convert_url, name="convert_url"),
    path("<str:short_url>", views.redirect_url, name="redirect_url"),
]
