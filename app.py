import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Economic Trends", layout="wide")

# ============ 5-YEAR PLAN MAPPING ============
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
    for plan, details in five_year_plans.items():
        start, end = details["years"]
        if start <= year <= end:
            return details["color"]
    return "#808080"

def get_plan_name(year):
    for plan, details in five_year_plans.items():
        start, end = details["years"]
        if start <= year <= end:
            return details["name"]
    return "Outside Plan Period"

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'selected_variable' not in st.session_state:
    st.session_state.selected_variable = None
if 'selected_scheme' not in st.session_state:
    st.session_state.selected_scheme = None
if 'edit_scheme' not in st.session_state:
    st.session_state.edit_scheme = None
if 'show_details' not in st.session_state:
    st.session_state.show_details = None

# ============ SAMPLE DATA (for deployment without Excel) ============
def get_sample_trend_data():
    """Return sample trend data when Excel is not available"""
    years = list(range(2015, 2026))
    trend_data = {
        "GDP": [8.0, 8.3, 6.8, 6.4, 3.9, -5.8, 9.7, 7.2, 7.5, 6.5, 7.0],
        "Inflation": [5.2, 4.9, 4.5, 4.8, 5.5, 5.1, 4.7, 5.3, 5.8, 5.4, 5.6]
    }
    return years, trend_data

def get_sample_schemes_data():
    """Return sample schemes data when Excel is not available"""
    return {
        "GDP": [
            {"year": 2016, "name": "Make in India", "details": "Launched to boost manufacturing sector", "url": "#", "image": None},
            {"year": 2018, "name": "GST Implementation", "details": "Unified tax structure", "url": "#", "image": None},
            {"year": 2020, "name": "Atmanirbhar Bharat", "details": "Self-reliant India campaign", "url": "#", "image": None},
            {"year": 2022, "name": "PLI Schemes", "details": "Production Linked Incentive", "url": "#", "image": None}
        ],
        "Inflation": [
            {"year": 2016, "name": "Demonetization", "details": "Withdrawal of ₹500 and ₹1000 notes", "url": "#", "image": None},
            {"year": 2019, "name": "RBI Rate Cuts", "details": "5 consecutive rate cuts", "url": "#", "image": None},
            {"year": 2020, "name": "COVID-19 Lockdown", "details": "Supply chain disruptions", "url": "#", "image": None},
            {"year": 2022, "name": "Rate Hikes", "details": "RBI hikes repo rate", "url": "#", "image": None}
        ]
    }

def get_sample_nobel_data():
    """Return sample Nobel laureate data"""
    return [
        {"year": 2019, "name": "Abhijit Banerjee, Esther Duflo, Michael Kremer", "contribution": "For experimental approach to poverty alleviation"},
        {"year": 2020, "name": "Paul Milgrom, Robert Wilson", "contribution": "For improvements to auction theory"},
        {"year": 2021, "name": "David Card, Joshua Angrist, Guido Imbens", "contribution": "For contributions to labor economics"},
        {"year": 2022, "name": "Ben Bernanke, Douglas Diamond, Philip Dybvig", "contribution": "For research on banks and financial crises"},
        {"year": 2023, "name": "Claudia Goldin", "contribution": "For understanding women's labor market outcomes"},
        {"year": 2024, "name": "Daron Acemoglu, Simon Johnson, James Robinson", "contribution": "For studies of how institutions affect prosperity"}
    ]

