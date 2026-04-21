import os
import csv
import smtplib
from google import genai  # 使用新的包
from email.mime.text import MIMEText
from email.header import Header
from tavily import TavilyClient

# 初始化客户端
client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

def get_news():
    query = "top important news in AI, robotics, physics, biotechnology, aerospace, and general science today"
    results = tavily.search(query=query, search_depth="advanced", max_results=25)
    return results

def generate_report(news_data):
    prompt = f"""
    你是一位顶尖的科技新闻主编。请根据以下提供的搜索结果，整理一份《全球前沿科技日报》。
    
    要求：
    1. 必须整理出 20 条最重要的新闻，按影响力降序排列。
    2. 类别涵盖：AI、机器人、基础科学、物理、生物、化学、医疗、航空航天、心理学、社会学、信息工程。
    3. 格式：
       - 【类目】中文标题 / English Title
       - 核心洞见：一句话总结，直击本质。
       - 来源：[链接]
    4. 内容必须中英双语，且简练有力。
    
    新闻搜索数据如下：
    {news_data}
    """
    
    # 新 SDK 的调用方式
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )
    return response.text

def send_email(subscriber_email, content):
    sender = os.environ["EMAIL_USER"]
    password = os.environ["EMAIL_PASS"]
    
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['Subject'] = Header("🌐 全球前沿科技日报 - 今日精选", 'utf-8')
    msg['From'] = sender
    msg['To'] = subscriber_email
    
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(sender, password)
    server.sendmail(sender, [subscriber_email], msg.as_string())
    server.quit()

if __name__ == "__main__":
    raw_data = get_news()
    report = generate_report(raw_data)
    
    with open('subscribers.csv', mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            print(f"Sending to {row['email']}...")
            send_email(row['email'], report)
