"""
공통 유틸리티 함수
- 텍스트 추출 (웹훅의 attachments 포함)
- 키워드 카운팅
- 시간 윈도우 관리
"""
import threading
from collections import defaultdict, deque
from app.config import (
    WINDOW_SECONDS,
    GLOBAL_RATE_WINDOW_SECONDS,
    GLOBAL_RATE_LIMIT_COUNT,
)


# --------------------------------------------------------
# 상태 관리 (전역)
# --------------------------------------------------------
message_window = defaultdict(deque)
global_alert_sent_times = deque()
state_lock = threading.Lock()

# Mute 상태
_state = {
    "is_muted": False,
    "bot_user_id": None,
    "bot_id": None,
}


# --------------------------------------------------------
# 상태 접근자
# --------------------------------------------------------
def get_is_muted() -> bool:
    return _state["is_muted"]


def set_is_muted(muted: bool):
    _state["is_muted"] = muted


def get_bot_user_id():
    return _state["bot_user_id"]


def get_bot_id():
    return _state["bot_id"]


def set_bot_identity(user_id, bot_id):
    _state["bot_user_id"] = user_id
    _state["bot_id"] = bot_id


def clear_counters():
    """Mute/Unmute 시 카운터 초기화"""
    message_window.clear()
    global_alert_sent_times.clear()


# --------------------------------------------------------
# 메시지 텍스트 추출 (핵심: 웹훅 attachments 지원!)
# --------------------------------------------------------
def extract_message_text(event: dict) -> str:
    """
    Slack 이벤트에서 모든 텍스트를 추출합니다.
    웹훅 메시지(attachments, blocks)도 처리합니다.
    
    추출 순서:
    1. event["text"] (기본 메시지)
    2. event["attachments"][*]["text"] / ["fallback"] / ["pretext"] / ["title"]
    3. event["attachments"][*]["fields"][*]["title"/"value"]
    4. event["blocks"][*]["text"]["text"] (Block Kit)
    """
    parts = []
    
    # 1. 기본 text
    if event.get("text"):
        parts.append(event["text"])
    
    # 2. attachments (Legacy Webhook이 주로 사용)
    for att in event.get("attachments", []) or []:
        for key in ("pretext", "title", "text", "fallback"):
            if att.get(key):
                parts.append(att[key])
        
        # attachment fields
        for field in att.get("fields", []) or []:
            if field.get("title"):
                parts.append(field["title"])
            if field.get("value"):
                parts.append(field["value"])
    
    # 3. blocks (Modern Block Kit)
    for block in event.get("blocks", []) or []:
        # section block
        text_obj = block.get("text", {})
        if isinstance(text_obj, dict) and text_obj.get("text"):
            parts.append(text_obj["text"])
        
        # context block elements
        for element in block.get("elements", []) or []:
            if isinstance(element, dict) and element.get("text"):
                parts.append(element["text"])
        
        # fields in section
        for field in block.get("fields", []) or []:
            if isinstance(field, dict) and field.get("text"):
                parts.append(field["text"])
    
    return "\n".join(parts)


# --------------------------------------------------------
# 키워드 카운팅
# --------------------------------------------------------
def keyword_hits_in_text(keyword: str, text: str) -> int:
    """
    한 메시지에서 키워드가 몇 번 나오는지 카운트 (대소문자 무시)
    """
    if not keyword or not text:
        return 0
    return text.lower().count(keyword.lower())


# --------------------------------------------------------
# 시간 윈도우 관리
# --------------------------------------------------------
def prune_old_events(key, now_ts: float):
    """카운팅 윈도우 밖의 오래된 이벤트 제거"""
    dq = message_window[key]
    while dq and now_ts - dq[0] > WINDOW_SECONDS:
        dq.popleft()


def prune_global_alerts(now_ts: float):
    """레이트리밋 윈도우 밖의 오래된 알림 기록 제거"""
    while global_alert_sent_times and (
        now_ts - global_alert_sent_times[0] > GLOBAL_RATE_WINDOW_SECONDS
    ):
        global_alert_sent_times.popleft()


def global_can_speak_locked(now_ts: float) -> bool:
    """전역 발언 권한 체크 (state_lock 잡힌 상태에서만 호출)"""
    if _state["is_muted"]:
        return False
    prune_global_alerts(now_ts)
    return len(global_alert_sent_times) < GLOBAL_RATE_LIMIT_COUNT


def global_mark_spoke_locked(now_ts: float):
    """전역 발언 카운트 증가 (state_lock 잡힌 상태에서만 호출)"""
    prune_global_alerts(now_ts)
    global_alert_sent_times.append(now_ts)


def rollback_global_alert_locked(now_ts: float):
    """전송 실패 시 카운터 롤백"""
    if global_alert_sent_times and global_alert_sent_times[-1] == now_ts:
        global_alert_sent_times.pop()
