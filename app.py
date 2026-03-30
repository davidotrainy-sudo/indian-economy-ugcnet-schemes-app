import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os
import requests
from datetime import datetime
import io

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

# ============ EXCEL DATA LOADING FROM GITHUB ============
@st.cache_data(ttl=300)
def load_data_from_github():
    """Load Excel file directly from GitHub raw URL"""
    try:
        # Raw URL from your GitHub file
        url = "https://raw.githubusercontent.com/davidotrainy-sudo/indian-economy-ugcnet-schemes-app/main/economy_data.xlsx"
        
        st.info(f"📥 Loading data from GitHub: {url}")
        
        response = requests.get(url)
        
        if response.status_code == 200:
            st.success("✅ Excel file downloaded successfully!")
            
            # Read Excel file from memory
            excel_file = io.BytesIO(response.content)
            
            # Load Trends sheet
            trends_df = pd.read_excel(excel_file, sheet_name='Trends')
            years = trends_df['YEAR'].tolist()
            
            trend_data = {}
            if 'GDP' in trends_df.columns:
                trend_data['GDP'] = trends_df['GDP'].tolist()
            if 'Inflation' in trends_df.columns:
                trend_data['Inflation'] = trends_df['Inflation'].tolist()
            
            # Load Schemes sheet
            schemes_df = pd.read_excel(excel_file, sheet_name='Schemes')
            schemes_data = {}
            for variable in schemes_df['Variable'].unique():
                schemes_data[variable] = []
                var_data = schemes_df[schemes_df['Variable'] == variable]
                for _, row in var_data.iterrows():
                    scheme = {
                        "year": float(row['Year']),
                        "name": str(row['Scheme Name']) if pd.notna(row['Scheme Name']) else "",
                        "details": str(row['Details']) if pd.notna(row['Details']) else "",
                        "url": str(row['URL']) if pd.notna(row['URL']) else "#",
                        "image": str(row['Image']) if 'Image' in row and pd.notna(row['Image']) else None
                    }
                    schemes_data[variable].append(scheme)
            
            # Load NobelLaureates sheet
            nobel_data = []
            try:
                nobel_df = pd.read_excel(excel_file, sheet_name='NobelLaureates')
                for _, row in nobel_df.iterrows():
                    nobel_data.append({
                        "year": int(row['Year']),
                        "name": str(row['Name']),
                        "contribution": str(row['Contribution'])
                    })
                nobel_data = sorted(nobel_data, key=lambda x: x['year'])
            except Exception as e:
                st.warning(f"NobelLaureates sheet not found: {e}")
            
            # Load CensusData sheet
            census_data = []
            try:
                census_df = pd.read_excel(excel_file, sheet_name='CensusData')
                for _, row in census_df.iterrows():
                    census_data.append({
                        "year": int(row['Year']),
                        "population_crores": float(row['Population_Crores']),
                        "literacy_rate": float(row['Literacy_Rate']),
                        "urban_population": float(row['Urban_Population_Percent']),
                        "sex_ratio": int(row['Sex_Ratio']),
                        "density_per_sqkm": int(row['Density_Per_SqKm'])
                    })
                census_data = sorted(census_data, key=lambda x: x['year'])
            except Exception as e:
                st.warning(f"CensusData sheet not found: {e}")
            
            return years, trend_data, schemes_data, nobel_data, census_data
            
        else:
            st.error(f"❌ Failed to download file. Status code: {response.status_code}")
            st.error("Make sure the file exists at the URL and is accessible")
            return None, None, None, None, None
            
    except Exception as e:
        st.error(f"❌ Error loading from GitHub: {str(e)}")
        return None, None, None, None, None

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

# ============ LOAD DATA FROM GITHUB ============
years, trend_data, schemes_data, nobel_data, census_data = load_data_from_github()

