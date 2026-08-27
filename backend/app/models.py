import enum, uuid
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

def now(): return datetime.now(timezone.utc)
class EventStatus(str, enum.Enum): DRAFT="DRAFT"; OPEN="OPEN"; CLOSED="CLOSED"; CANCELLED="CANCELLED"
class ApplicantStatus(str, enum.Enum): PENDING="PENDING"; CONFIRMED="CONFIRMED"; CANCELLED="CANCELLED"; REFUNDED="REFUNDED"
class PaymentStatus(str, enum.Enum): READY="READY"; PAID="PAID"; FAILED="FAILED"; CANCELLED="CANCELLED"; REFUNDED="REFUNDED"
class Admin(Base):
    __tablename__="admin"
    admin_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    email: Mapped[str]=mapped_column(String(255),unique=True,index=True); password_hash: Mapped[str]=mapped_column(String(255)); name: Mapped[str]=mapped_column(String(100),default="관리자")
    is_active: Mapped[bool]=mapped_column(Boolean,default=True); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class Event(Base):
    __tablename__="event"
    event_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    title: Mapped[str]=mapped_column(String(200)); description: Mapped[str]=mapped_column(Text); instructor: Mapped[str]=mapped_column(String(100))
    start_date: Mapped[datetime]=mapped_column(DateTime(timezone=True)); end_date: Mapped[datetime]=mapped_column(DateTime(timezone=True)); price: Mapped[Decimal]=mapped_column(Numeric(12,2)); capacity: Mapped[int]=mapped_column(Integer)
    registration_start: Mapped[datetime|None]=mapped_column(DateTime(timezone=True)); registration_end: Mapped[datetime|None]=mapped_column(DateTime(timezone=True)); zoom_url: Mapped[str]=mapped_column(String(1000)); refund_policy: Mapped[str]=mapped_column(Text,default="교육 3일 전까지 전액 환불")
    status: Mapped[EventStatus]=mapped_column(Enum(EventStatus),default=EventStatus.OPEN); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
    applicants: Mapped[list["Applicant"]]=relationship(back_populates="event")
class Applicant(Base):
    __tablename__="applicant"
    applicant_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4); event_id: Mapped[uuid.UUID]=mapped_column(ForeignKey("event.event_id",ondelete="CASCADE"),index=True)
    name: Mapped[str]=mapped_column(String(100)); phone: Mapped[str]=mapped_column(String(30)); email: Mapped[str]=mapped_column(String(255)); company: Mapped[str|None]=mapped_column(String(200)); position: Mapped[str|None]=mapped_column(String(100))
    privacy_agreed_at: Mapped[datetime]=mapped_column(DateTime(timezone=True)); marketing_agreed_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True)); status: Mapped[ApplicantStatus]=mapped_column(Enum(ApplicantStatus),default=ApplicantStatus.PENDING); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
    event: Mapped[Event]=relationship(back_populates="applicants"); payment: Mapped["Payment|None"]=relationship(back_populates="applicant",uselist=False)
class Payment(Base):
    __tablename__="payment"; __table_args__=(UniqueConstraint("applicant_id"),)
    payment_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4); applicant_id: Mapped[uuid.UUID]=mapped_column(ForeignKey("applicant.applicant_id"),index=True)
    order_id: Mapped[str]=mapped_column(String(100),unique=True,index=True); amount: Mapped[Decimal]=mapped_column(Numeric(12,2)); payment_method: Mapped[str|None]=mapped_column(String(50)); payment_status: Mapped[PaymentStatus]=mapped_column(Enum(PaymentStatus),default=PaymentStatus.READY)
    approved_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True)); cancelled_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True)); failure_reason: Mapped[str|None]=mapped_column(String(500)); applicant: Mapped[Applicant]=relationship(back_populates="payment")
class Message(Base):
    __tablename__="message"
    message_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4); applicant_id: Mapped[uuid.UUID]=mapped_column(ForeignKey("applicant.applicant_id"),index=True)
    message_type: Mapped[str]=mapped_column(String(30)); message_content: Mapped[str]=mapped_column(Text); sent_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True)); status: Mapped[str]=mapped_column(String(30),default="PENDING")
