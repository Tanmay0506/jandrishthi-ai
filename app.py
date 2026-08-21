import streamlit as st

st.set_page_config(
    page_title="JanDrishti",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="collapsed" # Changed to collapsed to prevent it from popping open
)

# --------------------------------------------------
# STYLING
# --------------------------------------------------
st.markdown("""
<style>

/* HIDE STREAMLIT SIDEBAR COMPLETELY */
[data-testid="stSidebar"] {
    display: none !important;
}
[data-testid="collapsedControl"] {
    display: none !important;
}

/* HIDE DEFAULT TOP BAR (optional but looks cleaner) */
#MainMenu, footer, header {visibility: hidden;}

.stApp {
    background: #050814;
    color: white;
}

.hero {
    text-align: center;
    padding: 90px 20px 50px 20px;
}

.hero h1 {
    font-size: 64px;
    font-weight: 800;
    margin-bottom: 10px;
    background: linear-gradient(90deg, #6366f1, #2dd4bf);
    -webkit-background-clip: text;
    color: transparent;
}

.hero h3 {
    color: #cbd5e1;
    font-weight: 500;
}

.hero p {
    color: #94a3b8;
    font-size: 18px;
    max-width: 750px;
    margin: auto;
    line-height: 1.7;
}

.card {
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 30px;
    text-align: center;
    height: 100%;
}

.card h2 {
    color: white;
}

.card p {
    color: #94a3b8;
    line-height: 1.6;
}

/* BUTTON STYLING FIX */
div.stButton > button {
    background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    transition: all 0.3s ease !important;
}

div.stButton > button p {
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 16px !important;
}

div.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px -6px rgba(139, 92, 246, 0.6) !important;
}

.footer {
    text-align: center;
    color: #64748b;
    margin-top: 80px;
    padding: 30px;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# HERO
# --------------------------------------------------
st.markdown("""
<div class="hero">
    <h1>🇮🇳 JanDrishti</h1>
    <h3>Citizen-Driven Infrastructure Intelligence</h3>
    <p>
    A unified AI-powered platform that transforms citizen
    demands into actionable infrastructure intelligence
    for better governance and development planning.
    </p>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# PORTALS
# --------------------------------------------------
st.markdown("## Choose Your Portal")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="card">
        <h2>👤 Citizen Portal</h2>
        <p>
        Report infrastructure problems, submit citizen
        demands, and help authorities understand the
        issues affecting your community.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Open Citizen Portal →", use_container_width=True):
        # Update this to match your exact filename
        st.switch_page("pages/citizen_portal.py") 

with col2:
    st.markdown("""
    <div class="card">
        <h2>🏛️ Policy Portal</h2>
        <p>
        Analyze citizen demands, detect infrastructure hotspots, 
        and generate AI-driven policy recommendations.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Open Policy Portal →", use_container_width=True):
        # Update this to match your exact filename
        st.switch_page("pages/policy_portal.py")

st.markdown("""
<div class="footer">
    Powered by JanDrishti Intelligence Core
</div>
""", unsafe_allow_html=True)