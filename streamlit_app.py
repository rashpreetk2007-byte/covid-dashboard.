import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="COVID-19 Pulse",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(
            circle at 5% 5%,
            rgba(0, 220, 255, 0.12),
            transparent 25%
        ),
        radial-gradient(
            circle at 95% 15%,
            rgba(100, 80, 255, 0.14),
            transparent 28%
        ),
        #07111f;
    color: #f5f8fc;
}

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Sidebar */

section[data-testid="stSidebar"] {
    background: #081525;
    border-right: 1px solid rgba(255,255,255,0.08);
}

section[data-testid="stSidebar"] * {
    color: #eaf3ff;
}

/* Hero */

.hero {
    padding: 42px;
    border-radius: 30px;
    margin-bottom: 28px;

    background:
        linear-gradient(
            135deg,
            rgba(0,220,255,0.16),
            rgba(83,73,255,0.17)
        ),
        rgba(10,23,41,0.94);

    border: 1px solid rgba(255,255,255,0.10);

    box-shadow:
        0 25px 70px rgba(0,0,0,0.32);
}

.badge {
    display: inline-block;
    padding: 7px 15px;
    border-radius: 30px;

    background: rgba(0,220,255,0.12);
    border: 1px solid rgba(0,220,255,0.25);

    color: #6eeaff;
    font-size: 12px;
    font-weight: 700;

    letter-spacing: 1px;
    margin-bottom: 15px;
}

.hero-title {
    font-size: 48px;
    font-weight: 800;
    letter-spacing: -1px;
}

.hero-subtitle {
    margin-top: 12px;
    max-width: 800px;

    color: #a9bad0;
    font-size: 17px;
    line-height: 1.7;
}

/* KPI */

.kpi {
    padding: 24px;
    min-height: 145px;

    border-radius: 22px;

    background: rgba(14,30,50,0.90);

    border: 1px solid rgba(255,255,255,0.08);

    box-shadow:
        0 14px 40px rgba(0,0,0,0.22);
}

.kpi-label {
    color: #8fa5bd;

    font-size: 12px;
    font-weight: 700;

    text-transform: uppercase;
    letter-spacing: 1px;
}

.kpi-value {
    margin-top: 12px;

    font-size: 30px;
    font-weight: 800;

    color: #ffffff;
}

.kpi-note {
    margin-top: 7px;

    color: #6eeaff;
    font-size: 12px;
}

/* Section */

.section-title {
    margin-top: 30px;
    margin-bottom: 15px;

    font-size: 24px;
    font-weight: 750;
}

/* Info */

.info-box {
    padding: 24px;

    border-radius: 20px;

    background: rgba(12,27,46,0.85);

    border: 1px solid rgba(255,255,255,0.07);

    color: #b9c8d9;

    line-height: 1.7;
}

/* Footer */

.footer {
    margin-top: 50px;
    padding: 30px;

    text-align: center;

    border-top: 1px solid rgba(255,255,255,0.08);

    color: #8ea1b7;
}

