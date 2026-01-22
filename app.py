from flask import Flask, render_template, request, redirect, url_for, flash
from urllib.parse import quote
from dotenv import load_dotenv
load_dotenv()

import database as db
from scheduler import get_news_summary

app = Flask(__name__)
app.secret_key = 'tnews-secret-key-change-this-in-production'

BOT_USERNAME = "hana_sec_ai_bot"


@app.route('/')
def index():
    """메인 페이지 - 키워드 입력"""
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    """키워드로 뉴스 검색"""
    keyword = request.form.get('keyword', '').strip()

    if not keyword:
        flash('키워드를 입력해주세요.', 'error')
        return redirect(url_for('index'))

    # 뉴스 요약 가져오기
    news_summary = get_news_summary(keyword)

    # 텔레그램 딥링크 (키워드로 바로 구독)
    telegram_link = f"https://t.me/{BOT_USERNAME}?start={quote(keyword)}"

    # 같은 키워드 구독자 수
    subscriber_count = db.get_users_by_keyword(keyword)

    return render_template('result.html',
                          keyword=keyword,
                          news_summary=news_summary,
                          telegram_link=telegram_link,
                          subscriber_count=subscriber_count)


@app.route('/news/<keyword>')
def news(keyword):
    """키워드 뉴스 페이지 (공유용)"""
    news_summary = get_news_summary(keyword)
    telegram_link = f"https://t.me/{BOT_USERNAME}?start={quote(keyword)}"
    subscriber_count = db.get_users_by_keyword(keyword)

    return render_template('result.html',
                          keyword=keyword,
                          news_summary=news_summary,
                          telegram_link=telegram_link,
                          subscriber_count=subscriber_count)


# DB 초기화
db.init_db()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
