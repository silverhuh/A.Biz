# 🔔 Slack Error Monitor Bot

여러 Slack 채널에서 발생하는 에러 메시지를 실시간으로 감지하여, 임계치 초과 시 담당자에게 자동 알림을 전송하는 봇입니다.

## ✨ 주요 특징

- ✅ **웹훅 메시지 인식**: Legacy Incoming Webhook(`bot_message`), Modern Block Kit, Attachments까지 모두 처리
- ✅ **Socket Mode**: 공인 IP 없이도 작동 (방화벽 안전)
- ✅ **임계치 기반 알림**: 단발성 에러는 무시, 지속 발생 시에만 알림
- ✅ **시간 윈도우**: 4분 내 카운팅
- ✅ **전역 레이트리밋**: 5분 내 최대 2회 알림 (스팸 방지)
- ✅ **다중 채널 전파**: 한 에러를 여러 채널에 동시 알림
- ✅ **Mute/Unmute**: `!mute`, `!unmute` 또는 `/mute`, `/unmute` 슬래시 커맨드

## 📂 프로젝트 구조

```
slack-error-monitor-bot/
├── app/
│   ├── __init__.py
│   ├── main.py          # 엔트리포인트
│   ├── config.py        # 환경설정
│   ├── constants.py     # 채널/멘션 ID
│   ├── rules.py         # 알림 규칙
│   ├── handlers.py      # 이벤트 핸들러 (웹훅 인식 핵심)
│   └── utils.py         # 유틸리티
├── requirements.txt
├── Procfile
├── runtime.txt
├── railway.toml
├── .env.example
├── .gitignore
└── README.md
```

## 🚀 빠른 시작

### 1. Slack App 생성

1. [https://api.slack.com/apps](https://api.slack.com/apps) 접속
2. **Create New App** → **From scratch**
3. 워크스페이스 선택

### 2. 권한 설정

**OAuth & Permissions** 메뉴에서 Bot Token Scopes 추가:
- `chat:write`
- `channels:history`
- `groups:history`
- `commands`

### 3. Socket Mode 활성화

**Socket Mode** 메뉴 → ON

### 4. App-Level Token 발급

**Basic Information** → **App-Level Tokens** → Generate
- Scope: `connections:write`
- 발급된 토큰(xapp-)을 환경변수에 저장

### 5. Event Subscriptions

**Event Subscriptions** → ON

다음 이벤트 구독 추가:
- `message.channels`
- `message.groups`

### 6. Slash Commands

`/mute`, `/unmute` 커맨드 등록

### 7. 봇 토큰 발급

**OAuth & Permissions** → **Install to Workspace**
- Bot Token(xoxb-)을 환경변수에 저장

## 🛠 로컬 실행

```bash
# 1. 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 환경변수 설정
cp .env.example .env
# .env 파일 편집

# 4. 실행
python -m app.main
```

## 🚂 Railway 배포

### 1. GitHub 저장소 연결

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/slack-error-monitor-bot.git
git push -u origin main
```

### 2. Railway 프로젝트 생성

1. [Railway](https://railway.app) 접속
2. **New Project** → **Deploy from GitHub repo**
3. 저장소 선택

### 3. 환경변수 설정

Railway 대시보드 → **Variables** 탭에서 추가:
- `SLACK_BOT_TOKEN`
- `SLACK_APP_TOKEN`
- `DEBUG_MODE` (선택, 기본값: false)

### 4. 배포

자동으로 빌드 & 배포가 시작됩니다.

## 🔧 웹훅 메시지 인식 원리

기존 봇과의 핵심 차이점은 **subtype 처리**입니다.

```python
# ❌ 기존 코드: 웹훅 메시지 차단
if event.get("subtype") is not None:
    return

# ✅ 개선된 코드: 웹훅 메시지 허용
ALLOWED_SUBTYPES = {None, "bot_message", "file_share", "thread_broadcast"}
if subtype in IGNORED_SUBTYPES:
    return
if subtype is not None and subtype not in ALLOWED_SUBTYPES:
    return
```

또한 텍스트 추출 시 `attachments`와 `blocks`까지 파싱하여 웹훅이 보낸 모든 텍스트를 인식합니다.

```python
# attachments, blocks까지 텍스트 추출
def extract_message_text(event: dict) -> str:
    parts = [event.get("text", "")]
    for att in event.get("attachments", []):
        for key in ("pretext", "title", "text", "fallback"):
            if att.get(key):
                parts.append(att[key])
    # ... blocks 처리
    return "\n".join(parts)
```

## 📊 알림 규칙 추가

`app/rules.py`에 새 규칙 추가:

```python
{
    "name": "MY_NEW_RULE",
    "channel": "C12345678",      # 감지할 채널
    "keyword": "에러 키워드",
    "threshold": 5,                # 5회 이상 시 알림
    "notify": [
        {
            "channel": "C87654321",
            "text": "❗ 에러 감지!",
            "include_log": True,
        },
    ],
}
```

## 🎮 명령어

| 명령어 | 설명 |
|--------|------|
| `!mute` | 알림 일시 중지 |
| `!unmute` | 알림 재개 |
| `/mute` | 슬래시 커맨드로 중지 |
| `/unmute` | 슬래시 커맨드로 재개 |

## 🐛 디버깅

환경변수에 `DEBUG_MODE=true` 설정 시 모든 메시지 이벤트 로그 출력:

```
[DEBUG] subtype=bot_message, user=None, bot_id=B01ABC123, 
        username=WatchtowerBot, channel=C04M1UCMCFQ,
        has_attachments=True, text_preview=...
```

## 📝 라이선스

MIT
