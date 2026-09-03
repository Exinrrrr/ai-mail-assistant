# 邮件助手

自动读取学校邮箱（经 Gmail 转发），每天 23:55 发当日摘要、每周日 22:00 发本周汇总到你的邮箱。

## 工作原理

```
学校 Outlook ──自动转发──▶ Gmail
                              │ IMAP 读取（fetcher.py）
                              ▼
                     DeepSeek 总结（summarizer.py）
                              ▼
                     发邮件给你自己（sender.py）
```

## 环境准备

1. 安装 Python 3（Windows 下 `python.org` 下载安装即可）。
2. 安装依赖：
   ```bash
   pip install requests
   ```

## 配置

1. 打开本目录的 `config.json`，填入你的真实信息：

   ```json
   {
     "gmail_address": "你的Gmail地址@gmail.com",
     "gmail_app_password": "16位应用专用密码",
     "deepseek_api_key": "sk-开头的DeepSeek key",
     "receiver": "接收摘要的邮箱"
   }
   ```

   > 凭据不要发给别人、不要提交到公开仓库。

2. 说明：
   - `gmail_app_password` 是 Gmail 的「应用专用密码」（不是登录密码），IMAP 和 SMTP 共用。
   - `deepseek_api_key` 在 [platform.deepseek.com](https://platform.deepseek.com) 创建。

## 手动测试

```bash
python main.py --daily     # 当天摘要
python main.py --weekly    # 本周汇总
```

成功的话，你的邮箱会收到一封摘要邮件。

## 设置定时任务（Windows 任务计划程序）

先确认 Python 的完整路径：

```bash
python -c "import sys; print(sys.executable)"
```

然后用下面命令创建两个定时任务（把 `<python路径>` 换成上一步的结果）：

```bat
schtasks /Create /TN "邮件助手-每日" /SC DAILY /ST 23:55 /TR "\"<python路径>\" \"D:\ai_v\email_digest\main.py\" --daily" /F

schtasks /Create /TN "邮件助手-每周" /SC WEEKLY /D SUN /ST 22:00 /TR "\"<python路径>\" \"D:\ai_v\email_digest\main.py\" --weekly" /F
```

也可以图形界面操作：Win+R 输入 `taskschd.msc` → 创建基本任务，按提示设触发时间、程序填 Python、参数填脚本路径和 `--daily`/`--weekly`。

> 注意：任务只在电脑**开机且登录**时才会跑；电脑关机/睡眠到点不会执行，也不会补跑。

## 文件说明

| 文件 | 作用 |
|---|---|
| `main.py` | 入口，`--daily` / `--weekly` |
| `fetcher.py` | IMAP 读 Gmail 当天/本周邮件 |
| `summarizer.py` | 调 DeepSeek 生成「待办 + 注意事项」 |
| `sender.py` | SMTP 发摘要邮件 |
| `config.json` | 你的凭据（本地私密） |

## 常见问题

- **收不到摘要**：检查 `config.json` 是否填对、网络能否连 Google 和 DeepSeek、Gmail 是否开了 IMAP。
- **Gmail 连不上**：国内直连 Gmail 可能不稳，可把邮箱换成 QQ 邮箱（`imap.qq.com` / `smtp.qq.com`，代码结构不变）。
- **中文乱码**：脚本已强制 UTF-8 输出，一般不会出现。
