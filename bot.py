import os
import subprocess
import time
import sys
from dotenv import load_dotenv
load_dotenv()

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import database as db
from scheduler import get_news_summary

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7949423850:AAEY4izjt652nGs53oQf6urJxw93V28I72U")


def kill_other_bot_instances():
    """현재 프로세스를 제외한 다른 bot.py 프로세스 종료"""
    current_pid = os.getpid()
    print(f"[BOT] 현재 PID: {current_pid}", flush=True)
    print("[BOT] 기존 봇 인스턴스 확인 중...", flush=True)

    try:
        # Windows에서 python 프로세스 목록 가져오기
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq python*', '/FO', 'CSV'],
            capture_output=True, text=True, encoding='cp949'
        )

        lines = result.stdout.strip().split('\n')
        killed = False

        for line in lines[1:]:  # 헤더 제외
            if 'python' in line.lower():
                parts = line.replace('"', '').split(',')
                if len(parts) >= 2:
                    try:
                        pid = int(parts[1])
                        if pid != current_pid:
                            subprocess.run(['taskkill', '/F', '/PID', str(pid)],
                                         capture_output=True)
                            print(f"[BOT] PID {pid} 종료됨", flush=True)
                            killed = True
                    except (ValueError, IndexError):
                        pass

        if killed:
            print("[BOT] 기존 인스턴스 종료 완료, 3초 대기...", flush=True)
            time.sleep(3)
        else:
            print("[BOT] 기존 인스턴스 없음", flush=True)

    except Exception as e:
        print(f"[BOT] 인스턴스 정리 중 오류: {e}", flush=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    웹에서 /start 키워드 링크로 들어오면
    해당 키워드 뉴스를 보여주고 자동 구독
    """
    chat_id = str(update.effective_chat.id)
    user_name = update.effective_user.first_name or "사용자"

    if context.args:
        # 웹에서 키워드 링크로 들어온 경우: /start 비트코인
        keyword = ' '.join(context.args)

        # 구독 등록
        db.subscribe_keyword(chat_id, keyword)

        # 뉴스 보여주기
        news_summary = get_news_summary(keyword)
        if news_summary:
            await update.message.reply_text(f"[{keyword}] 오늘의 뉴스\n\n{news_summary}")
            await update.message.reply_text(f"매일 아침 '{keyword}' 뉴스를 보내드릴게요!")
        else:
            await update.message.reply_text("뉴스를 가져오는 중 문제가 발생했습니다.")
    else:
        # 그냥 /start만 누른 경우
        subscriber = db.get_subscriber(chat_id)
        if subscriber:
            # 이미 구독 중이면 뉴스 보여주기
            keyword = subscriber['keyword']
            news_summary = get_news_summary(keyword)
            if news_summary:
                await update.message.reply_text(f"[{keyword}] 오늘의 뉴스\n\n{news_summary}")
            else:
                await update.message.reply_text("뉴스를 가져오는 중 문제가 발생했습니다.")
        else:
            # 신규 사용자
            await update.message.reply_text(
                f"안녕하세요, {user_name}님!\n"
                f"AI 뉴스 브리핑 봇입니다.\n"
                f"웹사이트에서 키워드를 검색하고 구독해주세요!"
            )


def main():
    """봇 실행"""
    # 먼저 기존 인스턴스 종료
    kill_other_bot_instances()

    print("[BOT] 텔레그램 봇 시작...", flush=True)

    db.init_db()

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    print("[BOT] 봇이 실행 중입니다. Ctrl+C로 종료하세요.", flush=True)
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
