#!/usr/bin/env python3
"""
Waybar custom weather module using Google Weather API.

Prints current conditions for Waybar as JSON.

Requirements:
    - Google Cloud project with Weather API enabled
    - API key with Weather API access, in $GOOGLE_API_KEY
"""

import argparse
import html
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from http.client import HTTPResponse
from typing import cast

API_URL = "https://weather.googleapis.com/v1/currentConditions:lookup"

# Weather condition to icon mapping
WEATHER_ICONS = {
    "CLEAR": "☀️",
    "MOSTLY_CLEAR": "🌤️",
    "PARTLY_CLOUDY": "⛅",
    "MOSTLY_CLOUDY": "☁️",
    "CLOUDY": "☁️",
    "WINDY": "🌬️",
    "WIND_AND_RAIN": "🌧️💨",
    "CHANCE_OF_SHOWERS": "🌦️",
    "SCATTERED_SHOWERS": "🌦️",
    "RAIN_SHOWERS": "🌧️",
    "HEAVY_RAIN_SHOWERS": "🌧️☔",
    "LIGHT_TO_MODERATE_RAIN": "🌦️",
    "MODERATE_TO_HEAVY_RAIN": "🌧️",
    "LIGHT_RAIN": "🌦️",
    "RAIN_PERIODICALLY_HEAVY": "🌧️☔",
    "LIGHT_SNOW_SHOWERS": "🌨️",
    "CHANCE_OF_SNOW_SHOWERS": "🌨️",
    "SCATTERED_SNOW_SHOWERS": "🌨️",
    "SNOW_SHOWERS": "🌨️",
    "HEAVY_SNOW_SHOWERS": "❄️🌨️",
    "LIGHT_TO_MODERATE_SNOW": "🌨️",
    "MODERATE_TO_HEAVY_SNOW": "❄️",
    "SNOWSTORM": "🌨️💨",
    "SNOW_PERIODICALLY_HEAVY": "🌨️❄️",
    "HEAVY_SNOW_STORM": "❄️🌬️",
    "BLOWING_SNOW": "🌨️💨",
    "RAIN_AND_SNOW": "🌧️🌨️",
    "HAIL_SHOWERS": "🌧️🧊",
    "THUNDERSHOWER": "⛈️",
    "LIGHT_THUNDERSTORM_RAIN": "🌦️⚡",
    "SCATTERED_THUNDERSTORMS": "🌩️",
    "HEAVY_THUNDERSTORM": "⛈️⚡",
    "LIGHT_RAIN_SHOWERS": "🌦️",
    "RAIN": "🌧️",
    "HEAVY_RAIN": "🌧️☔",
    "SNOW": "🌨️",
    "LIGHT_SNOW": "🌨️",
    "HEAVY_SNOW": "❄️",
    "THUNDERSTORM": "⛈️",
    "HAIL": "🌨️🧊",
    "DEFAULT": "🌡️",
}

UNITS = {
    "CELSIUS": "°C",
    "FAHRENHEIT": "°F",
    "MILES": " mi",
    "KILOMETERS": " km",
    "KILOMETERS_PER_HOUR": " km/h",
    "MILES_PER_HOUR": " mph",
    "METERS_PER_SECOND": " m/s",
    "MILLIMETERS": " mm",
    "INCHES": " in",
}


class Args(argparse.Namespace):
    api_key: str | None = None
    latitude: str = ""
    longitude: str = ""
    units: str = "metric"


def dig(data: object, *keys: str) -> object:
    """Walk nested JSON objects; None if any key is missing."""
    for key in keys:
        if not isinstance(data, dict):
            return None
        data = cast("dict[str, object]", data).get(key)
    return data


def unit(data: object, *keys: str) -> str:
    """Short unit suffix for the API unit at keys; "" if absent."""
    name = dig(data, *keys)
    return UNITS.get(name, f" {name}") if isinstance(name, str) else ""


def get_icon(condition_type: str, is_daytime: bool) -> str:
    """Return icon for condition, adjusted for day/night."""
    icon = WEATHER_ICONS.get(condition_type.upper(), WEATHER_ICONS["DEFAULT"])
    if not is_daytime and icon in ("☀️", "🌤️"):
        icon = "🌙"
    return icon


def show(value: object, suffix: str = "", prefix: str = "") -> str | None:
    return None if value is None else f"{prefix}{value}{suffix}"


def fetch_weather(api_key: str, latitude: str, longitude: str, units: str) -> object:
    """Current conditions JSON; raises OSError or ValueError on failure."""
    query = urllib.parse.urlencode(
        {
            "location.latitude": latitude,
            "location.longitude": longitude,
            "unitsSystem": units.upper(),
        }
    )
    # key in a header, not the URL, so it never appears in error messages
    request = urllib.request.Request(
        f"{API_URL}?{query}", headers={"X-Goog-Api-Key": api_key}
    )
    with cast(HTTPResponse, urllib.request.urlopen(request, timeout=10)) as response:
        return cast(object, json.load(response))


