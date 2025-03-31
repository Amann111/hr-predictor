import streamlit as st
import pandas as pd
from pybaseball import statcast_batter, playerid_lookup
from datetime import datetime, timedelta

st.set_page_config(page_title="HR Predictor", layout="centered")
st.title("⚾ Home Run Predictor")

# Sample players and overrides
PLAYER_ID_OVERRIDES = {
    "shohei ohtani": 660271,
    "aaron judge": 592450,
    "juan soto": 665742,
    "mookie betts": 605141,
    "mike trout": 545361
}

PARK_HR_FACTORS = {
    "coors field": 1.35,
    "great american ball park": 1.25,
    "yankee stadium": 1.20,
    "fenway park": 1.10,
    "wrigley field": 1.05,
    "oracle park": 0.85,
    "tropicana field": 0.80
}

DEFAULT_PLAYERS = ["Aaron Judge", "Shohei Ohtani", "Juan Soto", "Mookie Betts", "Mike Trout"]

def get_player_id(name):
    name = name.strip().lower()
    if name in PLAYER_ID_OVERRIDES:
        return PLAYER_ID_OVERRIDES[name]
    try:
        result = playerid_lookup(*name.title().split())
        return result['key_mlbam'].iloc[0]
    except:
        return None

def get_hr_score(player_id, pitcher_boost, park_factor, wind, temp):
    try:
        end_date = datetime.today()
        start_date = end_date - timedelta(days=365)
        data = statcast_batter(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), player_id)
        flyballs = data[data['launch_angle'] > 10]
        if flyballs.empty:
            return 0
        fb_ld = flyballs['launch_speed'].mean()
        barrel = data['barrel'].mean() if 'barrel' in data.columns else 0
        pull = data['pull'].mean() if 'pull' in data.columns else 0
        fb = data['launch_angle'].mean()
        score = (barrel * 2 + fb + pull + (fb_ld / 5)) * park_factor
        score *= 1 + (pitcher_boost / 20)
        score *= 1 + (wind / 100)
        score *= 1 + ((temp - 70) / 100)
        return round(score, 2)
    except:
        return 0

# Sidebar Inputs
st.sidebar.header("⚙️ Settings")
pitcher_boost = st.sidebar.slider("Pitcher HR Boost (0 = elite, 10 = HR-prone)", 0, 10, 5)
ballpark = st.sidebar.selectbox("Ballpark", list(PARK_HR_FACTORS.keys()))
wind = st.sidebar.slider("Wind (mph)", 0, 30, 10)
temp = st.sidebar.slider("Temperature (°F)", 40, 100, 75)

# Main Prediction Button
if st.button("Run Prediction"):
    park_boost = PARK_HR_FACTORS[ballpark]
    results = []
    for name in DEFAULT_PLAYERS:
        pid = get_player_id(name)
        if pid:
            score = get_hr_score(pid, pitcher_boost, park_boost, wind, temp)
            results.append((name, score))
    results = sorted(results, key=lambda x: x[1], reverse=True)
    st.subheader("🔮 Predicted HR Scores")
    st.table(pd.DataFrame(results, columns=["Player", "HR Score"]))
