"""
Slack Bot 메인 엔트리포인트
- Socket Mode로 Slack과 연결
- 웹훅 메시지 포함 모든 메시지 이벤트 수신
"""
import os
import socket
import time

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from app.config import SLACK_BOT_TOKEN, SLACK_APP_TOKEN, validate_tokens
from app.utils import set_bot_identity
from app.handlers import register_handlers


def init_bot_identity(app):
    """봇의 user_id와 bot_id를 확인하여 저장 (무한루프 방지용)"""
    try:
        resp = app.client.auth_test()
        user_id = resp.get("user_id")
        bot_id = resp.get("bot_id")
        set_bot_identity(user_id, bot_id)
        print(f"[BOOT] BOT_USER_ID={user_id}, BOT_ID={bot_id}")
    except Exception as e:
        set_bot_identity(None, None)
        print(f"[BOOT] auth_test failed: {repr(e)}")


def main():
    print(
        f"[BOOT] pid={os.getpid()} "
        f"host={socket.gethostname()} "
        f"time={time.time()}"
    )
    
    # 1. 환경변수 검증
    validate_tokens()
    
    # 2. Slack App 초기화
    app = App(token=SLACK_BOT_TOKEN)
    
    # 3. 봇 자기 식별 정보 로드
    init_bot_identity(app)
    
    # 4. 이벤트 핸들러 등록
    register_handlers(app)
    
    # 5. Socket Mode 시작
    print("[BOOT] Starting SocketModeHandler...")
    SocketModeHandler(app, SLACK_APP_TOKEN).start()


if __name__ == "__main__":
    main()
