import yfinance as yf
from typing import List, Dict, Any

class APIAgent:
    @staticmethod
    async def fetch_stock_data(tickers: List[str]) -> Dict[str, Any]:
        """
        Fetch real-time and historical stock data for given tickers using batch request
        """
        stock_data = {}
        
        try:
            # Batch download recent close prices
            price_data = yf.download(tickers=tickers, period='1d', group_by='ticker', threads=False)

            for ticker in tickers:
                try:
                    stock = yf.Ticker(ticker)
                    info = stock.info

                    # Get current price safely from batch data
                    if len(tickers) == 1:
                        current_price = price_data['Close'][-1]
                    else:
                        current_price = price_data[ticker]['Close'][-1]

                    stock_data[ticker] = {
                        'current_price': current_price,
                        'company_name': info.get('longName', ticker),
                        'sector': info.get('sector', 'N/A'),
                        'market_cap': info.get('marketCap', 0),
                        'pe_ratio': info.get('trailingPE', None),
                        '52_week_high': info.get('fiftyTwoWeekHigh', None),
                        '52_week_low': info.get('fiftyTwoWeekLow', None),
                        'earnings_date': info.get('earningsDate', None)
                    }

                except Exception as e:
                    print(f"Error fetching {ticker}: {e}")
                    stock_data[ticker] = {'error': str(e)}
        
        except Exception as e:
            print(f"Batch download failed: {e}")
            for ticker in tickers:
                stock_data[ticker] = {'error': 'Batch fetch failed'}

        return stock_data

    @staticmethod
    def get_stock_recommendations(stock_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        recommendations = []

        for ticker, data in stock_data.items():
            if 'error' not in data:
                recommendation = {
                    'ticker': ticker,
                    'company_name': data['company_name'],
                    'recommendation': 'Hold',
                    'reasons': []
                }

                if data.get('pe_ratio') and data['pe_ratio'] < 15:
                    recommendation['recommendation'] = 'Buy'
                    recommendation['reasons'].append('Low P/E Ratio')

                if data.get('52_week_high') and data.get('current_price'):
                    percent_from_high = ((data['52_week_high'] - data['current_price']) / data['52_week_high']) * 100
                    if percent_from_high > 20:
                        recommendation['recommendation'] = 'Buy'
                        recommendation['reasons'].append('Significantly Below 52-Week High')

                recommendations.append(recommendation)

        return recommendations
