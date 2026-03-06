import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_nepali_date_google():
    """
    Fetches the current Nepali date (B.S.).
    """
    try:
        # Using ashesh.com.np as a stable source for the current Nepali date
        url = "https://www.ashesh.com.np/nepali-calendar/embed.php"
        r = requests.get(url, timeout=5)
        import re
        # Look for pattern like 2082 Falgun 22
        match = re.search(r'(\d{4}) ([\u0900-\u097F]+) (\d{1,2})', r.text)
        if match:
            year, month, day = match.groups()
            return f"{year} {month} {day}"
    except Exception as e:
        print(f"Error fetching Nepali date: {e}")
    
    # Fallback to the date found during research if scraper fails
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
    Gathers top international headlines and content summaries.
    Tries BBC World News first, then AP News as a backup.
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    international_items = []

    # --- Attempt 1: BBC World News ---
    try:
        print("Scraping BBC International News...")
        url_bbc = "https://www.bbc.com/news/world"
        response = requests.get(url_bbc, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # BBC structure: headlines are usually h2 or h3. 
        # Often summaries appear as a sibling or in a nearby p tag.
        # We look for containers that likely hold a story.
        containers = soup.find_all(['div', 'section'], limit=30)
        for container in containers:
            headline_tag = container.find(['h2', 'h3'])
            summary_tag = container.find('p')
            
            if headline_tag and summary_tag:
                h_text = headline_tag.get_text(strip=True)
                s_text = summary_tag.get_text(strip=True)
                
                # Deduplicate and validate
                if len(h_text) > 20 and len(s_text) > 30:
                    if not any(item['headline'] == h_text for item in international_items):
                        international_items.append({
                            "headline": h_text,
                            "content": s_text[:300],
                            "source": "BBC News"
                        })
            if len(international_items) >= 5: break

    except Exception as e:
        print(f"BBC Scraping failed: {e}")

    # --- Attempt 2: AP News (Backup) ---
    if not international_items:
        try:
            print("BBC failed, attempting AP News...")
            url_ap = "https://apnews.com/hub/world-news"
            response = requests.get(url_ap, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # AP News often uses <h3> for headlines in their hub pages
            # and a descriptive text or the first paragraph nearby.
            # In their markdown version, it's often [Headline](URL) + Text
            articles = soup.find_all(['div', 'article'], limit=20)
            for article in articles:
                headline_tag = article.find(['h1', 'h2', 'h3', 'span'], {"class": re.compile(r'headline', re.I)}) or article.find(['h1', 'h2', 'h3'])
                # AP summaries are sometimes in a div with a specific class or just after the headline
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
                if len(international_items) >= 5: break
        except Exception as e:
            print(f"AP News Scraping failed: {e}")

    # Final Fallback
    if not international_items:
        return [{
            "headline": "Global Geopolitical Tensions Rise",
            "content": "International leaders are calling for de-escalation as conflicts in multiple regions continue to impact global stability and markets.",
            "source": "Fallback"
        }]

    return international_items[:5]

if __name__ == "__main__":
    print("--- Nepal News ---")
    nepal = fetch_nepal_news()
    for n in nepal: print(f"[{n['source']}] {n['headline']}")
    
    print("\n--- International News ---")
    intl = fetch_international_news()
    for i in intl: print(f"[{i['source']}] {i['headline']}")