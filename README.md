# weniv.link - URL 단축 서비스

위니브에서 개발한 심플한 URL 단축 서비스입니다.

## 주요 기능

- **URL 단축**: 긴 URL을 6자리 단축 URL로 변환
- **중복 처리**: 동일한 URL에 대해 기존 단축 URL 재사용
- **QR 코드**: 단축 URL의 QR 코드 생성 및 다운로드
- **커스텀 링크**: 관리자용 커스텀 단축 URL 생성
- **API 제공**: RESTful API 엔드포인트 지원
- **레이트 리미팅**: 악용 방지를 위한 API 호출 제한

## 기술 스택

- **Backend**: Django 5.0, Python 3.x
- **Database**: PostgreSQL
- **Cache**: Redis
- **Frontend**: HTML5, CSS3, JavaScript
- **Deployment**: Docker, Nginx

## 설치 및 실행

### Docker Compose 사용 (권장)

```bash
# 저장소 클론
git clone <repository-url>
cd shortener_url

# 환경 변수 설정
cp .env.example .env
# .env 파일을 수정하여 필요한 설정을 입력하세요

# 컨테이너 빌드 및 실행
docker-compose up -d

# 데이터베이스 마이그레이션
docker-compose exec web python manage.py migrate

# 정적 파일 수집
docker-compose exec web python manage.py collectstatic --noinput
```

### 로컬 개발 환경

```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
cd application
pip install -r requirements.txt

# 데이터베이스 설정 (PostgreSQL과 Redis가 미리 설치되어야 함)
python manage.py migrate

# 개발 서버 실행
python manage.py runserver
```

## 환경 변수

`.env` 파일에 다음 변수들을 설정해야 합니다:

```env
# 기본 설정
SECRET_KEY=your-secret-key-here
MODE=dev  # dev 또는 prod
BASE_NAME=weniv.link

# 데이터베이스
DB_NAME=shortener_db
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
```

## API 사용법

### URL 단축 생성

```bash
curl -X POST http://localhost:8000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/very/long/url"}'
```

**응답:**
```json
{
  "shorten_url": "https://weniv.link/ABC123"
}
```

### 리다이렉트

단축 URL에 접속하면 원본 URL로 자동 리다이렉트됩니다:
```
https://weniv.link/ABC123 → https://example.com/very/long/url
```

## 주요 구조

```
application/
├── application/          # Django 프로젝트 설정
├── shortener/           # 메인 앱
│   ├── models.py       # 데이터 모델
│   ├── views.py        # 비즈니스 로직
│   └── urls.py         # URL 라우팅
├── static/             # 정적 파일
├── templates/          # HTML 템플릿
└── requirements.txt    # 의존성 목록
```

## 핵심 기능 설명

### URL 단축 알고리즘
- SHA256 해시 + Base64 인코딩으로 6자리 코드 생성
- 충돌 방지를 위한 재시도 로직 (최대 10회)
- 동일 URL에 대한 중복 생성 방지

### 캐싱 전략
- Redis를 사용한 단축 URL 캐싱
- 빠른 리다이렉트 성능 제공

### 레이트 리미팅
- 일반 요청: 8회/분
- 리다이렉트: 30회/분
- IP 기반 제한

## 라이선스

MIT License

## 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 문의

- Website: [weniv.co.kr](https://weniv.co.kr)
- Email: paul-lab@naver.com

---

© 2024-2025 WENIV. All rights reserved.