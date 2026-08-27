import hashlib,secrets
from datetime import datetime,timedelta,timezone
from uuid import UUID
from fastapi import Depends,HTTPException
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from jose import JWTError,jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from .config import settings
from .database import get_db
from .models import Admin
pwd=CryptContext(schemes=["bcrypt"],deprecated="auto"); bearer=HTTPBearer(auto_error=False)
def hash_password(v:str): return pwd.hash(v)
def verify_password(v:str,h:str): return pwd.verify(v,h)
def password_version(password_hash:str): return hashlib.sha256(password_hash.encode()).hexdigest()
def create_token(admin:Admin): return jwt.encode({"sub":str(admin.admin_id),"role":"admin","pwd":password_version(admin.password_hash),"exp":datetime.now(timezone.utc)+timedelta(hours=8)},settings.jwt_secret,algorithm="HS256")
async def require_admin(c:HTTPAuthorizationCredentials|None=Depends(bearer),db:AsyncSession=Depends(get_db)):
    if not c: raise HTTPException(401,"로그인이 필요합니다")
    try:
        p=jwt.decode(c.credentials,settings.jwt_secret,algorithms=["HS256"])
        if p.get("role")!="admin": raise ValueError
        admin=await db.get(Admin,UUID(p["sub"]))
        if not admin or not admin.is_active or not secrets.compare_digest(p.get("pwd",""),password_version(admin.password_hash)): raise ValueError
        return admin
    except (JWTError,ValueError,KeyError): raise HTTPException(401,"유효하지 않은 인증입니다")