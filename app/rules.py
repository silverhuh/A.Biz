"""
에러 감지 알림 규칙 정의
"""

# --------------------------------------------------------
# 채널 ID 정의
# --------------------------------------------------------
TM_SERVICEDEVTEAM_DEV_BIZ = "C0B12JP7ARW"   # 서비스개발팀 dev biz 채널
ERRORDISPATCHER_HUH = "C092DJVHVPY"         # Test 수신 채널
BIZ_BOT_TEST = "C0B2RGH80M9"                # Test 발신 채널
REPORT_API_ALERT_DEV = "C0AV98LHR8W"        # 비즈 리포트 발신 채널

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
        "name": "BIZ_TEST1",
        "channel": TM_SERVICEDEVTEAM_DEV_BIZ,    # A채널: 서비스개발팀 dev biz
        "keyword": "Class",                      # 감지 키워드
        "threshold": 1,                          # 1회 이상 감지 시
        "notify": [
            {
                "channel": ERRORDISPATCHER_HUH,         # B채널: Test 수신 채널
                "text": f"Test 알림 {MENTION_HEO}",  # @허은석 멘션
                "include_log": True,             # 원본 로그 포함
            },
        ],
    },
    {
        "name": "BIZ_TEST2",
        "channel": REPORT_API_ALERT_DEV,    # A채널: 비즈 리포트 발신 채널
        "keyword": "400",                   # 감지 키워드
        "threshold": 1,                     # 1회 이상 감지 시
        "notify": [
            {
                "channel": ERRORDISPATCHER_HUH,      # B채널: Test 수신 채널
                "text": f"Test 알림 {MENTION_HEO}",  # @허은석 멘션
                "include_log": True,                # 원본 로그 포함
            },
        ],
    },    
    {
        "name": "BIZ_TEST3",
        "channel": BIZ_BOT_TEST,            # A채널: Test 발신 채널
        "keyword": "400",                   # 감지 키워드
        "threshold": 1,                     # 1회 이상 감지 시
        "notify": [
            {
                "channel": ERRORDISPATCHER_HUH,      # B채널: Test 수신 채널
                "text": f"Test 알림 {MENTION_HEO}",  # @허은석 멘션
                "include_log": True,                # 원본 로그 포함
            },
        ],
    },        
]