.footer strong {
    color: #ffffff;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA SOURCES
# ============================================================

CASES_URL = (
    "https://ourworldindata.org/grapher/"
    "weekly-covid-cases.csv"
)

DEATHS_URL = (
    "https://ourworldindata.org/grapher/"
    "weekly-covid-deaths.csv"
)

VACCINE_URL = (
    "https://ourworldindata.org/grapher/"
    "share-people-fully-vaccinated-covid.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data(ttl=3600)
def load_data():

    cases = pd.read_csv(CASES_URL)
    deaths = pd.read_csv(DEATHS_URL)
    vaccines = pd.read_csv(VACCINE_URL)

    cases["Date"] = pd.to_datetime(cases["Date"])
    deaths["Date"] = pd.to_datetime(deaths["Date"])
    vaccines["Date"] = pd.to_datetime(vaccines["Date"])

    return cases, deaths, vaccines


try:

    cases, deaths, vaccines = load_data()

except Exception as error:

    st.error("Could not load COVID-19 data.")

    st.code(str(error))

    st.stop()


# ============================================================
# FIND VALUE COLUMNS
# ============================================================

def find_value_column(data):

    ignored = [
        "Entity",
        "Code",
        "Date"
    ]

    available = [
        column
        for column in data.columns
        if column not in ignored
    ]

    if len(available) == 0:
        return None

    return available[0]


case_column = find_value_column(cases)
death_column = find_value_column(deaths)
vaccine_column = find_value_column(vaccines)


# ============================================================
# COUNTRY LIST
# ============================================================

country_list = sorted(
    cases["Entity"]
    .dropna()
    .unique()
    .tolist()
)

country_options = [
    "🌍 All Countries"
] + country_list


# ============================================================
# HERO
# ============================================================

st.markdown("""
<div class="hero">

<div class="badge">
GLOBAL HEALTH DATA • LIVE DASHBOARD
</div>

<div class="hero-title">
🧬 COVID-19 Pulse
</div>

<div class="hero-subtitle">
Explore COVID-19 reporting trends across countries
using interactive charts, global comparisons,
vaccination information and downloadable data.
</div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    "## 🧬 COVID-19 Pulse"
)

st.sidebar.markdown("---")

selected_location = st.sidebar.selectbox(
    "🌍 Explore",
    country_options,
    index=0
)

st.sidebar.markdown("---")

st.sidebar.markdown(
    "### 📅 Time Period"
)

# ============================================================
# GLOBAL DATE RANGE
# ============================================================

available_dates = cases["Date"].dropna()

global_min_date = available_dates.min().date()
global_max_date = available_dates.max().date()

date_range = st.sidebar.date_input(
    "Select date range",
    value=(
        global_min_date,
        global_max_date
    ),
    min_value=global_min_date,
    max_value=global_max_date
)


# ============================================================
# FILTER DATE
# ============================================================

if len(date_range) == 2:

    start_date = pd.Timestamp(
        date_range[0]
    )

    end_date = pd.Timestamp(
        date_range[1]
    )

else:

    start_date = pd.Timestamp(
        global_min_date
    )

    end_date = pd.Timestamp(
        global_max_date
    )


filtered_cases = cases[
    (cases["Date"] >= start_date) &
    (cases["Date"] <= end_date)
].copy()

filtered_deaths = deaths[
    (deaths["Date"] >= start_date) &
    (deaths["Date"] <= end_date)
].copy()

filtered_vaccines = vaccines[
    (vaccines["Date"] >= start_date) &
    (vaccines["Date"] <= end_date)
].copy()


# ============================================================
# MODE: ALL COUNTRIES
# ============================================================

if selected_location == "🌍 All Countries":

    mode_title = "Global Overview"

    # --------------------------------------------------------
    # GLOBAL WEEKLY CASES
    # --------------------------------------------------------

    global_cases = (
        filtered_cases
        .groupby("Date", as_index=False)[case_column]
        .sum()
    )

    global_deaths = (
        filtered_deaths
        .groupby("Date", as_index=False)[death_column]
        .sum()
    )

    # --------------------------------------------------------
    # LATEST GLOBAL VALUES
    # --------------------------------------------------------

    case_values = pd.to_numeric(
        global_cases[case_column],
        errors="coerce"
    ).dropna()

    death_values = pd.to_numeric(
        global_deaths[death_column],
        errors="coerce"
    ).dropna()

    latest_global_cases = (
        case_values.iloc[-1]
        if len(case_values)
        else 0
    )

    latest_global_deaths = (
        death_values.iloc[-1]
        if len(death_values)
        else 0
    )

    # --------------------------------------------------------
    # VACCINATION GLOBAL AVERAGE
    # --------------------------------------------------------

    vaccine_numeric = pd.to_numeric(
        filtered_vaccines[vaccine_column],
        errors="coerce"
    )

    latest_vaccine_date = (
        filtered_vaccines["Date"].max()
        if len(filtered_vaccines)
        else None
    )

    if latest_vaccine_date is not None:

        latest_vaccine_data = filtered_vaccines[
            filtered_vaccines["Date"]
            == latest_vaccine_date
        ]

        latest_vaccine = (
            pd.to_numeric(
                latest_vaccine_data[vaccine_column],
                errors="coerce"
            )
            .mean()
        )

    else:

        latest_vaccine = 0


    # ========================================================
    # GLOBAL KPI
    # ========================================================

    st.markdown(
        '<div class="section-title">🌍 Global Overview</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown(
            f"""
            <div class="kpi">

            <div class="kpi-label">
            Latest Weekly Cases
            </div>

            <div class="kpi-value">
            {latest_global_cases:,.0f}
            </div>

            <div class="kpi-note">
            Worldwide reported cases
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:

        st.markdown(
            f"""
            <div class="kpi">

            <div class="kpi-label">
            Latest Weekly Deaths
            </div>

            <div class="kpi-value">
            {latest_global_deaths:,.0f}
            </div>

            <div class="kpi-note">
            Worldwide reported deaths
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:

        st.markdown(
            f"""
            <div class="kpi">

            <div class="kpi-label">
            Vaccination Coverage
            </div>

            <div class="kpi-value">
            {latest_vaccine:.1f}%
            </div>

            <div class="kpi-note">
            Average reported population share
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    # ========================================================
    # GLOBAL CASE CHART
    # ========================================================

    st.markdown(
        '<div class="section-title">📈 Global Case Trend</div>',
        unsafe_allow_html=True
    )

    fig_global_cases = px.area(
        global_cases,
        x="Date",
        y=case_column,
        title="Worldwide Weekly COVID-19 Cases"
    )

    fig_global_cases.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        )
    )

    st.plotly_chart(
        fig_global_cases,
        use_container_width=True
    )


    # ========================================================
    # GLOBAL DEATH CHART
    # ========================================================

    st.markdown(
        '<div class="section-title">🕯️ Global Death Trend</div>',
        unsafe_allow_html=True
    )

    fig_global_deaths = px.line(
        global_deaths,
        x="Date",
        y=death_column,
        title="Worldwide Weekly COVID-19 Deaths"
    )

    fig_global_deaths.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        )
    )

    st.plotly_chart(
        fig_global_deaths,
        use_container_width=True
    )


    # ========================================================
    # TOP 15 COUNTRIES
    # ========================================================

    st.markdown(
        '<div class="section-title">🌎 Country Comparison</div>',
        unsafe_allow_html=True
    )

    latest_country_cases = (
        filtered_cases
        .sort_values("Date")
        .groupby("Entity")
        .tail(1)
        .copy()
    )

    latest_country_cases[case_column] = pd.to_numeric(
        latest_country_cases[case_column],
        errors="coerce"
    )

    latest_country_cases = (
        latest_country_cases
        .dropna(subset=[case_column])
        .sort_values(
            case_column,
            ascending=False
        )
        .head(15)
    )

    fig_top = px.bar(
        latest_country_cases,
        x=case_column,
        y="Entity",
        orientation="h",
        title="Top 15 Countries — Latest Weekly Cases"
    )

    fig_top.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(
            categoryorder="total ascending"
        ),
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        )
    )

    st.plotly_chart(
        fig_top,
        use_container_width=True
    )


    # ========================================================
    # GLOBAL TABLE
    # ========================================================

    st.markdown(
        '<div class="section-title">📋 Country Data</div>',
        unsafe_allow_html=True
    )

    table = latest_country_cases[
        [
            "Entity",
            "Date",
            case_column
        ]
    ].copy()

    table.columns = [
        "Country",
        "Latest Date",
        "Weekly Cases"
    ]

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# MODE: INDIVIDUAL COUNTRY
# ============================================================

