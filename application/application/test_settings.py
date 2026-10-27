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

# 직원 로그인·화면 검사용
INSTALLED_APPS += ['django.contrib.sessions', 'django.contrib.messages']
MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'application.middleware.XForwardedForMiddleware',
]
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [__import__('pathlib').Path(__file__).resolve().parent.parent / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': ['django.template.context_processors.request']},
}]
INSTALLED_APPS += ['django.contrib.staticfiles']
STATIC_URL = '/static/'
STAFF_PASSWORD = 'staff-test-password'
