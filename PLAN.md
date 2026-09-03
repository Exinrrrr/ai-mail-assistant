# 邮件助手 — 方案与交接文档

> 用途：本文件是「邮件助手」项目的唯一权威方案 + 进度记录。任何一台电脑的 Claude Code
> 打开本文件即可接手，无需重新澄清需求。**除非用户明确要求，否则不要改动「已确定方案」。**

## 一句话目标
自动读取学校 Outlook 邮件（经 Gmail 转发），每天 23:55 发当日摘要、每周日 22:00 发本周汇总
到用户自己的 Gmail，帮助用户不漏事、不错过待办。

## 背景与约束（已确认）
- 学校邮箱是 Microsoft 365「工作/学校账户」，租户限制多，AI 无法直接读取 → 用「自动转发到 Gmail」绕过。
- 用户在国内，Gmail 的 IMAP/SMTP 直连可能不稳；**若连不上，代码结构不变，仅需把邮箱换成 QQ 邮箱（163 亦可）**。当前先按 Gmail 实现。
- **不用 Anthropic API key**。总结用 DeepSeek（便宜，用户已有 token）。

## 已确定的方案（不要改，除非用户明确要求）
| 项目 | 决定 |
|---|---|
| 收件邮箱 | Gmail（接收学校 Outlook 自动转发）|
| 总结 LLM | DeepSeek API（模型 `deepseek-chat`）|
| 输出方式 | SMTP 发邮件到用户自己的 Gmail |
| 定时 | Windows 任务计划程序（Task Scheduler）：每天 23:55、每周日 22:00 |
| 写代码 | 当前 Claude Code |
| 运行位置 | 用户 Windows 电脑本地 |

## 目标架构
```
学校 Outlook ──自动转发──▶ Gmail
                              │ IMAP 读取
                        fetcher.py 抓当天/本周邮件
                              │
                        summarizer.py 调 DeepSeek 总结
                              │
                        sender.py 用 SMTP 发摘要邮件给自己
定时：Windows 任务计划程序（每天 23:55 跑 --daily；周日 22:00 跑 --weekly）
```

## 计划文件结构（待创建于 AI_V/email_digest/）
```
email_digest/
├── main.py             # 入口：--daily / --weekly
├── fetcher.py          # IMAP 读 Gmail（当天 / 本周）
├── summarizer.py       # 调 DeepSeek API 生成「待办 + 注意事项」
├── sender.py           # SMTP 发送摘要邮件
├── config.example.json # 配置模板（邮箱、应用专用密码、DeepSeek key）
├── requirements.txt    # 依赖（尽量少第三方库，DeepSeek 用 requests 或标准库 urllib）
└── README.md           # 使用说明
```

## 关键技术点
- **Gmail IMAP**：`imap.gmail.com:993` (SSL)；**SMTP**：`smtp.gmail.com:587` (STARTTLS)。
  用户名用邮箱，密码用「应用专用密码」（同一个即可用于 IMAP + SMTP）。
- **DeepSeek API**：base_url `https://api.deepseek.com`，模型 `deepseek-chat`，
  OpenAI 兼容的 `chat/completions` 接口。（编码时若 API 有变动，以 DeepSeek 官方文档为准。）
- **--daily**：抓「今天 00:00 至今」的邮件；**--weekly**：抓「本周（上周日 00:00 至今）」的邮件。
- **邮件解析**：取 From / Subject / Date / 正文纯文本（HTML 需转纯文本），正文过长截断。
- **摘要邮件**：主题示例 `【邮件助手】每日摘要 2026-09-02`；正文分「今日待办」和「注意事项」两块。

## 当前进度（已完成 ✅，截至 2026-09-03）
- [x] 需求已澄清、方案已确定（本文件）。
- [x] 代码全部写好：`fetcher.py` / `summarizer.py` / `sender.py` / `main.py` / `run_daily.bat` / `run_weekly.bat` / `config.json` / `README.md`。
- [x] 环境：Python 3.12.10 + requests 已装。
- [x] 端到端测试通过（抓 27 封邮件 → DeepSeek 总结 → SMTP 发摘要）。
- [x] 两个定时任务已创建并验证：
  - `EmailAssistant-Daily`：每天 23:55 跑 `run_daily.bat`（`--daily`）
  - `EmailAssistant-Weekly`：每周日 22:00 跑 `run_weekly.bat`（`--weekly`）

## 关键路径信息
- Python：`%LOCALAPPDATA%\Programs\Python\Python312\python.exe`
- 项目目录：`D:\ai_v\email_digest\`
- 凭据：`config.json`（本地私密，勿外传）
- 手动跑：`python main.py --daily` / `python main.py --weekly`

## 用户需准备（非代码，用户侧）
1. Gmail：开两步验证 → 生成「邮件」应用专用密码；确认 IMAP 已开启。
2. DeepSeek：`platform.deepseek.com` 建 API key。
3. 学校 Outlook：设置自动转发到 Gmail。

## 项目规范提醒
遵循 AI_V 的 `CLAUDE.md` 规范：回复以「小新，你好」开头、行动前先确认、只操作 AI_V 内文件、
完成后检查/测试、旧功能回退测试等。
