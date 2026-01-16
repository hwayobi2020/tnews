# AI News Briefing Service (tnews)

웹에서 키워드를 검색하고, 텔레그램으로 매일 AI 요약 뉴스를 받는 서비스입니다.

## 핵심 컨셉

**"웹에서 검색 → 텔레그램으로 구독"**

- 사용자가 웹에서 키워드 검색
- 뉴스 미리보기 확인
- "텔레그램으로 이동" 클릭 → 자동 구독
- **텔레그램 첫 진입 시 뉴스 먼저 표시** → 구독 확인 메시지
- 매일 아침 해당 키워드 뉴스 수신

사용자는 텔레그램에서 명령어를 입력하지 않습니다. 웹에서 모든 것을 컨트롤합니다.

## 시스템 구조

```
[웹 브라우저] → [Flask 웹서버] → 뉴스 미리보기
                    ↓
            텔레그램 딥링크
                    ↓
[텔레그램 봇] → 자동 구독 + 뉴스 전송
                    ↓
              [SQLite DB]
```

- **웹**: 키워드 검색, 뉴스 미리보기 (DB 저장 안함)
- **텔레그램**: 구독 저장, 뉴스 전송 (DB 저장)
- **1인 1키워드**: 각 사용자는 하나의 키워드만 구독

## 파일 구조

```
tnews/
├── app.py              # Flask 웹서버
├── bot.py              # 텔레그램 봇
├── scheduler.py        # 뉴스 수집 + Claude AI 요약
├── database.py         # SQLite DB 관리
├── templates/
│   ├── index.html      # 키워드 검색 페이지
│   └── result.html     # 뉴스 결과 + 텔레그램 링크
├── news_data.db        # SQLite 데이터베이스
└── .env                # API 키 (ANTHROPIC_API_KEY, TELEGRAM_BOT_TOKEN)
```

## 실행 방법

```bash
# 1. 웹서버 실행
python app.py

# 2. 텔레그램 봇 실행 (별도 터미널)
python bot.py
```

- 웹: http://127.0.0.1:5000
- 텔레그램 봇: @hana_sec_ai_bot

## 사용 흐름

1. 웹에서 "비트코인" 검색
2. AI 요약 뉴스 미리보기
3. "텔레그램으로 이동" 클릭
4. 텔레그램 열리며 자동 구독
5. 매일 아침 "비트코인" 뉴스 수신

## 환경 변수 (.env)

```
ANTHROPIC_API_KEY=your-claude-api-key
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
```

## 데이터베이스

**subscribers 테이블**
- `chat_id`: 텔레그램 채팅 ID
- `keyword`: 구독 키워드
- `created_at`: 구독 시간

**news_cache 테이블**
- 뉴스 캐시 (중복 API 호출 방지)

---

**Made by hwayobi2020**
