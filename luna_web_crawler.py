# luna_web_crawler.py
"""
Luna Web Crawler System
Crawls websites and analyzes content with Luna's personality
Integrated with Global Awareness System
"""

import requests
from bs4 import BeautifulSoup
import re
import time
from typing import Dict, Optional
from datetime import datetime

class LunaWebCrawler:
    """Web crawler for Luna to analyze websites"""
    
    def __init__(self):
        self.crawl_history = []
        self.max_history = 50
        print("🌐 Luna Web Crawler initialized")
    
    def crawl_website(self, url: str) -> Dict:
        """Crawl a website and extract readable content"""
        try:
            # Add user agent to avoid being blocked
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            print(f"🌐 Crawling website: {url}")
            
            # Fetch the webpage
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text content
            text = soup.get_text()
            
            # Clean up the text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Get page title
            title = soup.find('title')
            title_text = title.get_text() if title else "No title found"
            
            # Extract main content (try to find the most relevant content)
            main_content = ""
            
            # Look for main content areas
            main_selectors = ['main', 'article', '.content', '.main', '#content', '#main']
            for selector in main_selectors:
                main_elem = soup.select_one(selector)
                if main_elem:
                    main_content = main_elem.get_text()
                    break
            
            # If no main content found, use the first few paragraphs
            if not main_content:
                paragraphs = soup.find_all('p')
                main_content = ' '.join([p.get_text() for p in paragraphs[:5]])
            
            # Limit content length to avoid overwhelming the AI
            if len(main_content) > 2000:
                main_content = main_content[:2000] + "..."
            
            # Store in crawl history
            crawl_data = {
                'title': title_text,
                'content': main_content,
                'full_text': text[:1000] + "..." if len(text) > 1000 else text,
                'url': url,
                'timestamp': time.time()
            }
            
            self.crawl_history.append(crawl_data)
            if len(self.crawl_history) > self.max_history:
                self.crawl_history.pop(0)
            
            print(f"✅ Successfully crawled: {title_text}")
            return crawl_data
            
        except requests.exceptions.Timeout:
            print(f"❌ Timeout crawling {url}")
            return {
                'title': "Timeout Error",
                'content': f"The website took too long to respond. Try again later.",
                'full_text': f"Timeout accessing {url}",
                'url': url,
                'error': True
            }
        except requests.exceptions.RequestException as e:
            print(f"❌ Request error crawling {url}: {e}")
            return {
                'title': "Connection Error",
                'content': f"Failed to connect to the website: {str(e)}",
                'full_text': f"Error accessing {url}: {str(e)}",
                'url': url,
                'error': True
            }
        except Exception as e:
            print(f"❌ Web Crawl Error: {e}")
            return {
                'title': "Error",
                'content': f"Failed to crawl website: {str(e)}",
                'full_text': f"Error accessing {url}: {str(e)}",
                'url': url,
                'error': True
            }
    
    def analyze_with_luna(self, webpage_data: Dict, username: str, generate_luna_reply_func) -> str:
        """Analyze webpage content with Luna's personality"""
        try:
            title = webpage_data.get('title', 'Unknown')
            content = webpage_data.get('content', 'No content found')
            url = webpage_data.get('url', 'Unknown URL')
            
            # Check if there was an error
            if webpage_data.get('error', False):
                return f"Tch... I tried to check out that website but ran into some issues. {content} Maybe try a different link?"
            
            # Create analysis prompt for Luna
            analysis_prompt = f"""Website Analysis Request:
Title: {title}
URL: {url}
Content Summary: {content[:500]}...

Analyze this website and share your thoughts about it. Be tsundere, sassy, and authentic to your personality. Comment on what you found interesting, useful, or notable about the content."""
            
            # Generate Luna's analysis
            reply_result = generate_luna_reply_func(analysis_prompt, username, "discord")
            
            # Handle tuple unpacking
            if isinstance(reply_result, tuple):
                response, success = reply_result
            else:
                response = reply_result
                success = True
            
            if success and response:
                # Add website context
                final_response = f"🌐 **{title}**\n{response}\n\n🔗 {url}"
                return final_response
            else:
                return f"Hmph... I looked at that website but I'm having trouble organizing my thoughts about it right now. Try asking me again?"
                
        except Exception as e:
            print(f"❌ Error analyzing webpage with Luna: {e}")
            return f"Tch... I ran into some issues analyzing that website. Error: {e}"
    
    def get_crawl_history(self, limit: int = 10) -> list:
        """Get recent crawl history"""
        return self.crawl_history[-limit:]
    
    def search_crawl_history(self, query: str) -> list:
        """Search crawl history for specific content"""
        results = []
        query_lower = query.lower()
        
        for crawl in self.crawl_history:
            if (query_lower in crawl['title'].lower() or 
                query_lower in crawl['content'].lower() or 
                query_lower in crawl['url'].lower()):
                results.append(crawl)
        
        return results

# Global instance
luna_web_crawler = None

def initialize_luna_web_crawler() -> LunaWebCrawler:
    """Initialize the Luna web crawler"""
    global luna_web_crawler
    if not luna_web_crawler:
        luna_web_crawler = LunaWebCrawler()
    return luna_web_crawler

def get_luna_web_crawler() -> Optional[LunaWebCrawler]:
    """Get the Luna web crawler instance"""
    return luna_web_crawler

def crawl_and_analyze(url: str, username: str, generate_luna_reply_func, add_to_awareness_func=None, channel: str = "discord") -> str:
    """Crawl a website and analyze it with Luna"""
    global luna_web_crawler
    
    if not luna_web_crawler:
        luna_web_crawler = initialize_luna_web_crawler()
    
    # Crawl the website
    webpage_data = luna_web_crawler.crawl_website(url)
    
    # Analyze with Luna
    analysis = luna_web_crawler.analyze_with_luna(webpage_data, username, generate_luna_reply_func)
    
    # Add to Global Awareness System if available
    if add_to_awareness_func and not webpage_data.get('error', False):
        try:
            add_to_awareness_func(
                platform='discord',
                channel=channel,
                username=username,
                user_message=f"[Web Analysis Request] {url}",
                luna_response=analysis,
                emotion='curious',
                context='web_browsing'
            )
            print(f"🌍 Added web analysis to Global Awareness")
        except Exception as e:
            print(f"⚠️ Error adding to Global Awareness: {e}")
    
    return analysis

