# 📈 Fund-Quota-Tracker | 基金额度追踪器

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Automated-2088FF?logo=github-actions)
![Data Source](https://img.shields.io/badge/Data-AkShare%20%7C%20EastMoney-orange)
![License](https://img.shields.io/badge/License-MIT-green)

> **A powerful, fully automated tracker for QDII funds (S&P 500, Nasdaq 100) purchase limits.** > 一个强大、全自动的 QDII 基金（标普 500、纳斯达克 100）单日申购限额监控工具。

---

## 📖 Introduction | 项目简介

**Fund-Quota-Tracker** is designed for smart investors who trade cross-border ETFs and OTC QDII funds. Due to foreign exchange quota limits, popular funds often restrict or suspend daily purchases. This tool completely automates the monitoring process, keeping you informed of any quota changes. 

本项目专为经常进行跨境 ETF 和场外 QDII 基金交易的投资者设计。由于外汇额度限制，热门美股指数基金经常限制单日申购额度甚至暂停申购。本工具将监控流程彻底自动化，让您第一时间掌握额度放开或收紧的动态。

---

## ✨ Key Features | 核心亮点

* 🤖 **Fully Automated (全自动运行)**: Powered by GitHub Actions. Zero server costs, zero manual maintenance. (基于 GitHub Actions，零服务器成本，免维护)。
* 📊 **Smart Trend Tracking (智能趋势对比)**: Automatically compares today's limits with yesterday's. Up/Down arrows and color codes intuitively show if quotas are expanding or tightening. (自动对比前一交易日数据，使用红绿箭头直观展示限额是放开还是收紧)。
* 📧 **Rich HTML Reports (精美 HTML 报表)**: Delivers a clean, responsive, and mobile-friendly HTML data table directly to your inbox. (发送排版精美、适配手机端的响应式 HTML 邮件报表)。
* 🔄 **Self-Updating Roster (自我进化)**: Integrates with `AkShare` to automatically scan the entire market every month and update the watchlist with newly issued S&P/Nasdaq funds. (集成 AkShare 接口，每月自动扫描全市场，将新发行的标普/纳指基金补充进监控名单)。
* 💬 **Multi-Channel (多通道通知)**: Prefers Email notifications but fully supports WeChat Work Bots. (首选邮件推送，同时保留企业微信机器人支持)。

---

## 🚀 Quick Start | 快速部署

You don't need to know how to code. Just follow these steps to deploy your own tracker:  
无需任何编程基础，按以下步骤即可拥有你自己的监控机器人：

### 1. Fork this repository (复刻本项目)
Click the `Fork` button at the top right of this page to copy it to your own GitHub account.  
点击页面右上角的 `Fork` 按钮，将项目复制到您的账号下。

### 2. Configure Secrets (配置环境变量)
Go to your repository **Settings** -> **Secrets and variables** -> **Actions** -> **New repository secret**. Add the following variables:  
进入仓库的 **Settings** -> **Secrets and variables** -> **Actions**，添加以下密钥：

| Secret Name (变量名) | Example / Description (示例及说明) |
| :--- | :--- |
| `EMAIL_SENDER` | Your email address (e.g., `invest_bot@outlook.com`) |
| `EMAIL_PASSWORD` | App Password / SMTP Auth Code (NOT your login password) |
| `SMTP_SERVER` | e.g., `smtp-mail.outlook.com` or `smtp.qq.com` |
| `SMTP_PORT` | Usually `587` (TLS) or `465` (SSL) |
| `EMAIL_RECEIVER` | Where to receive reports (e.g., `your_email@qq.com`) |

### 3. Grant Write Permissions (开启写入权限)
To allow the monthly auto-update script to save data, go to **Settings** -> **Actions** -> **General** -> **Workflow permissions**, and select **`Read and write permissions`**.  
为了让每月的自动更新脚本能够保存最新基金名单，请进入 **Settings** -> **Actions** -> **General** -> **Workflow permissions**，勾选 **`Read and write permissions`**。

### 4. Enable Workflows (激活自动化工作流)
Go to the **Actions** tab, click `I understand my workflows, go ahead and enable them`.  
进入 **Actions** 标签页，点击允许运行工作流。你可以手动点击 `Run workflow` 立即测试一次！

---

## 📈 Preview | 报表预览

*(You can replace this section with a screenshot of your actual beautiful HTML email)* *(你可以稍后截一张你收到的精美 HTML 邮件图，将图片上传到 GitHub Issue 里，然后替换到这里)*

<details>
<summary>Click to view HTML Email Example (点击查看邮件报表示例)</summary>

**[ 🟢 可申购 Available ]**
* **Fund A (01xxxx)**: 100元 -> <span style="color:green">**↑ 500元**</span>
* **Fund B (02xxxx)**: 50元 -> <span style="color:gray">**- 无变化**</span>

**[ 🔴 暂停申购 Unavailable ]**
* **Fund C (03xxxx)**: 50元 -> <span style="color:red">**↓ 暂停申购**</span>

</details>

---

## ⚠️ Disclaimer | 免责声明

* **For Educational Purposes Only**: This tool scrapes public data from EastMoney (天天基金网). It is intended for personal study and reference, not for commercial use. 
* **Not Financial Advice**: The data provided by this tool does not constitute investment advice. Users should verify limits on their trading platforms before making transactions.
* **仅供学习交流**：本项目抓取天天基金网公开数据，仅供个人学习和参考，请勿用于高频商业爬虫。工具提供的数据不构成任何投资建议，交易前请以券商实际交易界面的额度为准。

---

**Made with ❤️ by [Leeeesun](https://github.com/Leeeesun) | If you find this helpful, please give it a ⭐️!**