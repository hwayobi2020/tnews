from flask import Flask, render_template, request, redirect, url_for, flash, session
import database as db

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

    if request.method == 'POST':
        keyword = request.form.get('keyword')
        if keyword:
            db.update_keyword(user['email'], keyword)
            flash('키워드가 저장되었습니다!', 'success')
            user = db.get_user_by_email(session['user_email'])  # 갱신

    # 텔레그램 딥링크 생성
    telegram_link = f"https://t.me/{BOT_USERNAME}?start={user['code']}"

    user_count = db.get_user_count()

    return render_template('settings.html', user=user, telegram_link=telegram_link, user_count=user_count)


# DB 초기화
db.init_db()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
