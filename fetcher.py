"""从 Gmail 抓取邮件的模块。"""
import email
import html
import imaplib
import re
from datetime import timedelta, timezone
from email.header import decode_header, make_header
from email.utils import parsedate_to_datetime


def _decode(s):
    """解码邮件头字符串（处理 =?utf-8?...?= 这种编码）。"""
    if not s:
        return ""
    try:
        return str(make_header(decode_header(s)))
    except Exception:
        return str(s)


def _html_to_text(s):
    """把 HTML 粗略转成纯文本。"""
    s = re.sub(r"(?is)<(style|script)[^>]*>.*?</\1>", " ", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _get_body_text(msg):
    """尽量提取邮件纯文本正文；没有纯文本就用 HTML 转。"""
    plain, html_parts = [], []
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            cdisp = str(part.get("Content-Disposition") or "")
            if "attachment" in cdisp.lower():
                continue
            payload = part.get_payload(decode=True)
            if not payload:
                continue
            charset = part.get_content_charset() or "utf-8"
            text = payload.decode(charset, errors="replace")
            if ctype == "text/plain":
                plain.append(text)
            elif ctype == "text/html":
                html_parts.append(text)
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            plain.append(payload.decode(charset, errors="replace"))

    if plain:
        return "\n".join(p.strip() for p in plain if p.strip())
    if html_parts:
        return _html_to_text("\n".join(html_parts))
    return ""


def _parse_date_local(msg):
    """解析邮件 Date 头，转成本地时间（naive datetime）；失败返回 None。"""
    raw = msg.get("Date")
    if not raw:
        return None
    try:
        dt = parsedate_to_datetime(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone().replace(tzinfo=None)
    except Exception:
        return None


def fetch_emails(address, app_password, since, max_body_chars=1500):
    """读取 Gmail 收件箱里 Date >= since 的邮件。since 为本地时间 datetime。"""
    mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    try:
        mail.login(address, app_password)
        mail.select("INBOX")
        # 多取一天避免服务器时区导致漏信，再在本地精确过滤
        search_since = (since - timedelta(days=1)).strftime("%d-%b-%Y")
        typ, data = mail.search(None, f'(SINCE "{search_since}")')
        if typ != "OK":
            raise RuntimeError(f"IMAP 搜索失败: {data}")

        results = []
        for num in data[0].split():
            typ, msg_data = mail.fetch(num, "(RFC822)")
            if typ != "OK":
                continue
            msg = email.message_from_bytes(msg_data[0][1])
            dt = _parse_date_local(msg)
            if dt is None or dt < since:
                continue
            body = _get_body_text(msg)
            if len(body) > max_body_chars:
                body = body[:max_body_chars] + "…(已截断)"
            results.append({
                "from": _decode(msg.get("From")),
                "subject": _decode(msg.get("Subject")),
                "date": dt.strftime("%Y-%m-%d %H:%M"),
                "body": body,
            })
        return results
    finally:
        try:
            mail.logout()
        except Exception:
            pass
