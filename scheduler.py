import os
import ssl
import requests
import feedparser
import anthropic
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import database as db

# SSL 우회 (필요시)
ssl._create_default_https_context = ssl._create_unverified_context

# 환경 변수 (환경변수가 빈 문자열이면 기본값 사용)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") or "sk-ant-api03-W6eT4wKVjr-VK0yLq17I4cZPTwb4LfKN0u5i0wkrTk0d0fAn1mS5n8-sVQdJZkKBKmnAKtX2v8H3vKcWLgCyqQ-jlN6SwAA"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8250016808:AAHhsQoEaq_ORUKSFhjJ4NWB049YmbMl-Qw")


def get_google_news(keyword, max_results=10):
    """Google News RSS에서 키워드로 뉴스 검색"""
    url = f"https://news.google.com/rss/search?q={keyword}&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(url)

    news_list = []
    for entry in feed.entries[:max_results]:
        news_item = {
            'title': entry.title,
            'link': entry.link,
            'published': entry.get('published', 'N/A'),
            'source': entry.source.title if hasattr(entry, 'source') else 'N/A'
        }
        news_list.append(news_item)

    return news_list


def summarize_news_with_claude(news_list, keyword):
    """Claude API로 뉴스 리스트를 요약"""
    if not ANTHROPIC_API_KEY:
        print("[ERROR] ANTHROPIC_API_KEY가 설정되지 않았습니다.")
        return None

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # 뉴스 리스트를 텍스트로 변환
    news_text = f"키워드: {keyword}\n\n"
    for i, news in enumerate(news_list, 1):
        news_text += f"{i}. {news['title']}\n"
        news_text += f"   출처: {news['source']}\n"
        news_text += f"   날짜: {news['published']}\n\n"

    prompt = f"""다음은 '{keyword}' 키워드로 검색한 오늘의 뉴스 목록입니다.

{news_text}

위 뉴스들을 분석하고 다음 형식으로 요약해주세요:

**[{keyword}] 오늘의 뉴스 브리핑**

**주요 트렌드**
- 전체적인 흐름과 주요 이슈 2-3줄 요약

**핵심 뉴스 TOP 5**
1. [제목] - 한 줄 요약
2. [제목] - 한 줄 요약
3. [제목] - 한 줄 요약
4. [제목] - 한 줄 요약
5. [제목] - 한 줄 요약

**시사점**
- 이 뉴스들이 의미하는 바를 1-2줄로 정리

간결하고 명확하게 작성해주세요."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        print(f"[ERROR] Claude API 오류: {e}")
        return None


def send_telegram_message(chat_id, message):
    """텔레그램으로 메시지 전송"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=data, verify=False)
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] 텔레그램 전송 오류: {e}")
        return False


def get_news_summary(keyword):
    """키워드로 뉴스 요약 가져오기 (캐시 우선)"""
    # 1. 캐시 확인
    cached = db.get_cached_news(keyword)
    if cached:
        print(f"  [CACHE] 캐시된 요약 사용: {keyword}")
        return cached['summary']

    # 2. 캐시 없으면 새로 생성
    news = get_google_news(keyword, max_results=10)
    if not news:
        print(f"  [SKIP] 뉴스 없음")
        return None

    summary = summarize_news_with_claude(news, keyword)
    if not summary:
        print(f"  [SKIP] 요약 실패")
        return None

    # 3. 캐시에 저장
    db.save_news_cache(keyword, summary)

    return summary


def send_news_to_all_users():
    """모든 활성 사용자에게 뉴스 전송"""
    print("=" * 60)
    print("[SCHEDULER] 뉴스 브리핑 시작!")
    print("=" * 60)

    users = db.get_all_active_users()
    print(f"[INFO] 총 {len(users)}명에게 뉴스 전송 예정")

    for user in users:
        email = user['email']
        keyword = user['keyword']
        chat_id = user['chat_id']

        print(f"\n[USER] {email} - 키워드: {keyword}")

        # 1. 뉴스 요약 가져오기 (캐시 우선)
        summary = get_news_summary(keyword)
        if not summary:
            continue

        # 2. 텔레그램 전송
        success = send_telegram_message(chat_id, summary)
        if success:
            print(f"  [OK] 전송 완료!")
        else:
            print(f"  [FAIL] 전송 실패")

    print("\n" + "=" * 60)
    print("[SCHEDULER] 뉴스 브리핑 완료!")
    print("=" * 60)


def run_scheduler():
    """스케줄러 실행 - 매일 오전 9시"""
    print("[SCHEDULER] 스케줄러 시작...")
    print("[SCHEDULER] 매일 오전 9시에 뉴스를 전송합니다.")

    scheduler = BlockingScheduler()

    # 매일 오전 9시
    scheduler.add_job(
        send_news_to_all_users,
        CronTrigger(hour=9, minute=0),
        id='daily_news'
    )

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n[SCHEDULER] 종료됨")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "now":
        # python scheduler.py now -> 즉시 실행
        send_news_to_all_users()
    else:
        # python scheduler.py -> 스케줄러 실행
        run_scheduler()
