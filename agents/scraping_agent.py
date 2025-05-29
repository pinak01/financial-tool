import requests
from bs4 import BeautifulSoup
import asyncio
from typing import List, Dict, Any

class ScrapingAgent:
    @staticmethod
    async def crawl_financial_news(tickers: List[str]) -> Dict[str, List[Dict[str, str]]]:
        """
        Crawl financial news sites for latest news about given tickers
        
        Args:
            tickers (List[str]): List of stock ticker symbols
        
        Returns:
            Dict[str, List[Dict[str, str]]]: News articles for each ticker
        """
        news_data = {}
        
        async def fetch_news_for_ticker(ticker):
            try:
                # Example news sources (modify URLs as needed)
                news_sources = [
                    f"https://finance.yahoo.com/quote/{ticker}/news",
                    
                ]
                
                ticker_news = []
                
                for source_url in news_sources:
                    try:
                        response = requests.get(source_url, headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                        })
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Extract news articles (this is a simplified example)
                        articles = soup.find_all(['h3', 'h2'], class_=['news-title', 'article-title'])
                        
                        for article in articles[:3]:  # Limit to 3 articles per source
                            title = article.get_text(strip=True)
                            link = article.find('a')['href'] if article.find('a') else source_url
                            
                            ticker_news.append({
                                'title': title,
                                'link': link,
                                'source': source_url
                            })
                    except Exception as e:
                        print(f"Error scraping {source_url} for {ticker}: {e}")
                
                news_data[ticker] = ticker_news
            except Exception as e:
                print(f"Error processing news for {ticker}: {e}")
                news_data[ticker] = []
        
        # Use asyncio to fetch news concurrently
        await asyncio.gather(*[fetch_news_for_ticker(ticker) for ticker in tickers])
        
        return news_data
    
    @staticmethod
    def extract_key_insights(news_data: Dict[str, List[Dict[str, str]]]) -> Dict[str, List[str]]:
        """
        Extract key insights from scraped news articles
        
        Args:
            news_data (Dict[str, List[Dict[str, str]]]): News articles for tickers
        
        Returns:
            Dict[str, List[str]]: Key insights for each ticker
        """
        insights = {}
        
        for ticker, articles in news_data.items():
            ticker_insights = []
            
            for article in articles:
                # Basic sentiment and insight extraction 
                # (In a real scenario, you'd use NLP for more advanced analysis)
                if any(keyword in article['title'].lower() for keyword in ['earnings', 'beat', 'miss']):
                    ticker_insights.append(f"Earnings-related: {article['title']}")
                
                if any(keyword in article['title'].lower() for keyword in ['merger', 'acquisition', 'partnership']):
                    ticker_insights.append(f"Strategic move: {article['title']}")
                
                if any(keyword in article['title'].lower() for keyword in ['technology', 'innovation', 'breakthrough']):
                    ticker_insights.append(f"Tech development: {article['title']}")
            
            insights[ticker] = ticker_insights
        
        return insights