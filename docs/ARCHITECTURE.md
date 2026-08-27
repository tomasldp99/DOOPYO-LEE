# EduPay Link 설계

## 시스템 구조

참가자/관리자 → Next.js UI → FastAPI → PostgreSQL 구조입니다. PG 및 카드정보는 사용하지 않습니다. 참가자는 `계좌이체` 또는 `현장결제`를 선택하고 PAYMENT가 `READY`로 생성됩니다. 관리자가 실제 입금 또는 수납을 확인해 완료 버튼을 누르면, 서버 트랜잭션 안에서 PAYMENT를 `PAID`, APPLICANT를 `CONFIRMED`로 변경한 후 Zoom 안내 이메일을 발송합니다.

## 화면 구조

- 관리자: `/login`, `/admin`, `/admin/events`, `/admin/events/new`, `/admin/applicants`, `/admin/payments`, `/admin/messages`, `/admin/zoom`, `/admin/stats`, `/admin/settings`
- 참가자: `/e/[eventId]` 교육 소개·신청, `/checkout/[applicantId]` 결제방법 선택, `/complete` 접수·입금 안내

## API 목록

- `POST /api/v1/auth/login` 관리자 JWT 발급
- `GET/POST /api/v1/events` 교육 목록·등록
- `GET /api/v1/events/{id}` 공개 교육 조회
- `POST /api/v1/events/{id}/applicants` 비회원 신청
- `GET /api/v1/applicants` 신청자 목록
- `GET /api/v1/applicants/export.xlsx` Excel 다운로드
- `POST /api/v1/payments/prepare` 계좌이체·현장결제 요청 생성
- `GET /api/v1/payments` 결제 요청 목록
- `POST /api/v1/payments/{id}/mark-paid` 관리자 수납 확인 및 신청 확정
- `POST /api/v1/payments/{id}/refund` 관리자 환불 기록
- `GET /api/v1/dashboard/summary` 대시보드 집계

## 상태 흐름

`신청(PENDING) → 결제방법 선택(PAYMENT.READY) → 관리자 수납 확인(PAYMENT.PAID + APPLICANT.CONFIRMED) → Zoom 이메일 발송`. 환불 처리 시 PAYMENT와 APPLICANT 모두 `REFUNDED`가 됩니다. 완료 API는 행 잠금과 상태 검사를 사용해 중복 처리를 막습니다.

## 데이터와 보안

요청된 EVENT, APPLICANT, PAYMENT, MESSAGE와 인증용 ADMIN을 사용합니다. `order_id`와 applicant별 PAYMENT는 unique입니다. 결제금액은 항상 서버의 EVENT 가격으로 생성하고 완료 처리 전에 다시 비교합니다. 관리자 API는 JWT가 필요하며 입력은 Pydantic으로 검증합니다. 카드번호, CVC, 유효기간, PG 키나 Webhook 경로는 존재하지 않습니다. Zoom URL은 결제대기 화면에 노출하지 않고 관리자 확인 후 이메일로만 전달합니다.
