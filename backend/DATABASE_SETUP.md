# PostgreSQL 데이터베이스 설정 가이드

## 1. PostgreSQL 설치

### macOS (Homebrew)
```bash
brew install postgresql@15
brew services start postgresql@15
```

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### Windows
[PostgreSQL 공식 다운로드](https://www.postgresql.org/download/windows/)에서 설치 프로그램 다운로드

---

## 2. 데이터베이스 생성

```bash
# PostgreSQL 접속
psql postgres

# 또는 (사용자명 지정)
psql -U postgres
```

SQL 명령어 실행:
```sql
-- 데이터베이스 생성
CREATE DATABASE findyourstage;

-- 사용자 생성 (선택사항, 보안을 위해 권장)
CREATE USER fys_user WITH PASSWORD 'your_secure_password';

-- 권한 부여
GRANT ALL PRIVILEGES ON DATABASE findyourstage TO fys_user;

-- 종료
\q
```

---

## 3. 환경변수 설정

`backend/.env` 파일에 DATABASE_URL 추가:

```bash
# 기본 PostgreSQL 사용자로 연결
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/findyourstage

# 또는 생성한 사용자로 연결
DATABASE_URL=postgresql://fys_user:your_secure_password@localhost:5432/findyourstage
```

### URL 형식 설명
```
postgresql://[사용자명]:[비밀번호]@[호스트]:[포트]/[데이터베이스명]
```

---

## 4. 마이그레이션 생성 및 적용

### 초기 마이그레이션 생성
```bash
# 가상환경 활성화
source .venv/bin/activate

# 마이그레이션 파일 자동 생성
alembic revision --autogenerate -m "Initial migration: users, bookmarks, reviews, analytics tables"
```

### 마이그레이션 적용
```bash
# 최신 버전으로 업그레이드
alembic upgrade head
```

### 마이그레이션 되돌리기
```bash
# 한 단계 뒤로
alembic downgrade -1

# 특정 버전으로
alembic downgrade <revision_id>

# 모두 되돌리기
alembic downgrade base
```

---

## 5. 데이터베이스 스키마 확인

PostgreSQL에 접속하여 테이블 확인:

```bash
psql -U postgres -d findyourstage
```

```sql
-- 테이블 목록 보기
\dt

-- 특정 테이블 구조 보기
\d users
\d bookmarks
\d reviews
\d analytics

-- 데이터 확인
SELECT * FROM users;
```

---

## 6. 데이터베이스 스키마 상세

### users 테이블
- `id`: 사용자 고유 ID (PK, Auto Increment)
- `email`: 이메일 (Unique, Not Null)
- `name`: 사용자 이름
- `provider`: OAuth 제공자 ('google', 'kakao', 'email')
- `provider_id`: OAuth 제공자의 사용자 ID
- `profile_image`: 프로필 이미지 URL
- `created_at`: 생성 시간
- `updated_at`: 수정 시간

### bookmarks 테이블
- `id`: 북마크 ID (PK)
- `user_id`: 사용자 ID (FK → users.id, CASCADE DELETE)
- `concert_id`: 공연 ID (KOPIS mt20id)
- `concert_name`: 공연명
- `poster_url`: 포스터 이미지 URL
- `created_at`: 생성 시간
- **Unique Constraint**: (user_id, concert_id) - 중복 북마크 방지

### reviews 테이블
- `id`: 리뷰 ID (PK)
- `user_id`: 사용자 ID (FK → users.id, CASCADE DELETE)
- `concert_id`: 공연 ID
- `rating`: 평점 (1-5, Check Constraint)
- `content`: 리뷰 내용
- `created_at`: 생성 시간
- `updated_at`: 수정 시간

### analytics 테이블
- `id`: 분석 ID (PK)
- `user_id`: 사용자 ID (FK → users.id, SET NULL on DELETE)
- `event_type`: 이벤트 타입 ('view', 'search', 'bookmark', 'review')
- `concert_id`: 공연 ID
- `metadata`: 추가 메타데이터 (JSON)
- `created_at`: 생성 시간

---

## 7. 트러블슈팅

### 연결 오류
```
ERROR: could not connect to server: Connection refused
```
**해결**: PostgreSQL 서비스가 실행 중인지 확인
```bash
# macOS
brew services list

# Ubuntu
sudo systemctl status postgresql
```

### 권한 오류
```
ERROR: permission denied for database findyourstage
```
**해결**: 사용자 권한 재설정
```sql
GRANT ALL PRIVILEGES ON DATABASE findyourstage TO fys_user;
GRANT ALL ON ALL TABLES IN SCHEMA public TO fys_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO fys_user;
```

### 마이그레이션 충돌
```
ERROR: Target database is not up to date
```
**해결**: 현재 버전 확인 후 수동 해결
```bash
alembic current
alembic history
alembic stamp head  # 강제로 최신으로 표시 (주의!)
```

---

## 8. 프로덕션 배포 시 주의사항

### Render.com / Railway
1. 대시보드에서 PostgreSQL 애드온 추가
2. 자동 생성된 `DATABASE_URL` 환경변수 사용
3. 배포 후 마이그레이션 실행:
   ```bash
   alembic upgrade head
   ```

### Docker 사용 시
```yaml
# docker-compose.yml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: findyourstage
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## 9. 유틸리티 명령어

### 데이터베이스 백업
```bash
pg_dump -U postgres findyourstage > backup.sql
```

### 데이터베이스 복원
```bash
psql -U postgres findyourstage < backup.sql
```

### 데이터베이스 삭제 (주의!)
```sql
DROP DATABASE findyourstage;
```
