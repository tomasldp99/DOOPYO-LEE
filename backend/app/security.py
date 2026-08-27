from datetime import datetime,timedelta,timezone
from fastapi import Depends,HTTPException
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from jose import JWTError,jwt
from passlib.context import CryptContext
from .config import settings
pwd=CryptContext(schemes=["bcrypt"],deprecated="auto"); bearer=HTTPBearer(auto_error=False)
def hash_password(v:str): return pwd.hash(v)
def verify_password(v:str,h:str): return pwd.verify(v,h)
def create_token(s:str): return jwt.encode({"sub":s,"role":"admin","exp":datetime.now(timezone.utc)+timedelta(hours=8)},settings.jwt_secret,algorithm="HS256")
async def require_admin(c:HTTPAuthorizationCredentials|None=Depends(bearer)):
    if not c: raise HTTPException(401,"로그인이 필요합니다")
    try:
        p=jwt.decode(c.credentials,settings.jwt_secret,algorithms=["HS256"])
        if p.get("role")!="admin": raise ValueError
        return p["sub"]
    except (JWTError,ValueError,KeyError): raise HTTPException(401,"유효하지 않은 인증입니다")
