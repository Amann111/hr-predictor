# weather.py

import requests

WEATHER_API_KEY = "1f520944434ebb7bec7c4c10dcae7e72"  # your API key

BALLPARK_LOCATIONS = {
    "coors field": (39.7562, -104.9942),
    "yankee stadium": (40.8296, -73.9262),
    "fenway park": (42.3467, -71.0972),
    "oracle park": (37.7786, -122.3893),
    "wrigley field": (41.9484, -87.6553),
    "great american ball park": (39.0972, -84.5073),
    "tropicana field": (27.7683, -82.6534)
}

def get_weather(ballpark):
    lat, lon = BALLPARK_LOCATIONS.get(ballpark.lower(), (0, 0))
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=imperial"
    try:
        r = requests.get(url)
        data = r.json()
        wind = data['wind']['speed']
        temp = data['main']['temp']
        return wind, temp
    except:
        return 10, 75  # default fallback
