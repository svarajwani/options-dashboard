import numpy as np, yfinance as yf
from scipy.stats import norm
from datetime import date, timedelta
from enum import Enum


"""
According to the Black-Scholes option pricing model (its Merton's extension that accounts for dividends), there are six parameters which affect option prices:
S = underlying price ($$$ per share)
K = strike price ($$$ per share)
σ = volatility (% p.a.)
r = continuously compounded risk-free interest rate (% p.a.)
q = continuously compounded dividend yield (% p.a.)
t = time to expiration (% of year)
"""

#note for when you come back to this - keep putting logic into a class. basically half done.

class OptionsCalculator:
    def __init__(self, ticker: str, strikePrice: float, expiryDate: date, optionType: str = 'call'):
        self.ticker = ticker
        self.strikePrice = strikePrice
        self.daysUntilExpiry = (expiryDate - date.today()).days #parse to calculate days
        self.optionType = optionType
        self.riskFree = 0.0045 #change later to fetch from FRED API
        self.underlyingPrice = None
        self.volatility = None 
        self.dividendYield = None

    def getMarketData(self):
        stock = yf.Ticker(self.ticker)
        info = stock.info
        self.underlyingPrice = info.get('regularMarketPrice', 0)
        # timeToExpiryPercent = timeToExpiryInDays / 365.0
        self.dividendYield = info.get('dividendYield', 0) 
        self.volatility = 0.2529 


    def calculateGreeks(self, S: float, K: float, sigma: float, r: float, q: float, t: float, optionType: str = 'call') -> dict:

        d1 = (np.log(S/K) + t * (r - q + (sigma**2)/2)) / (sigma * np.sqrt(t))
        d2 = d1 - sigma * np.sqrt(t)

        optionPrice = 0
        if optionType == 'call':
            optionPrice = S * np.exp(-q * t) * norm.cdf(d1) - (K * np.exp(-r * t) * norm.cdf(d2))
        elif optionType == 'put':
            optionPrice = K * np.exp(-r * t) * norm.cdf(-d2) - (S * np.exp(-q * t) * norm.cdf(-d1))
        else:
            print("Invalid option type")
            return None
        
        delta = 0
        if optionType == 'call':
            delta = np.exp(-q * t) * norm.cdf(d1)
        elif optionType == 'put':
            delta = np.exp(-q * t) * (norm.cdf(d1) - 1)

        gamma = (np.exp(-q * t) / (S * sigma * np.sqrt(t))) * norm.pdf(d1)

        theta = 0
        if optionType == 'call':
            theta = ((-(((S * sigma * np.exp(-q * t)) / (2 * np.sqrt(t))) * norm.pdf(d1)))
                    - r * K * np.exp(-r * t) * norm.cdf(d2) + q * S * np.exp(-q * t) * norm.cdf(d1))
        elif optionType == 'put':
            theta = ((-(((S * sigma * np.exp(-q * t)) / (2 * np.sqrt(t))) * norm.pdf(d1)))
                    - r * K * np.exp(-r * t) * norm.cdf(-d2) + q * S * np.exp(-q * t) * norm.cdf(-d1))
        theta = theta / 365.0
            
        vega = 0.01 * S * np.exp(-q * t) * np.sqrt(t) * norm.pdf(d1)

        rho = 0
        if optionType == 'call':
            rho = 0.01 * K * t * np.exp(-r * t) * norm.cdf(d2)
        elif optionType == 'put':
            rho = -0.01 * K * t * np.exp(-r * t) * norm.cdf(-d2)
        
        return {
            "optionPrice": round(float(optionPrice), 2),
            "delta": round(float(delta), 5),
            "gamma": round(float(gamma), 5),
            "theta": round(float(theta), 5),
            "vega": round(float(vega), 5),
            "rho": round(float(rho), 5),
        }

    def getOptionsData(self):  
        self.getMarketData()
        greeks = self.calculateGreeks(self.underlyingPrice, 
                                        self.strikePrice, 
                                        self.volatility, 
                                        self.riskFree, 
                                        self.dividendYield / 100, 
                                        (self.daysUntilExpiry / 365.0)
                                    )

        return {
            "underlyingPrice": self.underlyingPrice,
            "strikePrice": self.strikePrice,
            "greeks": greeks
        }

calc = OptionsCalculator("AAPL", 225.00, date.today() + timedelta(days=29))
print(calc.getOptionsData())
print(calc.underlyingPrice)
print(calc.strikePrice)
print(calc.daysUntilExpiry)
print(calc.riskFree)
print(calc.volatility)
print(calc.dividendYield)