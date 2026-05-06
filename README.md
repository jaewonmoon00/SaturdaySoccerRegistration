# Saturday Soccer Auto-Registration

카카오톡 메시지를 감시하다가 축구 등록 링크가 올라오면 자동으로 신청해주는 도구.  
날씨가 나쁘면 (강수확률 초과 시) 등록을 건너뜀.

## 동작 방식

```
[매주 수요일 10:30] cron → watcher.py 실행
        ↓
카카오톡 감시 (최대 1시간)
        ↓
"택" 발신 + 등록 URL 포함 메시지 감지
        ↓
Montreal 토요일 오전 날씨 확인 (Open-Meteo API)
        ↓
강수확률 ≤ 30%  →  등록 API 호출 (이미 등록된 인원 자동 스킵)
강수확률 > 30%  →  등록 안 함
        ↓
Mac 알림 전송
```

## 사전 요구사항

- Python 3.10+
- [kakaocli](https://github.com/wonjun-dev/kakaocli) — KakaoTalk DB 읽기용

```bash
brew install kakaocli   # 또는 직접 빌드
```

## 설치

```bash
# 1. 가상환경 생성 및 의존성 설치
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 또는 cron 설정까지 한 번에
bash setup_cron.sh
```

## config.json 설정

```json
{
  "names": ["홍길동", "김철수"],          // 등록할 이름 목록
  "chat_id": 437189095976595,            // 카카오톡 채팅방 ID
  "sender_keyword": "택",                // 트리거 발신자 키워드
  "trigger_url_keyword": "saturday-soccer-queue.vercel.app",  // 트리거 URL 키워드
  "registration_api": "https://.../api/join",
  "queue_api": "https://.../api/queue",
  "weather": {
    "latitude": 45.5017,
    "longitude": -73.5673,
    "timezone": "America/Toronto",
    "max_precipitation_probability": 30, // 이 값 초과 시 등록 안 함 (%)
    "game_hour": 9                       // 경기 시작 시간 (오전 9시)
  },
  "watcher": {
    "timeout_hours": 1,                  // 감시 최대 시간
    "kakao_launch_wait_seconds": 5       // KakaoTalk 실행 대기 시간
  }
}
```

## 실행 방법

| 명령어 | 설명 |
|--------|------|
| `python watcher.py` | 카카오톡 감시 시작 (트리거 대기) |
| `python watcher.py --run` | 날씨 확인 → 등록 → 알림 전체 파이프라인 즉시 실행 |
| `python watcher.py --dry-run` | 전체 파이프라인 실행 (등록은 안 함, 시뮬레이션) |
| `python watcher.py --test` | DB 연결 / 날씨 / 큐 API / 등록 시뮬레이션 전체 테스트 |
| `python register.py` | 날씨 무시하고 지금 바로 등록만 실행 |
| `python register.py --dry-run` | 등록 시뮬레이션만 출력 |
| `python weather.py` | 이번 토요일 날씨 확인 |

## cron 자동 설정

매주 수요일 오전 10:30에 자동 실행되도록 cron 등록:

```bash
bash setup_cron.sh
```

등록 확인:
```bash
crontab -l | grep soccer
```

cron 제거:
```bash
crontab -e   # 해당 줄 삭제
```

## 로그 확인

```bash
tail -f /tmp/soccer_watcher.log
```
