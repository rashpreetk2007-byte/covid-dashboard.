import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# PAGE CONFIG
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

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(
            circle at 5% 5%,
            rgba(0, 220, 255, 0.13),
            transparent 25%
        ),
        radial-gradient(
            circle at 95% 10%,
            rgba(100, 80, 255, 0.16),
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
        );

    border: 1px solid rgba(255,255,255,0.10);

    box-shadow:
        0 25px 70px rgba(0,0,0,0.30);
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

.hero-text {
    margin-top: 12px;

    max-width: 850px;

    color: #a9bad0;

    font-size: 17px;

    line-height: 1.7;
}


/* KPI CARDS */

.kpi {
    padding: 24px;

    min-height: 140px;

    border-radius: 22px;

    background:
        rgba(14,30,50,0.90);

    border:
        1px solid rgba(255,255,255,0.08);

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

    color: white;
}

.kpi-note {
    margin-top: 7px;

    color: #6eeaff;

    font-size: 12px;
}


/* SECTIONS */

.section-title {
    margin-top: 30px;

    margin-bottom: 15px;

    font-size: 25px;

    font-weight: 750;
}


/* INFO */

.info-box {
    padding: 24px;

    border-radius: 20px;

    background:
        rgba(12,27,46,0.85);

    border:
        1px solid rgba(255,255,255,0.07);

    color: #b9c8d9;

    line-height: 1.7;
}


/* FOOTER */

.footer {
    margin-top: 50px;

    padding: 30px;

    text-align: center;

    border-top:
        1px solid rgba(255,255,255,0.08);

    color: #8ea1b7;
}

