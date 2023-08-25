from django.urls import path
from rest_framework import routers

from apps.app_shortener_url import views

# router = routers.DefaultRouter()
#
# router.register("post", viewSets.UrlShortnerViewSet)
urlpatterns = [
    # path("home/", views.home, name="home"),
    path("shortner/", views.convert_url, name="convert_url"),
    path("<str:short_url>", views.redirect_url, name="redirect_url"),
]
