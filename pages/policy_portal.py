import streamlit as st
import folium
from streamlit_folium import st_folium

from utils.analytics import load_requests
from utils.hotspots import detect_hotspots
from utils.priority import calculate_priority

from ai.recommender import generate_policy_recommendation

from database.database import (
    get_policy_recommendation,
    save_policy_recommendation
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="JanDrishti Policy Dashboard",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# GLOBAL CSS
# ============================================================

CSS = """
<style>

@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', system-ui, sans-serif !important;
}

.stApp {
    background:
        radial-gradient(
            circle at 15% 50%,
            rgba(45, 212, 191, 0.05),
            transparent 25%
        ),
        radial-gradient(
            circle at 85% 30%,
            rgba(99, 102, 241, 0.05),
            transparent 25%
        ),
        #050814;

    color: #f8fafc;
}

#MainMenu,
footer,
header {
    visibility: hidden;
}

div[data-testid="stToolbar"] {
    display: none;
}

iframe {
    border-radius: 20px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
}

hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(
        90deg,
        transparent,
        rgba(255,255,255,0.12),
        transparent
    ) !important;
    margin: 40px 0 !important;
}


/* HERO */

.hero-wrapper {
    padding: 55px;
    margin-bottom: 35px;
    border-radius: 30px;

    background:
        linear-gradient(
            135deg,
            rgba(30,41,59,0.65),
            rgba(15,23,42,0.45)
        );

    border: 1px solid rgba(255,255,255,0.08);

    box-shadow:
        0 30px 70px rgba(0,0,0,0.45);

    position: relative;
    overflow: hidden;
}

.hero-wrapper:before {
    content: "";
    position: absolute;

    width: 500px;
    height: 500px;

    top: -250px;
    left: -150px;

    background: radial-gradient(
        circle,
        rgba(99,102,241,0.18),
        transparent 65%
    );
}

.hero-wrapper:after {
    content: "";
    position: absolute;

    width: 500px;
    height: 500px;

    bottom: -300px;
    right: -150px;

    background: radial-gradient(
        circle,
        rgba(45,212,191,0.16),
        transparent 65%
    );
}

.hero-title {
    position: relative;

    font-size: 52px;
    font-weight: 800;

    letter-spacing: -1.5px;

    background:
        linear-gradient(
            90deg,
            #6366f1,
            #2dd4bf,
            #6366f1
        );

    background-size: 200% auto;

    color: transparent;

    -webkit-background-clip: text;
    background-clip: text;

    margin-bottom: 10px;
}

.hero-subtitle {
    position: relative;

    font-size: 21px;
    font-weight: 500;

    color: #cbd5e1;

    margin-bottom: 25px;
}

.badge-row {
    position: relative;

    display: flex;
    flex-wrap: wrap;

    gap: 12px;
}

.modern-badge {
    display: inline-block;

    padding: 8px 16px;

    border-radius: 10px;

    background: rgba(255,255,255,0.05);

    border: 1px solid rgba(255,255,255,0.1);

    color: #cbd5e1;

    font-size: 13px;
    font-weight: 600;
}


/* SECTION */

.section-header {
    font-size: 28px;
    font-weight: 700;

    color: #ffffff;

    margin-top: 35px;
    margin-bottom: 8px;
}

.section-caption {
    color: #94a3b8;

    font-size: 14px;

    margin-bottom: 20px;
}


/* METRICS */

.ai-metric-grid {
    display: grid;

    grid-template-columns:
        repeat(4, minmax(0, 1fr));

    gap: 20px;

    margin-bottom: 30px;
}

.ai-metric {
    position: relative;

    padding: 25px;

    border-radius: 20px;

    background:
        linear-gradient(
            145deg,
            rgba(30,41,59,0.75),
            rgba(15,23,42,0.9)
        );

    border: 1px solid rgba(255,255,255,0.06);

    box-shadow:
        0 15px 35px rgba(0,0,0,0.25);
}

.metric-dot {
    position: absolute;

    right: 20px;
    top: 20px;

    width: 8px;
    height: 8px;

    border-radius: 50%;
}

.ai-metric-label {
    font-size: 12px;

    color: #94a3b8;

    font-weight: 700;

    text-transform: uppercase;

    letter-spacing: 1px;

    margin-bottom: 8px;
}

.ai-metric-value {
    font-size: 28px;

    font-weight: 800;

    color: #ffffff;
}


/* GLASS */

.glass-panel {
    padding: 30px;

    border-radius: 22px;

    background:
        rgba(15,23,42,0.65);

    border:
        1px solid rgba(255,255,255,0.06);

    box-shadow:
        0 20px 50px rgba(0,0,0,0.3);
}


/* INFO */

.info-row {
    display: flex;

    gap: 20px;

    padding: 16px 0;

    border-bottom:
        1px solid rgba(255,255,255,0.06);

    line-height: 1.6;
}

.info-label {
    min-width: 190px;

    color: #64748b;

    font-weight: 700;
}

.info-value {
    color: #cbd5e1;

    font-weight: 500;
}


/* FOOTER */

.footer {
    text-align: center;

    margin-top: 70px;

    padding: 40px 0;

    border-top:
        1px solid rgba(255,255,255,0.06);
}

.footer-title {
    font-size: 18px;

    font-weight: 700;

    color: #e2e8f0;

    margin-bottom: 8px;
}

.footer-text {
    color: #64748b;

    font-size: 14px;

    line-height: 1.6;
}


/* MOBILE */

@media(max-width: 900px) {

    .ai-metric-grid {
        grid-template-columns:
            repeat(2, 1fr);
    }

    .hero-title {
        font-size: 38px;
    }

}

@media(max-width: 600px) {

    .ai-metric-grid {
        grid-template-columns:
            1fr;
    }

    .hero-wrapper {
        padding: 30px;
    }

}

</style>
"""


# ============================================================
# APPLY CSS
# ============================================================

st.html(CSS)


# ============================================================
# HERO
# ============================================================

st.html("""
<div class="hero-wrapper">

    <div class="hero-title">
        Policy Intelligence Dashboard
    </div>

    <div class="hero-subtitle">
        JanDrishti: Citizen-driven infrastructure demand mapping
    </div>

    <div class="badge-row">

        <span class="modern-badge">
            📊 Data Analytics
        </span>

        <span class="modern-badge">
            🔥 Hotspot Detection
        </span>

        <span class="modern-badge">
            🤖 AI Policy Engine
        </span>

    </div>

</div>
""")


# ============================================================
# LOAD DATA
# ============================================================

try:

    df = load_requests()

except Exception as e:

    st.error("Unable to load citizen request data.")

    st.exception(e)

    st.stop()


if df.empty:

    st.warning(
        "No citizen requests are available."
    )

    st.stop()


# ============================================================
# ANALYTICS
# ============================================================

try:

    priority_df = calculate_priority(df)

    hotspots = detect_hotspots(df)

except Exception as e:

    st.error("Analytics engine failed.")

    st.exception(e)

    st.stop()


# ============================================================
# TOP METRICS
# ============================================================

total_requests = len(df)

critical_requests = len(
    df[df["severity"] == "Critical"]
)

district_count = df["district"].nunique()

top_category = (
    df["category"]
    .value_counts()
    .index[0]
)


st.html(f"""

<div class="ai-metric-grid">

    <div class="ai-metric">

        <div
            class="metric-dot"
            style="
                background:#2dd4bf;
                box-shadow:0 0 10px #2dd4bf;
            "
        ></div>

        <div class="ai-metric-label">
            Citizen Requests
        </div>

        <div class="ai-metric-value">
            {total_requests:,}
        </div>

    </div>


    <div class="ai-metric">

        <div
            class="metric-dot"
            style="
                background:#ef4444;
                box-shadow:0 0 10px #ef4444;
            "
        ></div>

        <div class="ai-metric-label">
            Critical Requests
        </div>

        <div class="ai-metric-value">
            {critical_requests:,}
        </div>

    </div>


    <div class="ai-metric">

        <div
            class="metric-dot"
            style="
                background:#8b5cf6;
                box-shadow:0 0 10px #8b5cf6;
            "
        ></div>

        <div class="ai-metric-label">
            Districts Impacted
        </div>

        <div class="ai-metric-value">
            {district_count:,}
        </div>

    </div>


    <div class="ai-metric">

        <div
            class="metric-dot"
            style="
                background:#f59e0b;
                box-shadow:0 0 10px #f59e0b;
            "
        ></div>

        <div class="ai-metric-label">
            Top Demand Area
        </div>

        <div
            class="ai-metric-value"
            style="font-size:20px;"
        >
            {top_category}
        </div>

    </div>

</div>

""")


# ============================================================
# CHARTS
# ============================================================

col1, col2 = st.columns(2)


with col1:

    st.html("""
    <div class="section-header">
        📊 Citizen Demand
    </div>
    """)

    category_data = (
        df["category"]
        .value_counts()
        .reset_index()
    )

    category_data.columns = [
        "Category",
        "Requests"
    ]

    st.bar_chart(
        category_data.set_index("Category"),
        color="#2dd4bf"
    )


with col2:

    st.html("""
    <div class="section-header">
        🚨 Severity Distribution
    </div>
    """)

    severity_data = (
        df["severity"]
        .value_counts()
        .reindex(
            [
                "Critical",
                "High",
                "Medium",
                "Low"
            ]
        )
        .fillna(0)
    )

    st.bar_chart(
        severity_data,
        color="#8b5cf6"
    )


st.divider()


# ============================================================
# HOTSPOTS
# ============================================================

st.html("""
<div class="section-header">
    🔥 Infrastructure Demand Hotspots
</div>

<div class="section-caption">
    🗺️ Click any hotspot marker to generate localized AI policy intelligence.
</div>
""")


if hotspots.empty:

    st.info(
        "No significant geographic hotspots detected."
    )

else:

    # --------------------------------------------------------
    # MAP CENTER
    # --------------------------------------------------------

    center_lat = hotspots["latitude"].mean()

    center_lon = hotspots["longitude"].mean()


    m = folium.Map(

        location=[
            center_lat,
            center_lon
        ],

        zoom_start=5,

        tiles="CartoDB dark_matter"
    )


    # --------------------------------------------------------
    # MARKERS
    # --------------------------------------------------------

    for index, hotspot in hotspots.iterrows():

        latitude = float(
            hotspot["latitude"]
        )

        longitude = float(
            hotspot["longitude"]
        )

        district = str(
            hotspot.get(
                "district",
                "Unknown"
            )
        )

        state = str(
            hotspot.get(
                "state",
                "Unknown"
            )
        )

        requests = int(
            hotspot.get(
                "requests",
                0
            )
        )

        population = int(
            hotspot.get(
                "population_affected",
                0
            )
        )

        intensity = float(
            hotspot.get(
                "intensity",
                0
            )
        )


        popup_html = f"""

        <div
            style="
                font-family:Arial;
                min-width:220px;
                color:#111827;
            "
        >

            <h4>
                🔥 {district}
            </h4>

            <b>State:</b>
            {state}
            <br>

            <b>Requests:</b>
            {requests:,}
            <br>

            <b>Population:</b>
            {population:,}
            <br>

            <b>Intensity:</b>
            {intensity:.2f}

            <br><br>

            <b>
                Click marker to analyze
            </b>

        </div>

        """


        folium.CircleMarker(

            location=[
                latitude,
                longitude
            ],

            radius=12,

            color="#f43f5e",

            fill=True,

            fill_color="#f43f5e",

            fill_opacity=0.8,

            weight=3,

            popup=folium.Popup(
                popup_html,
                max_width=300
            ),

            tooltip=f"""
            🔥 {district}, {state}
            """

        ).add_to(m)


    # --------------------------------------------------------
    # DISPLAY MAP
    # --------------------------------------------------------

    map_data = st_folium(

        m,

        width=None,

        height=520,

        returned_objects=[
            "last_object_clicked"
        ]

    )


    # ========================================================
    # DETECT CLICK
    # ========================================================

    clicked_hotspot = None


    if map_data:

        clicked = map_data.get(
            "last_object_clicked"
        )


        if clicked:

            clicked_lat = clicked.get(
                "lat"
            )

            clicked_lon = clicked.get(
                "lng"
            )


            if (
                clicked_lat is not None
                and
                clicked_lon is not None
            ):

                hotspots_copy = (
                    hotspots.copy()
                )


                hotspots_copy["distance"] = (

                    (
                        hotspots_copy["latitude"]
                        - clicked_lat
                    ) ** 2

                    +

                    (
                        hotspots_copy["longitude"]
                        - clicked_lon
                    ) ** 2

                )


                nearest_index = (
                    hotspots_copy[
                        "distance"
                    ].idxmin()
                )


                clicked_hotspot = (
                    hotspots.loc[
                        nearest_index
                    ]
                )


    # ========================================================
    # SESSION STATE
    # ========================================================

    if clicked_hotspot is not None:

        st.session_state[
            "selected_hotspot"
        ] = clicked_hotspot.to_dict()


    selected_hotspot = (
        st.session_state.get(
            "selected_hotspot"
        )
    )


    # ========================================================
    # AI HOTSPOT ANALYSIS
    # ========================================================

    if selected_hotspot is not None:

        top_hotspot = selected_hotspot


        hotspot_state = str(
            top_hotspot["state"]
        )

        hotspot_district = str(
            top_hotspot["district"]
        )


        # ----------------------------------------------------
        # PRIORITY DATA
        # ----------------------------------------------------

        district_priority = priority_df[

            (
                priority_df["state"]
                == hotspot_state
            )

            &

            (
                priority_df["district"]
                == hotspot_district
            )

        ]


        if district_priority.empty:

            st.warning(
                "Priority information is not available "
                "for this hotspot."
            )

        else:

            district_priority = (
                district_priority
                .sort_values(
                    "priority_score",
                    ascending=False
                )
            )


            top_problem = (
                district_priority.iloc[0]
            )


            # ------------------------------------------------
            # HEADER
            # ------------------------------------------------

            st.html(f"""

            <div class="section-header">

                🎯 {hotspot_district},
                {hotspot_state}

            </div>

            <div class="section-caption">

                Deep-dive intelligence into the
                selected demand cluster.

            </div>

            """)


            # ------------------------------------------------
            # HOTSPOT METRICS
            # ------------------------------------------------

            st.html(f"""

            <div class="ai-metric-grid">

                <div class="ai-metric">

                    <div class="ai-metric-label">
                        Priority Score
                    </div>

                    <div class="ai-metric-value">
                        {float(top_problem["priority_score"]):.1f}
                        <span
                            style="
                                font-size:15px;
                                color:#64748b;
                            "
                        >
                            /100
                        </span>
                    </div>

                </div>


                <div class="ai-metric">

                    <div class="ai-metric-label">
                        Citizen Requests
                    </div>

                    <div class="ai-metric-value">
                        {int(top_hotspot["requests"]):,}
                    </div>

                </div>


                <div class="ai-metric">

                    <div class="ai-metric-label">
                        Population Affected
                    </div>

                    <div class="ai-metric-value">
                        {int(top_hotspot["population_affected"]):,}
                    </div>

                </div>


                <div class="ai-metric">

                    <div class="ai-metric-label">
                        Primary Issue
                    </div>

                    <div
                        class="ai-metric-value"
                        style="font-size:20px;"
                    >
                        {top_problem["category"]}
                    </div>

                </div>

            </div>

            """)


            # ------------------------------------------------
            # GAP ANALYSIS
            # ------------------------------------------------

            st.html("""
            <div class="glass-panel">

                <h3>
                    📊 Gap Analysis Indicators
                </h3>

            </div>
            """)


            gap1, gap2, gap3 = st.columns(3)


            with gap1:

                st.metric(
                    "Infrastructure Deficit",
                    f"{float(top_problem['infrastructure_gap']):.0f}%"
                )


            with gap2:

                st.metric(
                    "Development Gap",
                    f"{float(top_problem['development_gap']):.0f}%"
                )


            with gap3:

                st.metric(
                    "Mean Severity",
                    f"{float(top_problem['avg_severity']):.0f}/100"
                )


            # ------------------------------------------------
            # GEMINI DATA
            # ------------------------------------------------

            recommendation_data = {

                "state":
                    hotspot_state,

                "district":
                    hotspot_district,

                "category":
                    top_problem["category"],

                "requests":
                    int(
                        top_hotspot[
                            "requests"
                        ]
                    ),

                "population_affected":
                    int(
                        top_hotspot[
                            "population_affected"
                        ]
                    ),

                "avg_severity":
                    float(
                        top_problem[
                            "avg_severity"
                        ]
                    ),

                "infrastructure_gap":
                    float(
                        top_problem[
                            "infrastructure_gap"
                        ]
                    ),

                "development_gap":
                    float(
                        top_problem[
                            "development_gap"
                        ]
                    ),

                "priority_score":
                    float(
                        top_problem[
                            "priority_score"
                        ]
                    )

            }


            # ------------------------------------------------
            # AI HEADER
            # ------------------------------------------------

            st.html("""
            <div class="section-header">
                🤖 AI Policy Recommendation
            </div>
            """)


            # ------------------------------------------------
            # DATABASE CACHE
            # ------------------------------------------------

            try:

                saved_recommendation = (
                    get_policy_recommendation(

                        hotspot_state,

                        hotspot_district,

                        top_problem[
                            "category"
                        ]

                    )
                )

            except Exception:

                saved_recommendation = None


            is_cached = False


            # ------------------------------------------------
            # GENERATE / LOAD
            # ------------------------------------------------

            if saved_recommendation is not None:

                recommendation = (
                    saved_recommendation
                )

                is_cached = True


            else:

                try:

                    with st.spinner(
                        "🤖 Gemini is analyzing this hotspot..."
                    ):

                        recommendation = (
                            generate_policy_recommendation(
                                recommendation_data
                            )
                        )


                    save_policy_recommendation(

                        recommendation_data,

                        recommendation

                    )

                except Exception as e:

                    st.error(
                        "Gemini policy analysis failed."
                    )

                    st.exception(e)

                    recommendation = None


            # ------------------------------------------------
            # DISPLAY RESULT
            # ------------------------------------------------

            if recommendation is not None:

                if is_cached:

                    st.success(
                        "💾 Loaded from policy database"
                    )

                else:

                    st.success(
                        "✨ New Gemini analysis generated"
                    )


                # --------------------------------------------
                # HANDLE DICT / PYDANTIC
                # --------------------------------------------

                if isinstance(
                    recommendation,
                    dict
                ):

                    project_title = (
                        recommendation.get(
                            "project_title",
                            "Untitled Initiative"
                        )
                    )

                    priority = (
                        recommendation.get(
                            "priority",
                            "N/A"
                        )
                    )

                    reason = (
                        recommendation.get(
                            "reason",
                            "N/A"
                        )
                    )

                    recommended_action = (
                        recommendation.get(
                            "recommended_action",
                            "N/A"
                        )
                    )

                    expected_impact = (
                        recommendation.get(
                            "expected_impact",
                            "N/A"
                        )
                    )

                    key_beneficiaries = (
                        recommendation.get(
                            "key_beneficiaries",
                            "N/A"
                        )
                    )

                    implementation_notes = (
                        recommendation.get(
                            "implementation_notes",
                            "N/A"
                        )
                    )

                else:

                    project_title = (
                        recommendation.project_title
                    )

                    priority = (
                        recommendation.priority
                    )

                    reason = (
                        recommendation.reason
                    )

                    recommended_action = (
                        recommendation.recommended_action
                    )

                    expected_impact = (
                        recommendation.expected_impact
                    )

                    key_beneficiaries = (
                        recommendation.key_beneficiaries
                    )

                    implementation_notes = (
                        recommendation.implementation_notes
                    )


                # --------------------------------------------
                # AI CARD
                # --------------------------------------------

                st.html(f"""

                <div
                    class="glass-panel"
                    style="
                        border-top:
                            4px solid #6366f1;
                        margin-top:25px;
                    "
                >

                    <div
                        style="
                            color:#6366f1;
                            font-size:13px;
                            font-weight:800;
                            text-transform:uppercase;
                            letter-spacing:1px;
                        "
                    >
                        Proposed Initiative
                    </div>


                    <h2
                        style="
                            color:#f8fafc;
                            margin-top:10px;
                        "
                    >
                        {project_title}
                    </h2>


                    <div
                        style="
                            margin:20px 0;
                            color:#f43f5e;
                            font-weight:700;
                        "
                    >
                        Priority Level:
                        {priority}
                    </div>


                    <div class="info-row">

                        <div class="info-label">
                            🔎 Analytical Rationale
                        </div>

                        <div class="info-value">
                            {reason}
                        </div>

                    </div>


                    <div class="info-row">

                        <div class="info-label">
                            💡 Execution Blueprint
                        </div>

                        <div class="info-value">
                            {recommended_action}
                        </div>

                    </div>


                    <div class="info-row">

                        <div class="info-label">
                            📈 Projected Impact
                        </div>

                        <div class="info-value">
                            {expected_impact}
                        </div>

                    </div>


                    <div class="info-row">

                        <div class="info-label">
                            👥 Core Beneficiaries
                        </div>

                        <div class="info-value">
                            {key_beneficiaries}
                        </div>

                    </div>


                    <div
                        class="info-row"
                        style="
                            border-bottom:none;
                        "
                    >

                        <div class="info-label">
                            🏗️ Logistics & Notes
                        </div>

                        <div class="info-value">
                            {implementation_notes}
                        </div>

                    </div>

                </div>

                """)


    else:

        st.info(
            "👆 Click any red hotspot marker "
            "to unlock AI policy intelligence."
        )


    # ========================================================
    # HOTSPOT TABLE
    # ========================================================

    st.divider()


    st.html("""
    <div class="section-header">
        📍 Macro Cluster Database
    </div>

    <div class="section-caption">
        Tabular breakdown of detected infrastructure demand zones.
    </div>
    """)


    hotspot_display = hotspots[

        [
            "state",
            "district",
            "requests",
            "population_affected",
            "intensity"
        ]

    ].copy()


    hotspot_display.columns = [

        "State",
        "District",
        "Requests",
        "Population Affected",
        "Intensity"

    ]


    st.dataframe(

        hotspot_display,

        use_container_width=True,

        hide_index=True

    )


# ============================================================
# FOOTER
# ============================================================

st.html("""

<div class="footer">

    <div class="footer-title">
        🇮🇳 JanDrishti Policy Core
    </div>

    <div class="footer-text">

        Empowering governance with
        citizen-driven spatial intelligence.

        <br>

        Accelerating India's infrastructural future.

    </div>

</div>

""")