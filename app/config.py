"""
환경 변수 및 공통 설정
"""
import os

# --------------------------------------------------------
# Slack 토큰
# --------------------------------------------------------
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")


def validate_tokens():
    """필수 토큰 환경 변수 검증"""
    if not SLACK_BOT_TOKEN or not SLACK_APP_TOKEN:
        raise RuntimeError(
            "Missing SLACK_BOT_TOKEN or SLACK_APP_TOKEN in environment variables."
        )


# --------------------------------------------------------
# 카운팅 / 레이트리밋 설정
# --------------------------------------------------------
WINDOW_SECONDS = 240  # threshold 카운팅 윈도우 (4분)

# 전역 발언 제한: 5분 동안 2회 (전 채널 통합)
GLOBAL_RATE_WINDOW_SECONDS = 300
GLOBAL_RATE_LIMIT_COUNT = 2

# --------------------------------------------------------
# 웹훅 메시지 허용 subtypes (핵심 차이점!)
# --------------------------------------------------------
# Legacy Incoming Webhook 및 다른 봇 메시지를 처리하기 위함
ALLOWED_SUBTYPES = {
    None,              # 일반 사용자 메시지
    "bot_message",     # Legacy Incoming Webhook
    "file_share",      # 파일 첨부 메시지
    "thread_broadcast",# 스레드 브로드캐스트
}

# 무시할 subtypes (메시지 본문이 아닌 이벤트)
IGNORED_SUBTYPES = {
    "message_changed",
    "message_deleted",
    "channel_join",
    "channel_leave",
    "channel_topic",
    "channel_purpose",
    "channel_name",
    "pinned_item",
    "unpinned_item",
}

# --------------------------------------------------------
# 디버그 모드
# --------------------------------------------------------
DEBUG_MODE = os.environ.get("DEBUG_MODE", "false").lower() == "true"
