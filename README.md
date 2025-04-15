# GOMOS 미장 단타 시그널 자동화

미국 주식 시장을 대상으로 한 자동화된 단타 매매 타이밍 분석 시스템입니다.

## 주요 기능
- 매일 주요 기술주의 변동률 및 거래량 기반 분석
- "매수 / 매도 / 대기" 신호 판단
- Notion DB에 자동 기록
- GitHub Actions를 통한 완전 자동 실행

## 설정 방법

1. `.github/workflows/auto_run.yml`은 매일 오전 7:10 (KST) 실행됨
2. GitHub Secrets에 아래 값 등록:
   - `NOTION_TOKEN`
   - `NOTION_DB_ID`

## 종목
- NVDA, AMD, AAPL, MSFT, GOOGL, TSLA, PLTR, META, AMZN
