#!/usr/bin/env python3
"""
Waybar custom weather module using Google Weather API.

Fetches and formats weather data for Waybar as JSON.

Requirements:
    - Google Cloud project with Weather API enabled
    - API key with Weather API access
    - pip install requests click
"""

import json
import sys
import time

import click
import requests

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


def print_error(text: str, tooltip: str, exit_code: int = 1):
    """Prints a JSON error message for Waybar and exits."""
    output = {"text": text, "tooltip": tooltip, "class": "error"}
    print(json.dumps(output))
    sys.exit(exit_code)


def get_icon(condition_type: str, is_daytime: bool) -> str:
    """Return icon for condition, adjusted for day/night."""
    icon = WEATHER_ICONS.get(condition_type.upper(), WEATHER_ICONS["DEFAULT"])

    # Basic day/night tweak
    if not is_daytime and icon in ("☀️", "🌤️"):
        icon = "🌙"
    return icon


def format_unit(unit: str) -> str:
    """Convert metric unit to short form."""
    unit_map = {
        "CELSIUS": "°C",
        "FAHRENHEIT": "°F",
        "MILES": "mi",
        "KILOMETERS": "km",
        "KILOMETERS_PER_HOUR": "km/h",
        "MILES_PER_HOUR": "mph",
        "METERS_PER_SECOND": "m/s",
        "MILLIMETERS": "mm",
        "INCHES": " in",
    }
    return unit_map.get(unit, unit)


