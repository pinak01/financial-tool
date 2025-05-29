import numpy as np
from typing import List, Dict, Any, Optional
import statistics

class AnalysisAgent:
    @staticmethod
    def portfolio_risk_analysis(stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive portfolio risk analysis
        
        Args:
            stock_data (Dict[str, Any]): Comprehensive stock data
        
        Returns:
            Dict[str, Any]: Detailed portfolio risk analysis results
        """
        # Filter out error entries
        valid_stocks = {
            ticker: data for ticker, data in stock_data.items() 
            if 'error' not in data
        }
        
        # Prepare data collections
        market_caps = []
        pe_ratios = []
        prices = []
        sector_distribution = {}
        
        # Collect financial metrics
        for ticker, data in valid_stocks.items():
            # Market Cap
            market_cap = data.get('market_cap', 0)
            market_caps.append(market_cap)
            
            # Price
            current_price = data.get('current_price', 0)
            prices.append(current_price)
            
            # PE Ratio
            pe_ratio = data.get('pe_ratio', 0)
            if pe_ratio:
                pe_ratios.append(pe_ratio)
            
            # Sector Distribution
            sector = data.get('sector', 'Unknown')
            sector_distribution[sector] = sector_distribution.get(sector, 0) + 1
        
        # Risk Calculations
        analysis_results = {
            'total_stocks': len(valid_stocks),
            'risk_metrics': {
                # Market Cap Analysis
                'total_market_cap': sum(market_caps),
                'avg_market_cap': np.mean(market_caps) if market_caps else 0,
                'market_cap_std_dev': np.std(market_caps) if len(market_caps) > 1 else 0,
                
                # Price Analysis
                'avg_price': np.mean(prices) if prices else 0,
                'price_volatility': np.std(prices) if len(prices) > 1 else 0,
                
                # PE Ratio Analysis
                'avg_pe_ratio': np.mean(pe_ratios) if pe_ratios else 0,
                'pe_ratio_volatility': np.std(pe_ratios) if len(pe_ratios) > 1 else 0,
                
                # Sector Concentration
                'sector_distribution': sector_distribution
            },
            'portfolio_health_indicators': AnalysisAgent._assess_portfolio_health(
                market_caps, 
                pe_ratios, 
                sector_distribution
            )
        }
        
        return analysis_results
    
    @classmethod
    def _assess_portfolio_health(
        cls, 
        market_caps: List[float], 
        pe_ratios: List[float], 
        sector_distribution: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Assess overall portfolio health
        
        Args:
            market_caps (List[float]): List of market capitalizations
            pe_ratios (List[float]): List of PE ratios
            sector_distribution (Dict[str, int]): Sector distribution
        
        Returns:
            Dict[str, Any]: Portfolio health indicators
        """
        health_indicators = {
            # Diversification Assessment
            'diversification_score': cls._calculate_diversification_score(sector_distribution),
            
            # Concentration Risk
            'sector_concentration': cls._analyze_sector_concentration(sector_distribution),
            
            # Market Cap Distribution
            'market_cap_distribution': cls._classify_market_cap_distribution(market_caps),
            
            # Valuation Assessment
            'valuation_health': cls._assess_valuation_health(pe_ratios)
        }
        
        return health_indicators
    
    @staticmethod
    def _calculate_diversification_score(sector_distribution: Dict[str, int]) -> float:
        """
        Calculate portfolio diversification score
        
        Args:
            sector_distribution (Dict[str, int]): Sector distribution
        
        Returns:
            float: Diversification score (0-100)
        """
        total_stocks = sum(sector_distribution.values())
        num_sectors = len(sector_distribution)
        
        # Calculate entropy-based diversification score
        entropy_scores = []
        for count in sector_distribution.values():
            sector_proportion = count / total_stocks
            entropy_scores.append(-sector_proportion * np.log(sector_proportion))
        
        # Normalize and scale
        max_possible_entropy = np.log(num_sectors) if num_sectors > 0 else 1
        diversification_score = (sum(entropy_scores) / max_possible_entropy) * 100
        
        return min(max(diversification_score, 0), 100)
    
    @staticmethod
    def _analyze_sector_concentration(sector_distribution: Dict[str, int]) -> Dict[str, Any]:
        """
        Analyze sector concentration risks
        
        Args:
            sector_distribution (Dict[str, int]): Sector distribution
        
        Returns:
            Dict[str, Any]: Sector concentration analysis
        """
        total_stocks = sum(sector_distribution.values())
        
        # Identify most and least concentrated sectors
        sector_percentages = {
            sector: (count / total_stocks) * 100 
            for sector, count in sector_distribution.items()
        }
        
        # Sort sectors by percentage
        sorted_sectors = sorted(
            sector_percentages.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return {
            'most_concentrated_sector': sorted_sectors[0][0] if sorted_sectors else 'N/A',
            'most_concentrated_percentage': sorted_sectors[0][1] if sorted_sectors else 0,
            'sector_percentages': sector_percentages
        }
    
    @staticmethod
    def _classify_market_cap_distribution(market_caps: List[float]) -> Dict[str, Any]:
        """
        Classify market cap distribution
        
        Args:
            market_caps (List[float]): List of market capitalizations
        
        Returns:
            Dict[str, Any]: Market cap distribution analysis
        """
        if not market_caps:
            return {
                'large_cap_percentage': 0,
                'mid_cap_percentage': 0,
                'small_cap_percentage': 0
            }
        
        # Market cap classification thresholds (in billions)
        large_cap_threshold = 10_000_000_000  # $10B
        mid_cap_threshold = 2_000_000_000    # $2B
        
        # Classify market caps
        large_cap = sum(1 for cap in market_caps if cap >= large_cap_threshold)
        mid_cap = sum(1 for cap in market_caps if large_cap_threshold > cap >= mid_cap_threshold)
        small_cap = sum(1 for cap in market_caps if cap < mid_cap_threshold)
        
        total_stocks = len(market_caps)
        
        return {
            'large_cap_percentage': (large_cap / total_stocks) * 100,
            'mid_cap_percentage': (mid_cap / total_stocks) * 100,
            'small_cap_percentage': (small_cap / total_stocks) * 100
        }
    
    @staticmethod
    def _assess_valuation_health(pe_ratios: List[float]) -> Dict[str, Any]:
        """
        Assess portfolio valuation health
        
        Args:
            pe_ratios (List[float]): List of PE ratios
        
        Returns:
            Dict[str, Any]: Valuation health indicators
        """
        if not pe_ratios:
            return {
                'average_pe_ratio': 0,
                'pe_ratio_range': {'min': 0, 'max': 0},
                'valuation_status': 'Insufficient Data'
            }
        
        # Basic valuation assessment
        avg_pe = np.mean(pe_ratios)
        
        # Determine valuation status
        if avg_pe < 10:
            valuation_status = 'Potentially Undervalued'
        elif 10 <= avg_pe < 20:
            valuation_status = 'Fairly Valued'
        elif 20 <= avg_pe < 30:
            valuation_status = 'Slightly Overvalued'
        else:
            valuation_status = 'Overvalued'
        
        return {
            'average_pe_ratio': avg_pe,
            'pe_ratio_range': {
                'min': min(pe_ratios),
                'max': max(pe_ratios)
            },
            'valuation_status': valuation_status
        }
    
    @staticmethod
    def generate_investment_insights(analysis_results: Dict[str, Any]) -> str:
        """
        Generate textual investment insights based on analysis results
        
        Args:
            analysis_results (Dict[str, Any]): Portfolio analysis results
        
        Returns:
            str: Narrative investment insights
        """
        insights = "Portfolio Investment Insights:\n\n"
        
        # Diversification Insights
        div_score = analysis_results['portfolio_health_indicators']['diversification_score']
        insights += f"Diversification Score: {div_score:.2f}/100\n"
        if div_score < 40:
            insights += "- Your portfolio lacks diversification. Consider spreading investments across more sectors.\n"
        elif div_score < 70:
            insights += "- Moderate diversification. There's room for improvement in sector allocation.\n"
        else:
            insights += "- Excellent diversification across different sectors.\n"
        
        # Sector Concentration
        sector_conc = analysis_results['portfolio_health_indicators']['sector_concentration']
        insights += f"\nSector Concentration:\n"
        insights += f"- Most Concentrated Sector: {sector_conc['most_concentrated_sector']}\n"
        insights += f"- Sector Concentration: {sector_conc['most_concentrated_percentage']:.2f}%\n"
        
        # Valuation Insights
        val_health = analysis_results['portfolio_health_indicators']['valuation_health']
        insights += f"\nValuation Health:\n"
        insights += f"- Average PE Ratio: {val_health['average_pe_ratio']:.2f}\n"
        insights += f"- Valuation Status: {val_health['valuation_status']}\n"
        
        # Market Cap Distribution
        cap_dist = analysis_results['portfolio_health_indicators']['market_cap_distribution']
        insights += f"\nMarket Cap Distribution:\n"
        insights += f"- Large Cap: {cap_dist['large_cap_percentage']:.2f}%\n"
        insights += f"- Mid Cap: {cap_dist['mid_cap_percentage']:.2f}%\n"
        insights += f"- Small Cap: {cap_dist['small_cap_percentage']:.2f}%\n"
        
        return insights