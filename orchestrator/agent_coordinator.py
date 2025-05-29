


import os
import asyncio
from typing import List, Dict, Any
import google.generativeai as genai

from agents.api_agent import APIAgent
from agents.scraping_agent import ScrapingAgent
from agents.retriever_agent import RetrieverAgent
from agents.analysis_agent import AnalysisAgent
from agents.voice_agent import VoiceAgent
class AgentCoordinator:
    def __init__(self, gemini_api_key: str = None):
        """
        Initialize all agents and Gemini API
        
        Args:
            gemini_api_key (str, optional): Google Gemini API key
        """
        # Configure Gemini API
        if not gemini_api_key:
            gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        if not gemini_api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable.")
        
        genai.configure(api_key=gemini_api_key)
        
        # Initialize generation model
        self.llm_model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Initialize agents
        self.api_agent = APIAgent()
        self.scraping_agent = ScrapingAgent()
        self.retriever_agent = RetrieverAgent()
        self.analysis_agent = AnalysisAgent()
        self.voice_agent = VoiceAgent()
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """
        Coordinate agents to process a financial query using Gemini
        
        Args:
            query (str): User's financial query
        
        Returns:
            Dict[str, Any]: Comprehensive query response
        """
        # 1. Use Gemini to extract tickers and generate insights
        tickers = await self._extract_tickers_with_gemini(query)
        print(tickers)
        # 2. Fetch stock data concurrently
        stock_data = await self.api_agent.fetch_stock_data(tickers)
        
        # 3. Scrape financial news
        news_data = await self.scraping_agent.crawl_financial_news(tickers)
        
        # 4. Combine and index documents
        combined_docs = self.retriever_agent.combine_document_sources(
            list(stock_data.values()),
            [item for sublist in news_data.values() for item in sublist]
        )
        self.retriever_agent.index_documents(combined_docs)
        
        # 5. Perform semantic search
        contextual_results = self.retriever_agent.semantic_search(query)
        
        # 6. Analyze portfolio
        risk_analysis = self.analysis_agent.portfolio_risk_analysis(stock_data)
        
        # 7. Generate narrative response with Gemini
        narrative_response = await self._generate_narrative_with_gemini(
            stock_data, 
            news_data, 
            risk_analysis, 
            contextual_results
        )
        
        # 8. Generate voice response (optional)
        voice_response = self.voice_agent.generate_voice_response(narrative_response)
        
        return {
            'stock_data': stock_data,
            'news_data': news_data,
            'risk_analysis': risk_analysis,
            'narrative_response': narrative_response,
            'voice_response': voice_response
        }
    
    async def _extract_tickers_with_gemini(self, query: str) -> List[str]:
        """
        Extract ticker symbols using Gemini
        
        Args:
            query (str): User's financial query
        
        Returns:
            List[str]: Extracted ticker symbols
        """
        prompt = f"""
        Extract stock ticker symbols from the following financial query. 
        Return ONLY the ticker symbols as a comma-separated list. 
        If no clear tickers are found, suggest relevant tech or finance tickers.
        
        Query: {query}
        """
        
        try:
            response = self.llm_model.generate_content(prompt)
            
            # Extract and clean tickers
            tickers_str = response.text.strip()
            tickers = [ticker.strip().upper() for ticker in tickers_str.split(',')]
            
            # Fallback to some default tickers if none found
            return tickers if tickers else ['AAPL', 'GOOGL', 'MSFT', 'AMZN']
        
        except Exception as e:
            print(f"Ticker extraction error: {e}")
            return ['AAPL', 'GOOGL', 'MSFT', 'AMZN']
    
    async def _generate_narrative_with_gemini(
        self, 
        stock_data: Dict[str, Any], 
        news_data: Dict[str, Any], 
        risk_analysis: Dict[str, Any],
        contextual_results: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a narrative response using Gemini
        
        Args:
            stock_data (Dict[str, Any]): Stock information
            news_data (Dict[str, Any]): News information
            risk_analysis (Dict[str, Any]): Portfolio risk analysis
            contextual_results (List[Dict[str, Any]]): Semantic search results
        
        Returns:
            str: Narrative response
        """
        # Prepare data for Gemini prompt
        stocks_summary = "\n".join([
            f"{ticker}: Price=${data.get('current_price', 'N/A')}, "
            f"Market Cap=${data.get('market_cap', 'N/A'):,}"
            for ticker, data in stock_data.items() if 'error' not in data
        ])
        
        news_summary = "\n".join([
            f"{ticker} News: " + 
            ", ".join([article.get('title', 'No title') for article in news[:2]])
            for ticker, news in news_data.items()
        ])
        
        prompt = f"""
        Generate a comprehensive market brief based on the following financial data:

        Stock Overview:
        {stocks_summary}

        Recent News:
        {news_summary}

        Risk Analysis:
        Total Stocks: {risk_analysis.get('total_stocks', 0)}

        Contextual Insights:
        {', '.join([result.get('title', 'Insight') for result in contextual_results])}

        Create a professional, concise market brief that provides:
        1. An overview of stock performance
        2. Key news highlights
        3. Potential market implications
        4. Brief risk assessment
        """
        
        try:
            response = self.llm_model.generate_content(prompt)
            return response.text
        
        except Exception as e:
            print(f"Narrative generation error: {e}")
            return "Unable to generate market brief at this time."