def get_sample_census_data():
    """Return sample census data"""
    return [
        {"year": 1951, "population_crores": 36.1, "literacy_rate": 18.3, "urban_population": 17.3, "sex_ratio": 946, "density_per_sqkm": 117},
        {"year": 1961, "population_crores": 43.9, "literacy_rate": 28.3, "urban_population": 18.0, "sex_ratio": 941, "density_per_sqkm": 142},
        {"year": 1971, "population_crores": 54.8, "literacy_rate": 34.5, "urban_population": 20.2, "sex_ratio": 930, "density_per_sqkm": 177},
        {"year": 1981, "population_crores": 68.3, "literacy_rate": 43.6, "urban_population": 23.3, "sex_ratio": 934, "density_per_sqkm": 216},
        {"year": 1991, "population_crores": 84.6, "literacy_rate": 52.2, "urban_population": 25.7, "sex_ratio": 927, "density_per_sqkm": 267},
        {"year": 2001, "population_crores": 102.9, "literacy_rate": 64.8, "urban_population": 27.8, "sex_ratio": 933, "density_per_sqkm": 324},
        {"year": 2011, "population_crores": 121.1, "literacy_rate": 74.0, "urban_population": 31.2, "sex_ratio": 943, "density_per_sqkm": 382},
        {"year": 2021, "population_crores": 139.0, "literacy_rate": 77.7, "urban_population": 34.5, "sex_ratio": 950, "density_per_sqkm": 450}
    ]

# ============ EXCEL DATA LOADING ============
@st.cache_data(ttl=10)
def load_data_from_excel():
    try:
        file_path = "economy_data.xlsx"
        
        if not os.path.exists(file_path):
            return None, None
        
        df = pd.read_excel(file_path, sheet_name='Trends')
        years = df['YEAR'].tolist()
        
        trend_data = {}
        if 'GDP' in df.columns:
            trend_data['GDP'] = df['GDP'].tolist()
        if 'Inflation' in df.columns:
            trend_data['Inflation'] = df['Inflation'].tolist()
        
        return years, trend_data
        
    except Exception:
        return None, None

def load_schemes_from_excel():
    try:
        file_path = "economy_data.xlsx"
        if not os.path.exists(file_path):
            return None
        
        df = pd.read_excel(file_path, sheet_name='Schemes')
        schemes_data = {}
        
        for variable in df['Variable'].unique():
            schemes_data[variable] = []
            var_data = df[df['Variable'] == variable]
            
            for _, row in var_data.iterrows():
                details_value = row['Details'] if pd.notna(row['Details']) else ""
                scheme = {
                    "year": float(row['Year']),
                    "name": str(row['Scheme Name']) if pd.notna(row['Scheme Name']) else "",
                    "details": str(details_value),
                    "url": str(row['URL']) if pd.notna(row['URL']) else "#",
                    "image": str(row['Image']) if 'Image' in row and pd.notna(row['Image']) else None
                }
                schemes_data[variable].append(scheme)
        
        return schemes_data
    except Exception:
        return None

def load_nobel_data_from_excel():
    try:
        file_path = "economy_data.xlsx"
        if not os.path.exists(file_path):
            return None
        
        df = pd.read_excel(file_path, sheet_name='NobelLaureates')
        nobel_data = []
        
        for _, row in df.iterrows():
            laureate = {
                "year": int(row['Year']) if pd.notna(row['Year']) else 0,
                "name": str(row['Name']) if pd.notna(row['Name']) else "",
                "contribution": str(row['Contribution']) if pd.notna(row['Contribution']) else ""
            }
            nobel_data.append(laureate)
        
        return sorted(nobel_data, key=lambda x: x['year'])
    except Exception:
        return None

def load_census_data_from_excel():
    try:
        file_path = "economy_data.xlsx"
        if not os.path.exists(file_path):
            return None
        
        df = pd.read_excel(file_path, sheet_name='CensusData')
        census_data = []
        
        for _, row in df.iterrows():
            data = {
                "year": int(row['Year']) if pd.notna(row['Year']) else 0,
                "population_crores": float(row['Population_Crores']) if pd.notna(row['Population_Crores']) else 0,
                "literacy_rate": float(row['Literacy_Rate']) if pd.notna(row['Literacy_Rate']) else 0,
                "urban_population": float(row['Urban_Population_Percent']) if pd.notna(row['Urban_Population_Percent']) else 0,
                "sex_ratio": int(row['Sex_Ratio']) if pd.notna(row['Sex_Ratio']) else 0,
                "density_per_sqkm": int(row['Density_Per_SqKm']) if pd.notna(row['Density_Per_SqKm']) else 0
            }
            census_data.append(data)
        
        return sorted(census_data, key=lambda x: x['year'])
    except Exception:
        return None

