import io,secrets
from contextlib import asynccontextmanager
from datetime import datetime,timezone
from uuid import UUID
from fastapi import BackgroundTasks,Depends,FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from sqlalchemy import func,select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from .config import settings
from .database import Base,engine,get_db
from .models import Admin,Applicant,ApplicantStatus,Event,Message,Payment,PaymentStatus
from .schemas import ApplicantCreate,ApplicantOut,EventCreate,EventOut,LoginIn,PasswordChangeIn,PaymentOut,PrepareIn,PrepareOut,TokenOut
from .security import create_token,hash_password,require_admin,verify_password
from .services import send_zoom_email

@asynccontextmanager
async def lifespan(app:FastAPI):
    async with engine.begin() as c: await c.run_sync(Base.metadata.create_all)
    async with AsyncSession(engine) as db:
        if not await db.scalar(select(Admin).where(Admin.email==settings.admin_email)):
            db.add(Admin(email=settings.admin_email,password_hash=hash_password(settings.admin_password),name="EduPay 관리자")); await db.commit()
    yield
app=FastAPI(title="EduPay Link API",version="1.0.0",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=[settings.frontend_url],allow_origin_regex=r"https://edupay-link(?:-[a-z0-9-]+)?\.vercel\.app",allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
@app.get("/health")
async def health(): return {"status":"ok"}
@app.post("/api/v1/auth/login",response_model=TokenOut)
async def login(data:LoginIn,db:AsyncSession=Depends(get_db)):
    a=await db.scalar(select(Admin).where(Admin.email==data.email))
    if not a or not verify_password(data.password,a.password_hash): raise HTTPException(401,"이메일 또는 비밀번호를 확인하세요")
    return TokenOut(access_token=create_token(a),name=a.name)
@app.post("/api/v1/auth/change-password",response_model=TokenOut)
async def change_password(data:PasswordChangeIn,admin:Admin=Depends(require_admin),db:AsyncSession=Depends(get_db)):
    if not verify_password(data.current_password,admin.password_hash): raise HTTPException(400,"현재 비밀번호가 일치하지 않습니다")
    admin.password_hash=hash_password(data.new_password); await db.commit(); await db.refresh(admin)
    return TokenOut(access_token=create_token(admin),name=admin.name)
@app.get("/api/v1/events",response_model=list[EventOut])
async def events(admin=Depends(require_admin),db:AsyncSession=Depends(get_db)):
    rows=(await db.scalars(select(Event).options(selectinload(Event.applicants)).order_by(Event.start_date))).all()
    return [EventOut.model_validate(e).model_copy(update={"applicant_count":len(e.applicants)}) for e in rows]
@app.post("/api/v1/events",response_model=EventOut,status_code=201)
async def create_event(data:EventCreate,admin=Depends(require_admin),db:AsyncSession=Depends(get_db)):
    e=Event(**data.model_dump(mode="python")); db.add(e); await db.commit(); await db.refresh(e); return EventOut.model_validate(e)
@app.get("/api/v1/events/{event_id}",response_model=EventOut)
async def event_detail(event_id:UUID,db:AsyncSession=Depends(get_db)):
    e=await db.get(Event,event_id)
    if not e: raise HTTPException(404,"교육을 찾을 수 없습니다")
    n=await db.scalar(select(func.count(Applicant.applicant_id)).where(Applicant.event_id==event_id)); return EventOut.model_validate(e).model_copy(update={"applicant_count":n or 0})
@app.post("/api/v1/events/{event_id}/applicants",response_model=ApplicantOut,status_code=201)
async def apply(event_id:UUID,data:ApplicantCreate,db:AsyncSession=Depends(get_db)):
    e=await db.get(Event,event_id)
    if not e or e.status.value!="OPEN": raise HTTPException(409,"현재 신청할 수 없습니다")
    n=await db.scalar(select(func.count(Applicant.applicant_id)).where(Applicant.event_id==event_id))
    if (n or 0)>=e.capacity: raise HTTPException(409,"정원이 마감되었습니다")
    now=datetime.now(timezone.utc); vals=data.model_dump(exclude={"privacy_agreed","marketing_agreed"}); a=Applicant(event_id=event_id,**vals,privacy_agreed_at=now,marketing_agreed_at=now if data.marketing_agreed else None); db.add(a); await db.commit(); await db.refresh(a); return a
@app.get("/api/v1/applicants",response_model=list[ApplicantOut],dependencies=[Depends(require_admin)])
async def applicants(db:AsyncSession=Depends(get_db)): return (await db.scalars(select(Applicant).order_by(Applicant.created_at.desc()))).all()
@app.get("/api/v1/applicants/{applicant_id}",response_model=ApplicantOut)
async def applicant_detail(applicant_id:UUID,db:AsyncSession=Depends(get_db)):
    a=await db.get(Applicant,applicant_id)
    if not a: raise HTTPException(404,"신청자를 찾을 수 없습니다")
    return a
@app.get("/api/v1/applicants/export.xlsx",dependencies=[Depends(require_admin)])
async def export(db:AsyncSession=Depends(get_db)):
    rows=(await db.scalars(select(Applicant))).all(); wb=Workbook(); ws=wb.active; ws.append(["이름","휴대전화","이메일","회사/기관","직책","상태","신청일"])
    for a in rows: ws.append([a.name,a.phone,a.email,a.company,a.position,a.status.value,a.created_at.isoformat()])
    f=io.BytesIO(); wb.save(f); f.seek(0); return StreamingResponse(f,media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",headers={"Content-Disposition":"attachment; filename=applicants.xlsx"})
@app.post("/api/v1/payments/prepare",response_model=PrepareOut)
async def prepare(data:PrepareIn,db:AsyncSession=Depends(get_db)):
    a=await db.scalar(select(Applicant).options(selectinload(Applicant.event),selectinload(Applicant.payment)).where(Applicant.applicant_id==data.applicant_id).with_for_update())
    if not a: raise HTTPException(404,"신청자를 찾을 수 없습니다")
    if a.payment and a.payment.payment_status==PaymentStatus.PAID: raise HTTPException(409,"이미 결제되었습니다")
    p=a.payment or Payment(applicant_id=a.applicant_id,order_id=f"EDU-{datetime.now():%Y%m%d}-{secrets.token_hex(8)}",amount=a.event.price)
    if not a.payment: db.add(p)
    p.payment_method=data.payment_method
    await db.commit()
    return PrepareOut(payment_id=p.payment_id,order_id=p.order_id,amount=p.amount,order_name=a.event.title,customer_name=a.name,customer_email=a.email,payment_method=p.payment_method,bank_name=settings.bank_name if p.payment_method=="BANK_TRANSFER" else None,bank_account=settings.bank_account if p.payment_method=="BANK_TRANSFER" else None,bank_holder=settings.bank_holder if p.payment_method=="BANK_TRANSFER" else None)
@app.post("/api/v1/payments/{payment_id}/mark-paid",response_model=PaymentOut,dependencies=[Depends(require_admin)])
async def mark_paid(payment_id:UUID,tasks:BackgroundTasks,db:AsyncSession=Depends(get_db)):
    p=await db.scalar(select(Payment).options(selectinload(Payment.applicant).selectinload(Applicant.event)).where(Payment.payment_id==payment_id).with_for_update())
    if not p: raise HTTPException(404,"결제 요청을 찾을 수 없습니다")
    if p.payment_status==PaymentStatus.PAID: return p
    if p.payment_status not in (PaymentStatus.READY,PaymentStatus.FAILED): raise HTTPException(409,"완료 처리할 수 없는 상태입니다")
    if p.amount!=p.applicant.event.price: raise HTTPException(400,"교육비와 결제 요청 금액이 일치하지 않습니다")
    p.payment_status=PaymentStatus.PAID; p.approved_at=datetime.now(timezone.utc); p.applicant.status=ApplicantStatus.CONFIRMED
    db.add(Message(applicant_id=p.applicant_id,message_type="EMAIL",message_content=f"{p.applicant.event.title} Zoom 안내",status="QUEUED")); await db.commit(); tasks.add_task(send_zoom_email,p.applicant.email,p.applicant.name,p.applicant.event.title,p.applicant.event.zoom_url); return p
@app.post("/api/v1/payments/{payment_id}/refund",response_model=PaymentOut,dependencies=[Depends(require_admin)])
async def refund(payment_id:UUID,db:AsyncSession=Depends(get_db)):
    p=await db.scalar(select(Payment).options(selectinload(Payment.applicant)).where(Payment.payment_id==payment_id).with_for_update())
    if not p or p.payment_status!=PaymentStatus.PAID: raise HTTPException(409,"환불 처리할 수 없는 결제입니다")
    p.payment_status=PaymentStatus.REFUNDED; p.cancelled_at=datetime.now(timezone.utc); p.applicant.status=ApplicantStatus.REFUNDED; await db.commit(); return p
@app.get("/api/v1/payments",response_model=list[PaymentOut],dependencies=[Depends(require_admin)])
async def payments(db:AsyncSession=Depends(get_db)): return (await db.scalars(select(Payment).order_by(Payment.approved_at.desc().nullslast()))).all()
@app.get("/api/v1/dashboard/summary",dependencies=[Depends(require_admin)])
async def dashboard(db:AsyncSession=Depends(get_db)):
    total=await db.scalar(select(func.count(Applicant.applicant_id))); paid=await db.scalar(select(func.count(Payment.payment_id)).where(Payment.payment_status==PaymentStatus.PAID)); amount=await db.scalar(select(func.coalesce(func.sum(Payment.amount),0)).where(Payment.payment_status==PaymentStatus.PAID)); statuses=dict((await db.execute(select(Applicant.status,func.count()).group_by(Applicant.status))).all())
    return {"total_applicants":total or 0,"paid":paid or 0,"unpaid":statuses.get(ApplicantStatus.PENDING,0),"cancelled":statuses.get(ApplicantStatus.CANCELLED,0),"refunded":statuses.get(ApplicantStatus.REFUNDED,0),"revenue":amount}
