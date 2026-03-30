import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests
import io
from datetime import datetime

st.set_page_config(page_title="Economic Dashboard", layout="wide")

# ========= DEPENDENCY CHECK =========
def check_dependencies():
    try:
        import openpyxl
    except ImportError:
        st.error("❌ Missing dependency: openpyxl")
        st.info("👉 Run: pip install openpyxl")
        st.stop()

# ========= SESSION =========
for key, val in {
    "current_page": "home",
    "selected_variable": None
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ========= DATA LOADER =========
@st.cache_data(ttl=300)
def load_data():
    check_dependencies()

    url = "https://raw.githubusercontent.com/davidotrainy-sudo/indian-economy-ugcnet-schemes-app/main/economy_data.xlsx"

    try:
        res = requests.get(url)
        if res.status_code != 200:
            st.error("❌ Failed to fetch Excel")
            return None, None, None

        file = io.BytesIO(res.content)

        # -------- Trends --------
        trends = pd.read_excel(file, sheet_name="Trends", engine="openpyxl")
        trends["YEAR"] = trends["YEAR"].astype(int)

        years = trends["YEAR"].tolist()
        trend_data = {
            col: trends[col].tolist()
            for col in trends.columns if col != "YEAR"
        }

        # -------- Schemes --------
        file.seek(0)
        schemes_df = pd.read_excel(file, sheet_name="Schemes", engine="openpyxl")

        # Normalize columns
        schemes_df["Variable"] = schemes_df["Variable"].astype(str).str.strip().str.lower()
        schemes_df["Year"] = schemes_df["Year"].astype(int)

        schemes_data = {}

        for var in trend_data.keys():
            var_key = var.lower()

            filtered = schemes_df[
                schemes_df["Variable"].str.contains(var_key)
            ]

            schemes_data[var] = [
                {
                    "year": int(row["Year"]),
                    "name": str(row["Scheme Name"]),
                    "details": str(row["Details"]) if pd.notna(row["Details"]) else "",
                    "url": str(row["URL"]) if pd.notna(row["URL"]) else "#",
                    "image": str(row["Image"]) if "Image" in schemes_df.columns and pd.notna(row["Image"]) else None
                }
                for _, row in filtered.iterrows()
            ]

        return years, trend_data, schemes_data

    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None, None, None

# ========= LOAD =========
years, trend_data, schemes_data = load_data()

if years is None:
    st.stop()

# ========= HOME =========
st.title("📊 Economic Dashboard")

choice = st.radio("Choose Variable", list(trend_data.keys()))

if st.button(f"View {choice}"):
    st.session_state.selected_variable = choice
    st.session_state.current_page = "detail"
    st.rerun()

# ========= DETAIL =========
if st.session_state.current_page == "detail":
    var = st.session_state.selected_variable

    if st.button("⬅ Back"):
        st.session_state.current_page = "home"
        st.rerun()

    values = trend_data[var]

    fig = go.Figure()

    # Main line
    fig.add_trace(go.Scatter(
        x=years,
        y=values,
        mode="lines+markers",
        name=var
    ))

    # -------- SCHEMES --------
    schemes = schemes_data.get(var, [])

    if schemes:
        for scheme in schemes:
            year = int(scheme["year"])

            if year in years:
                idx = years.index(year)
                y_val = values[idx]

                fig.add_trace(go.Scatter(
                    x=[year],
                    y=[y_val],
                    mode="markers+text",
                    marker=dict(size=12, symbol="star"),
                    text=[scheme["name"]],
                    textposition="top center",
                    name=scheme["name"],
                    hovertemplate=f"{scheme['name']}<br>Year: {year}<extra></extra>"
                ))

    fig.update_layout(
        title=f"{var} with Government Schemes",
        xaxis_title="Year",
        yaxis_title=var,
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)

    # ========= DEBUG (remove later) =========
    with st.expander("🔍 Debug Info"):
        st.write("Available Variables in Schemes:", schemes_data.keys())
        st.write("Schemes for this variable:", schemes)
