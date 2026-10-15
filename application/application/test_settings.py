"""외부 DB·Redis·운영 환경변수 없이 실행하는 연결 규칙 검사."""

SECRET_KEY = 'local-shortener-tests'
BASE_NAME = 'weniv.link'
WENIVERSITY_URL = 'https://weniversity.co.kr'
ALLOWED_HOSTS = ['testserver']
ROOT_URLCONF = 'application.urls'
INSTALLED_APPS = ['django.contrib.auth', 'django.contrib.contenttypes', 'shortener.apps.ShortenerConfig']
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
MIDDLEWARE = []
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