else:

    selected_country = selected_location

    mode_title = selected_country

    country_cases = filtered_cases[
        filtered_cases["Entity"]
        == selected_country
    ].copy()

    country_deaths = filtered_deaths[
        filtered_deaths["Entity"]
        == selected_country
    ].copy()

    country_vaccines = filtered_vaccines[
        filtered_vaccines["Entity"]
        == selected_country
    ].copy()

    country_cases = country_cases.sort_values(
        "Date"
    )

    country_deaths = country_deaths.sort_values(
        "Date"
    )

    country_vaccines = country_vaccines.sort_values(
        "Date"
    )

    # --------------------------------------------------------
    # VALUES
    # --------------------------------------------------------

    case_values = pd.to_numeric(
        country_cases[case_column],
        errors="coerce"
    ).dropna()

    death_values = pd.to_numeric(
        country_deaths[death_column],
        errors="coerce"
    ).dropna()

    vaccine_values = pd.to_numeric(
        country_vaccines[vaccine_column],
        errors="coerce"
    ).dropna()

    latest_cases = (
        case_values.iloc[-1]
        if len(case_values)
        else 0
    )

    latest_deaths = (
        death_values.iloc[-1]
        if len(death_values)
        else 0
    )

    latest_vaccine = (
        vaccine_values.iloc[-1]
        if len(vaccine_values)
        else 0
    )

    # --------------------------------------------------------
    # COUNTRY KPI
    # --------------------------------------------------------

    st.markdown(
        f"""
        <div class="section-title">
        📍 {selected_country} Overview
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown(
            f"""
            <div class="kpi">

            <div class="kpi-label">
            Latest Weekly Cases
            </div>

            <div class="kpi-value">
            {latest_cases:,.0f}
            </div>

            <div class="kpi-note">
            Latest reported period
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:

        st.markdown(
            f"""
            <div class="kpi">

            <div class="kpi-label">
            Latest Weekly Deaths
            </div>

            <div class="kpi-value">
            {latest_deaths:,.0f}
            </div>

            <div class="kpi-note">
            Latest reported period
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:

        st.markdown(
            f"""
            <div class="kpi">

            <div class="kpi-label">
            Fully Vaccinated
            </div>

            <div class="kpi-value">
            {latest_vaccine:.1f}%
            </div>

            <div class="kpi-note">
            Reported population share
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    # ========================================================
    # COUNTRY CASE CHART
    # ========================================================

    st.markdown(
        '<div class="section-title">📈 Case Trend</div>',
        unsafe_allow_html=True
    )

    fig_cases = px.area(
        country_cases,
        x="Date",
        y=case_column,
        title=f"Weekly COVID-19 Cases — {selected_country}"
    )

    fig_cases.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_cases,
        use_container_width=True
    )


    # ========================================================
    # COUNTRY DEATH CHART
    # ========================================================

    st.markdown(
        '<div class="section-title">🕯️ Death Trend</div>',
        unsafe_allow_html=True
    )

    fig_deaths = px.line(
        country_deaths,
        x="Date",
        y=death_column,
        title=f"Weekly COVID-19 Deaths — {selected_country}"
    )

    fig_deaths.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_deaths,
        use_container_width=True
    )


    # ========================================================
    # VACCINATION CHART
    # ========================================================

    st.markdown(
        '<div class="section-title">💉 Vaccination Progress</div>',
        unsafe_allow_html=True
    )

    fig_vaccine = px.area(
        country_vaccines,
        x="Date",
        y=vaccine_column,
        title=f"Fully Vaccinated Population — {selected_country}"
    )

    fig_vaccine.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_vaccine,
        use_container_width=True
    )


    # ========================================================
    # COUNTRY TABLE
    # ========================================================

    st.markdown(
        '<div class="section-title">📋 Recent Cases</div>',
 unsafe_allow_html=True
    )

    recent = country_cases[
        [
            "Date",
            case_column
        ]
    ].tail(15).copy()

    recent.columns = [
        "Date",
        "Weekly Cases"
    ]

    st.dataframe(
        recent,
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # DOWNLOAD
    # ========================================================

    st.markdown(
        '<div class="section-title">📥 Export Data</div>',
        unsafe_allow_html=True
    )

    csv_file = country_cases.to_csv(
        index=False
    )

    st.download_button(
        label="⬇️ Download Country CSV",
        data=csv_file,
        file_name=(
            selected_country
            .lower()
            .replace(" ", "_")
            + "_covid_data.csv"
        ),
        mime="text/csv"
    )


# ============================================================
# ABOUT
# ============================================================

st.markdown(
    '<div class="section-title">ℹ️ About This Project</div>',
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div class="info-box">

    <strong>COVID-19 Pulse</strong> is an academic
    data-visualization website designed to explore
    COVID-19 reporting data.

    <br><br>

    <strong>Current view:</strong>
    {mode_title}

    <br><br>

    <strong>Technologies:</strong>
    Python • Pandas • Plotly • Streamlit

    <br><br>

    <strong>Data:</strong>
    Our World in Data and official reporting sources,
    including the World Health Organization.

    <br><br>

    The figures represent reported surveillance data.
    Reporting gaps, revisions and differences between
    countries can affect comparisons.

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">

    <strong>🧬 COVID-19 Pulse</strong>

    <br><br>

    Developed by
    <strong>Rashpreet Kaur Arora</strong>

    <br>

    BCA 2nd Year Student

    <br><br>

    Academic Data Visualization Project

    </div>
    """,
    unsafe_allow_html=True
)
