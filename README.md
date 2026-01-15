# AI News Briefing Bot (tnews)

텔레그램 봇을 통해 매일 자동으로 뉴스를 수집하고 Claude AI가 요약해서 전송하는 프로젝트입니다.

## 📚 문서

- [사용 가이드](NEWS_BOT_README.md) - 설치 및 사용 방법
- [개발 히스토리](DEVELOPMENT_HISTORY.md) - 프로젝트 개발 과정

## 🚀 빠른 시작

```bash
# 1. 저장소 클론
git clone https://github.com/hwayobi2020/tnews.git
cd tnews

# 2. 라이브러리 설치
pip install feedparser anthropic requests urllib3

# 3. 환경 변수 설정
export ANTHROPIC_API_KEY="your-key"
export TELEGRAM_BOT_TOKEN="your-token"
export TELEGRAM_CHAT_ID="your-chat-id"

# 4. 실행
python telegram_news_bot.py
```

## ✨ 주요 기능

- 🔍 키워드 기반 뉴스 검색 (Google News RSS)
- 🤖 Claude AI 요약
- 📱 텔레그램 자동 전송
- ⏰ 스케줄러 (예정)

## 📂 프로젝트 구조

```
tnews/
├── telegram_news_bot.py       # 메인 스크립트
├── news_summarizer.py         # 뉴스 수집 + 요약
├── get_chat_id.py            # Chat ID 확인
├── README.md                 # 이 파일
├── NEWS_BOT_README.md        # 상세 가이드
├── DEVELOPMENT_HISTORY.md    # 개발 히스토리
└── .env.example              # 환경 변수 예제
```

## 📝 라이센스

MIT

---

**Made with ❤️ by hwayobi2020**
