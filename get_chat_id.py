import requests
import ssl
import urllib3

# SSL 인증 우회
ssl._create_default_https_context = ssl._create_unverified_context

# SSL 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 환경 변수에서 봇 토큰 가져오기
import os
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")

# getUpdates API 호출
url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

try:
    response = requests.get(url, verify=False)

    # 응답을 파일로 저장
    with open("telegram_response.txt", "w", encoding="utf-8") as f:
        f.write(f"Status: {response.status_code}\n")
        f.write(f"Response: {response.text}\n")

    if response.status_code == 200:
        data = response.json()

        if data['result']:
            print("=" * 60)
            print("텔레그램 메시지 목록:")
            print("=" * 60)

            for update in data['result']:
                if 'message' in update:
                    chat_id = update['message']['chat']['id']
                    username = update['message']['chat'].get('username', 'N/A')
                    first_name = update['message']['chat'].get('first_name', 'N/A')
                    text = update['message'].get('text', 'N/A')

                    print(f"Chat ID: {chat_id}")
                    print(f"사용자: {first_name} (@{username})")
                    print(f"메시지: {text}")
                    print("-" * 60)

            print("\n위의 Chat ID를 telegram_news_bot.py 파일의 TELEGRAM_CHAT_ID에 입력하세요!")
        else:
            print("메시지가 없습니다.")
            print("텔레그램에서 @ainews_hana_bot 봇에게 /start 메시지를 보내고 다시 실행하세요!")
    else:
        print(f"오류: {response.text}")

except Exception as e:
    print(f"오류 발생: {e}")
