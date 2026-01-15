# 개발 히스토리

## 프로젝트 개요
텔레그램 봇을 통해 매일 자동으로 뉴스를 수집하고 Claude AI가 요약해서 전송하는 시스템

**개발 기간**: 2026-01-16
**개발자**: hwayobi2020
**목표**: 회사 사람들이 관심 키워드로 매일 뉴스 브리핑을 받을 수 있는 서비스

---

## 개발 과정

### 1단계: 프로젝트 기획 (Phase 1)

**초기 아이디어**
- 텔레그램 봇으로 Claude API 연동
- 사용자가 키워드 입력하면 뉴스 요약 전송

**요구사항 변경**
- 단순 대화형 봇 → **매일 자동 배치 실행** 뉴스 브리핑 서비스
- 개인용 → **회사 사람들이 사용할 수 있는 다중 사용자 서비스**

**최종 구조 설계**
- Phase 1: 뉴스 수집 + 요약 + 텔레그램 전송 (MVP)
- Phase 2: 스케줄러 + 웹 UI + 다중 사용자
- Phase 3: AWS Lambda 배포

---

### 2단계: GitHub 저장소 설정

**첫 번째 테스트: ai_interface.py**
- OpenAI API 키가 하드코딩되어 있는 파일 발견
- API 키 제거 후 환경 변수로 변경
- Git 초기화 및 첫 커밋

```bash
git init
git add ai_interface.py .gitignore
git commit -m "Add ai_interface.py with secure API key handling"
git remote add origin https://github.com/hwayobi2020/tnews.git
git push -u origin main
```

**교훈**: API 키는 절대 코드에 하드코딩하지 말 것!

---

### 3단계: 텔레그램 봇 생성

**BotFather를 통한 봇 생성**
- 봇 이름: `@ainews_hana_bot`
- 봇 토큰: `8250016808:AAHhsQoEaq_ORUKSFhjJ4NWB049YmbMl-Qw`

---

### 4단계: 뉴스 수집 기능 구현

**뉴스 소스 선택**
- **옵션 1**: 네이버 뉴스 API (신청 필요)
- **옵션 2**: Google News RSS ✅ **(선택)**

**이유**: 즉시 사용 가능, 무료, 한국 뉴스 지원

**구현**
```python
# news_test.py 작성
import feedparser

def get_google_news(keyword, max_results=10):
    url = f"https://news.google.com/rss/search?q={keyword}&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(url)
    # ... 뉴스 파싱
```

**테스트 결과**
- "인공지능" 키워드로 10개 뉴스 수집 성공
- 제목, 출처, 날짜, 링크 정상 추출

---

### 5단계: Claude API 요약 기능 구현

**API 키 준비**
- Anthropic API 키 발급
- $10 크레딧 충전
- curl로 연결 테스트 성공

**구현**
```python
# news_summarizer.py 작성
import anthropic

def summarize_news_with_claude(news_list, keyword):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text
```

**프롬프트 설계**
- 주요 트렌드 요약
- 핵심 뉴스 TOP 5
- 시사점 정리

**출력 형식**
```
📊 **[키워드] 오늘의 뉴스 브리핑**

🔥 **주요 트렌드**
- 전체적인 흐름 요약

📰 **핵심 뉴스 TOP 5**
1. [제목] - 한 줄 요약
...

💡 **시사점**
- 종합 분석
```

**테스트 결과**
- "인공지능" 뉴스 10개 → 완벽한 한글 요약 생성
- 파일 저장: `news_summary.txt`

---

### 6단계: 텔레그램 통합

**Chat ID 확인 스크립트 작성**
```python
# get_chat_id.py
import requests

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
response = requests.get(url)
# Chat ID 추출
```

**문제 발생: 회사 방화벽**
- WebKeeper 10.0이 텔레그램 API 차단
- 차단 분류: "채팅"
- `api.telegram.org` 접근 불가

**해결 방안**
- ✅ 노트북(집)에서 테스트
- ⏳ AWS Lambda 배포 (최종 목표)

**메인 통합 스크립트 작성**
```python
# telegram_news_bot.py
def main(keyword, bot_token, chat_id):
    # 1. 뉴스 수집
    news = get_google_news(keyword, max_results=10)

    # 2. Claude 요약
    summary = summarize_news_with_claude(news, keyword)

    # 3. 텔레그램 전송
    send_telegram_message(bot_token, chat_id, summary)
```

---

### 7단계: 환경 변수 관리

