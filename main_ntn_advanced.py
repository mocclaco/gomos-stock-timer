import yfinance as yf
import requests
from datetime import datetime
import os

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DB_ID = os.getenv("NOTION_DB_ID")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

TICKERS = ["NVDA", "AMD", "AAPL", "MSFT", "GOOGL", "TSLA", "PLTR", "META", "AMZN"]

results = []

for ticker in TICKERS:
    stock = yf.Ticker(ticker)
    hist = stock.history(period="5d")

    if len(hist) < 3:
        continue

    today = hist.iloc[-1]
    yesterday = hist.iloc[-2]
    day_before = hist.iloc[-3]

    price_change = (today["Close"] - yesterday["Close"]) / yesterday["Close"] * 100
    volume_ratio = today["Volume"] / hist["Volume"].mean()
    high_ratio = today["High"] / hist["High"][-3:].mean()
    prev_change = (yesterday["Close"] - day_before["Close"]) / day_before["Close"] * 100

    score = 0
    if price_change > 1.5:
        score += 1
    if volume_ratio > 1.2:
        score += 1
    if high_ratio > 1.05:
        score += 1
    if prev_change > 1:
        score += 1

    if score >= 2:
        signal = "매수"
        reason = f"점수 {score}점 / 상승률 {price_change:.1f}% / 거래량 {volume_ratio:.1f}배 / 고점비율 {high_ratio:.2f}"
    elif price_change < -2:
        signal = "매도"
        reason = f"급락 (-{abs(price_change):.1f}%) 발생"
    else:
        signal = "대기"
        reason = "특이점 없음"

    results.append({
        "ticker": ticker,
        "signal": signal,
        "reason": reason
    })

# 결과를 Notion에 기록
for item in results:
    payload = {
        "parent": { "database_id": NOTION_DB_ID },
        "properties": {
            "종목": {
                "title": [
                    {
                        "text": {
                            "content": item["ticker"]
                        }
                    }
                ]
            },
            "시그널": {
                "select": {
                    "name": item["signal"]
                }
            },
            "날짜": {
                "date": {
                    "start": datetime.now().isoformat()
                }
            },
            "이유": {
                "rich_text": [
                    {
                        "text": {
                            "content": item["reason"]
                        }
                    }
                ]
            }
        }
    }

    res = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload)
    print(f"{item['ticker']} → Status: {res.status_code} / {res.text}")
