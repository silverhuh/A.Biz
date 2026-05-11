"""
Slack 이벤트 핸들러
- 메시지 수신 (사람 + 봇 + 웹훅 모두 처리)
- !mute, !unmute 명령어 처리
- 슬래시 커맨드 처리
"""
import time
from app.config import (
    ALLOWED_SUBTYPES,
    IGNORED_SUBTYPES,
    DEBUG_MODE,
)
from app.constants import SVC_TMAP_DIV_CH, ALERT_PREFIX
from app.rules import RULES
from app.utils import (
    state_lock,
    message_window,
    get_is_muted,
    set_is_muted,
    get_bot_user_id,
    get_bot_id,
    clear_counters,
    extract_message_text,
    keyword_hits_in_text,
    prune_old_events,
    global_can_speak_locked,
    global_mark_spoke_locked,
    rollback_global_alert_locked,
    global_alert_sent_times,
)


def register_handlers(app):
    """Slack App에 이벤트 핸들러 등록"""
    
    # ----------------------------------------------------
    # 메시지 이벤트
    # ----------------------------------------------------
    @app.event("message")
    def handle_message(body, say, client, logger):
        event = body.get("event", {}) or {}
        subtype = event.get("subtype")
        
        # 디버그 로그
        if DEBUG_MODE:
            print(
                f"[DEBUG] subtype={subtype}, "
                f"user={event.get('user')}, "
                f"bot_id={event.get('bot_id')}, "
                f"username={event.get('username')}, "
                f"channel={event.get('channel')}, "
                f"has_attachments={bool(event.get('attachments'))}, "
                f"text_preview={(event.get('text') or '')[:80]}"
            )
        
        # ====================================================
        # 🎯 핵심: subtype 필터링 (웹훅 메시지 허용)
        # ====================================================
        # - None: 일반 사용자 메시지 ✅
        # - "bot_message": Legacy Incoming Webhook ✅
        # - "file_share": 파일 첨부 메시지 ✅
        # - "thread_broadcast": 스레드 브로드캐스트 ✅
        # - "message_changed"/"message_deleted" 등: ❌ 무시
        if subtype in IGNORED_SUBTYPES:
            return
        if subtype is not None and subtype not in ALLOWED_SUBTYPES:
            # 알려지지 않은 subtype은 안전하게 무시
            if DEBUG_MODE:
                print(f"[SKIP] Unknown subtype: {subtype}")
            return
        
        # ====================================================
        # 무한루프 방지: 내 봇이 보낸 메시지만 차단
        # (다른 봇/웹훅은 처리!)
        # ====================================================
        bot_user_id = get_bot_user_id()
        bot_id = get_bot_id()
        
        if bot_user_id and event.get("user") == bot_user_id:
            return
        if bot_id and event.get("bot_id") == bot_id:
            return
        
        # ====================================================
        # 채널 및 텍스트 추출 (웹훅 attachments 포함!)
        # ====================================================
        channel = event.get("channel")
        text = extract_message_text(event)
        cmd = text.strip().lower()
        
        # ====================================================
        # !mute / !unmute 명령어 (사용자가 보낸 메시지만)
        # ====================================================
        if subtype is None:  # 사용자 메시지만 명령어로 처리
            if cmd.startswith("!mute"):
                _handle_mute(client, channel, mute=True)
                return
            if cmd.startswith("!unmute"):
                _handle_mute(client, channel, mute=False)
                return
        
        # ====================================================
        # Mute 상태면 처리 중단
        # ====================================================
        with state_lock:
            if get_is_muted():
                return
        
        # ====================================================
        # 메시지 처리
        # ====================================================
        process_message(client, channel, text, event)
    
    # ----------------------------------------------------
    # Slash commands
    # ----------------------------------------------------
    @app.command("/mute")
    def slash_mute(ack, respond):
        ack()
        with state_lock:
            set_is_muted(True)
            clear_counters()
        respond("🔇 Bot mute 설정 완료")
    
    @app.command("/unmute")
    def slash_unmute(ack, respond):
        ack()
        with state_lock:
            set_is_muted(False)
            clear_counters()
        respond("🔔 Bot unmute 완료 (카운트 초기화)")


