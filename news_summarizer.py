import os
import anthropic
import feedparser
import ssl
from datetime import datetime

# SSL 인증 우회 (회사 환경용)
ssl._create_default_https_context = ssl._create_unverified_context

# Claude 클라이언트 (나중에 초기화)
claude_client = None


def get_google_news(keyword, max_results=10):
    """Google News RSS에서 키워드로 뉴스 검색"""
    url = f"https://news.google.com/rss/search?q={keyword}&hl=ko&gl=KR&ceid=KR:ko"

    print(f"[NEWS] 뉴스 검색 중: {keyword}")

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

    print(f"[OK] {len(news_list)}개의 뉴스를 찾았습니다.\n")
    return news_list


def summarize_news_with_claude(news_list, keyword):
    """Claude API로 뉴스 리스트를 요약"""
    print("[CLAUDE] 뉴스를 요약하는 중...")

    # 뉴스 리스트를 텍스트로 변환
    news_text = f"키워드: {keyword}\n\n"
    for i, news in enumerate(news_list, 1):
        news_text += f"{i}. {news['title']}\n"
        news_text += f"   출처: {news['source']}\n"
        news_text += f"   날짜: {news['published']}\n"
        news_text += f"   링크: {news['link']}\n\n"

    # Claude에게 요약 요청
    prompt = f"""다음은 '{keyword}' 키워드로 검색한 오늘의 뉴스 목록입니다.

{news_text}

위 뉴스들을 분석하고 다음 형식으로 요약해주세요:

📊 **[{keyword}] 오늘의 뉴스 브리핑**

🔥 **주요 트렌드**
- 전체적인 흐름과 주요 이슈 2-3줄 요약

📰 **핵심 뉴스 TOP 5**
1. [제목] - 한 줄 요약
2. [제목] - 한 줄 요약
3. [제목] - 한 줄 요약
4. [제목] - 한 줄 요약
5. [제목] - 한 줄 요약

💡 **시사점**
- 이 뉴스들이 의미하는 바를 1-2줄로 정리

간결하고 명확하게 작성해주세요."""

    try:
        message = claude_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        summary = message.content[0].text
        print("[OK] 요약 완료!\n")
        return summary

    except Exception as e:
        print(f"[ERROR] 오류 발생: {e}")
        return None


# 테스트
if __name__ == "__main__":
    # 환경 변수에서 API 키 가져오기
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

    claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # 뉴스 수집
    keyword = "인공지능"
    news = get_google_news(keyword, max_results=10)

    # Claude로 요약
    summary = summarize_news_with_claude(news, keyword)

    if summary:
        # 파일로 저장
        with open("news_summary.txt", "w", encoding="utf-8") as f:
            f.write(summary)
        print("=" * 60)
        print("[SUCCESS] 요약이 완료되었습니다!")
        print("파일에 저장됨: news_summary.txt")
        print("=" * 60)
