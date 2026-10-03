#!/usr/bin/env python3
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime

args = [a.strip() for a in sys.argv[1:] if a.strip()] or ["Arlington", "Texas"]
city, region = args[0], " ".join(args[1:]).lower()

try:
    geo_url = ("https://geocoding-api.open-meteo.com/v1/search?count=10&name="
               + urllib.parse.quote(city))
    with urllib.request.urlopen(geo_url, timeout=30) as response:
        results = json.loads(response.read().decode()).get("results", [])
    places = [p for p in results
              if region in (p.get("admin1", "") + " " + p["country"]).lower()]
    if not places:
        raise ValueError("city not found: " + city + " " + region)
    place = places[0]

    url = ("https://api.open-meteo.com/v1/forecast"
           f"?latitude={place['latitude']}&longitude={place['longitude']}"
           "&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
           "&timezone=auto")
    if place["country_code"] == "US":
        url += "&temperature_unit=fahrenheit&wind_speed_unit=mph"
    with urllib.request.urlopen(url, timeout=30) as response:
        data = json.loads(response.read().decode())

    current, units = data["current"], data["current_units"]
    print("-" * 32)
    where = [place["name"], place.get("admin1"), place["country"]]
    print("Weather for", ", ".join(filter(None, where)))
    print("Time:", datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("Temperature:", current["temperature_2m"], units["temperature_2m"])
    print("Humidity:", current["relative_humidity_2m"], units["relative_humidity_2m"])
    print("Wind Speed:", current["wind_speed_10m"], units["wind_speed_10m"].replace("mp/h", "mph"))
    print("-" * 32)

except Exception as error:
    print("Weather report failed:", error)
    sys.exit(1)