.footer strong {
    color: white;
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
# LOAD CSV
# ============================================================

@st.cache_data(ttl=3600)
def load_csv(url):

    return pd.read_csv(
        url,
        storage_options={
            "User-Agent":
            "Mozilla/5.0 COVID-19 Pulse Dashboard"
        }
    )


# ============================================================
# NORMALIZE DATE COLUMN
# ============================================================

def normalize_date_column(df):

    df = df.copy()

    # Some OWID datasets use "day"
    if "Date" in df.columns:

        df["Date"] = pd.to_datetime(
            df["Date"],
            errors="coerce"
        )

        return df

    if "date" in df.columns:

        df["Date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

        return df

    if "day" in df.columns:

        df["Date"] = pd.to_datetime(
            df["day"],
            errors="coerce"
        )

        return df

    raise ValueError(
        "Date column not found. Columns received: "
        + str(df.columns.tolist())
    )


# ============================================================
# FIND VALUE COLUMN
# ============================================================

def find_value_column(df):

    ignored = {
        "Entity",
        "Code",
        "Date",
        "date",
        "day"
    }

    possible_columns = [
        column
        for column in df.columns
        if column not in ignored
    ]

    if not possible_columns:

        raise ValueError(
            "No data value column found. Columns received: "
            + str(df.columns.tolist())
        )

    return possible_columns[0]


# ============================================================
# LOAD ALL DATA
# ============================================================

@st.cache_data(ttl=3600)
def load_all_data():

    cases = load_csv(CASES_URL)

    deaths = load_csv(DEATHS_URL)

    vaccines = load_csv(VACCINE_URL)

    cases = normalize_date_column(cases)

    deaths = normalize_date_column(deaths)

    vaccines = normalize_date_column(vaccines)

    case_col = find_value_column(cases)

    death_col = find_value_column(deaths)

    vaccine_col = find_value_column(vaccines)

    return (
        cases,
        deaths,
        vaccines,
        case_col,
        death_col,
        vaccine_col
    )


# ============================================================
# ERROR HANDLING
# ============================================================

try:

    (
        cases,
        deaths,
        vaccines,
        case_col,
        death_col,
        vaccine_col
    ) = load_all_data()

except Exception as error:

    st.error(
        "Could not load COVID-19 data."
    )

    st.warning(
        "The COVID-19 data source could not be "
        "loaded or its format has changed."
    )

    st.code(str(error))

    st.stop()


# ============================================================
# CLEAN DATA
# ============================================================

cases = cases.dropna(
    subset=["Entity", "Date"]
).copy()

deaths = deaths.dropna(
    subset=["Entity", "Date"]
).copy()

vaccines = vaccines.dropna(
    subset=["Entity", "Date"]
).copy()


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

<div class="hero-text">
Explore COVID-19 trends across countries with
interactive statistics, global comparisons,
case trends, death trends, vaccination data
and downloadable information.
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

min_date = cases["Date"].min().date()

max_date = cases["Date"].max().date()


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

cases_filtered = cases[
    (cases["Date"] >= start_date)
    &
    (cases["Date"] <= end_date)
].copy()


deaths_filtered = deaths[
    (deaths["Date"] >= start_date)
    &
    (deaths["Date"] <= end_date)
].copy()


vaccines_filtered = vaccines[
    (vaccines["Date"] >= start_date)
    &
    (vaccines["Date"] <= end_date)
].copy()


# ============================================================
# GLOBAL MODE
# ============================================================

if selected_country == "🌍 All Countries":

    st.markdown(
        '<div class="section-title">'
        '🌍 Global Overview'
        '</div>',
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # IMPORTANT:
    # Do NOT add continent/World aggregate rows.
    # Keep actual countries only.
    # --------------------------------------------------------

    global_cases_data = cases_filtered.copy()

    if "Code" in global_cases_data.columns:

        global_cases_data = global_cases_data[
            ~global_cases_data["Code"]
            .astype(str)
            .str.startswith("OWID_")
        ]


    global_deaths_data = deaths_filtered.copy()

    if "Code" in global_deaths_data.columns:

        global_deaths_data = global_deaths_data[
            ~global_deaths_data["Code"]
            .astype(str)
            .str.startswith("OWID_")
        ]
        # --------------------------------------------------------
    # GLOBAL CASES
    # --------------------------------------------------------

    global_cases = (
        global_cases_data
        .groupby(
            "Date",
            as_index=False
        )[case_col]
        .sum()
    )


    # --------------------------------------------------------
    # GLOBAL DEATHS
    # --------------------------------------------------------

    global_deaths = (
        global_deaths_data
        .groupby(
            "Date",
            as_index=False
        )[death_col]
        .sum()
    )


    # --------------------------------------------------------
    # LATEST CASES
    # --------------------------------------------------------

    if not global_cases.empty:

        latest_cases = (
            global_cases[case_col]
            .dropna()
            .iloc[-1]
        )

    else:

        latest_cases = 0


    # --------------------------------------------------------
    # LATEST DEATHS
    # --------------------------------------------------------

    if not global_deaths.empty:

        latest_deaths = (
            global_deaths[death_col]
            .dropna()
            .iloc[-1]
        )

    else:

        latest_deaths = 0


    # --------------------------------------------------------
    # GLOBAL VACCINATION
    # --------------------------------------------------------

    latest_vaccine = 0


    if not vaccines_filtered.empty:

        vaccine_data = vaccines_filtered.copy()

        if "Code" in vaccine_data.columns:

            vaccine_data = vaccine_data[
                ~vaccine_data["Code"]
                .astype(str)
                .str.startswith("OWID_")
            ]


        latest_vaccine_date = (
            vaccine_data["Date"].max()
        )


        latest_vaccine_rows = vaccine_data[
            vaccine_data["Date"]
            == latest_vaccine_date
        ]


        latest_vaccine = (
            latest_vaccine_rows[
                vaccine_col
            ]
            .dropna()
            .mean()
        )


        if pd.isna(latest_vaccine):

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
    # CASE TREND
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
        hovermode="x unified"
    )


    st.plotly_chart(
        fig_cases,
        use_container_width=True
    )


    # ========================================================
    # DEATH TREND
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
        hovermode="x unified"
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
        global_cases_data
        .sort_values("Date")
        .groupby("Entity")
        .tail(1)
        .copy()
    )


    latest_country = latest_country.dropna(
        subset=[case_col]
    )


    latest_country = (
        latest_country
        .sort_values(
            case_col,
            ascending=False
        )
        .head(20)
    )


    fig_rank = px.bar(
        latest_country,
        x=case_col,
        y="Entity",
        orientation="h",
        title="Top 20 Countries — Latest Weekly Cases"
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


    # ========================================================
    # COUNTRY TABLE
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '📋 Global Country Data'
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

        file_name=
        "global_covid_country_data.csv",

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
        📍 {country} Dashboard
        </div>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # FILTER COUNTRY
    # --------------------------------------------------------

    country_cases = cases_filtered[
        cases_filtered["Entity"]
        == country
    ].copy()


    country_deaths = deaths_filtered[
        deaths_filtered["Entity"]
        == country
    ].copy()


    country_vaccine = vaccines_filtered[
        vaccines_filtered["Entity"]
        == country
    ].copy()


    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    country_cases = country_cases.sort_values(
        "Date"
    )

    country_deaths = country_deaths.sort_values(
        "Date"
    )

    country_vaccine = country_vaccine.sort_values(
        "Date"
    )


    # --------------------------------------------------------
    # LATEST VALUES
    # --------------------------------------------------------

    if not country_cases.empty:

        latest_cases = (
            country_cases[case_col]
            .dropna()
            .iloc[-1]
        )

    else:

        latest_cases = 0


    if not country_deaths.empty:

        latest_deaths = (
            country_deaths[death_col]
            .dropna()
            .iloc[-1]
        )

    else:

        latest_deaths = 0


    if not country_vaccine.empty:

        latest_vaccine = (
            country_vaccine[vaccine_col]
            .dropna()
            .iloc[-1]
        )

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
    # CASE CHART
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '📈 Case Trend'
        '</div>',
        unsafe_allow_html=True
    )


    if not country_cases.empty:

        fig_cases = px.area(
            country_cases,
            x="Date",
            y=case_col,
            title=
            f"Weekly COVID-19 Cases — {country}"
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

    else:

        st.info(
            "No case data available for this country "
            "in the selected period."
        )


    # ========================================================
    # DEATH CHART
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🕯️ Death Trend'
        '</div>',
        unsafe_allow_html=True
    )


    if not country_deaths.empty:

        fig_deaths = px.line(
            country_deaths,
            x="Date",
            y=death_col,
            title=
            f"Weekly COVID-19 Deaths — {country}"
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

    else:

        st.info(
            "No death data available for this country "
            "in the selected period."
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


    if not country_vaccine.empty:

        fig_vaccine = px.area(
            country_vaccine,
            x="Date",
            y=vaccine_col,
            title=
            f"Vaccination Progress — {country}"
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

    else:

        st.info(
            "No vaccination data available for this country."
        )


    # ========================================================
    # RECENT DATA
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '📋 Recent COVID-19 Data'
        '</div>',
        unsafe_allow_html=True
    )


    if not country_cases.empty:

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


        # ----------------------------------------------------
        # DOWNLOAD
        # ----------------------------------------------------

        safe_name = (
            country
            .lower()
            .replace(" ", "_")
            .replace("/", "_")
        )


        st.download_button(
            "⬇️ Download Country CSV",

            data=country_cases.to_csv(
                index=False
            ),

            file_name=
            f"{safe_name}_covid_data.csv",

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

    <strong>COVID-19 Pulse</strong> is an academic
    data-visualization project developed using
    Python, Pandas, Plotly and Streamlit.

    <br><br>

    The dashboard provides COVID-19 case trends,
    death trends, vaccination information,
    country comparison and downloadable data.

    <br><br>

    The data is sourced from Our World in Data.
    COVID-19 reporting figures may change because
    of reporting revisions, testing differences
    and differences in reporting practices between
    countries.

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
