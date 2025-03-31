import streamlit as st
import pandas as pd
from pybaseball import statcast_batter, playerid_lookup
from datetime import datetime, timedelta

st.set_page_config(page_title="HR Predictor", layout="centered")

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

DEFAULT_PLAYERS = [
    "Aaron Judge", "Shohei Ohtani", "Juan Soto", "Mookie Betts", "Mike Trout"
]

def get_player_id(name):
    name = name.strip().lower()
    if name in PLAYER_ID_OVERRIDES:
        return PLAYER_ID_OVERRIDES[name]
    info = playerid_lookup(*name.strip().split())
    return info.iloc[0]["key_mlbam"] if not info.empty else None

def get_hr_stats(name):
    pid = get_player_id(name)
    if not pid:
        return {"Player": name, "Error": "Not found"}
    end = datetime.now()
    start = end - timedelta(days=30)
    df = statcast_batter(start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'), pid)
    if df.empty or len(df) < 5:
        return {"Player": name, "Error": "No recent data"}

    fb = df[df['launch_angle'] > 10]
    barrels = df[df['barrel'] == 1] if 'barrel' in df.columns else pd.DataFrame()
    pulled = df[df['hc_x'] < 125]
    barrel_pct = len(barrels) / len(df) * 100 if len(df) else 0
    fb_pct = len(fb) / len(df) * 100 if len(df) else 0
    pull_pct = len(pulled) / len(df) * 100 if len(df) else 0
    ev = fb['exit_velocity'].mean() if 'exit_velocity' in fb.columns and not fb.empty else 0
    return {
        "Player": name,
        "Barrel%": round(barrel_pct, 2),
        "FB%": round(fb_pct, 2),
        "Pull%": round(pull_pct, 2),
        "EV_FB_LD": round(ev, 2)
    }

def compute_hr_score(row, pitcher_boost, park_boost, weather_boost):
    return round(
        row["Barrel%"] * 0.25 +
        row["FB%"] * 0.15 +
        row["Pull%"] * 0.10 +
        row["EV_FB_LD"] * 0.15 +
        pitcher_boost * 0.20 +
        park_boost * 0.10 +
        weather_boost * 0.05,
        2
    )

st.title("⚾ Home Run Predictor")

col1, col2 = st.columns(2)
pitcher_boost = col1.slider("Pitcher HR Boost (0 = elite, 10 = HR-prone)", 0, 10, 5)
ballpark = col2.selectbox("Ballpark", list(PARK_HR_FACTORS.keys()))
wind = st.slider("Wind (mph)", 0, 30, 10)
temp = st.slider("Temperature (°F)", 40, 100, 75)

if st.button("Run Prediction"):
    park_boost = PARK_HR_FACTORS.get(ballpark.lower(), 1.0) * 10
    weather_boost = (wind * 0.5) + ((temp - 70) * 0.25)

    st.subheader("Predicted HR Scores")
    results = []
    for name in DEFAULT_PLAYERS:
        row = get_hr_stats(name)
        if "Error" not in row:
            row["HR Score"] = compute_hr_score(row, pitcher_boost, park_boost, weather_boost)
        else:
            row["Barrel%"] = row["FB%"] = row["Pull%"] = row["EV_FB_LD"] = row["HR Score"] = 0
        results.append(row)

    st.dataframe(pd.DataFrame(results).set_index("Player"))

st.markdown("### 🔎 Look Up a Player")
lookup_name = st.text_input("Player Name (e.g., Matt Olson)")
if st.button("Look Up"):
    row = get_hr_stats(lookup_name)
    if "Error" in row:
        st.error(row["Error"])
    else:
        st.json(row)
