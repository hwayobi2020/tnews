import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'tnews.db')


def get_connection():
    """DB 연결"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """DB 초기화 - 테이블 생성"""
    conn = get_connection()
    cursor = conn.cursor()

    # 구독자 테이블 (키워드 기반)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT UNIQUE NOT NULL,
            keyword TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 뉴스 캐시 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL,
            summary TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("[DB] 테이블 생성 완료!")


def subscribe_keyword(chat_id, keyword):
    """키워드 구독 (신규 or 업데이트)"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM subscribers WHERE chat_id = ?', (chat_id,))
    existing = cursor.fetchone()

    if existing:
        cursor.execute('''
            UPDATE subscribers
            SET keyword = ?, is_active = 1, updated_at = ?
            WHERE chat_id = ?
        ''', (keyword, datetime.now().isoformat(), chat_id))
        print(f"[DB] 구독 업데이트: chat_id={chat_id}, keyword={keyword}")
    else:
        cursor.execute('''
            INSERT INTO subscribers (chat_id, keyword, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        ''', (chat_id, keyword, datetime.now().isoformat(), datetime.now().isoformat()))
        print(f"[DB] 신규 구독: chat_id={chat_id}, keyword={keyword}")

    conn.commit()
    conn.close()
    return True


def get_subscriber(chat_id):
    """구독자 조회"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM subscribers WHERE chat_id = ? AND is_active = 1', (chat_id,))
    subscriber = cursor.fetchone()
    conn.close()

    return dict(subscriber) if subscriber else None


def unsubscribe(chat_id):
    """구독 해제"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE subscribers SET is_active = 0, updated_at = ?
        WHERE chat_id = ?
    ''', (datetime.now().isoformat(), chat_id))

    conn.commit()
    conn.close()
    print(f"[DB] 구독 해제: chat_id={chat_id}")


def get_all_active_subscribers():
    """모든 활성 구독자 조회"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM subscribers WHERE is_active = 1')
    subscribers = cursor.fetchall()
    conn.close()

    return [dict(s) for s in subscribers]


def get_users_by_keyword(keyword):
    """키워드별 구독자 수"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) as count FROM subscribers WHERE keyword = ? AND is_active = 1', (keyword,))
    result = cursor.fetchone()
    conn.close()

    return result['count']


def get_cached_news(keyword):
    """오늘 날짜의 캐시된 뉴스 요약 조회"""
    conn = get_connection()
    cursor = conn.cursor()

    today = datetime.now().strftime('%Y-%m-%d')

    cursor.execute('''
        SELECT * FROM news_cache
        WHERE keyword = ? AND DATE(created_at) = ?
        ORDER BY created_at DESC LIMIT 1
    ''', (keyword, today))

    cache = cursor.fetchone()
    conn.close()

    return dict(cache) if cache else None


def save_news_cache(keyword, summary):
    """뉴스 요약 캐시 저장"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO news_cache (keyword, summary, created_at)
        VALUES (?, ?, ?)
    ''', (keyword, summary, datetime.now().isoformat()))

    conn.commit()
    conn.close()
    print(f"[DB] 뉴스 캐시 저장: {keyword}")


if __name__ == "__main__":
    init_db()
    print(f"[DB] 경로: {DB_PATH}")
