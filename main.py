import yfinance as yf
from notion_client import Client
from datetime import datetime
import os

# 환경변수에서 토큰과 DB ID 불러오기
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DB_ID = os.getenv("NOTION_DB_ID")

notion = Client(auth=NOTION_TOKEN)

# 분석 대상 종목 리스트 (미장 중심 AI/기술주 샘플)
TICKERS = ["NVDA", "AMD", "AAPL", "MSFT", "GOOGL", "TSLA", "PLTR", "META", "AMZN"]

results = []

for ticker in TICKERS:
    stock = yf.Ticker(ticker)
    hist = stock.history(period="5d")

    if len(hist) < 2:
        continue

    today = hist.iloc[-1]
    yesterday = hist.iloc[-2]

    price_change = (today["Close"] - yesterday["Close"]) / yesterday["Close"] * 100
    volume_ratio = today["Volume"] / hist["Volume"].mean()

    if price_change > 3 and volume_ratio > 2:
        signal = "매수"
        reason = f"전일 대비 +{price_change:.1f}%, 거래량 폭증 ({volume_ratio:.1f}배)"
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

# 결과를 노션에 기록
for item in results:
    notion.pages.create(
        parent={"database_id": NOTION_DB_ID},
        properties={
            "종목": {"title": [{"text": {"content": item["ticker"]}}]},
            "날짜": {"date": {"start": datetime.now().isoformat()}},
            "시그널": {"select": {"name": item["signal"]}},
            "이유": {"rich_text": [{"text": {"content": item["reason"]}}]}
        }
    )