**문제점**
- API 키가 코드에 하드코딩됨
- GitHub에 올리면 보안 위험

**해결**
```python
# 환경 변수로 변경
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
NEWS_KEYWORD = os.getenv("NEWS_KEYWORD", "인공지능")
```

**`.env.example` 생성**
```bash
ANTHROPIC_API_KEY=your-anthropic-api-key-here
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
TELEGRAM_CHAT_ID=your-telegram-chat-id-here
NEWS_KEYWORD=인공지능
```

**`.gitignore` 업데이트**
```
.env
news_summary.txt
telegram_response.txt
```

---

### 8단계: GitHub 배포

**최종 파일 구조**
```
tnews/
├── telegram_news_bot.py       # 메인 통합 스크립트
├── news_summarizer.py         # 뉴스 수집 + 요약 (테스트용)
├── get_chat_id.py            # Chat ID 확인
├── NEWS_BOT_README.md        # 프로젝트 문서
├── .env.example              # 환경 변수 템플릿
├── .gitignore                # Git 제외 파일
└── ai_interface.py           # 참고용 (OpenAI)
```

**커밋 및 푸시**
```bash
git add telegram_news_bot.py news_summarizer.py get_chat_id.py NEWS_BOT_README.md .env.example .gitignore
git commit -m "Add AI News Briefing Bot (Phase 1)"
git push
```

---

## 주요 기술 스택

### Backend
- **Python 3.9+**
- **feedparser**: RSS 파싱
- **anthropic**: Claude AI API
- **requests**: HTTP 통신

### APIs
- **Google News RSS**: 뉴스 수집
- **Claude API (Sonnet 4)**: 뉴스 요약
- **Telegram Bot API**: 메시지 전송

### Infrastructure
- **로컬 개발**: Windows 회사 PC
- **배포 예정**: AWS Lambda

---

## 개발 중 발견한 이슈

### 1. SSL 인증서 문제
**문제**: 회사 프록시로 인한 SSL 검증 실패

**해결**:
```python
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# pip 설치 시
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org
```

### 2. Windows 콘솔 인코딩
**문제**: 이모지 출력 시 `UnicodeEncodeError`

**해결**: 이모지 제거, 파일 저장 시 `encoding="utf-8"` 사용

### 3. 회사 방화벽
**문제**: 텔레그램 API 차단

**해결**: 노트북(집)에서 테스트, AWS Lambda 배포 계획

---

## 성과

✅ **Phase 1 완료**
- 뉴스 수집: Google News RSS 10개
- 요약 기능: Claude AI로 한글 요약
- 텔레그램 전송: 봇 통합 완료
- GitHub 배포: 안전한 API 키 관리

📊 **테스트 결과**
- 뉴스 수집: 1초 이내
- Claude 요약: 5-10초
- 전체 프로세스: 15초 이내

---

## 다음 단계 (Phase 2)

### 1. 스케줄러 구현
- `APScheduler` 또는 `schedule` 라이브러리
- 매일 오전 9시 자동 실행

### 2. 웹 UI 개발
- Flask/FastAPI
- 사용자 등록 페이지
- 키워드 설정 UI

### 3. 데이터베이스
- SQLite 또는 PostgreSQL
- 사용자 정보 저장
- 키워드 매핑

### 4. AWS Lambda 배포
- 서버리스 아키텍처
- EventBridge로 스케줄링
- 비용 최소화

### 5. 다중 사용자 지원
- 여러 사람이 각자 키워드 설정
- 개별 텔레그램 전송

---

## 배운 점

1. **API 키 관리의 중요성**
   - 절대 코드에 하드코딩하지 말 것
   - 환경 변수 또는 AWS Secrets Manager 사용

2. **MVP 우선 개발**
   - 완벽한 시스템보다 작동하는 프로토타입 먼저
   - Phase별로 단계적 개발

3. **네트워크 환경 고려**
   - 회사 방화벽, 프록시 이슈 사전 파악
   - 대안 마련 (AWS Lambda)

4. **문서화의 중요성**
   - README 작성으로 나중에 다시 보기 쉬움
   - `.env.example`로 설정 가이드 제공

---

## 참고 자료

- [Claude API Documentation](https://docs.anthropic.com/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Google News RSS](https://news.google.com/rss)
- [feedparser Documentation](https://feedparser.readthedocs.io/)

---

**프로젝트 저장소**: https://github.com/hwayobi2020/tnews
