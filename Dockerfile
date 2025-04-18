FROM python:3.12-slim

WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치를 위한 requirements.txt 복사
COPY application/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY application/ .

## 정적 파일 수집
#RUN python manage.py collectstatic --noinput

EXPOSE 9103

# 컨테이너가 시작될 때 실행할 명령
CMD ["sh", "-c", "python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:9103 --workers 1 application.wsgi:application"]