import json
import sys
import time
import subprocess
from datetime import datetime

import requests


def load_config() -> dict:
    with open("config.json") as f:
        return json.load(f)


# ── Queue API ──────────────────────────────────────────────────────────────────

def get_queue(queue_api: str) -> list:
    resp = requests.get(queue_api, timeout=10)
    resp.raise_for_status()
    return resp.json().get("queue", [])


# ── Notification ───────────────────────────────────────────────────────────────

def send_notification(message: str):
    if sys.platform == "darwin":
        lines = message.split("\n")
        title = "Saturday Soccer"
        subtitle = lines[0]
        body = "\n".join(lines[1:]) if len(lines) > 1 else ""
        script = f'display notification "{body}" with title "{title}" subtitle "{subtitle}"'
        subprocess.run(["osascript", "-e", script])
    else:
        print(f"[알림] {message}")


# ── Pipeline ───────────────────────────────────────────────────────────────────

def run_pipeline(config: dict, dry_run: bool = False) -> str:
    from weather import is_weather_good, get_next_saturday
    from register import register_names, format_result_message

    print("\n--- 파이프라인 시작 ---")
    next_saturday = get_next_saturday()
    print(f"대상: 토요일 {next_saturday} 오전 {config['weather']['game_hour']}시 Montreal")

    good, prob = is_weather_good(config)
    print(f"강수확률: {prob}% (기준: {config['weather']['max_precipitation_probability']}%)")

    if not good:
        msg = f"⛔ 비 예보로 축구 신청 안 했어요\n토요일 ({next_saturday}) 강수확률: {prob}%"
        print(msg)
        return msg

    results = register_names(config, dry_run=dry_run)
    msg = format_result_message(results, prob)
    print(f"\n{msg}")
    return msg


# ── Watcher ────────────────────────────────────────────────────────────────────

def watch_site(config: dict, dry_run: bool = False):
    interval = config["watcher"]["poll_interval_seconds"]
    timeout_seconds = config["watcher"]["timeout_hours"] * 3600
    start_time = time.time()

    baseline = len(get_queue(config["queue_api"]))
    print(f"\n큐 감시 시작 (현재: {baseline}명, {interval}초 간격, 최대 {config['watcher']['timeout_hours']}시간)")

    while time.time() - start_time < timeout_seconds:
        time.sleep(interval)
        try:
            current = len(get_queue(config["queue_api"]))
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 요청 실패: {e}")
            continue

        print(f"[{datetime.now().strftime('%H:%M:%S')}] 큐: {current}명")

        if (baseline > 0 and current == 0) or (baseline == 0 and current > 0):
            print(f"\n✅ 변화 감지! {baseline}명 → {current}명 — 파이프라인 실행...")
            result_msg = run_pipeline(config, dry_run=dry_run)
            if not dry_run:
                send_notification(result_msg)
            return

    print("타임아웃 — 감시 종료")


# ── Test ───────────────────────────────────────────────────────────────────────

def test_mode(config: dict):
    print("=== 테스트 모드 ===\n")

    print("1. 큐 API 테스트...")
    queue = get_queue(config["queue_api"])
    print(f"   현재 등록 인원: {len(queue)}명")

    print("\n2. 날씨 API 테스트...")
    from weather import is_weather_good, get_next_saturday
    good, prob = is_weather_good(config)
    print(f"   토요일 강수확률: {prob}% → {'등록 진행 ✅' if good else '등록 스킵 ⛔'}")

    print("\n3. 등록 시뮬레이션 (dry-run)...")
    run_pipeline(config, dry_run=True)

    print("\n✅ 모든 테스트 완료")


if __name__ == "__main__":
    config = load_config()

    if "--test" in sys.argv:
        test_mode(config)
    elif "--dry-run" in sys.argv:
        run_pipeline(config, dry_run=True)
    else:
        watch_site(config)
