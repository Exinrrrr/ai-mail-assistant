"""通过 Gmail SMTP 发送摘要邮件。"""
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr


def send_email(address, app_password, to_addr, subject, body):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = formataddr((str(Header("邮件助手", "utf-8")), address))
    msg["To"] = to_addr
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=60) as server:
        server.starttls()
        server.login(address, app_password)
        server.sendmail(address, [to_addr], msg.as_string())
