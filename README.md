# Fund Limit Monitor (基金限额监控)

此项目用于监控指定 QDII 基金（如纳斯达克 100、标普 500）的单日申购限额，并通过企业微信机器人发送通知。

## 功能

- 爬取天天基金网的基金详情数据。
- 提取“交易状态”和“单日限额”信息。
- 生成日报并通过 邮件（优先）或 企业微信 推送。
- 支持 HTML 格式邮件，阅读体验更佳。

## 目录结构

```
.
├── config.json       # 配置文件 (需填入监控名单)
├── monitor.py        # 主程序
├── history.json      # 历史限额数据 (自动更新)
└── requirements.txt  # Python依赖
```

## 安装与配置

1. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

2. **配置通知方式**

   您可以选择使用邮件推送（推荐）或企业微信机器人。程序会优先检查邮件配置。

   ### 邮件推送配置 (推荐)
   为了安全，建议将以下配置通过 **GitHub Secrets** 输入（见下文），但在本地测试时可以在环境变量中设置：

   - `EMAIL_SENDER`: 发信邮箱 (如 `your_email@qq.com`)
   - `EMAIL_USER`: SMTP 账号 (通常与发信邮箱一致)
   - `EMAIL_PASSWORD`: SMTP 授权码 (非登录密码，需在邮箱设置中开启 SMTP 获取)
   - `SMTP_SERVER`: SMTP 服务器地址 (如 `smtp.qq.com`)
   - `SMTP_PORT`: SMTP 端口 (SSL 通常使用 `465`, TLS 使用 `587`)
   - `EMAIL_RECEIVER`: 收件人邮箱 (支持多个，用逗号分隔，如 `a@me.com, b@me.com`)

   ### 企业微信配置
   打开 `config.json`，将 `webhook_url` 替换为您企业微信机器人的真实地址。

## 运行

**手动运行测试：**

```bash
python3 monitor.py
```

正常情况下，您会在终端看到输出（如果没有配置通知方式），或者收到邮件/推送消息。

## GitHub Actions 自动运行

本项目已配置 GitHub Actions，每天在北京时间 13:30 (UTC 05:30) 自动运行。

**配置步骤：**
1. 进入 GitHub 仓库设置：`Settings` -> `Secrets and variables` -> `Actions`。
2. 点击 `New repository secret`，依次添加上述邮件推送所需的变量（`EMAIL_SENDER`, `EMAIL_PASSWORD` 等）。
3. 如果使用企业微信，添加 `WEBHOOK_URL` 变量。

## 注意事项

- 脚本依赖天天基金网的页面结构，如果网站改版可能会失效。
- 请适度控制抓取频率，避免被封禁 IP。
