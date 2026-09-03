"""邮件助手入口：python main.py --daily 或 python main.py --weekly"""
import argparse
import json
import os
import sys
from datetime import datetime, timedelta

# 确保 Windows 下中文输出不乱码
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from fetcher import fetch_emails
from summarizer import summarize
from sender import send_email

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_config():
    path = os.path.join(BASE_DIR, "config.json")
    if not os.path.exists(path):
        print("缺少 config.json，请先填写配置。", file=sys.stderr)
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)

    problems = []
    addr = cfg.get("gmail_address", "")
    pwd = cfg.get("gmail_app_password", "")
    key = cfg.get("deepseek_api_key", "")
    if "@" not in addr or "你的" in addr:
        problems.append("gmail_address")
    if not pwd or "填" in pwd or "你的" in pwd:
        problems.append("gmail_app_password")
    if not key or "填" in key or "你的" in key:
        problems.append("deepseek_api_key")
    if problems:
        print("config.json 里以下项还没填好：" + "、".join(problems), file=sys.stderr)
        sys.exit(1)
    return cfg


def main():
    parser = argparse.ArgumentParser(description="邮件助手")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--daily", action="store_true", help="当天邮件摘要")
    group.add_argument("--weekly", action="store_true", help="本周邮件汇总")
    args = parser.parse_args()

    cfg = load_config()
    now = datetime.now()

    if args.daily:
        mode = "daily"
        since = now.replace(hour=0, minute=0, second=0, microsecond=0)
        subject = f"【邮件助手】每日摘要 {now.strftime('%Y-%m-%d')}"
    else:
        mode = "weekly"
        days_back = now.weekday() + 1  # 回到上周日 00:00
        since = (now - timedelta(days=days_back)).replace(hour=0, minute=0, second=0, microsecond=0)
        subject = f"【邮件助手】本周汇总 {now.strftime('%Y-%m-%d')}"

    emails = fetch_emails(cfg["gmail_address"], cfg["gmail_app_password"], since)

    if not emails:
        summary = "这段时间没有新邮件。"
    else:
        summary = summarize(emails, cfg["deepseek_api_key"], mode)

    body = f"【邮件助手】\n\n{summary}\n\n—— 共 {len(emails)} 封邮件 ——"
    to_addr = cfg.get("receiver") or cfg["gmail_address"]
    send_email(cfg["gmail_address"], cfg["gmail_app_password"], to_addr, subject, body)
    print(f"已发送：{subject}（{len(emails)} 封邮件）")


if __name__ == "__main__":
    main()
