from fastapi import FastAPI
from greeks import calculateGreeks

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Home page"}

@app.get("/greeks")
async def greeks():
    return calculateGreeks(228.36, 227.50, 0.3491, 0.0393, 0.0044, (4/365.0), 'call')