# Saturday Soccer Auto-Registration

등록 큐 사이트의 API를 주기적으로 확인하다가 신청이 열린 것으로 보이면(큐 인원 증가) 자동으로 신청한다.  
날씨가 나쁘면(강수확률 초과 시) 등록을 건너뜀.

## 동작 방식

```
[매주 수요일 15:00 UTC] GitHub Actions → watcher.py 실행
        ↓
queue API 폴링 (기준 인원 대비 증가 시 트리거, 최대 timeout_hours)
        ↓
Montreal 토요일 오전 날씨 확인 (Open-Meteo API)
        ↓
강수확률 ≤ 기준  →  등록 API 호출 (이미 등록된 인원 자동 스킵)
강수확률 > 기준  →  등록 안 함
        ↓
완료 (GitHub 로그 / 로컬 macOS면 알림)
```

## 사전 요구사항

- Python 3.10+
- `requests` ([requirements.txt](requirements.txt))

## 설치

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## config.json 설정

```json
{
  "names": ["홍길동", "김철수"],
  "registration_api": "https://.../api/join",
  "queue_api": "https://.../api/queue",
  "weather": {
    "latitude": 45.5017,
    "longitude": -73.5673,
    "timezone": "America/Toronto",
    "max_precipitation_probability": 30,
    "game_hour": 9
  },
  "watcher": {
    "timeout_hours": 4,
    "poll_interval_seconds": 15
  }
}
```

## 실행 방법

| 명령어 | 설명 |
|--------|------|
| `python watcher.py` | 큐 API 감시 시작 (인원 증가 시 파이프라인 실행) |
| `python watcher.py --dry-run` | 날씨 확인 → 등록 시뮬레이션 (실제 POST 없음) |
| `python watcher.py --test` | 날씨 / 큐 API / dry-run 파이프라인 테스트 |
| `python register.py` | 날씨 무시하고 지금 바로 등록만 실행 |
| `python register.py --dry-run` | 등록 시뮬레이션만 출력 |
| `python weather.py` | 이번 토요일 날씨 확인 |

## GitHub Actions

워크플로: [.github/workflows/soccer-registration.yml](.github/workflows/soccer-registration.yml)

- **스케줄**: 매주 수요일 15:00 UTC (미동부 서머타임이면 대략 오전 11시 EDT)
- **수동 실행**: Actions 탭 → **Soccer Auto-Registration** → **Run workflow**

## 로컬에서 빠른 테스트

```bash
python watcher.py --test
# 또는
python watcher.py --dry-run
```
