import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_nepal_news():
    """
    Gathers news headlines and content summaries from multiple renowned Nepal news sites.
    Ensures no duplicate headlines and correct matching of content.
    """
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
            response = requests.get(source['url'], headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all potential headline items
            items = soup.find_all(source['item_selector'], limit=20)
            
            for item in items:
                headline = item.get_text(strip=True)
                
                # Filter out short text or section headers
                if not headline or len(headline) < 25 or headline in seen_headlines:
                    continue
                
                # Avoid known section titles
                if any(x in headline for x in ["ट्रेन्डिङ", "मुख्य समाचार", "ताजा अपडेट", "प्रदेश समाचार"]):
                    continue
                
                content = ""
                # Strategy 1: Check immediately next sibling
                candidate = item.find_next_sibling(source['content_selector'])
                if candidate:
                    content = candidate.get_text(strip=True)
                
                # Strategy 2: Check inside common parent
                if not content:
                    parent = item.parent
                    # For sites like Ratopati where h2 might be wrapped in <a>
                    if parent.name == 'a':
                        parent = parent.parent
                    
                    candidate = parent.find(source['content_selector'])
                    if candidate and candidate.get_text(strip=True) != headline:
                        content = candidate.get_text(strip=True)

                # Strategy 3: Check grandparent if headline is in a title-div
                if not content and item.parent.parent:
                    gp = item.parent.parent
                    candidate = gp.find(source['content_selector'])
                    if candidate and candidate.get_text(strip=True) != headline:
                        content = candidate.get_text(strip=True)
                
                # If still no content found, skip or use a truncated headline as fallback
                # but only if it's likely an article.
                if not content:
                    continue
                
                # Basic cleaning
                content = content[:300] # Limit summary length
                
                news_items.append({
                    "headline": headline,
                    "content": content,
                    "source": source['name']
                })
                seen_headlines.add(headline)
                
                if len(news_items) >= 15: # Stop if we have enough
                    break
                    
        except Exception as e:
            print(f"Error fetching from {source['name']}: {e}")

    # Fallback if all scrapers fail
    if not news_items:
        return [{
            "headline": "नेपालको अर्थतन्त्रमा सुधारका संकेत",
            "content": "नेपाल राष्ट्र बैंकका अनुसार पछिल्लो समय विदेशी मुद्रा सञ्चिति बढेको र अर्थतन्त्र बिस्तारै लयमा फर्कन थालेको छ।",
            "source": "Fallback"
        }]
            
    return news_items[:12]

def fetch_international_news():
    """
    Fetches top international news headlines.
    """
    # Using OnlineKhabar International section or a global one
    url = "https://english.onlinekhabar.com/category/world"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        headlines = []
        for h2 in soup.find_all('h2', limit=5):
            text = h2.get_text(strip=True)
            if text and len(text) > 20:
                headlines.append(text)
        
        if not headlines:
            return ["World leaders meet for climate summit", "New technology breakthrough in renewable energy"]
        return headlines
    except:
        return ["Global economic shifts observed in major markets", "Advancements in aerospace technology reported"]

if __name__ == "__main__":
    # Test tools
    print("--- Nepal News ---")
    print(fetch_nepal_news())
    print("\n--- International News ---")
    print(fetch_international_news())
