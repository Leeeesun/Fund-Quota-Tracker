# 📈 Fund-Quota-Tracker | 基金额度追踪器

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Automated-2088FF?logo=github-actions)
![Data Source](https://img.shields.io/badge/Data-集思录%20%7C%20天天基金网-orange)
![License](https://img.shields.io/badge/License-MIT-green)

> **全自动 QDII 基金（标普 500、纳斯达克 100）单日申购限额 + 溢价率监控工具。**
>
> A fully automated tracker for QDII fund purchase limits and ETF premium rates, covering S&P 500 and Nasdaq 100 index funds.

---

## 📖 项目简介

QDII 基金由于外汇额度限制，热门美股指数基金经常限制单日申购额度甚至暂停申购。与此同时，场内 ETF 的溢价率也会随市场情绪大幅波动。

**Fund-Quota-Tracker** 将这些监控流程彻底自动化：

- 每个交易日自动抓取 113 只标普 500 / 纳斯达克 100 相关基金的最新申购状态
- 对比前一交易日数据，标记限额变化（↑ 放开 / ↓ 收紧）
- 对场内 ETF/LOF 展示实时**溢价率**，超过 1% 红色警示、折价绿色提示
- 生成精美 HTML 邮件报表，直接推送到邮箱

---

## ✨ 核心功能

| 功能 | 说明 |
|------|------|
| 🤖 **全自动运行** | 基于 GitHub Actions，工作日 13:30 定时执行，零服务器成本 |
| 📊 **智能趋势对比** | 自动对比昨日限额，红绿箭头直观展示额度变化方向 |
| 💹 **ETF 溢价率** | 从集思录获取场内 ETF 实时溢价率，红/绿色条件着色 |
| 📧 **精美 HTML 报表** | 响应式邮件表格，手机/电脑端均可完美显示 |
| 🔄 **自动更新基金名单** | 每月 1 号自动扫描全市场新发标普/纳指基金，补充进监控列表 |
| 💬 **多通道通知** | 支持 SMTP 邮件（首选）和企业微信机器人 |

---

## 📡 数据源

本项目采用**双数据源混合架构**，兼顾准确性和覆盖范围：

| 数据源 | 覆盖范围 | 提供数据 |
|--------|---------|---------|
| **[集思录](https://www.jisilu.cn/data/qdii/)** (Jisilu) | 场内 ETF/LOF（约 20 只） | 申购状态、溢价率、基金净值 |
| **[天天基金网](https://fund.eastmoney.com/)** (EastMoney) | 场外 OTC 基金 A/C/I 类（约 93 只） | 交易状态、申购限额 |

> 集思录数据通过一次批量 API 调用完成，场外基金逐只抓取。每次请求使用随机 User-Agent 并设置合理超时和重试。

---

## 🚀 快速部署

无需任何编程基础，按以下步骤即可部署你自己的监控机器人：

### 1. Fork 本项目

点击页面右上角的 **Fork** 按钮，将项目复制到你的 GitHub 账号下。

### 2. 配置 Secrets

进入仓库 **Settings** → **Secrets and variables** → **Actions** → **New repository secret**，添加以下变量：

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `EMAIL_SENDER` | 发件邮箱地址 | `bot@outlook.com` |
| `EMAIL_PASSWORD` | SMTP 授权码（非登录密码） | `xxxxxxxxxx` |
| `SMTP_SERVER` | SMTP 服务器地址 | `smtp-mail.outlook.com` |
| `SMTP_PORT` | SMTP 端口 | `587`（TLS）或 `465`（SSL） |
| `EMAIL_RECEIVER` | 收件邮箱（支持逗号分隔多个） | `you@qq.com` |

> **可选**：配置 `WEBHOOK_URL` 可同时推送到企业微信机器人。

### 3. 开启写入权限

进入 **Settings** → **Actions** → **General** → **Workflow permissions**，选择 **Read and write permissions**。

> 此权限用于每月自动更新 `config.json` 基金名单和每日保存 `history.json` 对比数据。

### 4. 激活工作流

进入 **Actions** 标签页，点击 **I understand my workflows, go ahead and enable them**，然后可以手动点击 **Run workflow** 立即测试一次。

---

## ⚙️ 自动化工作流

| 工作流 | 触发时间 | 功能 |
|--------|---------|------|
| `daily_run.yml` | 工作日 13:30（北京时间） | 抓取限额数据 → 生成报表 → 发送通知 → 保存历史 |
| `monthly_update.yml` | 每月 1 日 08:00（北京时间） | 扫描全市场新基金 → 更新 `config.json` |

---

## 📁 项目结构

```
Fund-Quota-Tracker/
├── monitor.py          # 核心监控脚本（集思录 + 天天基金网数据抓取、报表生成、通知推送）
├── update_funds.py     # 每月自动更新基金名单（通过 AkShare）
├── config.json         # 监控基金列表（113 只标普/纳指相关基金）
├── history.json        # 历史限额数据（用于趋势对比）
├── requirements.txt    # Python 依赖
└── .github/workflows/
    ├── daily_run.yml       # 每日监控工作流
    └── monthly_update.yml  # 每月更新工作流
```

---

## 📧 邮件报表示例

报表按 **可申购 / 不可申购** 分类，每类下按指数类型（纳斯达克 100、标普 500、其他）分组：

| 基金名称 | 当前状态 | 今日限额 | 较昨日变化 | 溢价率 |
|----------|---------|---------|-----------|--------|
| 纳斯达克指数ETF `159501` | 开放申购 | 不限额 | - | 🔴 6.34% |
| 广发纳指100人民币(QDII)A `270042` | 限大额 | 10元 | - | N/A |
| 纳指ETF `513100` | 暂停申购 | 暂停 | ↓ 暂停申购 | 🔴 6.82% |

- 🔴 **溢价率 > 1%**：红色高亮，表示溢价偏高
- 🟢 **溢价率 < 0%**：绿色高亮，表示折价
- **N/A**：场外 OTC 基金无溢价率

---

## ⚠️ 免责声明

- **仅供学习交流**：本项目抓取集思录与天天基金网公开数据，仅供个人学习和参考，请勿用于高频商业爬虫。
- **不构成投资建议**：工具提供的数据不构成任何投资建议，交易前请以券商实际交易界面的额度为准。

---

**Made with ❤️ by [Leeeesun](https://github.com/Leeeesun) | 觉得有用请点个 ⭐️**