from flask import Flask, render_template, request, redirect, url_for, flash, session
import database as db
from scheduler import get_news_summary

app = Flask(__name__)
app.secret_key = 'tnews-secret-key-change-this-in-production'

BOT_USERNAME = "ainews_hana_bot"


@app.route('/')
def index():
    """메인 페이지 - 바로 설정으로"""
    # 테스트용 사용자 자동 생성
    test_email = "test@test.com"
    user = db.get_user_by_email(test_email)

    if not user:
        user = db.create_user(test_email, "test")

    session['user_email'] = test_email
    return redirect(url_for('settings'))


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """키워드 설정 페이지"""
    if 'user_email' not in session:
        return redirect(url_for('index'))

    user = db.get_user_by_email(session['user_email'])
    news_summary = None

    if request.method == 'POST':
        keyword = request.form.get('keyword')
        if keyword:
            db.update_keyword(user['email'], keyword)
            flash('키워드가 저장되었습니다!', 'success')
            user = db.get_user_by_email(session['user_email'])  # 갱신
            # 키워드 변경 시 바로 뉴스 요약 보여주기
            news_summary = get_news_summary(keyword)

    # GET 요청이거나 POST 후에도 뉴스 요약 표시
    if not news_summary and user['keyword']:
        news_summary = get_news_summary(user['keyword'])

    # 텔레그램 딥링크 생성
    telegram_link = f"https://t.me/{BOT_USERNAME}?start={user['code']}"

    # 공유 링크 생성
    share_link_data = db.get_or_create_share_link(user['keyword'], user['email'])
    share_link = f"{request.host_url}join/{share_link_data['share_code']}"

    # 같은 키워드 사용자 수
    keyword_users = db.get_users_by_keyword(user['keyword'])
    user_count = db.get_user_count()

    return render_template('settings.html', user=user, telegram_link=telegram_link,
                          user_count=user_count, news_summary=news_summary,
                          share_link=share_link, keyword_users=keyword_users)


@app.route('/join/<share_code>')
def join(share_code):
    """공유 링크로 접속 - 같은 키워드로 자동 설정"""
    share = db.get_share_link_by_code(share_code)

    if not share:
        flash('유효하지 않은 공유 링크입니다.', 'error')
        return redirect(url_for('index'))

    # 테스트용 사용자 생성 (새 사용자)
    import secrets
    test_email = f"user_{secrets.token_hex(4)}@test.com"
    user = db.create_user(test_email, "test")

    if user:
        # 공유된 키워드로 설정
        db.update_keyword(test_email, share['keyword'])
        session['user_email'] = test_email
        flash(f"'{share['keyword']}' 키워드 그룹에 참여했습니다!", 'success')

    return redirect(url_for('settings'))


# DB 초기화
db.init_db()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