# ============ HOME PAGE ============
if st.session_state.current_page == 'home':
    st.title("📊 Economic & Statistical Data Dashboard")
    st.markdown("### Explore Economic Indicators, Government Schemes, and Statistical Data")
    
    add_refresh_controls()
    
    # Check if data loaded successfully
    if years is None or trend_data is None:
        st.error("❌ Failed to load data from Excel file. Please check:")
        st.markdown("""
        1. The file exists at: `https://raw.githubusercontent.com/davidotrainy-sudo/indian-economy-ugcnet-schemes-app/main/economy_data.xlsx`
        2. The file has the required sheets: `Trends`, `Schemes`, `NobelLaureates`, `CensusData`
        3. The file is publicly accessible
        """)
        st.stop()
    
    st.success("✅ Data loaded successfully from economy_data.xlsx!")
    
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
            st.warning("No GDP/Inflation data found in Excel file.")
        
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
        
        if nobel_data:
            search = st.text_input("🔍 Search by name or contribution:", placeholder="e.g., Sen, poverty, growth...")
            filtered_data = [n for n in nobel_data if search.lower() in n['name'].lower() or search.lower() in n['contribution'].lower()] if search else nobel_data
            st.caption(f"Showing {len(filtered_data)} of {len(nobel_data)} laureates")
            
            for laureate in filtered_data:
                with st.expander(f"🏅 **{laureate['year']} - {laureate['name']}**"):
                    st.markdown(f"**Contribution:** {laureate['contribution']}")
            
            st.markdown("---")
            st.subheader("📊 Descriptive Statistics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Laureates", len(nobel_data))
            with col2:
                st.metric("Year Range", f"{nobel_data[0]['year']} - {nobel_data[-1]['year']}")
            with col3:
                shared_count = sum(1 for n in nobel_data if ',' in n['name'] or ' and ' in n['name'])
                st.metric("Solo Laureates", len(nobel_data) - shared_count)
        else:
            st.warning("No Nobel Laureate data found in Excel file. Please add 'NobelLaureates' sheet.")
    
    elif selected_data == "Indian Census Data":
        st.markdown("---")
        st.subheader("🇮🇳 Indian Census Data")
        
        if census_data:
            st.dataframe(pd.DataFrame(census_data), use_container_width=True)
            
            st.markdown("---")
            st.subheader("📈 Population Trend")
            fig_pop = go.Figure()
            fig_pop.add_trace(go.Scatter(
                x=[c['year'] for c in census_data],
                y=[c['population_crores'] for c in census_data],
                mode='lines+markers', name='Population',
                line=dict(width=3, color='#1f77b4'), marker=dict(size=10)
            ))
            fig_pop.update_layout(title="India's Population Growth (Crores)", xaxis_title="Year", yaxis_title="Population (Crores)", height=400, plot_bgcolor='white')
            fig_pop.update_xaxes(gridcolor='lightgray', tickmode='linear', dtick=10)
            fig_pop.update_yaxes(gridcolor='lightgray')
            st.plotly_chart(fig_pop, use_container_width=True)
            
            st.subheader("📚 Literacy Rate Trend")
            fig_lit = go.Figure()
            fig_lit.add_trace(go.Scatter(
                x=[c['year'] for c in census_data],
                y=[c['literacy_rate'] for c in census_data],
                mode='lines+markers', name='Literacy Rate',
                line=dict(width=3, color='#ff7f0e'), marker=dict(size=10)
            ))
            fig_lit.update_layout(title="India's Literacy Rate (%)", xaxis_title="Year", yaxis_title="Literacy Rate (%)", height=400, plot_bgcolor='white')
            fig_lit.update_xaxes(gridcolor='lightgray', tickmode='linear', dtick=10)
            fig_lit.update_yaxes(gridcolor='lightgray')
            st.plotly_chart(fig_lit, use_container_width=True)
            
            st.markdown("---")
            st.subheader("📊 Descriptive Statistics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Latest Population", f"{census_data[-1]['population_crores']} Crores")
            with col2:
                st.metric("Latest Literacy", f"{census_data[-1]['literacy_rate']}%")
            with col3:
                pop_growth = ((census_data[-1]['population_crores'] - census_data[0]['population_crores']) / census_data[0]['population_crores']) * 100
                st.metric("Population Growth", f"+{pop_growth:.1f}%")
            with col4:
                lit_growth = census_data[-1]['literacy_rate'] - census_data[0]['literacy_rate']
                st.metric("Literacy Improvement", f"+{lit_growth:.1f}%")
        else:
            st.warning("No Census data found in Excel file. Please add 'CensusData' sheet.")

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
            x=years, y=values, mode='lines+markers', name=variable,
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
                        x=[x_position], y=[y_position], mode='markers',
                        marker=dict(size=15, color=plan_color, symbol='star', line=dict(width=1, color='white')),
                        name=scheme['name'], customdata=[scheme],
                        hovertemplate=f"<b>{scheme['name']}</b><br>Year: {year}<br>Plan: {get_plan_name(year)}<extra></extra>"
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=[x_position, year], y=[y_position, base_y], mode='lines',
                        line=dict(width=1, dash='dot', color='gray'), showlegend=False, hoverinfo='none'
                    ))
                    
                    fig.add_annotation(
                        x=x_position + 0.3, y=y_position, text=scheme['name'], showarrow=False,
                        font=dict(size=9, color='black'), bgcolor='rgba(255,255,255,0.8)',
                        bordercolor=plan_color, borderwidth=1, borderpad=2, xanchor='left'
                    )
        
        fig.add_trace(go.Scatter(
            x=years, y=values, mode='markers',
            marker=dict(size=10, color='darkblue', symbol='circle', line=dict(width=1, color='white')),
            name='Data Points', hovertemplate=f'Year: %{{x}}<br>{variable}: %{{y:.2f}}%<extra></extra>'
        ))
        
        fig.update_layout(
            title=f"{variable} Trends with Government Schemes ({min(years)}-{max(years)})",
            xaxis_title="Year", yaxis_title=f"{variable} (%)", hovermode='closest',
            height=600, plot_bgcolor='white', paper_bgcolor='white'
        )
        fig.update_xaxes(gridcolor='lightgray', gridwidth=0.5, tickmode='linear', dtick=1)
        fig.update_yaxes(gridcolor='lightgray', gridwidth=0.5)
        st.plotly_chart(fig, use_container_width=True)
        
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
        default_year = int(current_year_val) if current_year_val and 1951 <= current_year_val <= 2025 else 2020
        year = st.number_input("Year", min_value=1951, max_value=2025, value=default_year, step=1)
        year_plan = get_plan_name(int(year))
        year_color = get_plan_color(int(year))
        st.caption(f"📅 This year falls under: <span style='color:{year_color}'>★ {year_plan}</span>", unsafe_allow_html=True)
        
        name = st.text_input("Scheme Name *", value=scheme.get('name', ''), placeholder="Enter scheme name")
        details = st.text_area("Description/Details", value=scheme.get('details', ''), height=150, placeholder="Enter detailed description...")
        url = st.text_input("Website URL", value=scheme.get('url', ''), placeholder="https://...")
        
        st.markdown("---")
        st.subheader("📸 Scheme Image")
        if scheme.get('image') and scheme['image'] != 'None' and scheme['image']:
            try:
                st.image(scheme['image'], caption="Current Image", width=200)
            except:
                pass
        uploaded_image = st.file_uploader("Upload an image", type=['png', 'jpg', 'jpeg'], key=f"upload_{datetime.now().timestamp()}")
        if uploaded_image:
            st.image(uploaded_image, caption="Preview", width=200)
        
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        save_button = st.form_submit_button("💾 Save Scheme", width="stretch")
        delete_button = st.form_submit_button("🗑️ Delete Scheme", width="stretch")
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
                    image_path = os.path.join("scheme_images", f"{name.replace(' ', '_')}_{year}.png")
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
                
                st.success(f"✅ Scheme '{name}' saved!")
                st.session_state.current_page = 'variable_detail'
                st.session_state.edit_scheme = None
                st.rerun()
        
        if delete_button and scheme.get('name'):
            existing_schemes = schemes_data.get(variable, []) if schemes_data else []
            if schemes_data is not None:
                schemes_data[variable] = [s for s in existing_schemes if not (s.get('name') == scheme.get('name') and s.get('year') == scheme.get('year'))]
            st.success(f"✅ Scheme '{scheme.get('name')}' deleted!")
            st.session_state.current_page = 'variable_detail'
            st.session_state.edit_scheme = None
            st.rerun()
        
        if cancel_button:
            st.session_state.current_page = 'variable_detail'
            st.session_state.edit_scheme = None
            st.rerun()

# Footer
st.markdown("---")
st.markdown("📊 **Data Source:** economy_data.xlsx (loaded directly from GitHub)")
