#!/usr/bin/env python3
"""
Weather CLI Application
-----------------------
A command-line application that demonstrates:
1. Using the 'requests' library.
2. Making GET and POST requests.
3. Parsing JSON responses.
4. Handling API responses and error states gracefully.

It fetches real-time weather details for any city using the Open-Meteo API (GET),
and simulates uploading search statistics to a logging server using httpbin (POST).
"""

import sys
import argparse
from datetime import datetime
import requests

# Reconfigure stdout/stderr to use UTF-8 to prevent UnicodeEncodeError on Windows terminals
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# ANSI Color Codes for premium CLI appearance
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Map of WMO weather codes to descriptive text and emojis
# https://open-meteo.com/en/docs
WMO_CODES = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Fog", "🌫️"),
    48: ("Depositing rime fog", "🌫️"),
    51: ("Light drizzle", "🌧️"),
    53: ("Moderate drizzle", "🌧️"),
    55: ("Dense drizzle", "🌧️"),
    56: ("Light freezing drizzle", "🌧️❄️"),
    57: ("Dense freezing drizzle", "🌧️❄️"),
    61: ("Slight rain", "🌧️"),
    63: ("Moderate rain", "🌧️"),
    65: ("Heavy rain", "🌧️"),
    66: ("Light freezing rain", "🌧️❄️"),
    67: ("Heavy freezing rain", "🌧️❄️"),
    71: ("Slight snow fall", "❄️"),
    73: ("Moderate snow fall", "❄️"),
    75: ("Heavy snow fall", "❄️"),
    77: ("Snow grains", "❄️"),
    80: ("Slight rain showers", "🌦️"),
    81: ("Moderate rain showers", "🌦️"),
    82: ("Violent rain showers", "🌦️"),
    85: ("Slight snow showers", "❄️"),
    86: ("Heavy snow showers", "❄️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with slight hail", "⛈️🌨️"),
    99: ("Thunderstorm with heavy hail", "⛈️🌨️")
}

def get_weather_desc(code):
    """Map WMO code to description and emoji."""
    return WMO_CODES.get(code, ("Unknown weather condition", "❓"))

def geocode_city(city_name):
    """
    Geocodes a city name to coordinates (latitude, longitude) using Open-Meteo's Geocoding API.
    Demonstrates: GET request, query parameters, handling JSON parsing, response validation.
    """
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": city_name,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    print(f"\n{BLUE}🔍 Searching for city '{city_name}'...{RESET}")
    
    try:
        # Perform the GET request with a 10-second timeout
        response = requests.get(url, params=params, timeout=10)
        
        # Raise HTTPError if status code is 4xx or 5xx
        response.raise_for_status()
        
        # Parse the JSON response
        data = response.json()
        
        results = data.get("results")
        if not results or len(results) == 0:
            return None
        
        city_data = results[0]
        return {
            "name": city_data.get("name"),
            "country": city_data.get("country", "Unknown"),
            "admin1": city_data.get("admin1", ""),  # State/province if available
            "latitude": city_data.get("latitude"),
            "longitude": city_data.get("longitude")
        }
        
    except requests.exceptions.Timeout:
        print(f"{RED}❌ Error: The geocoding request timed out. Please check your connection.{RESET}")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"{RED}❌ Error: Failed to connect to the geocoding service. Check your internet connection.{RESET}")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"{RED}❌ Error: Geocoding server returned an error: {e}{RESET}")
        sys.exit(1)
    except ValueError:
        print(f"{RED}❌ Error: Failed to parse geocoding response JSON.{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{RED}❌ Error: An unexpected error occurred: {e}{RESET}")
        sys.exit(1)