def save_schemes_to_excel(schemes_data):
    try:
        file_path = "economy_data.xlsx"
        
        rows = []
        for variable, schemes in schemes_data.items():
            for scheme in schemes:
                rows.append({
                    'Variable': variable,
                    'Year': scheme['year'],
                    'Scheme Name': scheme['name'],
                    'Details': scheme['details'],
                    'URL': scheme['url'],
                    'Image': scheme.get('image', '')
                })
        
        df = pd.DataFrame(rows)
        
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name='Schemes', index=False)
        
        return True
    except Exception as e:
        st.error(f"Error saving to Excel: {e}")
        return False

# ============ REFRESH BUTTON ============
def add_refresh_controls():
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("🔄 Refresh Data", width="stretch"):
            st.cache_data.clear()
            st.rerun()
    with col2:
        st.caption(f"Updated: {datetime.now().strftime('%H:%M:%S')}")

# ============ NAVIGATION ============
def go_to_variable(variable):
    st.session_state.current_page = 'variable_detail'
    st.session_state.selected_variable = variable
    st.session_state.show_details = None
    st.rerun()

def go_back_home():
    st.session_state.current_page = 'home'
    st.session_state.selected_variable = None
    st.session_state.show_details = None
    st.rerun()

def go_to_edit_scheme(scheme):
    st.session_state.current_page = 'edit_scheme'
    st.session_state.edit_scheme = scheme
    st.rerun()

def show_scheme_details(scheme):
    st.session_state.show_details = scheme
    st.rerun()

# ============ LOAD DATA (with fallback to samples) ============
# Try loading from Excel, fall back to sample data
excel_years, excel_trend_data = load_data_from_excel()
excel_schemes = load_schemes_from_excel()
excel_nobel = load_nobel_data_from_excel()
excel_census = load_census_data_from_excel()

# Use Excel data if available, otherwise use samples
if excel_years and excel_trend_data:
    years = excel_years
    trend_data = excel_trend_data
else:
    years, trend_data = get_sample_trend_data()
    st.info("📌 Using sample trend data. Upload 'economy_data.xlsx' with 'Trends' sheet for custom data.")

if excel_schemes:
    schemes_data = excel_schemes
else:
    schemes_data = get_sample_schemes_data()
    if not excel_schemes and excel_years:
        st.info("📌 Using sample schemes data. Add 'Schemes' sheet to Excel for custom schemes.")

if excel_nobel:
    nobel_data = excel_nobel
else:
    nobel_data = get_sample_nobel_data()

if excel_census:
    census_data = excel_census
else:
    census_data = get_sample_census_data()