# --------------------------------------------------------
# Mute 처리
# --------------------------------------------------------
def _handle_mute(client, channel, mute: bool):
    with state_lock:
        set_is_muted(mute)
        clear_counters()
    
    msg = "🔇 Bot mute 상태입니다." if mute else "🔔 Bot unmute 되었습니다. (카운트 초기화)"
    try:
        client.chat_postMessage(channel=channel, text=msg)
    except Exception as e:
        print(f"[MUTE_REPLY_FAIL] {repr(e)}")


# --------------------------------------------------------
# 메시지 처리 핵심 로직
# --------------------------------------------------------
def process_message(client, channel, text, event):
    """메시지 텍스트를 RULES와 매칭하여 카운팅 후 임계치 초과 시 알림"""
    now_ts = time.time()
    
    # 1) RULES 기반 감지
    for rule in RULES:
        if channel != rule["channel"]:
            continue
        
        hits = keyword_hits_in_text(rule["keyword"], text)
        if hits <= 0:
            continue
        
        key = (channel, rule["name"])
        prune_old_events(key, now_ts)
        
        # 한 메시지에서 여러 번 등장하면 그 횟수만큼 timestamp 추가
        for _ in range(hits):
            message_window[key].append(now_ts)
        
        if len(message_window[key]) >= rule["threshold"]:
            send_alert_for_rule(client, rule, text)
            message_window[key].clear()
    
    # 2) TMAP 채널 전용 특수 룰: "API" 미포함 메시지 6회
    from app.constants import (
        ALERT_PREFIX, MENTION_HEO, MENTION_KHM, MENTION_GMS,
        MENTION_JUR, MENTION_KHJ, MENTION_PJH,
    )
    if channel == SVC_TMAP_DIV_CH and "api" not in text.lower():
        key = (channel, "TMAP_API_MISSING")
        prune_old_events(key, now_ts)
        message_window[key].append(now_ts)
        
        if len(message_window[key]) >= 6:
            pseudo_rule = {
                "name": "TMAP_API_MISSING",
                "notify": [
                    {
                        "channel": SVC_TMAP_DIV_CH,
                        "text": (
                            f"{ALERT_PREFIX} 내부 원인으로 추정되는 에러가 감지되어 확인 문의드립니다. "
                            f"{MENTION_KHJ}님, {MENTION_PJH}님 "
                            f"(cc. {MENTION_KHM}님, {MENTION_GMS}님, {MENTION_JUR}님, {MENTION_HEO}님)"
                        ),
                        "include_log": False,
                    }
                ],
            }
            send_alert_for_rule(client, pseudo_rule, text)
            message_window[key].clear()


def send_alert_for_rule(client, rule, original_text):
    """규칙 기반 알림 전송 (전역 레이트리밋 적용)"""
    now_ts = time.time()
    rule_name = rule.get("name")
    
    # 1) 전송 권한 확보
    with state_lock:
        if not global_can_speak_locked(now_ts):
            return
        global_mark_spoke_locked(now_ts)
    
    sent_count = 0
    errors = []
    
    # 2) 실제 전송 (최대 2건)
    for action in rule.get("notify", []):
        target_channel = action.get("channel")
        try:
            text = action["text"]
            if action.get("include_log"):
                text += f"\n\n```{original_text[:2500]}```"  # Slack 메시지 길이 제한 고려
            
            client.chat_postMessage(channel=target_channel, text=text)
            sent_count += 1
            
            if sent_count >= 2:
                break
        except Exception as e:
            errors.append(f"{target_channel} -> {repr(e)}")
    
    # 3) 전부 실패 시 카운터 롤백
    if sent_count == 0:
        with state_lock:
            rollback_global_alert_locked(now_ts)
    
    # 4) 부분 실패 로그
    if errors:
        print(f"[ALERT_PARTIAL_FAIL] rule={rule_name} sent={sent_count} errors={errors}")
