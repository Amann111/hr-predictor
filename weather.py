# STEP 1: Create a new file in your repo called 'weather.py' and paste this code:

import requests

WEATHER_API_KEY = "1f520944434ebb7bec7c4c10dcae7e72"

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
        return 10, 75  # default fallback values


# STEP 2: Open your app.py and update it
# - Add this import to the top:
from weather import get_weather

# - Replace the Wind and Temp sliders with this block:
st.sidebar.header("🔧 Settings")
pitcher_boost = st.sidebar.slider("Pitcher HR Boost (0 = elite, 10 = HR-prone)", 0, 10, 5)
ballpark = st.sidebar.selectbox("Ballpark", list(PARK_HR_FACTORS.keys()))

use_live_weather = st.sidebar.checkbox("🌦️ Use Live Weather")
if use_live_weather:
    wind, temp = get_weather(ballpark)
    st.sidebar.write(f"Live Wind: {wind} mph")
    st.sidebar.write(f"Live Temp: {temp}°F")
else:
    wind = st.sidebar.slider("Wind (mph)", 0, 30, 10)
    temp = st.sidebar.slider("Temperature (°F)", 40, 100, 75)


# STEP 3: Add Pitcher Input to Sidebar
pitcher_name = st.sidebar.text_input("Pitcher Name (Optional)")


# STEP 4: Modify scoring in get_hr_score()
# Inside get_hr_score(), after calculating `score`, add:
if pitcher_name:
    score *= 1.10  # Placeholder for now (add real stats later)


# STEP 5: Betting Odds Placeholder
# After results are shown, add:
ODDS_LOOKUP = {
    "aaron judge": 5.0,
    "shohei ohtani": 6.5,
    "mookie betts": 7.0
}

for name, score in results:
    odds = ODDS_LOOKUP.get(name.lower())
    if odds:
        st.write(f"🧩 {name} HR Odds: +{int(odds * 100)}")


# STEP 6: Save All Changes and Push to GitHub
# Click Commit & Push in VS Code top left.

# STEP 7: Streamlit Will Auto-Redeploy
# Go to your app URL and refresh.
# Done 🚀
