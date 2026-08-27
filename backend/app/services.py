import smtplib
from email.message import EmailMessage
from .config import settings
def send_zoom_email(to:str,name:str,title:str,url:str):
    if not settings.smtp_host: return False
    m=EmailMessage(); m["Subject"]=f"[EduPay Link] {title} 신청 완료"; m["From"]=settings.smtp_from; m["To"]=to; m.set_content(f"{name}님, 결제가 완료되었습니다.\n\nZoom 참가 링크: {url}")
    with smtplib.SMTP(settings.smtp_host,settings.smtp_port) as s: s.starttls(); s.login(settings.smtp_username,settings.smtp_password); s.send_message(m)
    return True
