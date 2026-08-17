import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="COVID-19 Pulse",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(
            circle at 5% 5%,
            rgba(0, 220, 255, 0.14),
            transparent 25%
        ),
        radial-gradient(
            circle at 95% 10%,
            rgba(100, 70, 255, 0.16),
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

/* SIDEBAR */

section[data-testid="stSidebar"] {
    background: #081525;
    border-right: 1px solid rgba(255,255,255,0.08);
}

/* HERO */

.hero {
    padding: 42px;
    border-radius: 30px;
    margin-bottom: 28px;

    background:
        linear-gradient(
            135deg,
            rgba(0,220,255,0.16),
            rgba(83,73,255,0.18)
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
    max-width: 850px;

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

/* SECTIONS */

.section-title {
    margin-top: 32px;
    margin-bottom: 15px;

    font-size: 25px;
    font-weight: 750;
}

/* INFO */

.info-box {
    padding: 24px;

    border-radius: 20px;

    background: rgba(12,27,46,0.85);

    border: 1px solid rgba(255,255,255,0.07);

    color: #b9c8d9;

    line-height: 1.7;
}

/* FOOTER */

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
    "?v=1&csvType=full&useColumnShortNames=false"
)

DEATHS_URL = (
    "https://ourworldindata.org/grapher/"
    "weekly-covid-deaths.csv"
    "?v=1&csvType=full&useColumnShortNames=false"
)

VACCINE_URL = (
    "https://ourworldindata.org/grapher/"
    "share-people-fully-vaccinated-covid.csv"
    "?v=1&csvType=full&useColumnShortNames=false"
)


# ============================================================
# LOAD CSV
# ============================================================

@st.cache_data(ttl=3600)
def load_csv(url):

    df = pd.read_csv(
        url,
        storage_options={
            "User-Agent":
            "Mozilla/5.0 COVID-19-Pulse-Dashboard"
        }
    )

    # --------------------------------------------------------
    # STANDARDIZE COLUMN NAMES
    # --------------------------------------------------------

    df.columns = [
        str(column).strip().lower()
        for column in df.columns
    ]

    # --------------------------------------------------------
    # RENAME COMMON OWID COLUMNS
    # --------------------------------------------------------

    rename_map = {}

    for column in df.columns:

        if column == "entity":
            rename_map[column] = "Entity"

        elif column == "code":
            rename_map[column] = "Code"

        elif column == "date":
            rename_map[column] = "Date"

    df = df.rename(
        columns=rename_map
    )

    # --------------------------------------------------------
    # CHECK REQUIRED COLUMNS
    # --------------------------------------------------------

    if "Date" not in df.columns:

        raise ValueError(
            "Date column not found. "
            "Columns received: "
            + str(df.columns.tolist())
        )

    if "Entity" not in df.columns:

        raise ValueError(
            "Entity column not found. "
            "Columns received: "
            + str(df.columns.tolist())
        )

    # --------------------------------------------------------
    # DATE CONVERSION
    # --------------------------------------------------------

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    return df


# ============================================================
# LOAD ALL DATA
# ============================================================

@st.cache_data(ttl=3600)
def load_all_data():

    cases = load_csv(
        CASES_URL
    )

    deaths = load_csv(
        DEATHS_URL
    )

    vaccines = load_csv(
        VACCINE_URL
    )

    return cases, deaths, vaccines


# ============================================================
# ERROR HANDLING
# ============================================================

try:

    cases, deaths, vaccines = load_all_data()

except Exception as error:

    st.error(
        "Could not load COVID-19 data."
    )

    st.warning(
        "The COVID-19 data source could not "
        "be loaded correctly."
    )

    st.code(
        str(error)
    )

    st.stop()


# ============================================================
# FIND VALUE COLUMNS
# ============================================================

def find_value_column(df):

    ignored_columns = {
        "Entity",
        "Code",
        "Date"
    }

    possible_columns = [
        column
        for column in df.columns
        if column not in ignored_columns
    ]

    if len(possible_columns) == 0:

        raise ValueError(
            "No data value column was found. "
            "Available columns: "
            + str(df.columns.tolist())
        )

    return possible_columns[0]


case_col = find_value_column(
    cases
)

death_col = find_value_column(
    deaths
)

vaccine_col = find_value_column(
    vaccines
)


# ============================================================
# CONVERT DATA TO NUMERIC
# ============================================================

cases[case_col] = pd.to_numeric(
    cases[case_col],
    errors="coerce"
)

deaths[death_col] = pd.to_numeric(
    deaths[death_col],
    errors="coerce"
)

vaccines[vaccine_col] = pd.to_numeric(
    vaccines[vaccine_col],
    errors="coerce"
)


# ============================================================
# COUNTRY LIST
# ============================================================

countries = sorted(
    cases["Entity"]
    .dropna()
    .unique()
    .tolist()
)

country_options = [
    "🌍 All Countries"
] + countries


# ============================================================
# HERO
# ============================================================

st.markdown("""
<div class="hero">

<div class="badge">
GLOBAL HEALTH DATA • COVID-19
</div>

<div class="hero-title">
🦠 COVID-19 Pulse
</div>

<div class="hero-subtitle">
Explore COVID-19 trends across countries with
interactive charts, global comparisons,
vaccination information and downloadable data.
</div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    "## 🦠 COVID-19 Pulse"
)

st.sidebar.markdown("---")

selected_country = st.sidebar.selectbox(
    "🌍 Select Country",
    country_options
)

st.sidebar.markdown("---")

st.sidebar.markdown(
    "### 📅 Time Period"
)


# ============================================================
# DATE RANGE
# ============================================================

valid_dates = (
    cases["Date"]
    .dropna()
)

if valid_dates.empty:

    st.error(
        "No valid COVID-19 dates were found."
    )

    st.stop()

min_date = valid_dates.min().date()
max_date = valid_dates.max().date()

date_range = st.sidebar.date_input(
    "Select date range",
    value=(
        min_date,
        max_date
    ),
    min_value=min_date,
    max_value=max_date
)


if isinstance(date_range, tuple) and len(date_range) == 2:

    start_date = pd.Timestamp(
        date_range[0]
    )

    end_date = pd.Timestamp(
        date_range[1]
    )

else:

    start_date = pd.Timestamp(
        min_date
    )

    end_date = pd.Timestamp(
        max_date
    )


# ============================================================
# FILTER DATA
# ============================================================

filtered_cases = cases[
    (cases["Date"] >= start_date)
    &
    (cases["Date"] <= end_date)
].copy()

filtered_deaths = deaths[
    (deaths["Date"] >= start_date)
    &
    (deaths["Date"] <= end_date)
].copy()

filtered_vaccines = vaccines[
    (vaccines["Date"] >= start_date)
    &
    (vaccines["Date"] <= end_date)
].copy()


# ============================================================
# ALL COUNTRIES MODE
# ============================================================

if selected_country == "🌍 All Countries":

    st.markdown(
        '<div class="section-title">'
        '🌍 Global Overview'
        '</div>',
        unsafe_allow_html=True
    )

    # ========================================================
    # GLOBAL CASES
    # ========================================================

    global_cases = (
        filtered_cases
        .groupby(
            "Date",
            as_index=False
        )[case_col]
        .sum()
    )

    global_cases[case_col] = pd.to_numeric(
        global_cases[case_col],
        errors="coerce"
    )

    # ========================================================
    # GLOBAL DEATHS
    # ========================================================

    global_deaths = (
        filtered_deaths
        .groupby(
            "Date",
            as_index=False
        )[death_col]
        .sum()
    )

    global_deaths[death_col] = pd.to_numeric(
        global_deaths[death_col],
        errors="coerce"
    )

    # ========================================================
    # LATEST CASES
    # ========================================================

    case_values = (
        global_cases[case_col]
        .dropna()
    )

    if len(case_values) > 0:

        latest_cases = case_values.iloc[-1]

    else:

        latest_cases = 0


    # ========================================================
    # LATEST DEATHS
    # ========================================================

    death_values = (
        global_deaths[death_col]
        .dropna()
    )

    if len(death_values) > 0:

        latest_deaths = death_values.iloc[-1]

    else:

        latest_deaths = 0


    # ========================================================
    # GLOBAL VACCINATION
    # ========================================================

    latest_vaccine = 0

    if not filtered_vaccines.empty:

        latest_vaccine_date = (
            filtered_vaccines["Date"]
            .max()
        )

        latest_vaccine_data = (
            filtered_vaccines[
                filtered_vaccines["Date"]
                == latest_vaccine_date
            ]
        )

        vaccine_values = pd.to_numeric(
            latest_vaccine_data[
                vaccine_col
            ],
            errors="coerce"
        )

        if not vaccine_values.dropna().empty:

            latest_vaccine = (
                vaccine_values
                .dropna()
                .mean()
            )


    # ========================================================
    # KPI CARDS
    # ========================================================

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
            {latest_deaths:,.0f}
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
        '<div class="section-title">'
        '📈 Global Case Trend'
        '</div>',
        unsafe_allow_html=True
    )

    fig_cases = px.area(
        global_cases,
        x="Date",
        y=case_col,
        title="Worldwide Weekly COVID-19 Cases"
    )

    fig_cases.update_layout(
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
        fig_cases,
        use_container_width=True
    )


    # ========================================================
    # GLOBAL DEATH CHART
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🕯️ Global Death Trend'
        '</div>',
        unsafe_allow_html=True
    )

    fig_deaths = px.line(
        global_deaths,
        x="Date",
        y=death_col,
        title="Worldwide Weekly COVID-19 Deaths"
    )

    fig_deaths.update_layout(
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
        fig_deaths,
        use_container_width=True
        )
    # ========================================================
    # COUNTRY COMPARISON
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🌎 Country Comparison'
        '</div>',
        unsafe_allow_html=True
    )

    latest_country = (
        filtered_cases
        .sort_values("Date")
        .groupby("Entity")
        .tail(1)
        .copy()
    )

    latest_country[case_col] = pd.to_numeric(
        latest_country[case_col],
        errors="coerce"
    )

    latest_country = (
        latest_country
        .dropna(
            subset=[case_col]
        )
        .sort_values(
            case_col,
            ascending=False
        )
        .head(15)
    )


    # ========================================================
    # BAR CHART
    # ========================================================

    fig_rank = px.bar(
        latest_country,
        x=case_col,
        y="Entity",
        orientation="h",
        title=(
            "Top 15 Countries — "
            "Latest Weekly Cases"
        )
    )

    fig_rank.update_layout(
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
        fig_rank,
        use_container_width=True
    )


    # ========================================================
    # COUNTRY TABLE
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '📋 Country Data'
        '</div>',
        unsafe_allow_html=True
    )

    table = latest_country[
        [
            "Entity",
            "Date",
            case_col
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


    # ========================================================
    # DOWNLOAD
    # ========================================================

    st.download_button(
        "⬇️ Download Global Country Data",
        data=table.to_csv(
            index=False
        ),
        file_name=(
            "global_covid_country_data.csv"
        ),
        mime="text/csv"
    )


# ============================================================
# INDIVIDUAL COUNTRY MODE
# ============================================================

else:

    country = selected_country

    st.markdown(
        f"""
        <div class="section-title">
        📍 {country} Overview
        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # COUNTRY DATA
    # ========================================================

    country_cases = filtered_cases[
        filtered_cases["Entity"]
        == country
    ].copy()

    country_deaths = filtered_deaths[
        filtered_deaths["Entity"]
        == country
    ].copy()

    country_vaccines = filtered_vaccines[
        filtered_vaccines["Entity"]
        == country
    ].copy()


    # ========================================================
    # SORT
    # ========================================================

    country_cases = country_cases.sort_values(
        "Date"
    )

    country_deaths = country_deaths.sort_values(
        "Date"
    )

    country_vaccines = country_vaccines.sort_values(
        "Date"
    )


    # ========================================================
    # LATEST CASES
    # ========================================================

    case_values = pd.to_numeric(
        country_cases[case_col],
        errors="coerce"
    ).dropna()

    if len(case_values) > 0:

        latest_cases = case_values.iloc[-1]

    else:

        latest_cases = 0


    # ========================================================
    # LATEST DEATHS
    # ========================================================

    death_values = pd.to_numeric(
        country_deaths[death_col],
        errors="coerce"
    ).dropna()

    if len(death_values) > 0:

        latest_deaths = death_values.iloc[-1]

    else:

        latest_deaths = 0


    # ========================================================
    # LATEST VACCINATION
    # ========================================================

    vaccine_values = pd.to_numeric(
        country_vaccines[vaccine_col],
        errors="coerce"
    ).dropna()

    if len(vaccine_values) > 0:

        latest_vaccine = vaccine_values.iloc[-1]

    else:

        latest_vaccine = 0


    # ========================================================
    # KPI CARDS
    # ========================================================

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
        '<div class="section-title">'
        '📈 Case Trend'
        '</div>',
        unsafe_allow_html=True
    )

    fig_country_cases = px.area(
        country_cases,
        x="Date",
        y=case_col,
        title=(
            f"Weekly COVID-19 Cases — "
            f"{country}"
        )
    )

    fig_country_cases.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_country_cases,
        use_container_width=True
    )


    # ========================================================
    # COUNTRY DEATH CHART
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🕯️ Death Trend'
        '</div>',
        unsafe_allow_html=True
    )

    fig_country_deaths = px.line(
        country_deaths,
        x="Date",
        y=death_col,
        title=(
            f"Weekly COVID-19 Deaths — "
            f"{country}"
        )
    )

    fig_country_deaths.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_country_deaths,
        use_container_width=True
    )


    # ========================================================
    # VACCINATION CHART
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '💉 Vaccination Progress'
        '</div>',
        unsafe_allow_html=True
    )

    fig_country_vaccine = px.area(
        country_vaccines,
        x="Date",
        y=vaccine_col,
        title=(
            f"Fully Vaccinated Population — "
            f"{country}"
        )
    )

    fig_country_vaccine.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_country_vaccine,
        use_container_width=True
    )


    # ========================================================
    # RECENT DATA
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '📋 Recent Data'
        '</div>',
        unsafe_allow_html=True
    )

    recent = country_cases[
        [
            "Date",
            case_col
        ]
    ].tail(20).copy()

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
    # DOWNLOAD COUNTRY DATA
    # ========================================================

    st.download_button(
        "⬇️ Download Country CSV",
        data=country_cases.to_csv(
            index=False
        ),
        file_name=(
            country.lower()
            .replace(" ", "_")
            .replace(",", "")
            + "_covid_data.csv"
        ),
        mime="text/csv"
    )


# ============================================================
# ABOUT PROJECT
# ============================================================

st.markdown(
    '<div class="section-title">'
    'ℹ️ About This Project'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="info-box">

    <strong>COVID-19 Pulse</strong> is a
    Python-based data visualization project.

    <br><br>

    Technologies used:

    <br>
    • Python
    <br>
    • Pandas
    <br>
    • Plotly
    <br>
    • Streamlit

    <br><br>

    The dashboard provides global and
    country-level COVID-19 reporting trends,
    interactive charts, vaccination information,
    country comparison and CSV downloads.

    <br><br>

    COVID-19 reporting can vary between countries
    because of differences in testing,
    reporting practices and data revisions.

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

    🦠 <strong>COVID-19 Pulse</strong>

    <br><br>

    Developed by
    <strong>Rashpreet Kaur Arora</strong>

    <br>

    BCA 2nd Year

    </div>
    """,
    unsafe_allow_html=True
    )