def fetch_weather(api_key, latitude, longitude, units):
    """Fetch weather data from Google Weather API."""
    url = "https://weather.googleapis.com/v1/currentConditions:lookup"

    params = {
        "key": api_key,
        "location.latitude": latitude,
        "location.longitude": longitude,
        "unitsSystem": units.upper(),
        "alt": "json",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print_error("❌", f"Network/API error: {e}")
    except Exception as e:
        print_error("❌", f"Unexpected error: {e}")


def format_output(data):
    """Format weather data for Waybar output."""
    try:
        # Extract temperature data
        temp = data.get("temperature", {}).get("degrees")
        if temp is None:
            return {"text": "n/a", "tooltip": "Temperature unavailable"}

        unit = data.get("temperature", {}).get("unit")
        unit_char = format_unit(unit)

        # Extract condition data
        condition = data.get("weatherCondition", {})
        condition_text = condition.get("description", {}).get("text", "Unknown")
        condition_type = condition.get("type", "DEFAULT")
        is_daytime = data.get("isDaytime", True)
        icon = get_icon(condition_type, is_daytime)

        # Format main text
        text = f"{icon} {temp:.0f}{unit_char}"

        # Build Tooltip
        tooltip = []
        tooltip.append(f"<b><span size='large'>{icon} {condition_text}</span></b>")

        # Temperature section
        tooltip.append("\n<b>🌡️ Temperature</b>")
        tooltip.append(f"  Current:\t<tt>{temp}{unit_char}</tt>")

        if feels_like := data.get("feelsLikeTemperature", {}).get("degrees"):
            tooltip.append(f"  Feels Like:\t<tt>{feels_like}{unit_char}</tt>")

        if history := data.get("currentConditionsHistory"):
            if max_temp := history.get("maxTemperature", {}).get("degrees"):
                tooltip.append(f"  High:\t\t<tt>{max_temp}{unit_char}</tt>")

            if min_temp := history.get("minTemperature", {}).get("degrees"):
                tooltip.append(f"  Low:\t\t<tt>{min_temp:.1f}{unit_char}</tt>")

        if wind_chill := data.get("windChill", {}).get("degrees"):
            tooltip.append(f"  Wind Chill:\t<tt>{wind_chill}{unit_char}</tt>")

        if heat_index := data.get("heatIndex", {}).get("degrees"):
            tooltip.append(f"  Heat Index:\t<tt>{heat_index}{unit_char}</tt>")

        # Atmosphere Section
        tooltip.append("\n<b>🌬️ Atmosphere</b>")

        if humidity := data.get("relativeHumidity"):
            tooltip.append(f"  Humidity:\t<tt>{humidity}%</tt>")

        if dew_point := data.get("dewPoint", {}).get("degrees"):
            tooltip.append(f"  Dew Point:\t<tt>{dew_point}{unit_char}</tt>")

        if pressure := data.get("airPressure", {}).get("meanSeaLevelMillibars"):
            tooltip.append(f"  Pressure:\t<tt>{pressure} mb</tt>")

        if visibility := data.get("visibility", {}).get("distance"):
            vis_unit = format_unit(data.get("visibility", {}).get("unit"))
            tooltip.append(f"  Visibility:\t<tt>{visibility} {vis_unit}</tt>")

        if cloud_cover := data.get("cloudCover"):
            tooltip.append(f"  Cloud Cover: <tt>{cloud_cover}%</tt>")

        if uv_index := data.get("uvIndex"):
            tooltip.append(f"  UV Index:\t<tt>{uv_index}</tt>")

        # Wind Section
        if wind := data.get("wind"):
            tooltip.append("\n<b>💨 Wind</b>")

            if speed := wind.get("speed", {}).get("value"):
                speed_unit = format_unit(wind.get("speed", {}).get("unit"))
                tooltip.append(f"  Speed:\t\t<tt>{speed} {speed_unit}</tt>")

            if gust := wind.get("gust", {}).get("value"):
                gust_unit = format_unit(wind.get("gust", {}).get("unit"))
                tooltip.append(f"  Gusts:\t\t<tt>up to {gust} {gust_unit}</tt>")

        # Precipitation Section
        tooltip.append("\n<b>💧 Precipitation</b>")
        precip = data.get("precipitation", {})
        if prob := precip.get("probability", {}).get("percent"):
            prob_type = (
                precip.get("probability", {}).get("type").replace("_", " ").lower()
            )
            tooltip.append(f"  Chance:\t<tt>{prob}% of {prob_type}</tt>")

            if qpf := precip.get("qpf", {}).get("quantity"):
                qpf_unit = format_unit(precip.get("qpf", {}).get("unit"))
                tooltip.append(f"  Amount (1hr):\t<tt>{qpf}{qpf_unit}</tt>")

            if qpf_snow := precip.get("snowQpf", {}).get("quantity"):
                qpf_snow_unit = format_unit(precip.get("snowQpf", {}).get("unit"))
                tooltip.append(f"  Snow (1hr):\t<tt>{qpf_snow}{qpf_snow_unit}</tt>")

        if thunder_prob := data.get("thunderstormProbability"):
            tooltip.append(f"  Thunder:\t<tt>{thunder_prob}% chance</tt>")

        # Timestamp - when data was pulled
        current_time = time.strftime("%H:%M:%S")
        tooltip.append(f"\n<i><small>Data pulled:\t{current_time}</small></i>")

        final_tooltip = "\n".join(tooltip)
        return {"text": text, "tooltip": final_tooltip, "class": "weather"}

    except (KeyError, TypeError, AttributeError) as e:
        return {"text": "❓", "tooltip": f"Error parsing weather data: {str(e)}"}


@click.command()
@click.option(
    "--api-key",
    required=True,
    envvar="GOOGLE_API_KEY",
    help="Google API key (can also set GOOGLE_API_KEY env var)",
)
@click.option("--latitude", required=True, help="Latitude coordinate")
@click.option("--longitude", required=True, help="Longitude coordinate")
@click.option(
    "--units",
    type=click.Choice(["metric", "imperial"], case_sensitive=False),
    default="metric",
    help="Unit system (metric or imperial)",
)
def main(api_key, latitude, longitude, units):
    """Fetch and display weather data for Waybar."""
    weather_data = fetch_weather(api_key, latitude, longitude, units)
    output = format_output(weather_data)
    print(json.dumps(output))


if __name__ == "__main__":
    main()
