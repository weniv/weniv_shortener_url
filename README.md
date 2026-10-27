# weniv.link - URL 단축 서비스

위니브에서 개발한 심플한 URL 단축 서비스입니다.

## 주요 기능

- **URL 단축**: 긴 URL을 6자리 단축 URL로 변환
- **중복 처리**: 동일한 URL에 대해 기존 단축 URL 재사용
- **QR 코드**: 단축 URL의 QR 코드 생성 및 다운로드
- **커스텀 링크**: 관리자용 커스텀 단축 URL 생성
- **API 제공**: RESTful API 엔드포인트 지원
- **레이트 리미팅**: 악용 방지를 위한 API 호출 제한
- **위룸 공개 주소**: `weniv.link/r/<주소 이름>[/<하위 페이지>]`(예: `weniv.link/r/km-482-731`)를 위니버시티 `/r/…`로 연결. 이름 발급·변경·공개 여부·자동 탐색 제한은 위니버시티가 관리하며, 기존 단축 링크·교재 번호 주소와 겹치지 않습니다. 302·no-store로 연결하며 이 단순 연결에는 IP 횟수 제한을 적용하지 않습니다.

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
MODE=dev  # dev 또는 prod. DEBUG는 dev에서만 켜진다 (운영에서 켜면 오류 화면에 소스·내부 주소가 나온다)
BASE_NAME=weniv.link
ALLOWED_HOSTS=weniv.link,localhost,127.0.0.1
STAFF_PASSWORD=  # 직원용 이름 지정 단축(/staff/shorten_url) 비밀번호. 비우면 직원 페이지를 쓸 수 없다

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

## 배포

- `master`에 push하면 GitHub Actions가 서버에서 `git pull` → `docker compose build` → `docker compose up -d`(새 이미지를 먼저 만든 뒤 바꿔 끼움)를 한다.
- 앱 컨테이너는 root가 아닌 `app`(uid·gid 10001)으로 돈다(`no-new-privileges`, 모든 커널 권한 뺌). 정적 파일 볼륨 `shortener_static_volume`이 예전 root 소유라면 처음 한 번 바꾼다:
  `docker run --rm -u 0 -v shortener_static_volume:/v alpine chown -R 10001:10001 /v`
- `.env`는 이미지에 넣지 않고(`.dockerignore`) compose `env_file`로만 넘긴다.
- DB는 슈퍼유저가 아닌 앱 전용 계정으로 붙는다. 만드는 법은 `deploy/app-db-role.sql` 머리말(비밀번호는 저장소에 두지 않는다).

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
