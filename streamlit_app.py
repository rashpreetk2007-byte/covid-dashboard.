import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="COVID-19 Pulse",
    page_icon="🦠",
    layout="wide"
)

# ============================================================
# CUSTOM DESIGN
# ============================================================

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(circle at 10% 10%,
        rgba(0, 210, 255, 0.12),
        transparent 25%),
        radial-gradient(circle at 90% 10%,
        rgba(100, 80, 255, 0.15),
        transparent 25%),
        #07111f;
}

.block-container {
    max-width: 1400px;
    padding-top: 2rem;
}

.hero {
    padding: 40px;
    border-radius: 28px;
    margin-bottom: 25px;

    background:
        linear-gradient(
            135deg,
            rgba(0,210,255,.15),
            rgba(90,70,255,.18)
        );

    border: 1px solid rgba(255,255,255,.12);
}

.hero-title {
    font-size: 46px;
    font-weight: 800;
}

.hero-text {
    color: #aabbd0;
    font-size: 17px;
    margin-top: 10px;
}

.card {
    padding: 24px;
    border-radius: 20px;

    background: rgba(15,32,53,.90);

    border: 1px solid rgba(255,255,255,.08);

    margin-bottom: 20px;
}

.card-title {
    color: #91a6bc;
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
}

.card-value {
    color: white;
    font-size: 30px;
    font-weight: 800;
    margin-top: 8px;
}

.section {
    font-size: 25px;
    font-weight: 750;
    margin-top: 30px;
    margin-bottom: 15px;
}

