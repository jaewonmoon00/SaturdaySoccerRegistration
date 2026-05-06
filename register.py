import requests
import json
import sys


def get_registered_names(queue_api: str) -> set[str]:
    resp = requests.get(queue_api, timeout=10)
    resp.raise_for_status()
    return {entry["name"].lower() for entry in resp.json()["queue"]}


def register_names(config: dict, dry_run: bool = False) -> list[dict]:
    names = config["names"]
    join_api = config["registration_api"]
    queue_api = config["queue_api"]

    already_registered = get_registered_names(queue_api)
    results = []

    for name in names:
        if name.lower() in already_registered:
            results.append({"name": name, "status": "skipped", "reason": "이미 등록됨"})
            print(f"⏭️  {name} - 이미 등록됨, 스킵")
            continue

        if dry_run:
            results.append({"name": name, "status": "dry_run"})
            print(f"🔍 [dry-run] {name} - 등록 예정")
            continue

        resp = requests.post(join_api, json={"name": name}, timeout=10)
        if resp.status_code == 201:
            position = resp.json()["position"]
            results.append({"name": name, "status": "registered", "position": position})
            print(f"✅ {name} - {position}번으로 등록 완료")
        else:
            results.append({"name": name, "status": "error", "code": resp.status_code})
            print(f"❌ {name} - 등록 실패 (HTTP {resp.status_code})")

    return results


def format_result_message(results: list[dict], precipitation_prob: int) -> str:
    registered = [r for r in results if r["status"] == "registered"]
    skipped = [r for r in results if r["status"] == "skipped"]

    lines = [f"⚽ 축구 자동 신청 완료! (토요일 강수확률: {precipitation_prob}%)"]

    if registered:
        entries = ", ".join(f"{r['name']}({r['position']}번)" for r in registered)
        lines.append(f"✅ 신규 등록: {entries}")

    if skipped:
        names = ", ".join(r["name"] for r in skipped)
        lines.append(f"⏭️ 이미 등록됨: {names}")

    return "\n".join(lines)


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    with open("config.json") as f:
        config = json.load(f)
    results = register_names(config, dry_run=dry_run)
    print("\n결과:", json.dumps(results, ensure_ascii=False, indent=2))
