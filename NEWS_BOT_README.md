# AI News Briefing Bot

텔레그램 봇을 통해 매일 자동으로 뉴스를 수집하고 Claude AI가 요약해서 전송하는 프로젝트입니다.

## 기능

- 키워드 기반 뉴스 검색 (Google News RSS)
- Claude AI를 이용한 뉴스 요약
- 텔레그램 봇으로 자동 전송
- 매일 자동 실행 (스케줄러 구현 예정)

## 파일 구조

```
telegram_news_bot.py     # 메인 통합 스크립트
news_summarizer.py       # 뉴스 수집 + Claude 요약 (테스트용)
get_chat_id.py          # 텔레그램 Chat ID 확인 스크립트
NEWS_BOT_README.md      # 이 파일
.env.example            # 환경 변수 예제
```

## 설치

```bash
pip install feedparser anthropic requests urllib3
```

## 환경 변수 설정

다음 환경 변수를 설정해야 합니다:

```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export TELEGRAM_BOT_TOKEN="your-telegram-bot-token"
export TELEGRAM_CHAT_ID="your-telegram-chat-id"
export NEWS_KEYWORD="인공지능"  # 선택사항, 기본값: 인공지능
```

## 사용 방법

### 1. 텔레그램 봇 생성

1. 텔레그램에서 `@BotFather` 검색
2. `/newbot` 명령어로 봇 생성
3. 봇 토큰 복사 → `TELEGRAM_BOT_TOKEN` 환경 변수에 설정

### 2. Chat ID 확인

```bash
# 먼저 텔레그램에서 봇에게 /start 메시지 전송
python get_chat_id.py
```

### 3. 뉴스 브리핑 실행

```bash
python telegram_news_bot.py
```

## Phase 1 (현재)

- ✅ 뉴스 수집 (Google News RSS)
- ✅ Claude AI 요약
- ✅ 텔레그램 전송 기능

## Phase 2 (예정)

- [ ] 스케줄러 추가 (매일 자동 실행)
- [ ] 웹 UI (사용자별 키워드 등록)
- [ ] 데이터베이스 (다중 사용자 지원)
- [ ] AWS Lambda 배포

## 주의사항

- API 키는 절대 GitHub에 올리지 마세요
- 회사 방화벽에서 텔레그램 API가 차단될 수 있습니다
- SSL 우회 코드는 개발용입니다 (운영 환경에서는 제거 권장)

## 라이센스

MIT