# ============ HOME PAGE ============
if st.session_state.current_page == 'home':
    st.title("📊 Economic & Statistical Data Dashboard")
    st.markdown("### Explore Economic Indicators, Government Schemes, and Statistical Data")
    
    add_refresh_controls()
    
    # Data source selector
    st.markdown("---")
    st.subheader("📁 Select Data Source")
    
    data_options = ["GDP & Inflation", "Nobel Laureates in Economics", "Indian Census Data"]
    selected_data = st.radio("Choose a dataset to explore:", data_options, horizontal=True)
    
    if selected_data == "GDP & Inflation":
        st.markdown("---")
        
        if trend_data and years:
            col1, col2 = st.columns(2)
            
            with col1:
                if "GDP" in trend_data:
                    if st.button("📊 **GDP**\n\nGross Domestic Product", key="gdp_btn", width="stretch"):
                        go_to_variable("GDP")
            
            with col2:
                if "Inflation" in trend_data:
                    if st.button("📈 **Inflation**\n\nPrice Rise (CPI)", key="inflation_btn", width="stretch"):
                        go_to_variable("Inflation")
        else:
            st.warning("No GDP/Inflation data available.")
        
        # 5-Year Plan Legend
        st.markdown("---")
        st.subheader("🎨 5-Year Plan Color Legend")
        cols = st.columns(4)
        plan_items = list(five_year_plans.items())
        for i, (plan_num, details) in enumerate(plan_items):
            with cols[i % 4]:
                st.markdown(f"<span style='color:{details['color']}'>★</span> **{details['name']}**", unsafe_allow_html=True)
    
    elif selected_data == "Nobel Laureates in Economics":
        st.markdown("---")
        st.subheader("🏆 Nobel Prize in Economic Sciences Laureates")
        st.markdown("Chronological list of Nobel laureates and their contributions")
        
        if nobel_data:
            search = st.text_input("🔍 Search by name or contribution:", placeholder="e.g., Sen, poverty, growth...")
            
            filtered_data = nobel_data
            if search:
                search_lower = search.lower()
                filtered_data = [n for n in nobel_data if search_lower in n['name'].lower() or search_lower in n['contribution'].lower()]
            
            st.caption(f"Showing {len(filtered_data)} of {len(nobel_data)} laureates")
            
            for laureate in filtered_data:
                with st.expander(f"🏅 **{laureate['year']} - {laureate['name']}**"):
                    st.markdown(f"**Contribution:** {laureate['contribution']}")
            
            # Descriptive Statistics
            st.markdown("---")
            st.subheader("📊 Descriptive Statistics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Laureates", len(nobel_data))
            with col2:
                years_range = f"{nobel_data[0]['year']} - {nobel_data[-1]['year']}"
                st.metric("Year Range", years_range)
            with col3:
                shared_count = sum(1 for n in nobel_data if ',' in n['name'] or ' and ' in n['name'])
                solo_count = len(nobel_data) - shared_count
                st.metric("Solo Laureates", solo_count)
        else:
            st.info("📌 No Nobel Laureate data available.")
    
    elif selected_data == "Indian Census Data":
        st.markdown("---")
        st.subheader("🇮🇳 Indian Census Data")
        
        if census_data:
            census_df = pd.DataFrame(census_data)
            st.dataframe(census_df, use_container_width=True)
            
            # Population trend chart
            st.markdown("---")
            st.subheader("📈 Population Trend")
            fig_pop = go.Figure()
            fig_pop.add_trace(go.Scatter(
                x=[c['year'] for c in census_data],
                y=[c['population_crores'] for c in census_data],
                mode='lines+markers',
                name='Population',
                line=dict(width=3, color='#1f77b4'),
                marker=dict(size=10)
            ))
            fig_pop.update_layout(
                title="India's Population Growth (Crores)",
                xaxis_title="Year",
                yaxis_title="Population (Crores)",
                height=400,
                plot_bgcolor='white'
            )
            fig_pop.update_xaxes(gridcolor='lightgray', tickmode='linear', dtick=10)
            fig_pop.update_yaxes(gridcolor='lightgray')
            st.plotly_chart(fig_pop, use_container_width=True)
            
            # Literacy rate trend
            st.subheader("📚 Literacy Rate Trend")
            fig_lit = go.Figure()
            fig_lit.add_trace(go.Scatter(
                x=[c['year'] for c in census_data],
                y=[c['literacy_rate'] for c in census_data],
                mode='lines+markers',
                name='Literacy Rate',
                line=dict(width=3, color='#ff7f0e'),
                marker=dict(size=10)
            ))
            fig_lit.update_layout(
                title="India's Literacy Rate (%)",
                xaxis_title="Year",
                yaxis_title="Literacy Rate (%)",
                height=400,
                plot_bgcolor='white'
            )
            fig_lit.update_xaxes(gridcolor='lightgray', tickmode='linear', dtick=10)
            fig_lit.update_yaxes(gridcolor='lightgray')
            st.plotly_chart(fig_lit, use_container_width=True)
            
            # Descriptive Statistics
            st.markdown("---")
            st.subheader("📊 Descriptive Statistics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                latest_pop = census_data[-1]['population_crores']
                st.metric("Latest Population", f"{latest_pop} Crores")
            with col2:
                latest_lit = census_data[-1]['literacy_rate']
                st.metric("Latest Literacy", f"{latest_lit}%")
            with col3:
                pop_growth = ((census_data[-1]['population_crores'] - census_data[0]['population_crores']) / census_data[0]['population_crores']) * 100
                st.metric("Population Growth", f"+{pop_growth:.1f}%", "since first census")
            with col4:
                lit_growth = census_data[-1]['literacy_rate'] - census_data[0]['literacy_rate']
                st.metric("Literacy Improvement", f"+{lit_growth:.1f}%", "since first census")
        else:
            st.info("📌 No Census data available.")

# ============ VARIABLE DETAIL PAGE ============
elif st.session_state.current_page == 'variable_detail':
    variable = st.session_state.selected_variable
    
    col1, col2 = st.columns([1, 11])
    with col1:
        if st.button("◀ Back", width="stretch"):
            go_back_home()
    with col2:
        st.title(f"📈 {variable} Trends")
    
    add_refresh_controls()
    
    if years and trend_data and variable in trend_data:
        values = trend_data[variable]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=years,
            y=values,
            mode='lines+markers',
            name=variable,
            line=dict(width=4, color='#1f77b4' if variable == 'GDP' else '#ff7f0e'),
            marker=dict(size=12),
            hovertemplate=f'Year: %{{x}}<br>{variable}: %{{y:.2f}}%<extra></extra>'
        ))
        
        schemes = schemes_data.get(variable, []) if schemes_data else []
        
        if schemes:
            max_y = max(values)
            base_y_position = max_y + (max_y * 0.1)
            
            schemes_by_year = {}
            for scheme in schemes:
                year = scheme['year']
                if year not in schemes_by_year:
                    schemes_by_year[year] = []
                schemes_by_year[year].append(scheme)
            
            for year, year_schemes in schemes_by_year.items():
                if year in years:
                    idx = years.index(year)
                    base_y = values[idx]
                else:
                    continue
                
                for i, scheme in enumerate(year_schemes):
                    y_position = base_y_position + (i * 2.5)
                    x_position = year
                    
                    plan_color = get_plan_color(year)
                    
                    fig.add_trace(go.Scatter(
                        x=[x_position],
                        y=[y_position],
                        mode='markers',
                        marker=dict(size=15, color=plan_color, symbol='star', line=dict(width=1, color='white')),
                        name=scheme['name'],
                        customdata=[scheme],
                        hovertemplate=f"<b>{scheme['name']}</b><br>Year: {year}<br>Plan: {get_plan_name(year)}<extra></extra>"
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=[x_position, year],
                        y=[y_position, base_y],
                        mode='lines',
                        line=dict(width=1, dash='dot', color='gray'),
                        showlegend=False,
                        hoverinfo='none'
                    ))
                    
                    fig.add_annotation(
                        x=x_position + 0.3,
                        y=y_position,
                        text=scheme['name'],
                        showarrow=False,
                        font=dict(size=9, color='black'),
                        bgcolor='rgba(255,255,255,0.8)',
                        bordercolor=plan_color,
                        borderwidth=1,
                        borderpad=2,
                        xanchor='left'
                    )
        
        fig.add_trace(go.Scatter(
            x=years,
            y=values,
            mode='markers',
            marker=dict(size=10, color='darkblue', symbol='circle', line=dict(width=1, color='white')),
            name='Data Points',
            hovertemplate=f'Year: %{{x}}<br>{variable}: %{{y:.2f}}%<extra></extra>'
        ))
        
        fig.update_layout(
            title=f"{variable} Trends with Government Schemes ({min(years)}-{max(years)})",
            xaxis_title="Year",
            yaxis_title=f"{variable} (%)",
            hovermode='closest',
            height=600,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        fig.update_xaxes(gridcolor='lightgray', gridwidth=0.5, tickmode='linear', dtick=1)
        fig.update_yaxes(gridcolor='lightgray', gridwidth=0.5)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 5-Year Plan Legend
        st.markdown("---")
        st.subheader("🎨 5-Year Plan Color Legend")
        cols = st.columns(4)
        plan_items = list(five_year_plans.items())
        for i, (plan_num, details) in enumerate(plan_items):
            with cols[i % 4]:
                st.markdown(f"<span style='color:{details['color']}'>★</span> **{details['name']}**", unsafe_allow_html=True)
        
        if schemes:
            st.markdown("---")
            st.subheader("📋 Government Schemes Timeline")
            st.markdown("*Click on any scheme to view details*")
            
            sorted_schemes = sorted(schemes, key=lambda x: x['year'])
            
            for i, scheme in enumerate(sorted_schemes):
                details_text = str(scheme.get('details', '')) if scheme.get('details') is not None else ''
                plan_color = get_plan_color(int(scheme['year']))
                plan_name = get_plan_name(int(scheme['year']))
                
                col1, col2, col3 = st.columns([1, 4, 1])
                with col1:
                    st.markdown(f"### {int(scheme['year'])}")
                with col2:
                    if st.button(f"📌 **{scheme['name']}**", key=f"view_{variable}_{i}"):
                        show_scheme_details(scheme)
                    st.markdown(f"<span style='color:{plan_color}'>★</span> {plan_name}", unsafe_allow_html=True)
                    if details_text:
                        preview = details_text[:80] + "..." if len(details_text) > 80 else details_text
                        st.caption(preview)
                with col3:
                    if st.button(f"✏️ Edit", key=f"edit_{variable}_{i}"):
                        go_to_edit_scheme(scheme)
                
                if i < len(sorted_schemes) - 1:
                    st.markdown("---")
            
            st.markdown("---")
            if st.button("➕ **Add New Government Scheme**", width="stretch"):
                new_scheme = {"year": 2020, "name": "", "details": "", "url": "#", "image": None, "variable": variable}
                go_to_edit_scheme(new_scheme)
            
            if st.session_state.show_details:
                scheme = st.session_state.show_details
                details_text = str(scheme.get('details', '')) if scheme.get('details') is not None else ''
                plan_color = get_plan_color(int(scheme['year']))
                plan_name = get_plan_name(int(scheme['year']))
                
                st.markdown("---")
                st.subheader(f"📖 {scheme['name']} - Details")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**Year:** {int(scheme['year'])}")
                    st.markdown(f"**Plan:** <span style='color:{plan_color}'>★</span> {plan_name}", unsafe_allow_html=True)
                    st.markdown(f"**Description:** {details_text}")
                    st.markdown(f"**🔗 [More Information]({scheme['url']})**")
                
                with col2:
                    if scheme.get('image') and scheme['image'] != 'None' and scheme['image']:
                        try:
                            st.image(scheme['image'], caption=scheme['name'], width=200)
                        except:
                            pass
                
                if st.button("❌ Close Details", width="stretch"):
                    st.session_state.show_details = None
                    st.rerun()
        
        st.info("💡 **Tip:** Click on any scheme name to see full details. Stars are colored by 5-Year Plan period.")
        
    else:
        st.error(f"No data found for {variable}")

# ============ EDIT SCHEME PAGE ============
elif st.session_state.current_page == 'edit_scheme':
    scheme = st.session_state.edit_scheme
    variable = st.session_state.selected_variable
    
    col1, col2 = st.columns([1, 11])
    with col1:
        if st.button("◀ Back", width="stretch"):
            st.session_state.current_page = 'variable_detail'
            st.session_state.edit_scheme = None
            st.rerun()
    with col2:
        if scheme.get('name'):
            st.title(f"✏️ Edit Scheme: {scheme['name']}")
        else:
            st.title("➕ Add New Government Scheme")
    
    current_year = scheme.get('year', 2020)
    plan_name = get_plan_name(int(current_year)) if current_year else "Select a year"
    plan_color = get_plan_color(int(current_year)) if current_year else "#808080"
    st.markdown(f"<span style='color:{plan_color}'>★</span> **Plan Period:** {plan_name}", unsafe_allow_html=True)
    
    st.markdown("---")
    
    with st.form(key="scheme_form", clear_on_submit=False):
        st.subheader("Scheme Information")
        
        current_year_val = scheme.get('year')
        if current_year_val and current_year_val >= 1951 and current_year_val <= 2025:
            default_year = int(current_year_val)
        else:
            default_year = 2020
        
        year = st.number_input(
            "Year",
            min_value=1951,
            max_value=2025,
            value=default_year,
            step=1
        )
        
        year_plan = get_plan_name(int(year))
        year_color = get_plan_color(int(year))
        st.caption(f"📅 This year falls under: <span style='color:{year_color}'>★ {year_plan}</span>", unsafe_allow_html=True)
        
        name = st.text_input(
            "Scheme Name *",
            value=scheme.get('name', ''),
            placeholder="Enter scheme name"
        )
        
        details = st.text_area(
            "Description/Details",
            value=scheme.get('details', ''),
            height=150,
            placeholder="Enter detailed description of the scheme..."
        )
        
        url = st.text_input(
            "Website URL",
            value=scheme.get('url', ''),
            placeholder="https://..."
        )
        
        st.markdown("---")
        st.subheader("📸 Scheme Image")
        
        if scheme.get('image') and scheme['image'] != 'None' and scheme['image']:
            try:
                st.image(scheme['image'], caption="Current Image", width=200)
            except:
                pass
        
        uploaded_image = st.file_uploader(
            "Upload an image",
            type=['png', 'jpg', 'jpeg'],
            key=f"upload_{datetime.now().timestamp()}"
        )
        
        if uploaded_image:
            st.image(uploaded_image, caption="Preview", width=200)
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            save_button = st.form_submit_button("💾 Save Scheme", width="stretch")
        with col2:
            delete_button = st.form_submit_button("🗑️ Delete Scheme", width="stretch")
        with col3:
            cancel_button = st.form_submit_button("❌ Cancel", width="stretch")
        
        if save_button:
            if not name:
                st.error("❌ Please enter a scheme name")
            else:
                scheme['year'] = year
                scheme['name'] = name
                scheme['details'] = details
                scheme['url'] = url if url else "#"
                
                if uploaded_image:
                    os.makedirs("scheme_images", exist_ok=True)
                    image_filename = f"{name.replace(' ', '_')}_{year}.png"
                    image_path = os.path.join("scheme_images", image_filename)
                    
                    with open(image_path, "wb") as f:
                        f.write(uploaded_image.getbuffer())
                    scheme['image'] = image_path
                
                existing_schemes = schemes_data.get(variable, []) if schemes_data else []
                scheme_exists = False
                
                for i, existing in enumerate(existing_schemes):
                    if existing.get('name') == scheme.get('name') and existing.get('year') == scheme.get('year'):
                        existing_schemes[i] = scheme
                        scheme_exists = True
                        break
                
                if not scheme_exists and scheme.get('name'):
                    existing_schemes.append(scheme)
                
                if schemes_data is not None:
                    schemes_data[variable] = existing_schemes
                
                if save_schemes_to_excel(schemes_data):
                    st.success(f"✅ Scheme '{name}' saved!")
                else:
                    st.warning(f"⚠️ Scheme '{name}' saved in memory.")
                
                st.cache_data.clear()
                st.session_state.current_page = 'variable_detail'
                st.session_state.edit_scheme = None
                st.rerun()
        
        if delete_button:
            if scheme.get('name'):
                existing_schemes = schemes_data.get(variable, []) if schemes_data else []
                if schemes_data is not None:
                    schemes_data[variable] = [s for s in existing_schemes if not (s.get('name') == scheme.get('name') and s.get('year') == scheme.get('year'))]
                
                if save_schemes_to_excel(schemes_data):
                    st.success(f"✅ Scheme '{scheme.get('name')}' deleted!")
                else:
                    st.warning("⚠️ Scheme marked for deletion.")
                
                st.cache_data.clear()
                st.session_state.current_page = 'variable_detail'
                st.session_state.edit_scheme = None
                st.rerun()
            else:
                st.error("No scheme to delete")
        
        if cancel_button:
            st.session_state.current_page = 'variable_detail'
            st.session_state.edit_scheme = None
            st.rerun()

# Footer
st.markdown("---")
st.markdown("📊 **Data Source:** economy_data.xlsx (optional) | Using sample data if Excel not found")
