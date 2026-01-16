import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import database as db

# 환경 변수
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8250016808:AAHhsQoEaq_ORUKSFhjJ4NWB049YmbMl-Qw")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start 명령어 처리
    딥링크: /start ABC123 형태로 들어오면 코드 연결
    """
    chat_id = str(update.effective_chat.id)
    user_name = update.effective_user.first_name or "사용자"

    # 딥링크 코드 확인
    if context.args:
        code = context.args[0]
        user = db.get_user_by_code(code)

        if user:
            # chat_id 연결
            db.update_chat_id(code, chat_id)

            await update.message.reply_text(
                f"안녕하세요, {user_name}님!\n\n"
                f"텔레그램 연결이 완료되었습니다.\n\n"
                f"설정된 키워드: {user['keyword']}\n\n"
                f"매일 아침 뉴스 브리핑을 받게 됩니다!"
            )
        else:
            await update.message.reply_text(
                f"유효하지 않은 코드입니다.\n"
                f"웹사이트에서 다시 링크를 받아주세요."
            )
    else:
        # 그냥 /start 만 친 경우
        await update.message.reply_text(
            f"안녕하세요, {user_name}님!\n\n"
            f"AI 뉴스 브리핑 봇입니다.\n\n"
            f"웹사이트에서 가입 후 텔레그램 연결 링크를 클릭해주세요.\n\n"
            f"명령어:\n"
            f"/status - 내 설정 확인\n"
            f"/help - 도움말"
        )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """현재 설정 확인"""
    chat_id = str(update.effective_chat.id)

    # chat_id로 사용자 찾기
    users = db.get_all_active_users()
    user = next((u for u in users if u['chat_id'] == chat_id), None)

    if user:
        await update.message.reply_text(
            f"현재 설정\n\n"
            f"이메일: {user['email']}\n"
            f"키워드: {user['keyword']}\n"
            f"상태: 활성화됨\n\n"
            f"매일 아침 뉴스 브리핑을 받게 됩니다!"
        )
    else:
        await update.message.reply_text(
            f"연결된 계정이 없습니다.\n\n"
            f"웹사이트에서 가입 후 텔레그램 연결 링크를 클릭해주세요."
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """도움말"""
    await update.message.reply_text(
        "AI 뉴스 브리핑 봇 도움말\n\n"
        "이 봇은 매일 아침 설정한 키워드로 뉴스를 검색하고,\n"
        "AI가 요약해서 보내드립니다.\n\n"
        "명령어:\n"
        "/start - 시작\n"
        "/status - 내 설정 확인\n"
        "/help - 이 도움말\n\n"
        "키워드 변경은 웹사이트에서 가능합니다."
    )


def main():
    """봇 실행"""
    import sys
    print("[BOT] 텔레그램 봇 시작...", flush=True)

    # DB 초기화
    db.init_db()

    # 봇 애플리케이션 생성
    app = Application.builder().token(BOT_TOKEN).build()

    # 핸들러 등록
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("help", help_command))

    # 봇 실행
    print("[BOT] 봇이 실행 중입니다. Ctrl+C로 종료하세요.", flush=True)
    sys.stdout.flush()
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
