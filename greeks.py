import numpy as np, yfinance as yf
from scipy.stats import norm
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

def calculateGreeks(S: float, K: float, sigma: float, r: float, q: float, t: float, optionType: str = 'call') -> dict:

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

def getOptionsData(ticker, strikePrice, volatility, riskFree, dividendYield, timeToExpiryInDays):
    
    underlyingPrice = yf.Ticker(ticker).fast_info["lastPrice"]
    timeToExpiryPercent = timeToExpiryInDays / 365.0

    greeks = calculateGreeks(underlyingPrice, strikePrice, volatility, riskFree, dividendYield, timeToExpiryPercent)

    return {
        "underlyingPrice": underlyingPrice,
        "strikePrice": strikePrice,
        "greeks": greeks
    }

print(getOptionsData("AAPL", 230.00, 0.3170, 0.0393, 0.0056, 3))
