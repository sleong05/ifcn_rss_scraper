import feedparser
import json
from datetime import datetime
import requests
feeds = [
    # { 'url': 'https://www.factcheck.org/feed/', 'country': 'US', 'organization': 'FactCheck', 'hasContent': True },
    # { 'url': 'https://www.politifact.com/rss/factchecks/', 'country': 'US', 'organization': 'PolitiFact', 'hasContent': True },
    # { 'url': 'https://thedispatch.com/feed/', 'country': 'US', 'organization': 'The Dispatch', 'hasContent': False },
    # { 'url': 'https://www.snopes.com/feed/', 'country': 'US', 'organization': 'Snopes', 'hasContent': False },
    # { 'url': 'https://wisconsinwatch.org/feed/', 'country': 'US', 'organization': 'Wisconsin Watch', 'hasContent': True },
    # { 'url': 'https://checkyourfact.com/feed/', 'country': 'US', 'organization': 'Check Your Fact', 'hasContent': True },
    # { 'url': 'https://factchequeado.com/feed', 'country': 'US', 'organization': 'Factchequeado', 'hasContent': True },
    # { 'url': 'https://leadstories.com/atom.xml', 'country': 'US', 'organization': 'Lead Stories', 'hasContent': True },
    # { 'url': 'https://feeds.feedburner.com/PublicoRSS', 'country': 'Portugal', 'organization': 'PUBLICO', 'hasContent': False },
]

from bs4 import BeautifulSoup
from datetime import datetime

def fetch_full_content(url):
    try:
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')
        # Remove noise
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            tag.decompose()
        # Most articles are in <article> tag, fall back to <main> or <body>
        article = soup.find('article') or soup.find('main') or soup.find('body')
        return article.get_text(separator=' ', strip=True) if article else ''
    except Exception as e:
        print(f"  Failed to fetch content from {url}: {e}")
        return ''
    
for feed_config in feeds:
    feed = feedparser.parse(feed_config['url'])
    
    articles = []
    for entry in feed.entries:

        if feed_config['hasContent']:
            content = entry.get('content', [{}])[0].get('value', '') or entry.get('summary', '')
        else:
            print(f"  Fetching full content for: {entry.get('title', '')[:50]}")
            content = fetch_full_content(entry.get('link', ''))

        articles.append({
            'title': entry.get('title', ''),
            'content': content,
            'url': entry.get('link', ''),
            'publication_date': entry.get('published', ''),
            'date_gathered': datetime.utcnow().isoformat(),
            'country': feed_config['country'],
            'organization': feed_config['organization'],
        })
    
    filename = f"{feed_config['organization']}.json"
    with open(filename, 'w') as f:
        json.dump(articles, f, indent=2)
    
    print(f"Wrote {len(articles)} articles to {filename}")