"""
에러 감지 알림 규칙 정의
"""

# --------------------------------------------------------
# 채널 ID 정의
# --------------------------------------------------------
TM_SERVICEDEVTEAM_DEV_BIZ = "C0B12JP7ARW"   # 서비스개발팀 dev biz 채널
TEST_ALERT_CH = "C092DJVHVPY"                # Test 채널
TEST_ERROR_STG_TEST = "C0B2RGH80M9"

# --------------------------------------------------------
# 멘션 ID 정의
# --------------------------------------------------------
MENTION_HEO = "<@U04MGC3BFCY>"                # 허은석


# ========================================================
# 알림 규칙
# ========================================================
RULES = [
    # ----------------------------------------------------
    # 🎯 BIZ_TEST 규칙
    # 서비스개발팀 dev biz 채널에서 5분 이내 "Class" 키워드
    # 1회 이상 감지 시, Test 채널에 알림 발송
    # ----------------------------------------------------
    {
        "name": "BIZ_TEST",
        "channel": TM_SERVICEDEVTEAM_DEV_BIZ,    # A채널: 서비스개발팀 dev biz
        "keyword": "Class",                       # 감지 키워드
        "threshold": 1,                           # 1회 이상 감지 시
        "notify": [
            {
                "channel": TEST_ALERT_CH,         # B채널: Test
                "text": f"Test 알림 {MENTION_HEO}",  # @허은석 멘션
                "include_log": False,             # 원본 로그 미포함
            },
        ],
    },
    {
        "name": "BIZ_TEST2",
        "channel": TEST_ERROR_STG_TEST,    # A채널: 서비스개발팀 dev biz
        "keyword": "Class",                       # 감지 키워드
        "threshold": 1,                           # 1회 이상 감지 시
        "notify": [
            {
                "channel": TEST_ALERT_CH,         # B채널: Test
                "text": f"Test 알림 {MENTION_HEO}",  # @허은석 멘션
                "include_log": False,             # 원본 로그 미포함
            },
        ],
    },    
]
