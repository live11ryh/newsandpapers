#!/usr/bin/env python3
"""
Daily Science & Technology News Collector and Email Sender
Collects news from multiple sources and sends via email
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
NEWS_PER_REPORT = 20
DATA_DIR = "data"
NEWSAPI_BASE_URL = "https://newsapi.org/v2/everything"
HACKERNEWS_BASE_URL = "https://hacker-news.firebaseio.com/v0"

def ensure_data_dir():
    """Create data directory if it doesn't exist"""
    Path(DATA_DIR).mkdir(exist_ok=True)

def get_newsapi_news(api_key):
    """Fetch news from NewsAPI"""
    if not api_key:
        print("⚠️  NewsAPI key not configured, skipping NewsAPI source")
        return []
    
    try:
        params = {
            "q": "science technology breakthrough discovery",
            "language": "en",
            "sortBy": "publishedAt",
            "apiKey": api_key,
            "pageSize": NEWS_PER_REPORT * 2,
        }
        
        response = requests.get(NEWSAPI_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        
        articles = response.json().get("articles", [])
        print(f"✓ Fetched {len(articles)} articles from NewsAPI")
        return articles
    except Exception as e:
        print(f"✗ Error fetching from NewsAPI: {e}")
        return []

def get_hackernews_top_stories():
    """Fetch top stories from Hacker News"""
    try:
        # Get top 100 story IDs
        response = requests.get(
            f"{HACKERNEWS_BASE_URL}/topstories.json",
            timeout=10
        )
        response.raise_for_status()
        story_ids = response.json()[:NEWS_PER_REPORT * 2]
        
        stories = []
        for story_id in story_ids:
            try:
                story_response = requests.get(
                    f"{HACKERNEWS_BASE_URL}/item/{story_id}.json",
                    timeout=5
                )
                story_response.raise_for_status()
                story = story_response.json()
                
                # Only include stories with URLs (not self posts)
                if story.get("url"):
                    stories.append({
                        "title": story.get("title", ""),
                        "url": story.get("url", ""),
                        "source": "Hacker News",
                        "score": story.get("score", 0),
                        "timestamp": story.get("time", 0),
                    })
            except Exception as e:
                print(f"  ✗ Error fetching story {story_id}: {e}")
                continue
        
        print(f"✓ Fetched {len(stories)} stories from Hacker News")
        return stories
    except Exception as e:
        print(f"✗ Error fetching from Hacker News: {e}")
        return []

def combine_and_deduplicate_news(newsapi_articles, hackernews_stories):
    """Combine news from multiple sources and remove duplicates"""
    combined = []
    seen_urls = set()
    
    # Add NewsAPI articles
    for article in newsapi_articles:
        url = article.get("url", "")
        if url and url not in seen_urls:
            combined.append({
                "title": article.get("title", ""),
                "description": article.get("description", ""),
                "url": url,
                "source": article.get("source", {}).get("name", "Unknown"),
                "published_at": article.get("publishedAt", ""),
                "image": article.get("urlToImage", ""),
            })
            seen_urls.add(url)
    
    # Add Hacker News stories
    for story in hackernews_stories:
        url = story.get("url", "")
        if url and url not in seen_urls:
            combined.append({
                "title": story.get("title", ""),
                "description": f"Score: {story.get('score', 0)}",
                "url": url,
                "source": story.get("source", "Hacker News"),
                "published_at": datetime.fromtimestamp(story.get("timestamp", 0)).isoformat(),
                "image": "",
            })
            seen_urls.add(url)
    
    # Sort by published date (newest first) and limit to NEWS_PER_REPORT
    combined.sort(
        key=lambda x: x.get("published_at", ""),
        reverse=True
    )
    
    return combined[:NEWS_PER_REPORT]

def save_news_to_json(news_items):
    """Save news items to JSON file"""
    ensure_data_dir()
    
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"{DATA_DIR}/news_{today}.json"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(news_items, f, ensure_ascii=False, indent=2)
        print(f"✓ Saved {len(news_items)} news items to {filename}")
        return filename
    except Exception as e:
        print(f"✗ Error saving to JSON: {e}")
        return None

def format_email_body(news_items):
    """Format news items as HTML email body"""
    today = datetime.now().strftime("%Y-%m-%d %A")
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
            .header h1 {{ margin: 0; font-size: 24px; }}
            .header p {{ margin: 5px 0 0 0; font-size: 14px; opacity: 0.9; }}
            .news-item {{ border: 1px solid #ddd; border-radius: 8px; padding: 15px; 
                          margin-bottom: 15px; transition: box-shadow 0.3s; }}
            .news-item:hover {{ box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
            .news-number {{ display: inline-block; background: #667eea; color: white; 
                           width: 32px; height: 32px; border-radius: 50%; 
                           text-align: center; line-height: 32px; 
                           margin-right: 10px; font-weight: bold; }}
            .news-title {{ font-size: 16px; font-weight: bold; color: #667eea; 
                          margin: 10px 0 5px 0; }}
            .news-source {{ color: #999; font-size: 12px; margin: 5px 0; }}
            .news-description {{ color: #666; font-size: 14px; margin: 10px 0; }}
            .news-link {{ display: inline-block; margin-top: 10px; }}
            .news-link a {{ background: #667eea; color: white; padding: 8px 16px; 
                           text-decoration: none; border-radius: 4px; font-size: 13px; }}
            .news-link a:hover {{ background: #764ba2; }}
            .footer {{ text-align: center; padding: 20px; color: #999; font-size: 12px; 
                      border-top: 1px solid #ddd; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📰 Daily Science & Tech News</h1>
                <p>Your curated news digest for {today}</p>
            </div>
    """
    
    for idx, item in enumerate(news_items, 1):
        title = item.get("title", "No Title")
        description = item.get("description", "")[:150] + "..." if item.get("description") else ""
        source = item.get("source", "Unknown Source")
        url = item.get("url", "#")
        published = item.get("published_at", "")
        
        # Format published date
        try:
            dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
            published_str = dt.strftime("%Y-%m-%d %H:%M UTC")
        except:
            published_str = published
        
        html += f"""
            <div class="news-item">
                <span class="news-number">{idx}</span>
                <div class="news-title">{title}</div>
                <div class="news-source">📌 {source} • {published_str}</div>
                <div class="news-description">{description}</div>
                <div class="news-link"><a href="{url}" target="_blank">Read Full Article →</a></div>
            </div>
        """
    
    html += """
            <div class="footer">
                <p>This is an automated daily report. You're receiving this because you subscribed to our news digest.</p>
                <p>© 2026 Daily Science & Tech News • Powered by NewsAPI & Hacker News</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def send_email(recipient_email, subject, html_body, sender_email, sender_password):
    """Send email with news report"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = recipient_email
        
        # Attach HTML body
        html_part = MIMEText(html_body, "html")
        msg.attach(html_part)
        
        # Send email via Gmail SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        
        print(f"✓ Email sent successfully to {recipient_email}")
        return True
    except Exception as e:
        print(f"✗ Error sending email: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("📰 Daily Science & Tech News Collector")
    print("=" * 60)
    
    # Get credentials from environment
    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_PASSWORD")
    recipient_email = os.getenv("RECIPIENT_EMAIL")
    news_api_key = os.getenv("NEWS_API_KEY", "")
    
    # Validate email configuration
    if not all([email_address, email_password, recipient_email]):
        print("✗ Error: Email credentials not configured")
        print("  Please set EMAIL_ADDRESS, EMAIL_PASSWORD, and RECIPIENT_EMAIL")
        sys.exit(1)
    
    print(f"📧 Recipient: {recipient_email}")
    print(f"🔑 NewsAPI: {'Configured' if news_api_key else 'Not configured'}")
    print()
    
    # Fetch news from multiple sources
    print("🔍 Collecting news from multiple sources...")
    newsapi_articles = get_newsapi_news(news_api_key)
    hackernews_stories = get_hackernews_top_stories()
    
    # Combine and deduplicate
    print(f"\n📝 Processing {len(newsapi_articles) + len(hackernews_stories)} total items...")
    news_items = combine_and_deduplicate_news(newsapi_articles, hackernews_stories)
    
    if not news_items:
        print("✗ No news items collected!")
        sys.exit(1)
    
    print(f"✓ Selected top {len(news_items)} items")
    
    # Save to JSON
    print("\n💾 Saving data...")
    save_news_to_json(news_items)
    
    # Send email
    print("\n📤 Sending email...")
    today = datetime.now().strftime("%Y-%m-%d")
    subject = f"📰 Daily Science & Tech News - {today}"
    html_body = format_email_body(news_items)
    
    success = send_email(
        recipient_email,
        subject,
        html_body,
        email_address,
        email_password
    )
    
    if success:
        print("\n✅ All tasks completed successfully!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n❌ Some tasks failed")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()
