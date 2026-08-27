from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, HttpUrl, model_validator
from .models import EventStatus, ApplicantStatus, PaymentStatus
class LoginIn(BaseModel): email:EmailStr; password:str=Field(min_length=8,max_length=128)
class TokenOut(BaseModel): access_token:str; token_type:str="bearer"; name:str
class EventCreate(BaseModel):
    title:str=Field(min_length=2,max_length=200); description:str=Field(min_length=10,max_length=10000); instructor:str=Field(min_length=2,max_length=100); start_date:datetime; end_date:datetime; price:Decimal=Field(ge=0); capacity:int=Field(gt=0,le=100000); registration_start:datetime|None=None; registration_end:datetime|None=None; zoom_url:HttpUrl; refund_policy:str=Field(min_length=5,max_length=3000); status:EventStatus=EventStatus.OPEN
    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date<=self.start_date: raise ValueError("종료일시는 시작일시 이후여야 합니다")
        return self
class EventOut(EventCreate):
    event_id:UUID; created_at:datetime; applicant_count:int=0
    model_config={"from_attributes":True}
class ApplicantCreate(BaseModel):
    name:str=Field(min_length=2,max_length=100); phone:str=Field(pattern=r"^[0-9+ -]{9,20}$"); email:EmailStr; company:str|None=None; position:str|None=None; privacy_agreed:bool; marketing_agreed:bool=False
    @model_validator(mode="after")
    def consent(self):
        if not self.privacy_agreed: raise ValueError("개인정보 수집 동의가 필요합니다")
        return self
class ApplicantOut(BaseModel):
    applicant_id:UUID; event_id:UUID; name:str; phone:str; email:EmailStr; company:str|None; position:str|None; status:ApplicantStatus; created_at:datetime
    model_config={"from_attributes":True}
class PrepareIn(BaseModel):
    applicant_id:UUID
    payment_method:str=Field(pattern=r"^(BANK_TRANSFER|ONSITE)$")
class PrepareOut(BaseModel):
    payment_id:UUID; order_id:str; amount:Decimal; order_name:str; customer_name:str; customer_email:EmailStr; payment_method:str; bank_name:str|None=None; bank_account:str|None=None; bank_holder:str|None=None
class PaymentOut(BaseModel):
    payment_id:UUID; applicant_id:UUID; order_id:str; amount:Decimal; payment_method:str|None; payment_status:PaymentStatus; approved_at:datetime|None; cancelled_at:datetime|None
    model_config={"from_attributes":True}
