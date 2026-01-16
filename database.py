import sqlite3
import os
import secrets
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

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            chat_id TEXT,
            keyword TEXT DEFAULT '인공지능',
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 뉴스 캐시 테이블 (같은 키워드면 캐시된 요약 사용)
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


def generate_code():
    """고유 코드 생성 (8자리)"""
    return secrets.token_urlsafe(6)  # 약 8자리


def create_user(email, password):
    """새 사용자 생성"""
    conn = get_connection()
    cursor = conn.cursor()

    code = generate_code()

    try:
        cursor.execute('''
            INSERT INTO users (email, password, code)
            VALUES (?, ?, ?)
        ''', (email, password, code))
        conn.commit()
        user_id = cursor.lastrowid
        print(f"[DB] 사용자 생성: {email}")
        return {'id': user_id, 'email': email, 'code': code}
    except sqlite3.IntegrityError:
        print(f"[DB] 이미 존재하는 이메일: {email}")
        return None
    finally:
        conn.close()


def get_user_by_email(email):
    """이메일로 사용자 조회"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()

    return dict(user) if user else None


def get_user_by_code(code):
    """코드로 사용자 조회"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE code = ?', (code,))
    user = cursor.fetchone()
    conn.close()

    return dict(user) if user else None


def update_chat_id(code, chat_id):
    """텔레그램 chat_id 연결"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE users
        SET chat_id = ?, updated_at = ?
        WHERE code = ?
    ''', (chat_id, datetime.now().isoformat(), code))

    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()

    if updated:
        print(f"[DB] chat_id 연결: code={code}, chat_id={chat_id}")
    return updated


def update_keyword(email, keyword):
    """키워드 업데이트"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE users
        SET keyword = ?, updated_at = ?
        WHERE email = ?
    ''', (keyword, datetime.now().isoformat(), email))

    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()

    if updated:
        print(f"[DB] 키워드 업데이트: {email} -> {keyword}")
    return updated


def get_all_active_users():
    """활성 사용자 전체 조회 (chat_id 있는)"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM users
        WHERE is_active = 1 AND chat_id IS NOT NULL
    ''')
    users = cursor.fetchall()
    conn.close()

    return [dict(user) for user in users]


def get_user_count():
    """전체 사용자 수"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) as count FROM users')
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


# 테스트
if __name__ == "__main__":
    init_db()
    print(f"[DB] 경로: {DB_PATH}")
