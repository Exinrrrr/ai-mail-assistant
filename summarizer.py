"""调用 DeepSeek API 生成邮件摘要。"""
import requests


def _build_prompt(emails, mode):
    title = "今天" if mode == "daily" else "本周"
    lines = []
    for i, m in enumerate(emails, 1):
        lines.append(
            f"{i}. 发件人：{m['from']}\n"
            f"   主题：{m['subject']}\n"
            f"   时间：{m['date']}\n"
            f"   正文：{m['body']}"
        )
    email_text = "\n\n".join(lines)
    return (
        f"你是一个邮件助手。以下是用户{title}收到的邮件（共 {len(emails)} 封）。\n"
        "请帮用户整理成两部分，用中文输出：\n\n"
        "【待办事项】\n"
        "从邮件中提取需要用户处理、回复、提交或截止的事项，按优先级列出；没有则写「无」。\n\n"
        "【注意事项】\n"
        "其他需要用户注意的信息（通知、活动、考试、课程变动、报名等），简要归纳；没有则写「无」。\n\n"
        "要求：简洁直接；每条标注来源邮件主题；不要编造邮件里没有的内容；重要信息不要遗漏。\n\n"
        f"邮件列表：\n\n{email_text}"
    )


def summarize(emails, api_key, mode):
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": _build_prompt(emails, mode)}],
        "temperature": 0.3,
        "max_tokens": 2000,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=180)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()
