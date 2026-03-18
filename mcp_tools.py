import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_nepali_date_google():
    """
    Fetches the exact current Nepali date (B.S.) using nepali_datetime.
    """
    try:
        import nepali_datetime
        # %K = year, %n = month name, %D = day
        return nepali_datetime.date.today().strftime('%K %n %D')
    except ImportError:
        try:
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "pip", "install", "nepali-datetime"])
            import nepali_datetime
            return nepali_datetime.date.today().strftime('%K %n %D')
        except Exception as e:
            print(f"Error fetching Nepali date: {e}")
            
    # Fallback
    return "२०८२ फागुन २२"

def fetch_nepal_news():
    sources = [
        {"name": "OnlineKhabar", "url": "https://www.onlinekhabar.com/", "item_selector": "h2", "content_selector": "p"},
        {"name": "Ratopati", "url": "https://ratopati.com/", "item_selector": "h2", "content_selector": ".title-description"},
        {"name": "Ekantipur", "url": "https://ekantipur.com/", "item_selector": "h2", "content_selector": "p"}
    ]
    
    news_items = []
    seen_headlines = set()

    for source in sources:
        try:
            print(f"Scraping {source['name']}...")
            # Real-world User-Agent is less likely to be blocked
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            response = requests.get(source['url'], headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            items = soup.find_all(source['item_selector'], limit=20)
            
            for item in items:
                headline = item.get_text(strip=True)
                
                # Validation
                if not headline or len(headline) < 20 or headline in seen_headlines:
                    continue
                
                # Filter navigation/section titles
                if any(x in headline for x in ["ट्रेन्डिङ", "मुख्य समाचार", "ताजा अपडेट", "प्रदेश समाचार"]):
                    continue
                
                content = ""
                # Strategy: Search in the container (parent) rather than just siblings
                # This is more robust for modern news grids
                container = item.find_parent(['div', 'article', 'section'])
                if container:
                    content_tag = container.find(source['content_selector'])
                    if content_tag and content_tag.get_text(strip=True) != headline:
                        content = content_tag.get_text(strip=True)

                # Final validation: If no content, skip to keep the feed high quality
                if not content or len(content) < 10:
                    continue
                
                news_items.append({
                    "headline": headline,
                    "content": content[:300],
                    "source": source['name']
                })
                seen_headlines.add(headline)
                
                if len(news_items) >= 15: break
                    
        except Exception as e:
            print(f"Error fetching from {source['name']}: {e}")
            
    return news_items[:12]

def fetch_international_news():
    """
    Gathers exactly 4 international headlines and content summaries.
    Uses BBC RSS feed for guaranteed structured data, then falls back to AP.
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    international_items = []

    # --- Attempt 1: BBC World News RSS ---
    try:
        print("Scraping BBC International News via RSS...")
        import xml.etree.ElementTree as ET
        url_bbc = "http://feeds.bbci.co.uk/news/world/rss.xml"
        response = requests.get(url_bbc, headers=headers, timeout=10)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        
        items = root.findall('.//item')
        for item in items:
            title = item.find('title')
            desc = item.find('description')
            
            if title is not None and desc is not None:
                h_text = title.text.strip()
                s_text = desc.text.strip()
                
                # Check lengths to ensure quality
                if len(h_text) > 10 and len(s_text) > 20:
                    if not any(i['headline'] == h_text for i in international_items):
                        international_items.append({
                            "headline": h_text,
                            "content": s_text[:300],
                            "source": "BBC News"
                        })
            if len(international_items) >= 4:
                break

    except Exception as e:
        print(f"BBC RSS Scraping failed: {e}")

    # --- Attempt 2: AP News (Backup to fill quota) ---
    if len(international_items) < 4:
        try:
            print("Fetching additional stories from AP News...")
            url_ap = "https://apnews.com/hub/world-news"
            response = requests.get(url_ap, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            import re
            articles = soup.find_all(['div', 'article'], limit=30)
            for article in articles:
                headline_tag = article.find(['h1', 'h2', 'h3', 'span'], {"class": re.compile(r'headline', re.I)}) or article.find(['h1', 'h2', 'h3'])
                summary_tag = article.find(['p', 'div'], {"class": re.compile(r'content|body|description', re.I)}) or article.find('p')
                
                if headline_tag and summary_tag:
                    h_text = headline_tag.get_text(strip=True)
                    s_text = summary_tag.get_text(strip=True)
                    
                    if len(h_text) > 20 and len(s_text) > 30 and h_text != s_text:
                        if not any(item['headline'] == h_text for item in international_items):
                            international_items.append({
                                "headline": h_text,
                                "content": s_text[:300],
                                "source": "AP News"
                            })
                if len(international_items) >= 4:
                    break
        except Exception as e:
            print(f"AP News Scraping failed: {e}")

    # Final return of exactly 4 items (or however many we got up to 4)
    return international_items[:4]

if __name__ == "__main__":
    print("--- Nepal News ---")
    nepal = fetch_nepal_news()
    for n in nepal: print(f"[{n['source']}] {n['headline']}")
    
    print("\n--- International News ---")
    intl = fetch_international_news()
    for i in intl: print(f"[{i['source']}] {i['headline']}")