def format_output(data: object) -> dict[str, str]:
    """Format weather data for Waybar output."""
    temp = dig(data, "temperature", "degrees")
    if temp is None:
        return {"text": "n/a", "tooltip": "Temperature unavailable"}

    t = unit(data, "temperature", "unit")
    condition_type = dig(data, "weatherCondition", "type")
    icon = get_icon(
        condition_type if isinstance(condition_type, str) else "DEFAULT",
        dig(data, "isDaytime") is not False,
    )
    condition = dig(data, "weatherCondition", "description", "text") or "Unknown"
    history = dig(data, "currentConditionsHistory")
    wind = dig(data, "wind")
    precip = dig(data, "precipitation")
    precip_type = str(dig(precip, "probability", "type") or "precipitation")

    tooltip = [f"<b><span size='large'>{icon} {html.escape(str(condition))}</span></b>"]

    def section(title: str, *rows: tuple[str, str | None]) -> None:
        """Add a titled block; rows with None text (field absent) are skipped."""
        lines = [f"  {k}<tt>{html.escape(v)}</tt>" for k, v in rows if v is not None]
        if lines:
            tooltip.extend([f"\n<b>{title}</b>", *lines])

    # 0 is a real value everywhere except gusts and thunder, where it's noise
    gust = dig(wind, "gust", "value") or None
    thunder = dig(data, "thunderstormProbability") or None
    chance = f"% of {precip_type.replace('_', ' ').lower()}"

    section(
        "🌡️ Temperature",
        ("Current:\t", show(temp, t)),
        ("Feels Like:\t", show(dig(data, "feelsLikeTemperature", "degrees"), t)),
        ("High:\t\t", show(dig(history, "maxTemperature", "degrees"), t)),
        ("Low:\t\t", show(dig(history, "minTemperature", "degrees"), t)),
        ("Wind Chill:\t", show(dig(data, "windChill", "degrees"), t)),
        ("Heat Index:\t", show(dig(data, "heatIndex", "degrees"), t)),
    )
    section(
        "🌬️ Atmosphere",
        ("Humidity:\t", show(dig(data, "relativeHumidity"), "%")),
        ("Dew Point:\t", show(dig(data, "dewPoint", "degrees"), t)),
        ("Pressure:\t", show(dig(data, "airPressure", "meanSeaLevelMillibars"), " mb")),
        (
            "Visibility:\t",
            show(dig(data, "visibility", "distance"), unit(data, "visibility", "unit")),
        ),
        ("Cloud Cover:\t", show(dig(data, "cloudCover"), "%")),
        ("UV Index:\t", show(dig(data, "uvIndex"))),
    )
    section(
        "💨 Wind",
        ("Speed:\t\t", show(dig(wind, "speed", "value"), unit(wind, "speed", "unit"))),
        ("Gusts:\t\t", show(gust, unit(wind, "gust", "unit"), "up to ")),
    )
    section(
        "💧 Precipitation",
        ("Chance:\t", show(dig(precip, "probability", "percent"), chance)),
        (
            "Amount (1hr):\t",
            show(dig(precip, "qpf", "quantity"), unit(precip, "qpf", "unit")),
        ),
        (
            "Snow (1hr):\t",
            show(dig(precip, "snowQpf", "quantity"), unit(precip, "snowQpf", "unit")),
        ),
        ("Thunder:\t", show(thunder, "% chance")),
    )
    tooltip.append(f"\n<i><small>Data pulled:\t{time.strftime('%H:%M:%S')}</small></i>")

    try:
        text = f"{icon} {temp:.0f}{t}"
    except (TypeError, ValueError):  # non-numeric temperature
        text = f"{icon} {temp}{t}"
    return {"text": text, "tooltip": "\n".join(tooltip), "class": "weather"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Google Weather for Waybar.")

    # prefer $GOOGLE_API_KEY: argv is visible to other processes
    _ = parser.add_argument("--api-key", help="default: $GOOGLE_API_KEY")
    _ = parser.add_argument("--latitude", required=True)
    _ = parser.add_argument("--longitude", required=True)
    _ = parser.add_argument(
        "--units", type=str.lower, choices=["metric", "imperial"], default="metric"
    )

    args = parser.parse_args(namespace=Args())
    api_key = args.api_key or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        parser.error("--api-key or $GOOGLE_API_KEY is required")

    try:
        data = fetch_weather(api_key, args.latitude, args.longitude, args.units)
    except (OSError, ValueError) as e:
        error = {
            "text": "❌",
            "tooltip": html.escape(f"Network/API error: {e}"),
            "class": "error",
        }
        print(json.dumps(error))
        sys.exit(1)
    print(json.dumps(format_output(data)))


if __name__ == "__main__":
    main()
