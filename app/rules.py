"""
에러 감지 알림 규칙 정의
"""
from app.constants import (
    ALERT_PREFIX,
    SVC_WATCHTOWER_CH, SVC_TMAP_DIV_CH, SVC_BTV_DIV_CH,
    RTZR_STT_SKT_ALERT_CH, EXT_GIP_REPAIRING_CH, LINER_ADOT_CH,
    ERROR_AX_CH, TEST_ALERT_CH, OPEN_MONITORING_CH, SKT_NAPKIN,
    ADOT_BIZ_TEAM, TM_SERVICEDEVTEAM_DEV_BIZ,
    MENTION_HEO, MENTION_KHM, MENTION_KDW, MENTION_NJK, MENTION_JJY,
    MENTION_KJH, MENTION_KHR, MENTION_KYH, MENTION_GJH, MENTION_YYJ,
    MENTION_PJY, MENTION_KAI, MENTION_BSR, MENTION_KSW, MENTION_LYS,
    MENTION_GMS, MENTION_JUR, MENTION_SYC, MENTION_KHJ, MENTION_PJH,
    MENTION_KTH, MENTION_ERW,
)


RULES = [
    {
        "name": "ADOTBIZ",
        "channel": TEST_ALERT_CH,
        "keyword": "이상 감지",
        "threshold": 1,
        "notify": [
            {
                "channel": TEST_ALERT_CH,
                "text": f"{ALERT_PREFIX} 이상 감지되어 관련 채널에 전파하였습니다.",
                "include_log": False,
            },
            {
                "channel": ADOT_BIZ_TEAM,
                "text": f"{ALERT_PREFIX} 이상 감지되어 안내드립니다.",
                "include_log": True,
            },
        ],
    },
    {
        "name": "RTZR_API",
        "channel": SVC_WATCHTOWER_CH,
        "keyword": "RTZR_API",
        "threshold": 6,
        "notify": [
            {
                "channel": SVC_WATCHTOWER_CH,
                "text": (
                    f"{ALERT_PREFIX} 노트 에러(RTZR_API)가 감지되어 담당자 전달하였습니다. "
                    f"(cc. {MENTION_HEO}님, {MENTION_KHM}님)"
                ),
                "include_log": False,
            },
            {
                "channel": RTZR_STT_SKT_ALERT_CH,
                "text": (
                    f"{ALERT_PREFIX} RTZR_API 6회 이상 감지중! "
                    f"{MENTION_KDW}님, {MENTION_NJK}님, {MENTION_JJY}님 확인 문의드립니다. "
                    f"(cc. {MENTION_HEO}님, {MENTION_KHM}님)"
                ),
                "include_log": False,
            },
        ],
    },
    {
        "name": "PET_API",
        "channel": SVC_WATCHTOWER_CH,
        "keyword": "PET_API",
        "threshold": 6,
        "notify": [
            {
                "channel": SVC_WATCHTOWER_CH,
                "text": (
                    f"{ALERT_PREFIX} 노트 에러(PET_API) 6회 이상 감지중! "
                    f"{MENTION_KJH}님, {MENTION_KHR}님 확인 문의드립니다. "
                    f"(cc. {MENTION_HEO}님, {MENTION_KHM}님)"
                ),
                "include_log": False,
            },
        ],
    },
    {
        "name": "BUILTIN_ONE",
        "channel": SVC_WATCHTOWER_CH,
        "keyword": "builtin.one",
        "threshold": 6,
        "notify": [
            {
                "channel": SVC_WATCHTOWER_CH,
                "text": (
                    f"{ALERT_PREFIX} One Agent 에러가 감지되었습니다."
                    f"(cc. {MENTION_HEO}님, {MENTION_KHM}님)"
                ),
                "include_log": False,
            },
        ],
    },
    {
        "name": "BIZ_TEST",
        "channel": TM_SERVICEDEVTEAM_DEV_BIZ,
        "keyword": "class",
        "threshold": 1,
        "notify": [
            {
                "channel": TEST_ALERT_CH,
                "text": f"{ALERT_PREFIX} Biz Test 알림 (cc. {MENTION_HEO}님)",
                "include_log": False,
            },
        ],
    },
    {
        "name": "PERPLEXITY",
        "channel": SVC_WATCHTOWER_CH,
        "keyword": "Perplexity",
        "threshold": 20,
        "notify": [
            {
                "channel": SVC_WATCHTOWER_CH,
                "text": (
                    f"{ALERT_PREFIX} Perplexity 에러가 감지되어 담당자 전달하였습니다. "
                    f"(cc. {MENTION_HEO}님, {MENTION_KHM}님)"
                ),
                "include_log": False,
            },
            {
                "channel": EXT_GIP_REPAIRING_CH,
                "text": (
                    f"{ALERT_PREFIX} Perplexity 에러가 발생되어 확인 문의드립니다. "
                    f"{MENTION_KYH}님, {MENTION_GJH}님 "
                    f"(cc. {MENTION_YYJ}님, {MENTION_PJY}님, {MENTION_HEO}님, {MENTION_KHM}님)"
                ),
                "include_log": True,
            },
        ],
    },
    {
        "name": "CLAUDE",
        "channel": SVC_WATCHTOWER_CH,
        "keyword": "Claude",
        "threshold": 20,
        "notify": [
            {
                "channel": SVC_WATCHTOWER_CH,
                "text": (
                    f"{ALERT_PREFIX} Claude 에러가 감지되어 담당자 전달하였습니다. "
                    f"(cc. {MENTION_HEO}님, {MENTION_KHM}님)"
                ),
                "include_log": False,
            },
            {
                "channel": EXT_GIP_REPAIRING_CH,
                "text": (
                    f"{ALERT_PREFIX} Claude 에러가 발생되어 확인 문의드립니다. "
                    f"{MENTION_KYH}님, {MENTION_GJH}님 "
                    f"(cc. {MENTION_YYJ}님, {MENTION_PJY}님, {MENTION_HEO}님, {MENTION_KHM}님)"
                ),
                "include_log": True,
            },
        ],
    },
    {
        "name": "GPT",
        "channel": SVC_WATCHTOWER_CH,
        "keyword": "MODEL_LABEL: GPT",
        "threshold": 20,
        "notify": [
            {
                "channel": SVC_WATCHTOWER_CH,
                "text": (
                    f"{ALERT_PREFIX} GPT 에러가 감지되어 담당자 전달하였습니다. "
                    f"(cc. {MENTION_HEO}님, {MENTION_KHM}님)"
                ),
                "include_log": False,
            },
            {
                "channel": EXT_GIP_REPAIRING_CH,
                "text": (
                    f"{ALERT_PREFIX} GPT 에러가 발생되어 확인 문의드립니다. "
                    f"{MENTION_KYH}님, {MENTION_GJH}님 "
                    f"(cc. {MENTION_YYJ}님, {MENTION_PJY}님, {MENTION_HEO}님, {MENTION_KHM}님)"
                ),
                "include_log": True,
            },
        ],
    },
    {
        "name": "GEMINI",
        "channel": SVC_WATCHTOWER_CH,
        "keyword": "Gemini",
        "threshold": 20,
        "notify": [
            {
                "channel": SVC_WATCHTOWER_CH,
                "text": (
                    f"{ALERT_PREFIX} Gemini 에러가 감지되어 담당자 전달하였습니다. "
                    f"(cc. {MENTION_HEO}님, {MENTION_KHM}님)"
                ),
                "include_log": False,
            },
            {
                "channel": EXT_GIP_REPAIRING_CH,
                "text": (
                    f"{ALERT_PREFIX} Gemini 에러가 발생되어 확인 문의드립니다. "
                    f"{MENTION_KYH}님, {MENTION_GJH}님 "
                    f"(cc. {MENTION_YYJ}님, {MENTION_PJY}님, {MENTION_HEO}님, {MENTION_KHM}님)"
                ),
                "include_log": True,
            },
        ],
    },
    {
        "name": "LINER",
        "channel": SVC_WATCHTOWER_CH,
        "keyword": "Liner",
        "threshold": 6,
        "notify": [
            {
                "channel": SVC_WATCHTOWER_CH,
                "text": (
                    f"{ALERT_PREFIX} Liner 모델 에러가 감지되어 담당자 전달하였습니다. "
                    f"(cc. {MENTION_HEO}님, {MENTION_KHM}님)"
                ),
                "include_log": False,
            },
            {
                "channel": LINER_ADOT_CH,
                "text": (
                    f"{ALERT_PREFIX} Liner 에러가 발생되어 확인 문의드립니다. "
                    f"{MENTION_KAI}님, {MENTION_BSR}님 "
                    f"(cc. {MENTION_HEO}님, {MENTION_KHM}님)"
                ),
                "include_log": True,
            },
        ],
    },
    {
        "name": "AX",
        "channel": SVC_WATCHTOWER_CH,
        "keyword": "A.X",
        "threshold": 10,
        "notify": [
            {
                "channel": SVC_WATCHTOWER_CH,
                "text": (
                    f"{ALERT_PREFIX} A.X 에러가 감지되어 담당자 전달하였습니다. "
                    f"(cc. {MENTION_HEO}님, {MENTION_KHM}님)"
                ),
                "include_log": False,
            },
            {
                "channel": ERROR_AX_CH,
                "text": (
                    f"{ALERT_PREFIX} A.X 에러가 발생되어 확인 문의드립니다. "
                    f"{MENTION_KSW}님, {MENTION_LYS}님 "
                    f"(cc. {MENTION_HEO}님, {MENTION_KHM}님)"
                ),
                "include_log": True,
            },
        ],
    },
    {
        "name": "REQUEST_ID",
        "channel": SVC_BTV_DIV_CH,
        "keyword": "REQUEST_ID",
        "threshold": 20,
        "notify": [
            {
                "channel": SVC_BTV_DIV_CH,
                "text": (
                    f"{ALERT_PREFIX} 에러가 감지되어 확인 문의드립니다. "
                    f"{MENTION_SYC}님, {MENTION_GMS}님 "
                    f"(cc. {MENTION_HEO}님, {MENTION_KHM}님)"
                ),
                "include_log": False,
            },
        ],
    },
    # 테스트
    {
        "name": "TEST",
        "channel": TEST_ALERT_CH,
        "keyword": "builtin.one",
        "threshold": 2,
        "notify": [
            {
                "channel": TEST_ALERT_CH,
                "text": f"{ALERT_PREFIX} 테스트 알림: test 감지됨. cc. {MENTION_HEO}님, {MENTION_KHM}님",
                "include_log": False,
            },
        ],
    },
    # napkin
    {
        "name": "diagramCreate",
        "channel": SVC_WATCHTOWER_CH,
        "keyword": "diagramCreate",
        "threshold": 6,
        "notify": [
            {
                "channel": SVC_WATCHTOWER_CH,
                "text": f"{ALERT_PREFIX} napkin 에러가 감지되어 담당자 전달하였습니다. (cc. {MENTION_HEO}님)",
                "include_log": False,
            },
            {
                "channel": SKT_NAPKIN,
                "text": (
                    f"{ALERT_PREFIX} napkin error has been detected. Could you please check? "
                    f"{MENTION_ERW}"
                    f"(cc. {MENTION_HEO})"
                ),
                "include_log": True,
            },
        ],
    },
    # napkin test
    {
        "name": "diagramCreate_test",
        "channel": TEST_ALERT_CH,
        "keyword": "diagramCreate",
        "threshold": 6,
        "notify": [
            {
                "channel": TEST_ALERT_CH,
                "text": f"{ALERT_PREFIX} napkin 에러가 감지되어 담당자 전달하였습니다. (cc. {MENTION_HEO}님)",
                "include_log": False,
            },
            {
                "channel": SKT_NAPKIN,
                "text": (
                    f"{ALERT_PREFIX} napkin error has been detected. Could you please check? "
                    f"{MENTION_ERW}"
                    f"(cc. {MENTION_HEO})"
                ),
                "include_log": True,
            },
        ],
    },
    # TMAP API
    {
        "name": "API",
        "channel": SVC_TMAP_DIV_CH,
        "keyword": "API",
        "threshold": 12,
        "notify": [
            {
                "channel": SVC_TMAP_DIV_CH,
                "text": (
                    f"{ALERT_PREFIX} TMAP API 에러가 감지되어 티모비 채널에 전파하였습니다. "
                    f"(cc. {MENTION_GMS}님, {MENTION_JUR}님, {MENTION_KHM}님, {MENTION_HEO}님)"
                ),
                "include_log": False,
            },
            {
                "channel": OPEN_MONITORING_CH,
                "text": (
                    f"{ALERT_PREFIX} TMAP API 에러가 지속 감지되어 확인 문의드립니다. "
                    f"<!here>\n"
                    f"(cc. {MENTION_HEO}님, {MENTION_KHM}님)"
                ),
                "include_log": True,
            },
        ],
    },
    # TMAP status=500
    {
        "name": "status=500",
        "channel": SVC_TMAP_DIV_CH,
        "keyword": "status=500",
        "threshold": 6,
        "notify": [
            {
                "channel": SVC_TMAP_DIV_CH,
                "text": (
                    f"{ALERT_PREFIX} status=500 에러가 감지되어 확인 문의드립니다. "
                    f"{MENTION_KHJ}님, {MENTION_PJH}님, {MENTION_KTH}님 "
                    f"(cc. {MENTION_KHM}님, {MENTION_GMS}님, {MENTION_JUR}님, {MENTION_HEO}님)"
                ),
                "include_log": False,
            },
        ],
    },
    # TMAP TOAST ERROR
    {
        "name": "TOAST ERROR",
        "channel": SVC_TMAP_DIV_CH,
        "keyword": "TOAST ERROR",
        "threshold": 6,
        "notify": [
            {
                "channel": SVC_TMAP_DIV_CH,
                "text": (
                    f"{ALERT_PREFIX} 토스트 에러 확인 문의드립니다. "
                    f"{MENTION_KHJ}님, {MENTION_PJH}님, {MENTION_KTH}님 "
                    f"(cc. {MENTION_KHM}님, {MENTION_GMS}님, {MENTION_JUR}님, {MENTION_HEO}님)"
                ),
                "include_log": False,
            },
        ],
    },
]