.footer {
    text-align: center;
    padding: 30px;
    margin-top: 40px;
    border-top: 1px solid rgba(255,255,255,.08);
    color: #8da0b5;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA URLs
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
# LOAD DATA
# ============================================================

@st.cache_data(ttl=3600)
def load_csv(url):

    return pd.read_csv(
        url,
        storage_options={
            "User-Agent":
            "COVID-19 Pulse Dashboard/1.0"
        }
    )


@st.cache_data(ttl=3600)
def load_all_data():

    cases = load_csv(CASES_URL)
    deaths = load_csv(DEATHS_URL)
    vaccines = load_csv(VACCINE_URL)

    cases["Date"] = pd.to_datetime(
        cases["Date"]
    )

    deaths["Date"] = pd.to_datetime(
        deaths["Date"]
    )

    vaccines["Date"] = pd.to_datetime(
        vaccines["Date"]
    )

    return cases, deaths, vaccines


# ============================================================
# ERROR HANDLING
# ============================================================

try:

    cases, deaths, vaccines = load_all_data()

except Exception as error:

    st.error("Could not load COVID-19 data.")

    st.warning(
        "The external COVID-19 data source rejected "
        "the request or is temporarily unavailable."
    )

    st.code(str(error))

    st.stop()


# ============================================================
# FIND DATA COLUMNS
# ============================================================

def value_column(df):

    ignored = {
        "Entity",
        "Code",
        "Date"
    }

    columns = [
        c for c in df.columns
        if c not in ignored
    ]

    if not columns:
        raise ValueError(
            "No numeric data column found."
        )

    return columns[0]


case_col = value_column(cases)
death_col = value_column(deaths)
vaccine_col = value_column(vaccines)


# ============================================================
# COUNTRY LIST
# ============================================================

countries = sorted(
    cases["Entity"]
    .dropna()
    .unique()
)

country_options = [
    "🌍 All Countries"
] + countries.tolist()


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="hero">

<div class="hero-title">
🦠 COVID-19 Pulse
</div>

<div class="hero-text">
A global COVID-19 data visualization dashboard
with country comparison, trends, vaccination data
and downloadable information.
</div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🦠 COVID-19 Pulse")

st.sidebar.markdown("---")

selected_country = st.sidebar.selectbox(
    "🌍 Select Country",
    country_options
)

st.sidebar.markdown("---")

st.sidebar.caption(
    "Data source: Our World in Data / WHO"
)


# ============================================================
# DATE RANGE
# ============================================================

min_date = cases["Date"].min().date()
max_date = cases["Date"].max().date()

date_range = st.sidebar.date_input(
    "📅 Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:

    start_date = pd.Timestamp(
        date_range[0]
    )

    end_date = pd.Timestamp(
        date_range[1]
    )

else:

    start_date = pd.Timestamp(min_date)
    end_date = pd.Timestamp(max_date)


# ============================================================
# FILTER DATA
# ============================================================

cases_filtered = cases[
    (cases["Date"] >= start_date) &
    (cases["Date"] <= end_date)
].copy()

deaths_filtered = deaths[
    (deaths["Date"] >= start_date) &
    (deaths["Date"] <= end_date)
].copy()

vaccines_filtered = vaccines[
    (vaccines["Date"] >= start_date) &
    (vaccines["Date"] <= end_date)
].copy()


# ============================================================
# GLOBAL MODE
# ============================================================

if selected_country == "🌍 All Countries":

    st.markdown(
        '<div class="section">🌍 Global Overview</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # GLOBAL CASES
    # --------------------------------------------------------

    global_cases = (
        cases_filtered
        .groupby("Date", as_index=False)[case_col]
        .sum()
    )

    global_cases[case_col] = pd.to_numeric(
        global_cases[case_col],
        errors="coerce"
    )

    # --------------------------------------------------------
    # GLOBAL DEATHS
    # --------------------------------------------------------

    global_deaths = (
        deaths_filtered
        .groupby("Date", as_index=False)[death_col]
        .sum()
    )

    global_deaths[death_col] = pd.to_numeric(
        global_deaths[death_col],
        errors="coerce"
    )

    # --------------------------------------------------------
    # LATEST VALUES
    # --------------------------------------------------------

    latest_cases = (
        global_cases[case_col]
        .dropna()
        .iloc[-1]
        if not global_cases.empty
        else 0
    )

    latest_deaths = (
        global_deaths[death_col]
        .dropna()
        .iloc[-1]
        if not global_deaths.empty
        else 0
    )

    # --------------------------------------------------------
    # VACCINATION
    # --------------------------------------------------------

    latest_vaccine = 0

    if not vaccines_filtered.empty:

        vaccine_values = pd.to_numeric(
            vaccines_filtered[vaccine_col],
            errors="coerce"
        )

        latest_date = (
            vaccines_filtered["Date"].max()
        )

        latest_vaccine_data = vaccines_filtered[
            vaccines_filtered["Date"]
            == latest_date
        ]

        latest_vaccine = (
            pd.to_numeric(
                latest_vaccine_data[vaccine_col],
                errors="coerce"
            )
            .mean()
        )

        if pd.isna(latest_vaccine):
            latest_vaccine = 0

    # --------------------------------------------------------
    # CARDS
    # --------------------------------------------------------

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown(
            f"""
            <div class="card">

            <div class="card-title">
            Latest Weekly Cases
            </div>

            <div class="card-value">
            {latest_cases:,.0f}
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:

        st.markdown(
            f"""
            <div class="card">

            <div class="card-title">
            Latest Weekly Deaths
            </div>

            <div class="card-value">
            {latest_deaths:,.0f}
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:

        st.markdown(
            f"""
            <div class="card">

            <div class="card-title">
            Vaccination Coverage
            </div>

            <div class="card-value">
            {latest_vaccine:.1f}%
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # CASE CHART
    # --------------------------------------------------------

    st.markdown(
        '<div class="section">📈 Global Case Trend</div>',
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
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_cases,
        use_container_width=True
    )

    # --------------------------------------------------------
    # DEATH CHART
    # --------------------------------------------------------

    st.markdown(
        '<div class="section">🕯️ Global Death Trend</div>',
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
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_deaths,
        use_container_width=True
    )

    # --------------------------------------------------------
    # COUNTRY RANKING
    # --------------------------------------------------------

    st.markdown(
        '<div class="section">🌎 Country Comparison</div>',
        unsafe_allow_html=True
    )

    latest = (
        cases_filtered
        .sort_values("Date")
        .groupby("Entity")
        .tail(1)
        .copy()
    )

    latest[case_col] = pd.to_numeric(
        latest[case_col],
        errors="coerce"
    )

    latest = (
        latest
        .dropna(subset=[case_col])
        .sort_values(
            case_col,
            ascending=False
        )
        .head(15)
    )

    fig_rank = px.bar(
        latest,
        x=case_col,
        y="Entity",
        orientation="h",
        title="Top 15 Countries by Latest Weekly Cases"
    )

    fig_rank.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(
            categoryorder="total ascending"
        )
    )

    st.plotly_chart(
        fig_rank,
        use_container_width=True
    )

    # --------------------------------------------------------
    # TABLE
    # --------------------------------------------------------

    table = latest[
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

    st.markdown(
        '<div class="section">📋 Country Data</div>',
        unsafe_allow_html=True
    )

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------------

    st.download_button(
        "⬇️ Download Global Country Data",
        data=table.to_csv(index=False),
        file_name="global_covid_country_data.csv",
        mime="text/csv"
    )


# ============================================================
# COUNTRY MODE
# ============================================================

else:

    country = selected_country

    st.markdown(
        f"""
        <div class="section">
        📍 {country} Dashboard
        </div>
        """,
        unsafe_allow_html=True
    )

    country_cases = cases_filtered[
        cases_filtered["Entity"] == country
    ].copy()

    country_deaths = deaths_filtered[
        deaths_filtered["Entity"] == country
    ].copy()

    country_vaccine = vaccines_filtered[
        vaccines_filtered["Entity"] == country
    ].copy()

    # --------------------------------------------------------
    # VALUES
    # --------------------------------------------------------

    country_cases[case_col] = pd.to_numeric(
        country_cases[case_col],
        errors="coerce"
    )

    country_deaths[death_col] = pd.to_numeric(
        country_deaths[death_col],
        errors="coerce"
    )

    country_vaccine[vaccine_col] = pd.to_numeric(
        country_vaccine[vaccine_col],
        errors="coerce"
    )

    latest_cases = (
        country_cases[case_col]
        .dropna()
        .iloc[-1]
        if not country_cases.empty
        else 0
    )

    latest_deaths = (
        country_deaths[death_col]
        .dropna()
        .iloc[-1]
        if not country_deaths.empty
        else 0
    )

    latest_vaccine = (
        country_vaccine[vaccine_col]
        .dropna()
        .iloc[-1]
        if not country_vaccine.empty
        else 0
    )

    # --------------------------------------------------------
    # CARDS
    # --------------------------------------------------------

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown(
            f"""
            <div class="card">

            <div class="card-title">
            Latest Weekly Cases
            </div>

            <div class="card-value">
            {latest_cases:,.0f}
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:

        st.markdown(
            f"""
            <div class="card">

            <div class="card-title">
            Latest Weekly Deaths
            </div>

            <div class="card-value">
            {latest_deaths:,.0f}
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:

        st.markdown(
            f"""
            <div class="card">

            <div class="card-title">
            Fully Vaccinated
            </div>

            <div class="card-value">
            {latest_vaccine:.1f}%
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # CASES
    # --------------------------------------------------------

    fig_cases = px.area(
        country_cases,
        x="Date",
        y=case_col,
        title=f"Weekly COVID-19 Cases — {country}"
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

    # --------------------------------------------------------
    # DEATHS
    # --------------------------------------------------------

    fig_deaths = px.line(
        country_deaths,
        x="Date",
        y=death_col,
        title=f"Weekly COVID-19 Deaths — {country}"
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

    # --------------------------------------------------------
    # VACCINATION
    # --------------------------------------------------------

    fig_vaccine = px.area(
        country_vaccine,
        x="Date",
        y=vaccine_col,
        title=f"Vaccination Progress — {country}"
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

    # --------------------------------------------------------
    # DATA TABLE
    # --------------------------------------------------------

    st.markdown(
        '<div class="section">📋 Recent Data</div>',
        unsafe_allow_html=True
    )

    recent = country_cases[
        [
            "Date",
            case_col
        ]
    ].tail(20)

    recent.columns = [
        "Date",
        "Weekly Cases"
    ]

    st.dataframe(
        recent,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------------

    st.download_button(
        "⬇️ Download Country CSV",
        data=country_cases.to_csv(index=False),
        file_name=(
            country.lower()
            .replace(" ", "_")
            + "_covid_data.csv"
        ),
        mime="text/csv"
    )


# ============================================================
# ABOUT
# ============================================================

st.markdown(
    '<div class="section">ℹ️ About This Project</div>',
    unsafe_allow_html=True
)

st.info(
    """
    COVID-19 Pulse is an academic data-visualization
    project created using Python, Pandas, Plotly and
    Streamlit.

    The dashboard uses COVID-19 reporting data processed
    by Our World in Data, including data originating from
    the World Health Organization.

    Reported COVID-19 figures can be affected by changes
    in testing, reporting practices, revisions and
    differences between countries.
    """
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
