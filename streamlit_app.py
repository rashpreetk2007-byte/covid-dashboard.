import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="COVID-19 Dashboard",
    page_icon="🦠",
    layout="wide"
)

# ============================================================
# TITLE
# ============================================================

st.title("🦠 COVID-19 Dashboard")
st.markdown("### Global COVID-19 Cases, Deaths and Vaccinations")

# ============================================================
# LOAD DATA
# ============================================================

DATA_URL = (
    "https://catalog.ourworldindata.org/garden/"
    "covid/latest/compact/compact.csv"
)

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    df["Date"] = pd.to_datetime(df["date"])

    return df


try:
    df = load_data()

except Exception as e:
    st.error("Unable to load COVID-19 data.")
    st.write(e)
    st.stop()

# ============================================================
# FIND AVAILABLE COLUMNS
# ============================================================

columns = df.columns.tolist()

# Try to find useful columns automatically
case_column = None
death_column = None
vaccination_column = None

for col in columns:

    col_lower = col.lower()

    if case_column is None and (
        "new_cases" in col_lower or
        "new_cases_smoothed" in col_lower
    ):
        case_column = col

    if death_column is None and (
        "new_deaths" in col_lower or
        "new_deaths_smoothed" in col_lower
    ):
        death_column = col

    if vaccination_column is None and (
        "people_vaccinated" in col_lower
    ):
        vaccination_column = col

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("⚙️ Dashboard Controls")

countries = sorted(
    df["country"].dropna().unique().tolist()
)

default_country = "India"

if default_country in countries:
    default_index = countries.index(default_country)
else:
    default_index = 0

selected_country = st.sidebar.selectbox(
    "Select Country",
    countries,
    index=default_index
)

# ============================================================
# FILTER DATA
# ============================================================

country_data = df[
    df["country"] == selected_country
].copy()

country_data = country_data.sort_values("Date")

# ============================================================
# LATEST DATA
# ============================================================

if len(country_data) > 0:

    latest = country_data.iloc[-1]

    if case_column:
        latest_cases = latest[case_column]
    else:
        latest_cases = 0

    if death_column:
        latest_deaths = latest[death_column]
    else:
        latest_deaths = 0

    if vaccination_column:
        latest_vaccinations = latest[vaccination_column]
    else:
        latest_vaccinations = 0

else:

    latest_cases = 0
    latest_deaths = 0
    latest_vaccinations = 0

# ============================================================
# KPI CARDS
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "🦠 Latest Cases",
        f"{latest_cases:,.0f}"
    )

with col2:
    st.metric(
        "💀 Latest Deaths",
        f"{latest_deaths:,.0f}"
    )

with col3:
    st.metric(
        "💉 Vaccinated",
        f"{latest_vaccinations:,.0f}"
    )

# ============================================================
# COUNTRY INFORMATION
# ============================================================

st.divider()

st.subheader(
    f"📍 COVID-19 Data — {selected_country}"
)

# ============================================================
# CASES CHART
# ============================================================

if case_column:

    fig_cases = px.line(
        country_data,
        x="Date",
        y=case_column,
        title=f"📈 New COVID-19 Cases — {selected_country}",
        labels={
            "Date": "Date",
            case_column: "Cases"
        }
    )

    fig_cases.update_layout(
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_cases,
        use_container_width=True
    )

# ============================================================
# DEATHS CHART
# ============================================================

if death_column:

    fig_deaths = px.line(
        country_data,
        x="Date",
        y=death_column,
        title=f"📉 New COVID-19 Deaths — {selected_country}",
        labels={
            "Date": "Date",
            death_column: "Deaths"
        }
    )

    fig_deaths.update_layout(
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_deaths,
        use_container_width=True
    )

# ============================================================
# VACCINATION CHART
# ============================================================

if vaccination_column:

    fig_vaccine = px.line(
        country_data,
        x="Date",
        y=vaccination_column,
        title=f"💉 COVID-19 Vaccination — {selected_country}",
        labels={
            "Date": "Date",
            vaccination_column: "People Vaccinated"
        }
    )

    fig_vaccine.update_layout(
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_vaccine,
        use_container_width=True
    )

# ============================================================
# DATA TABLE
# ============================================================

st.divider()

st.subheader("📋 COVID-19 Data")

display_columns = ["Date"]

if case_column:
    display_columns.append(case_column)

if death_column:
    display_columns.append(death_column)

if vaccination_column:
    display_columns.append(vaccination_column)

available_columns = [
    col for col in display_columns
    if col in country_data.columns
]

st.dataframe(
    country_data[available_columns].tail(20),
    use_container_width=True
)

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "COVID-19 Dashboard | Data source: Our World in Data"
)
