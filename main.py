import os
import csv
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from openai import OpenAI
from tavily import TavilyClient

# 初始化 API
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

def get_news():
    # 使用 Tavily 搜索全网，包含你要求的科技、科学、AI等领域
    query = "top important news in AI, robotics, physics, biotechnology, aerospace, and general science from major tech portals, journals, and social discussions today"
    results = tavily.search(query=query, search_depth="advanced", max_results=25)
    return results

def generate_report(news_data):
    # 构建提示词
    prompt = f"""
    你是一位顶尖的科技新闻主编。请根据以下提供的搜索结果（来自全球科技网站、期刊、论坛、社交媒体），整理一份《全球前沿科技日报》。
    
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
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "你是一个严谨的科学日报编辑。"},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

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
    # 1. 搜集
    raw_data = get_news()
    # 2. 总结
    report = generate_report(raw_data)
    # 3. 发送
    with open('subscribers.csv', mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            print(f"Sending to {row['email']}...")
            send_email(row['email'], report)
    print("All sent!")
