from fastapi import FastAPI
from calculator import getOptionsData

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Home page"}

@app.get("/options/{ticker}/{strikePrice}/{volatility}/{riskFree}/{dividendYield}/{timeToExpiryInDays}")
async def greeks():
    return getOptionsData("AAPL", 230.00, 0.3158, 0.0386, 0.0055, 2)