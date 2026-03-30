import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os
import requests
from datetime import datetime
import io

st.set_page_config(page_title="Economic Trends", layout="wide")

# ============ DEPENDENCY CHECK ============
def check_dependencies():
    try:
        import openpyxl
    except ImportError:
        st.error("❌ Missing dependency: openpyxl")
        st.info("👉 Install using: pip install openpyxl")
        st.stop()

# ============ 5-YEAR PLAN ============
five_year_plans = {
    1: {"years": (1951, 1956), "name": "1st Plan (1951-56)", "color": "#FF6B6B"},
    2: {"years": (1956, 1961), "name": "2nd Plan (1956-61)", "color": "#4ECDC4"},
    3: {"years": (1961, 1966), "name": "3rd Plan (1961-66)", "color": "#45B7D1"},
    4: {"years": (1969, 1974), "name": "4th Plan (1969-74)", "color": "#96CEB4"},
    5: {"years": (1974, 1979), "name": "5th Plan (1974-79)", "color": "#FFEAA7"},
    6: {"years": (1980, 1985), "name": "6th Plan (1980-85)", "color": "#DDA0DD"},
    7: {"years": (1985, 1990), "name": "7th Plan (1985-90)", "color": "#98D8C8"},
    8: {"years": (1992, 1997), "name": "8th Plan (1992-97)", "color": "#F7B787"},
    9: {"years": (1997, 2002), "name": "9th Plan (1997-2002)", "color": "#E27D5E"},
    10: {"years": (2002, 2007), "name": "10th Plan (2002-07)", "color": "#7FB77E"},
    11: {"years": (2007, 2012), "name": "11th Plan (2007-12)", "color": "#B1C2D9"},
    12: {"years": (2012, 2017), "name": "12th Plan (2012-17)", "color": "#C9A9A9"},
    "NITI": {"years": (2017, 2025), "name": "NITI Aayog (2017-25)", "color": "#9B59B6"}
}

def get_plan_color(year):
    for _, details in five_year_plans.items():
        if details["years"][0] <= year <= details["years"][1]:
            return details["color"]
    return "#808080"

def get_plan_name(year):
    for _, details in five_year_plans.items():
        if details["years"][0] <= year <= details["years"][1]:
            return details["name"]
    return "Outside Plan Period"

# ============ SESSION ============
for key, default in {
    "current_page": "home",
    "selected_variable": None,
    "selected_scheme": None,
    "edit_scheme": None,
    "show_details": None
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ============ DATA LOADER ============
@st.cache_data(ttl=300)
def load_data():
    check_dependencies()

    url = "https://raw.githubusercontent.com/davidotrainy-sudo/indian-economy-ugcnet-schemes-app/main/economy_data.xlsx"

    try:
        st.info("📥 Loading data from GitHub...")
        res = requests.get(url)

        if res.status_code != 200:
            st.error("❌ Failed to fetch file")
            return None, None, None, None, None

        file = io.BytesIO(res.content)

        # -------- Trends --------
        trends = pd.read_excel(file, sheet_name="Trends", engine="openpyxl")
        years = trends["YEAR"].tolist()

        trend_data = {}
        for col in ["GDP", "Inflation"]:
            if col in trends.columns:
                trend_data[col] = trends[col].tolist()

        # -------- Schemes --------
        file.seek(0)
        schemes_df = pd.read_excel(file, sheet_name="Schemes", engine="openpyxl")

        schemes_data = {}
        for var in schemes_df["Variable"].unique():
            schemes_data[var] = []
            temp = schemes_df[schemes_df["Variable"] == var]

            for _, row in temp.iterrows():
                schemes_data[var].append({
                    "year": float(row["Year"]),
                    "name": str(row["Scheme Name"]),
                    "details": str(row["Details"]),
                    "url": str(row["URL"]) if pd.notna(row["URL"]) else "#",
                    "image": str(row["Image"]) if "Image" in schemes_df.columns and pd.notna(row["Image"]) else None
                })

        # -------- Nobel --------
        file.seek(0)
        nobel_data = []
        try:
            df = pd.read_excel(file, sheet_name="NobelLaureates", engine="openpyxl")
            nobel_data = sorted([
                {"year": int(r["Year"]), "name": r["Name"], "contribution": r["Contribution"]}
                for _, r in df.iterrows()
            ], key=lambda x: x["year"])
        except:
            pass

        # -------- Census --------
        file.seek(0)
        census_data = []
        try:
            df = pd.read_excel(file, sheet_name="CensusData", engine="openpyxl")
            census_data = sorted([
                {
                    "year": int(r["Year"]),
                    "population_crores": float(r["Population_Crores"]),
                    "literacy_rate": float(r["Literacy_Rate"]),
                    "urban_population": float(r["Urban_Population_Percent"]),
                    "sex_ratio": int(r["Sex_Ratio"]),
                    "density_per_sqkm": int(r["Density_Per_SqKm"])
                }
                for _, r in df.iterrows()
            ], key=lambda x: x["year"])
        except:
            pass

        st.success("✅ Data loaded successfully!")
        return years, trend_data, schemes_data, nobel_data, census_data

    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None, None, None, None, None

# ============ LOAD ============
years, trend_data, schemes_data, nobel_data, census_data = load_data()

# ============ HOME ============
st.title("📊 Economic Dashboard")

if years is None:
    st.stop()

option = st.radio("Choose Dataset", ["GDP & Inflation", "Nobel", "Census"])

# -------- GDP --------
if option == "GDP & Inflation":
    for var in trend_data:
        if st.button(var):
            st.session_state.selected_variable = var
            st.session_state.current_page = "detail"
            st.rerun()

# -------- Nobel --------
elif option == "Nobel":
    for n in nobel_data:
        st.write(f"{n['year']} - {n['name']}")

# -------- Census --------
elif option == "Census":
    st.dataframe(pd.DataFrame(census_data))

# ============ DETAIL ============
if st.session_state.current_page == "detail":
    var = st.session_state.selected_variable

    if st.button("⬅ Back"):
        st.session_state.current_page = "home"
        st.rerun()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years,
        y=trend_data[var],
        mode="lines+markers",
        name=var
    ))

    st.plotly_chart(fig, use_container_width=True)
