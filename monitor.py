import requests
from bs4 import BeautifulSoup
import json
import time
import re
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import markdown

class FundMonitor:
    CONFIG_FILE = 'config.json'
    HISTORY_FILE = 'history.json'
    
    def __init__(self):
        self.config = self._load_json(self.CONFIG_FILE)
        self.history = self._load_json(self.HISTORY_FILE)
        
        # WeChat Webhook (Backward compatibility)
        self.webhook_url = os.environ.get('WEBHOOK_URL') or self.config.get('webhook_url')
        
        # Email Configuration (Securely from environment variables)
        self.email_sender = os.environ.get('EMAIL_SENDER')
        self.email_user = os.environ.get('EMAIL_USER') or self.email_sender
        self.email_password = os.environ.get('EMAIL_PASSWORD')
        self.smtp_server = os.environ.get('SMTP_SERVER')
        self.smtp_port = os.environ.get('SMTP_PORT')
        self.email_receiver = os.environ.get('EMAIL_RECEIVER') # Supports comma-separated list
        
        self.funds_config = self.config.get('funds', [])
        
    def _load_json(self, filename):
        if not os.path.exists(filename):
            return {}
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return {}

    def _save_history(self, data):
        with open(self.HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _parse_amount(self, text):
        """Parse amount text to numeric value."""
        if not text or text == "None":
            return 0
        
        match = re.search(r"(\d+(?:\.\d+)?)", text)
        if not match:
            return 0
        
        num = float(match.group(1))
        
        if "千万" in text:
            num *= 10000000
        elif "万" in text:
            num *= 10000
            
        return int(num)

    def _shorten_name(self, name):
        name = name.replace("纳斯达克100", "纳指100")
        keywords = ["ETF联接", "指数", "发起式", "发起", "精选", "股票", "(LOF)"]
        for kw in keywords:
            name = name.replace(kw, "")
        if name.endswith("A"):
            name = name[:-1]
        return name

    def _get_index_type(self, name):
        if "纳斯达克" in name or "纳指" in name:
            return "纳斯达克100"
        if "标普" in name:
            return "标普500"
        return "其他"

    def fetch_fund_info(self, code, name):
        url = f"http://fund.eastmoney.com/f10/jbgk_{code}.html"
        # Modern Browser User-Agent
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        }
        
        info = {
            "code": code,
            "name": name,
            "status": "Unknown",
            "limit_text": "None",
            "limit_val": -1 
        }

        max_retries = 3
        retry_delay = 2
        timeout = 30 # Increased timeout for GitHub Actions

        for attempt in range(max_retries):
            try:
                resp = requests.get(url, headers=headers, timeout=timeout)
                resp.encoding = "utf-8"
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                full_text = soup.get_text()
                
                # 1. Status
                status_match = re.search(r"交易状态：\s*(\S+)", full_text)
                if status_match:
                    info['status'] = status_match.group(1)
                else:
                    th = soup.find(lambda tag: tag.name in ['th', 'td'] and '交易状态' in tag.get_text())
                    if th and th.find_next_sibling('td'):
                        info['status'] = th.find_next_sibling('td').get_text(strip=True)

                # 2. Limit Text
                limit_match = re.search(r"（(.*单日.*上限.*)）", resp.text)
                if limit_match:
                     raw_limit = limit_match.group(1)
                     clean_limit = re.sub(r'<[^>]+>', '', raw_limit)
                     info['limit_text'] = re.sub(r"单日.*?上限", "", clean_limit).replace("（", "").replace("）", "")
                
                # 3. Numeric Value
                if "暂停" in info['status']:
                    info['limit_val'] = -1
                elif info['limit_text'] != "None":
                    info['limit_val'] = self._parse_amount(info['limit_text'])
                else:
                    info['limit_val'] = float('inf')
                
                # Success, break retry loop
                break

            except (requests.exceptions.RequestException, Exception) as e:
                print(f"Error fetching {code} (Attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    print(f"Failed to fetch {code} after {max_retries} attempts.")
            
        return info

    def send_notification(self, message, html_message=None):
        """Send notification via Email (preferred) or WeChat Webhook."""
        sent_email = False
        if self.email_sender and self.email_password and self.smtp_server and self.email_receiver:
            sent_email = self._send_email(message, html_message)
        
        # If email fails or is not configured, try WeChat
        if not sent_email:
            if self.webhook_url and "YOUR_WECHAT" not in self.webhook_url:
                self._send_wechat(message)
            else:
                print("Warning: No notification method configured. Printing message instead.")
                print(message)

    def _send_email(self, content_md, content_html=None):
        """Send notification via SMTP Email."""
        try:
            receivers = [r.strip() for r in self.email_receiver.split(',') if r.strip()]
            if not receivers:
                return False

            # Convert Markdown to basic HTML if custom HTML is not provided
            if not content_html:
                content_html = markdown.markdown(content_md)
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = '基金申购限额日报'
            msg['From'] = self.email_sender
            msg['To'] = ", ".join(receivers)

            # Plain text version for fallback
            text_part = MIMEText(content_md, 'plain', 'utf-8')
            # HTML version
            html_part = MIMEText(content_html, 'html', 'utf-8')

            msg.attach(text_part)
            msg.attach(html_part)

            # Connect and send
            port = int(self.smtp_port) if self.smtp_port else 465
            if port == 465:
                server = smtplib.SMTP_SSL(self.smtp_server, port)
            else:
                server = smtplib.SMTP(self.smtp_server, port)
                server.starttls()
            
            server.login(self.email_user, self.email_password)
            server.sendmail(self.email_sender, receivers, msg.as_string())
            server.quit()
            
            print(f"Email notification sent to {len(receivers)} receiver(s).")
            return True
        except Exception as e:
            print(f"Failed to send email notification: {e}")
            return False

    def _send_wechat(self, message):
        """Send notification via WeChat Webhook."""
        headers = {'Content-Type': 'application/json'}
        data = {
            "msgtype": "markdown",
            "markdown": {"content": message}
        }
        
        try:
            resp = requests.post(self.webhook_url, json=data, headers=headers)
            print(f"WeChat notification sent. Status: {resp.status_code}")
        except Exception as e:
            print(f"Failed to send WeChat notification: {e}")

    def generate_html_report(self, funds_data):
        """Generate a modern, responsive HTML report with a table and delta tracking."""
        # Categorize
        groups = {
            "可申购": {"纳斯达克100": [], "标普500": [], "其他": []},
            "不可申购": {"纳斯达克100": [], "标普500": [], "其他": []}
        }

        for info in funds_data:
            is_paused = "暂停" in info['status']
            category = "不可申购" if (is_paused or info['limit_val'] == 0) else "可申购"
            idx_type = self._get_index_type(info['name'])
            groups[category].get(idx_type, groups[category]["其他"]).append(info)

        last_limits = self.history.get('limits', {})
        now_time = time.strftime('%Y-%m-%d %H:%M:%S')

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta charset="utf-8">
        </head>
        <body style="margin: 0; padding: 0; background-color: #f4f7f9; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                <tr>
                    <td align="center" style="padding: 20px 0;">
                        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 800px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.05);">
                            <!-- Header -->
                            <tr>
                                <td style="padding: 40px 30px; background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%);">
                                    <h2 style="margin: 0 0 8px 0; color: #ffffff; font-size: 28px; font-weight: 700;">基金申购限额日报</h2>
                                    <p style="margin: 0; color: #ebf8ff; font-size: 14px; opacity: 0.9;">更新时间: {now_time}</p>
                                </td>
                            </tr>
        """

        for category, section_data in groups.items():
            total_count = sum(len(v) for v in section_data.values())
            if total_count == 0:
                continue

            section_color = "#38a169" if category == "可申购" else "#e53e3e"
            section_bg = "#f0fff4" if category == "可申购" else "#fff5f5"
            
            html += f"""
                            <!-- Section: {category} -->
                            <tr>
                                <td style="padding: 30px 30px 10px 30px;">
                                    <h3 style="margin: 0; color: {section_color}; font-size: 20px; border-bottom: 2px solid {section_color}; padding-bottom: 8px; display: inline-block;">{category}</h3>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 0 30px 20px 30px;">
            """

            for idx_name in ["纳斯达克100", "标普500", "其他"]:
                funds = section_data.get(idx_name, [])
                if not funds:
                    continue
                
                html += f"""
                                    <h4 style="margin: 20px 0 12px 0; color: #4a5568; font-size: 16px; font-weight: 600;">{idx_name}</h4>
                                    <table width="100%" style="border-collapse: collapse; margin-bottom: 10px;">
                                        <thead>
                                            <tr style="background-color: #f8fafc; border-bottom: 2px solid #edf2f7;">
                                                <th align="left" style="padding: 12px 8px; font-size: 13px; color: #718096; text-transform: uppercase;">基金名称</th>
                                                <th align="center" style="padding: 12px 8px; font-size: 13px; color: #718096; text-transform: uppercase;">当前状态</th>
                                                <th align="right" style="padding: 12px 8px; font-size: 13px; color: #718096; text-transform: uppercase;">今日限额</th>
                                                <th align="right" style="padding: 12px 8px; font-size: 13px; color: #718096; text-transform: uppercase;">较昨日变化</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                """
                
                for f in funds:
                    s_name = self._shorten_name(f['name'])
                    code = f['code']
                    status = f['status']
                    limit_text = f['limit_text']
                    limit_val = f['limit_val']
                    
                    # Status Styling
                    status_style = "color: #38a169; font-weight: 600;" if "暂停" not in status else "color: #e53e3e; font-weight: 600;"
                    
                    # Comparison Logic
                    prev_val = last_limits.get(code)
                    change_html = '<span style="color: #a0aec0;">-</span>'
                    
                    if prev_val is not None:
                        # Normalize values for infinity comparison
                        v_curr = limit_val if limit_val != float('inf') else 9999999999
                        v_prev = prev_val if prev_val != float('inf') else 9999999999
                        
                        if v_curr > v_prev:
                            diff = v_curr - v_prev
                            diff_text = f"+{limit_text}" if v_prev == 0 else f"+{int(diff)}"
                            if v_curr >= 9999999999: diff_text = "恢复不限额"
                            change_html = f'<span style="color: #38a169; font-weight: bold;">↑ {diff_text}</span>'
                        elif v_curr < v_prev:
                            diff = v_prev - v_curr
                            diff_text = f"-{int(diff)}" if v_curr != 0 else "进入暂停"
                            if v_curr == -1: diff_text = "暂停申购"
                            change_html = f'<span style="color: #e53e3e; font-weight: bold;">↓ {diff_text}</span>'

                    # Display Limit
                    disp_limit = limit_text if limit_text != "None" else ("不限额" if limit_val == float('inf') else status)
                    if limit_val == -1: disp_limit = "暂停"

                    html += f"""
                                            <tr style="border-bottom: 1px solid #edf2f7;">
                                                <td style="padding: 14px 8px; font-size: 14px;"><strong>{s_name}</strong> <br><span style="color: #a0aec0; font-size: 12px;">{code}</span></td>
                                                <td align="center" style="padding: 14px 8px; font-size: 14px; {status_style}">{status}</td>
                                                <td align="right" style="padding: 14px 8px; font-size: 14px; font-weight: 600; color: #2d3748;">{disp_limit}</td>
                                                <td align="right" style="padding: 14px 8px; font-size: 14px;">{change_html}</td>
                                            </tr>
                    """
                
                html += "                                        </tbody></table>"
            
            html += "                                </td></tr>"

        html += """
                            <!-- Footer -->
                            <tr>
                                <td style="padding: 30px; background-color: #f8fafc; border-top: 1px solid #edf2f7; color: #a0aec0; font-size: 12px; text-align: center;">
                                    <p style="margin: 0 0 5px 0;">此邮件由 <strong>Fund Limit Monitor</strong> 自动发送</p>
                                    <p style="margin: 0;">数据源: 天天基金网 | 仅供个人参考</p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        return html

    def generate_report(self, funds_data):
        # Sort by limit value descending
        funds_data.sort(key=lambda x: x['limit_val'], reverse=True)
        
        # Categorize
        groups = {
            "可申购": {"纳斯达克100": [], "标普500": [], "其他": []},
            "不可申购": {"纳斯达克100": [], "标普500": [], "其他": []}
        }

        for info in funds_data:
            is_paused = "暂停" in info['status']
            category = "不可申购" if (is_paused or info['limit_val'] == 0) else "可申购"
            
            idx_type = self._get_index_type(info['name'])
            if idx_type not in groups[category]:
                groups[category]["其他"] = groups[category].get("其他", [])
                groups[category]["其他"].append(info)
            else:
                groups[category][idx_type].append(info)

        # Build Message
        report_lines = ["# 基金申购限额日报 (A类)", f"> 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}"]
        
        last_limits = self.history.get('limits', {})

        def add_section(title, grouped_funds):
            total_count = sum(len(v) for v in grouped_funds.values())
            if total_count == 0:
                return

            report_lines.append(f"## {title}")
            
            for idx_name in ["纳斯达克100", "标普500", "其他"]:
                funds = grouped_funds.get(idx_name, [])
                if not funds:
                    continue
                
                report_lines.append(f"### {idx_name}")
                
                for f in funds:
                    s_name = self._shorten_name(f['name'])
                    code = f['code']
                    limit_text = f['limit_text']
                    limit_val = f['limit_val']
                    
                    # Emoji
                    emoji = "🔴" if title == "不可申购" else ""
                    
                    # Comparison Arrow
                    arrow = ""
                    prev = last_limits.get(code)
                    if prev is not None:
                        if limit_val > prev: arrow = " ↑"
                        elif limit_val < prev: arrow = " ↓"

                    line = f"{s_name}({code}) {emoji}"
                    
                    if title == "可申购" and limit_text != "None":
                        line += f" : {limit_text}{arrow}"
                    elif title == "可申购" and limit_val == float('inf') and arrow:
                        line += f" : 不限{arrow}"
                    
                    report_lines.append(line.strip())

        add_section("可申购", groups["可申购"])
        add_section("不可申购", groups["不可申购"])
        
        return "\n".join(report_lines)

    def run(self):
        funds_data = []
        print(f"Fetching data for {len(self.funds_config)} funds...")
        
        for fund in self.funds_config:
            info = self.fetch_fund_info(fund['code'], fund['name'])
            funds_data.append(info)
            time.sleep(0.5)
            
        message = self.generate_report(funds_data)
        html_message = self.generate_html_report(funds_data)
        self.send_notification(message, html_message)
        
        # Save History
        curr_limits = {f['code']: f['limit_val'] for f in funds_data}
        self._save_history({"date": time.strftime('%Y-%m-%d'), "limits": curr_limits})

if __name__ == "__main__":
    monitor = FundMonitor()
    monitor.run()
