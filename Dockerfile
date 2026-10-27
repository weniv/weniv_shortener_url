FROM python:3.12-slim

WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 앱은 root가 아닌 전용 사용자로 돈다 (uid·gid 10001)
RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --home-dir /app --no-create-home --shell /usr/sbin/nologin app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Python 패키지 설치를 위한 requirements.txt 복사
COPY application/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사 (코드는 root 소유·읽기 전용으로 둔다)
COPY application/ .

EXPOSE 9103

# 정적 파일 디렉토리: collectstatic이 쓰는 곳이라 앱 사용자 소유.
# 이미 있는 볼륨(shortener_static_volume)은 처음 한 번 `chown -R 10001:10001`이 필요하다 (README '배포').
RUN mkdir -p /app/staticfiles && chown app:app /app/staticfiles

USER app

# 컨테이너가 시작될 때 실행할 명령 - collectstatic은 컨테이너 실행 시점에 수행
CMD ["sh", "-c", "python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:9103 --workers 1 application.wsgi:application"]
