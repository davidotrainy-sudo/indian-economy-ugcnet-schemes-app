import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests
import io

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

        trends = trends.dropna(subset=["YEAR"])
        trends["YEAR"] = pd.to_numeric(trends["YEAR"], errors="coerce")
        trends = trends.dropna(subset=["YEAR"])
        trends["YEAR"] = trends["YEAR"].astype(int)

        years = trends["YEAR"].tolist()

        trend_data = {
            col: trends[col].tolist()
            for col in trends.columns if col != "YEAR"
        }

        # -------- Schemes --------
        file.seek(0)
        schemes_df = pd.read_excel(file, sheet_name="Schemes", engine="openpyxl")

        schemes_df = schemes_df.dropna(subset=["Year", "Variable"])

        schemes_df["Year"] = pd.to_numeric(schemes_df["Year"], errors="coerce")
        schemes_df = schemes_df.dropna(subset=["Year"])
        schemes_df["Year"] = schemes_df["Year"].astype(int)

        schemes_df["Variable"] = (
            schemes_df["Variable"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

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
                    "url": str(row["URL"]) if pd.notna(row["URL"]) else "#"
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

    # -------- MAIN LINE --------
    fig.add_trace(go.Scatter(
        x=years,
        y=values,
        mode="lines+markers",
        name=var,
        line=dict(width=3),
        marker=dict(size=8)
    ))

    # -------- ADVANCED SCHEME TIMELINE --------
# ========= RAW TIMELINE + CLEAN HOVER =========
from collections import defaultdict

schemes = schemes_data.get(var, [])

if schemes:
    offset = (max(values) - min(values)) * 0.15

    grouped = defaultdict(list)

    for s in schemes:
        grouped[s["year"]].append(s["name"])

    for year, scheme_names in grouped.items():
        if year in years:
            idx = years.index(year)
            base_y = values[idx]

            # Create clean hover text (THIS IS THE MAGIC)
            hover_text = "<br>".join([
                f"{i+1}. {name}" for i, name in enumerate(scheme_names)
            ])

            # Marker at point (with hover)
            fig.add_trace(go.Scatter(
                x=[year],
                y=[base_y],
                mode="markers",
                marker=dict(size=12, color="blue"),
                name=f"{year}",
                hovertemplate=(
                    f"<b>Year: {year}</b><br><br>"
                    f"<b>Schemes:</b><br>{hover_text}"
                    "<extra></extra>"
                ),
                showlegend=False
            ))

            # Stack labels (still messy visually)
            for i, name in enumerate(scheme_names):
                y_offset = base_y + offset + (i * 1.5)

                # vertical line
                fig.add_trace(go.Scatter(
                    x=[year, year],
                    y=[base_y, y_offset],
                    mode="lines",
                    line=dict(color="gray", width=1),
                    showlegend=False,
                    hoverinfo="none"
                ))

                # overlapping labels
                fig.add_trace(go.Scatter(
                    x=[year],
                    y=[y_offset],
                    mode="text",
                    text=[name],
                    textposition="top center",
                    textfont=dict(size=10),
                    showlegend=False,
                    hoverinfo="skip"  # IMPORTANT → avoid messy hover
                ))

    # -------- LAYOUT --------
    fig.update_layout(
        title=f"{var} with Government Schemes",
        xaxis_title="Year",
        yaxis_title=var,
        height=600,
        plot_bgcolor="white"
    )

    fig.update_xaxes(showgrid=True)
    fig.update_yaxes(showgrid=True)

    st.plotly_chart(fig, use_container_width=True)

    # -------- DEBUG --------
    with st.expander("🔍 Debug Info"):
        st.write("Years:", years[:10])
        st.write("Schemes:", schemes)
