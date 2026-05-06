import requests
import json
from datetime import date, timedelta


def get_next_saturday() -> date:
    today = date.today()
    days_until_saturday = (5 - today.weekday()) % 7
    if days_until_saturday == 0:
        days_until_saturday = 7
    return today + timedelta(days=days_until_saturday)


def get_precipitation_probability(config: dict) -> int:
    weather_cfg = config["weather"]
    next_saturday = get_next_saturday()
    target_datetime = f"{next_saturday}T{weather_cfg['game_hour']:02d}:00"

    resp = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": weather_cfg["latitude"],
            "longitude": weather_cfg["longitude"],
            "hourly": "precipitation_probability",
            "timezone": weather_cfg["timezone"],
            "forecast_days": 7,
        },
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    times = data["hourly"]["time"]
    probs = data["hourly"]["precipitation_probability"]

    for i, t in enumerate(times):
        if t == target_datetime:
            return probs[i]

    raise ValueError(f"토요일 {weather_cfg['game_hour']}시 날씨 데이터를 찾을 수 없음 ({target_datetime})")


def is_weather_good(config: dict) -> tuple[bool, int]:
    prob = get_precipitation_probability(config)
    threshold = config["weather"]["max_precipitation_probability"]
    return prob <= threshold, prob


if __name__ == "__main__":
    with open("config.json") as f:
        config = json.load(f)
    good, prob = is_weather_good(config)
    next_saturday = get_next_saturday()
    print(f"토요일 ({next_saturday}) 오전 {config['weather']['game_hour']}시 Montreal 강수확률: {prob}%")
    print(f"날씨 상태: {'좋음 ✅' if good else '비 예보 ⛔'} (기준: {config['weather']['max_precipitation_probability']}%)")