def fetch_weather(lat, lon):
    """
    Fetches current weather data for given coordinates using Open-Meteo's Forecast API.
    Demonstrates: GET request, path/query parameters, parsing nested JSON keys.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,weather_code",
        "timezone": "auto"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        current = data.get("current")
        if not current:
            print(f"{RED}❌ Error: Weather data format is invalid.{RESET}")
            return None
            
        return {
            "temperature_c": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "weather_code": current.get("weather_code")
        }
        
    except requests.exceptions.Timeout:
        print(f"{RED}❌ Error: The weather forecast request timed out.{RESET}")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"{RED}❌ Error: Failed to connect to the weather service.{RESET}")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"{RED}❌ Error: Weather service returned an error: {e}{RESET}")
        sys.exit(1)
    except ValueError:
        print(f"{RED}❌ Error: Failed to parse weather response JSON.{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{RED}❌ Error: An unexpected error occurred: {e}{RESET}")
        sys.exit(1)

def log_search_to_api(city_info, weather_info):
    """
    Logs the weather search details to httpbin.org/post.
    Demonstrates: POST request, sending JSON payload, parsing the server response echo.
    """
    url = "https://httpbin.org/post"
    
    # Construct payload representing search details
    payload = {
        "timestamp": datetime.now().isoformat(),
        "application": "Weather CLI App",
        "search_city": city_info["name"],
        "country": city_info["country"],
        "coordinates": {
            "lat": city_info["latitude"],
            "lon": city_info["longitude"]
        },
        "weather_data": {
            "temp_c": weather_info["temperature_c"],
            "humidity_percent": weather_info["humidity"],
            "weather_code": weather_info["weather_code"]
        }
    }
    
    print(f"\n{BLUE}📤 Uploading search report to logging server (POST requests.post)...{RESET}")
    
    try:
        # Perform POST request containing JSON payload
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        # httpbin returns the posted JSON in the 'json' key of response
        response_data = response.json()
        server_received_json = response_data.get("json", {})
        
        print(f"{GREEN}✅ Success! Server acknowledged receipt of the weather log.{RESET}")
        print(f"{CYAN}📡 Server Echo Details:{RESET}")
        print(f"  • Log Timestamp: {YELLOW}{server_received_json.get('timestamp')}{RESET}")
        print(f"  • Uploaded City: {YELLOW}{server_received_json.get('search_city')}{RESET}")
        print(f"  • Logged Temp:   {YELLOW}{server_received_json.get('weather_data', {}).get('temp_c')} °C{RESET}")
        
    except requests.exceptions.RequestException as e:
        print(f"{RED}⚠️ Warning: Failed to upload log to server: {e}{RESET}")
    except ValueError:
        print(f"{RED}⚠️ Warning: Failed to parse server log response.{RESET}")

def display_weather_card(city_info, weather_info):
    """Displays a beautifully formatted terminal 'card' with the weather info."""
    celsius = weather_info["temperature_c"]
    fahrenheit = (celsius * 9/5) + 32
    humidity = weather_info["humidity"]
    code = weather_info["weather_code"]
    
    desc, emoji = get_weather_desc(code)
    
    location = f"{city_info['name']}"
    if city_info['admin1']:
        location += f", {city_info['admin1']}"
    location += f" ({city_info['country']})"
    
    border_len = max(len(location) + 6, 45)
    horizontal_border = "═" * border_len
    
    print(f"\n{GREEN}╔{horizontal_border}╗{RESET}")
    print(f"{GREEN}║{RESET}  {BOLD}{YELLOW}🌤️  WEATHER REPORT{RESET}" + " " * (border_len - 17) + f"{GREEN}║{RESET}")
    print(f"{GREEN}╠{horizontal_border}╣{RESET}")
    
    # Location line
    loc_padding = border_len - len(f"📍 Location: {location}") - 2
    print(f"{GREEN}║{RESET}  📍 Location: {BOLD}{CYAN}{location}{RESET}" + " " * loc_padding + f"{GREEN}║{RESET}")
    
    # Temp line
    temp_str = f"🌡️ Temperature: {celsius:.1f}°C ({fahrenheit:.1f}°F)"
    temp_padding = border_len - len(temp_str) - 2
    print(f"{GREEN}║{RESET}  {temp_str}" + " " * temp_padding + f"{GREEN}║{RESET}")
    
    # Humidity line
    hum_str = f"💧 Humidity:    {humidity}%"
    hum_padding = border_len - len(hum_str) - 2
    print(f"{GREEN}║{RESET}  {hum_str}" + " " * hum_padding + f"{GREEN}║{RESET}")
    
    # Condition line
    cond_str = f"{emoji} Condition:   {desc}"
    cond_padding = border_len - len(cond_str) - 2
    # Compensate for emoji length (multibyte/wide characters) in padding if needed
    # We add an extra space in print because emojis can display as double-wide in some terminals
    emoji_len_compensation = 1
    print(f"{GREEN}║{RESET}  {cond_str}" + " " * (cond_padding + emoji_len_compensation) + f"{GREEN}║{RESET}")
    
    # Coordinates line
    coord_str = f"🌐 Coordinates: Lat: {city_info['latitude']:.2f}, Lon: {city_info['longitude']:.2f}"
    coord_padding = border_len - len(coord_str) - 2
    print(f"{GREEN}║{RESET}  {coord_str}" + " " * coord_padding + f"{GREEN}║{RESET}")
    
    print(f"{GREEN}╚{horizontal_border}╝{RESET}\n")

def run_weather_app(city_name):
    """Coordinates search, fetch, display, and upload flow."""
    city_name = city_name.strip()
    if not city_name:
        print(f"{RED}❌ Error: City name cannot be empty.{RESET}")
        return
        
    city_info = geocode_city(city_name)
    if not city_info:
        print(f"{RED}❌ Error: Could not resolve city '{city_name}'. Please verify the spelling.{RESET}")
        return
        
    weather_info = fetch_weather(city_info["latitude"], city_info["longitude"])
    if not weather_info:
        print(f"{RED}❌ Error: Failed to fetch weather data for {city_info['name']}.{RESET}")
        return
        
    display_weather_card(city_info, weather_info)
    
    # Prompt user to log this request via POST
    # When arguments are passed from CLI directly, we can automatically log or ask
    response = input(f"Would you like to upload/log this search report to the server? (y/N): ").strip().lower()
    if response in ['y', 'yes']:
        log_search_to_api(city_info, weather_info)

def main():
    parser = argparse.ArgumentParser(
        description="Weather CLI Tool demonstrating GET/POST HTTP requests, JSON parsing, and error handling."
    )
    parser.add_argument(
        "city",
        nargs="?",
        type=str,
        help="Name of the city to check weather for."
    )
    args = parser.parse_args()

    # Title header
    print(f"{BOLD}{MAGENTA}============================================")
    print("      🌦️  WELCOME TO THE WEATHER CLI  🌦️")
    print(f"============================================{RESET}")

    if args.city is not None:
        # Run directly if city passed as CLI argument
        run_weather_app(args.city)
    else:
        # Run interactive loop if no city arguments provided
        try:
            while True:
                city = input(f"\n{BOLD}Enter city name (or type 'exit' to quit): {RESET}").strip()
                if not city:
                    continue
                if city.lower() == 'exit':
                    print(f"\n{YELLOW}Goodbye! ☀️{RESET}")
                    break
                run_weather_app(city)
        except KeyboardInterrupt:
            print(f"\n\n{YELLOW}Exiting Weather CLI. Goodbye! ☀️{RESET}")
            sys.exit(0)

if __name__ == "__main__":
    main()
