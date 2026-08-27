# EduPay Link

교육·세미나 등록, 비회원 신청, 계좌이체·현장 수납 확인, Zoom 안내 메일 발송을 하나의 흐름으로 처리하는 반응형 웹 애플리케이션입니다.

## 프로젝트 구조

- `frontend/` — Next.js 15, TypeScript, Tailwind CSS 관리자·참가자 UI
- `backend/` — FastAPI, SQLAlchemy 2, PostgreSQL API
- `docs/ARCHITECTURE.md` — 화면 구조, API 목록, 결제·보안 설계
- `docker-compose.yml` — PostgreSQL 로컬 개발 환경

## 빠른 시작

1. `.env.example`을 `.env`로 복사합니다.
2. `docker compose up -d db`로 PostgreSQL을 실행합니다.
3. 백엔드: `cd backend`, 가상환경을 만든 뒤 `pip install -r requirements.txt`, `uvicorn app.main:app --reload --port 8000`
4. 프론트엔드: `cd frontend`, `npm install`, `npm run dev`
5. 브라우저에서 `http://localhost:3000`을 엽니다.

PG나 카드정보를 사용하지 않습니다. 참가자가 계좌이체 또는 현장결제를 선택하면 결제대기로 등록되고, 관리자가 실제 수납을 확인해 결제완료 처리합니다. 입금 계좌는 `.env`에서 설정합니다.
