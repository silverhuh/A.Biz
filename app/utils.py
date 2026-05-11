"""
공통 유틸리티 함수
- 텍스트 추출 (웹훅의 attachments, blocks 완벽 지원)
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
# 🎯 강화된 메시지 텍스트 추출 (Grafana 등 모든 봇 지원!)
# --------------------------------------------------------
def extract_message_text(event: dict) -> str:
    """
    Slack 이벤트에서 모든 텍스트를 추출합니다.
    
    지원 영역:
    1. event["text"]                            (기본 메시지)
    2. event["attachments"][*]["text"]          (Grafana, Webhook 등)
    3. event["attachments"][*]["fallback"]      (대체 텍스트)
    4. event["attachments"][*]["pretext"]       (위 텍스트)
    5. event["attachments"][*]["title"]         (제목)
    6. event["attachments"][*]["title_link"]    (제목 링크)
    7. event["attachments"][*]["author_name"]   (작성자)
    8. event["attachments"][*]["footer"]        (푸터)
    9. event["attachments"][*]["fields"][*]     (필드: 제목 + 값)
    10. event["blocks"][*]                      (Block Kit 전체)
        - section.text
        - section.fields
        - context.elements
        - rich_text.elements
        - header.text
    """
    parts = []
    
    # ===== 1. 기본 text =====
    if event.get("text"):
        parts.append(str(event["text"]))
    
    # ===== 2. attachments (Grafana, Legacy Webhook의 핵심!) =====
    for att in event.get("attachments", []) or []:
        # 일반 텍스트 필드들
        for key in ("pretext", "title", "text", "fallback", 
                    "author_name", "footer", "title_link"):
            value = att.get(key)
            if value:
                parts.append(str(value))
        
        # fields 배열 (Grafana가 자주 사용!)
        for field in att.get("fields", []) or []:
            if isinstance(field, dict):
                if field.get("title"):
                    parts.append(str(field["title"]))
                if field.get("value"):
                    parts.append(str(field["value"]))
        
        # blocks (attachment 안의 blocks)
        for block in att.get("blocks", []) or []:
            parts.extend(_extract_from_block(block))
    
    # ===== 3. blocks (Modern Block Kit) =====
    for block in event.get("blocks", []) or []:
        parts.extend(_extract_from_block(block))
    
    # ===== 4. 모든 텍스트 합치기 =====
    return "\n".join(p for p in parts if p)


def _extract_from_block(block: dict) -> list:
    """Block Kit의 단일 block에서 모든 텍스트 추출 (재귀적)"""
    if not isinstance(block, dict):
        return []
    
    parts = []
    
    # block.text (section, header 등)
    text_obj = block.get("text")
    if isinstance(text_obj, dict) and text_obj.get("text"):
        parts.append(str(text_obj["text"]))
    elif isinstance(text_obj, str):
        parts.append(text_obj)
    
    # block.fields (section block)
    for field in block.get("fields", []) or []:
        if isinstance(field, dict) and field.get("text"):
            parts.append(str(field["text"]))
        elif isinstance(field, str):
            parts.append(field)
    
    # block.elements (context, rich_text, actions 등)
    for element in block.get("elements", []) or []:
        if isinstance(element, dict):
            # text 필드
            if element.get("text"):
                if isinstance(element["text"], dict):
                    if element["text"].get("text"):
                        parts.append(str(element["text"]["text"]))
                else:
                    parts.append(str(element["text"]))
            
            # rich_text_section의 elements (재귀)
            for sub_element in element.get("elements", []) or []:
                if isinstance(sub_element, dict):
                    if sub_element.get("text"):
                        parts.append(str(sub_element["text"]))
    
    return parts


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
