import streamlit as st
import pandas as pd
from pybaseball import statcast_batter, playerid_lookup
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from weather import get_weather

st.set_page_config(page_title="HR Predictor", layout="centered")
st.title("🏀 Home Run Predictor")

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

ODDS_LOOKUP = {
    "aaron judge": 5.0,
    "shohei ohtani": 6.5,
    "mookie betts": 7.0
}

# Sidebar
st.sidebar.header("⚙️ Settings")
pitcher_boost = st.sidebar.slider("Pitcher HR Boost (0 = elite, 10 = HR-prone)", 0, 10, 5)
ballpark = st.sidebar.selectbox("Ballpark", list(PARK_HR_FACTORS.keys()))
use_live_weather = st.sidebar.checkbox("🌦️ Use Live Weather")
pitcher_name = st.sidebar.text_input("Pitcher Name (Optional)")

if use_live_weather:
    wind, temp = get_weather(ballpark)
    st.sidebar.write(f"Live Wind: {wind} mph")
    st.sidebar.write(f"Live Temp: {temp}°F")
else:
    wind = st.sidebar.slider("Wind (mph)", 0, 30, 10)
    temp = st.sidebar.slider("Temperature (°F)", 40, 100, 75)

# Search Input
st.subheader("🔍 Search for Players")
player_input = st.text_input("Enter player names separated by commas", "Aaron Judge, Shohei Ohtani")

# Prediction Logic
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
            return 0, pd.DataFrame()
        fb_data = flyballs[['launch_speed', 'launch_angle']].dropna()
        barrel = data['barrel'].mean() if 'barrel' in data.columns else 0
        score = (barrel * 2 + fb_data['launch_angle'].mean() + (fb_data['launch_speed'].mean() / 5)) * park_factor
        score *= 1 + (pitcher_boost / 20)
        score *= 1 + (wind / 100)
        score *= 1 + ((temp - 70) / 100)
        if pitcher_name:
            score *= 1.10  # Adjust for pitcher manually
        return round(score, 2), fb_data
    except:
        return 0, pd.DataFrame()

if st.button("Run Prediction"):
    park_boost = PARK_HR_FACTORS[ballpark]
    names = [name.strip() for name in player_input.split(",") if name.strip()]
    results = []
    for name in names:
        pid = get_player_id(name)
        if pid:
            score, fb_data = get_hr_score(pid, pitcher_boost, park_boost, wind, temp)
            results.append({
                "Player": name.title(),
                "HR Score": score,
                "FB Launch Speed Avg": round(fb_data['launch_speed'].mean(), 2) if not fb_data.empty else 0,
                "FB Launch Angle Avg": round(fb_data['launch_angle'].mean(), 2) if not fb_data.empty else 0
            })

    df = pd.DataFrame(results)

    # Display Results
    st.subheader("🔮 Predicted HR Scores")
    st.dataframe(df.sort_values("HR Score", ascending=False), use_container_width=True)

    # Betting Odds
    for row in results:
        odds = ODDS_LOOKUP.get(row["Player"].lower())
        if odds:
            st.write(f"🧩 {row['Player']} HR Odds: +{int(odds * 100)}")

    # Download
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Results as CSV", data=csv, file_name="hr_predictions.csv", mime="text/csv")

    # Chart
    st.subheader("📊 Visualization")
    fig, ax = plt.subplots()
    sns.barplot(x="HR Score", y="Player", data=df.sort_values("HR Score"), ax=ax)
    ax.set_title("Predicted HR Score by Player")
    st.pyplot(fig)
