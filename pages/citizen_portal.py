import requests
import streamlit as st
from streamlit_mic_recorder import speech_to_text
from streamlit_geolocation import streamlit_geolocation
from dotenv import load_dotenv

# User's custom modules (assumed to exist in their environment)
from ai.extractor import analyze_request
from database.database import create_table, save_request
from utils.geocoding import geocode_location

load_dotenv()
create_table()

st.set_page_config(
    page_title="JanDrishti AI",
    page_icon="IN",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# Session state
# -----------------------------
if "request_text" not in st.session_state:
    st.session_state.request_text = ""
if "voice_text" not in st.session_state:
    st.session_state.voice_text = ""
if "precise_location" not in st.session_state:
    st.session_state.precise_location = None


def reverse_geocode_coordinates(latitude, longitude):
    """Turn browser GPS coordinates into locality, district, and state data."""
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={
                "lat": latitude,
                "lon": longitude,
                "format": "jsonv2",
                "addressdetails": 1,
                "accept-language": "en",
            },
            headers={
                "User-Agent": "JanDrishti-AI/1.0 Citizen Infrastructure Platform",
                "Accept": "application/json",
            },
            timeout=(5, 20),
        )
        response.raise_for_status()
        result = response.json()
        address = result.get("address", {})

        return {
            "latitude": float(latitude),
            "longitude": float(longitude),
            "village": (
                address.get("village")
                or address.get("hamlet")
                or address.get("suburb")
                or address.get("neighbourhood")
                or address.get("town")
                or address.get("city")
                or "Precise GPS location"
            ),
            "district": (
                address.get("state_district")
                or address.get("district")
                or address.get("county")
                or "Unknown"
            ),
            "state": address.get("state", "Unknown"),
            "country": address.get("country", "India"),
            "display_name": result.get(
                "display_name", f"{float(latitude):.6f}, {float(longitude):.6f}"
            ),
        }
    except (requests.RequestException, ValueError, TypeError):
        return None


def gps_fallback_data(gps_data):
    """Allow GPS complaints to save and cluster even if reverse lookup fails."""
    latitude = float(gps_data["latitude"])
    longitude = float(gps_data["longitude"])
    return {
        "latitude": latitude,
        "longitude": longitude,
        "village": "Precise GPS location",
        "district": "Unknown",
        "state": "Unknown",
        "country": "India",
        "display_name": f"{latitude:.6f}, {longitude:.6f}",
    }

# -----------------------------
# Premium Dark CSS & Animations
# -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

/* ========== GLOBAL RESET & TYPOGRAPHY ========== */
html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif !important;
}

.stApp {
    background-color: #050814;
    background-image: 
        radial-gradient(circle at 15% 50%, rgba(45, 212, 191, 0.05), transparent 25%),
        radial-gradient(circle at 85% 30%, rgba(99, 102, 241, 0.05), transparent 25%);
    background-attachment: fixed;
    color: #f8fafc;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header {visibility: hidden;}
div[data-testid="stToolbar"] {display: none;}

/* Smooth scrolling & selection */
* {
    scroll-behavior: smooth;
}

::selection {
    background: rgba(45, 212, 191, 0.3);
    color: #ffffff;
}

/* ========== ANIMATIONS ========== */
@keyframes float {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
    100% { transform: translateY(0px); }
}

@keyframes pulseGlow {
    0% { box-shadow: 0 0 0 0 rgba(45, 212, 191, 0.4); }
    70% { box-shadow: 0 0 0 15px rgba(45, 212, 191, 0); }
    100% { box-shadow: 0 0 0 0 rgba(45, 212, 191, 0); }
}

@keyframes gradientText {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* ========== HERO SECTION ========== */
.hero-wrapper {
    position: relative;
    padding: 60px 70px;
    margin-bottom: 50px;
    border-radius: 32px;
    background: rgba(15, 23, 42, 0.4);
    backdrop-filter: blur(20px) saturate(150%);
    -webkit-backdrop-filter: blur(20px) saturate(150%);
    border: 1px solid rgba(255, 255, 255, 0.05);
    box-shadow: 
        0 30px 60px -10px rgba(0, 0, 0, 0.5),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
    overflow: hidden;
    z-index: 1;
}

/* Decorative Glows inside Hero */
.hero-wrapper::before {
    content: '';
    position: absolute;
    top: -50%; left: -20%;
    width: 60%; height: 200%;
    background: radial-gradient(circle, rgba(45, 212, 191, 0.15) 0%, transparent 60%);
    transform: rotate(15deg);
    pointer-events: none;
    z-index: -1;
}

.hero-wrapper::after {
    content: '';
    position: absolute;
    bottom: -50%; right: -20%;
    width: 60%; height: 200%;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, transparent 60%);
    transform: rotate(-15deg);
    pointer-events: none;
    z-index: -1;
}

.hero-title {
    font-size: 64px;
    font-weight: 800;
    letter-spacing: -2px;
    margin-bottom: 15px;
    line-height: 1.1;
    background: linear-gradient(300deg, #2dd4bf, #6366f1, #2dd4bf);
    background-size: 200% auto;
    color: transparent;
    -webkit-background-clip: text;
    background-clip: text;
    animation: gradientText 6s linear infinite;
}

.hero-subtitle {
    font-size: 24px;
    font-weight: 500;
    color: #e2e8f0;
    margin-bottom: 25px;
    letter-spacing: -0.5px;
}

.hero-description {
    max-width: 680px;
    color: #94a3b8;
    font-size: 17px;
    line-height: 1.8;
    margin-bottom: 35px;
    font-weight: 400;
}

.badge-row {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
}

.modern-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 18px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: #cbd5e1;
    font-size: 13.5px;
    font-weight: 600;
    letter-spacing: 0.3px;
    transition: all 0.3s ease;
}

.modern-badge:hover {
    background: rgba(45, 212, 191, 0.1);
    border-color: rgba(45, 212, 191, 0.4);
    color: #2dd4bf;
    transform: translateY(-2px);
}

/* ========== SECTION HEADERS ========== */
.section-header {
    font-size: 28px;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.5px;
    margin-top: 20px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.section-caption {
    color: #64748b;
    font-size: 15px;
    margin-bottom: 30px;
    line-height: 1.6;
}

/* ========== ADVANCED GLASS CARDS ========== */
.glass-panel {
    background: rgba(15, 23, 42, 0.5);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 24px;
    padding: 30px;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
    position: relative;
    overflow: hidden;
}

.glass-panel::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
}

.glass-panel:hover {
    border-color: rgba(45, 212, 191, 0.3);
    transform: translateY(-5px);
    box-shadow: 0 20px 40px -15px rgba(0,0,0,0.7), 0 0 20px rgba(45, 212, 191, 0.1);
}

/* ========== METRIC CARDS OVERHAUL ========== */
.ai-metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.ai-metric {
    background: linear-gradient(145deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.9));
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 20px;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    transition: all 0.3s ease;
    position: relative;
}

.ai-metric:hover {
    transform: translateY(-5px) scale(1.02);
    border-color: rgba(99, 102, 241, 0.4);
    box-shadow: 0 15px 30px -10px rgba(99, 102, 241, 0.2);
}

.metric-dot {
    position: absolute;
    top: 24px;
    right: 24px;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #2dd4bf;
    box-shadow: 0 0 10px #2dd4bf;
    animation: pulse 2s infinite;
}

.ai-metric-label {
    font-size: 13px;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.ai-metric-value {
    font-size: 28px;
    font-weight: 800;
    color: #ffffff;
    background: linear-gradient(to right, #ffffff, #a5b4fc);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}

/* ========== INFO ROWS ========== */
.info-row {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    padding: 14px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    font-size: 15px;
    line-height: 1.6;
}
.info-row:last-child {
    border-bottom: none;
    padding-bottom: 0;
}

.info-label {
    font-weight: 600;
    color: #64748b;
    min-width: 140px;
    flex-shrink: 0;
}

.info-value {
    color: #f1f5f9;
    font-weight: 500;
}

/* ========== STREAMLIT COMPONENT OVERRIDES ========== */

/* Tabs */
div[data-testid="stTabs"] {
    background: transparent;
}
div[data-testid="stTabs"] button {
    background: transparent !important;
    border: none !important;
    color: #64748b !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    border-bottom: 2px solid transparent !important;
    transition: all 0.3s ease !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #2dd4bf !important;
    border-bottom: 2px solid #2dd4bf !important;
}

/* Primary Button (Analyze) */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0d9488 0%, #3b82f6 100%) !important;
    color: #ffffff !important;
    border-radius: 16px !important;
    font-weight: 700 !important;
    font-size: 18px !important;
    padding: 1.2rem 2rem !important;
    border: none !important;
    box-shadow: 
        0 10px 25px -5px rgba(59, 130, 246, 0.4),
        inset 0 1px 1px rgba(255, 255, 255, 0.2) !important;
    transition: all 0.3s ease !important;
    animation: pulseGlow 3s infinite;
}

.stButton > button[kind="primary"]:hover {
    transform: translateY(-3px) scale(1.01) !important;
    box-shadow: 
        0 15px 35px -5px rgba(59, 130, 246, 0.6),
        inset 0 1px 1px rgba(255, 255, 255, 0.3) !important;
}

/* Inputs */
.stTextArea textarea, 
.stTextInput input,
.stSelectbox > div > div {
    background-color: rgba(15, 23, 42, 0.4) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 16px !important;
    color: #f8fafc !important;
    padding: 14px !important;
    font-size: 15px !important;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease !important;
}

.stTextArea textarea:focus, 
.stTextInput input:focus,
.stSelectbox > div > div:focus-within {
    background-color: rgba(15, 23, 42, 0.6) !important;
    border-color: #2dd4bf !important;
    box-shadow: 0 0 0 4px rgba(45, 212, 191, 0.15) !important;
}

/* Status / Alerts */
div[data-testid="stStatusWidget"] {
    background: rgba(15, 23, 42, 0.6) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 16px !important;
    backdrop-filter: blur(10px);
}

div[data-testid="stAlert"] {
    border-radius: 16px !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
    backdrop-filter: blur(10px);
}

/* Expander */
.streamlit-expanderHeader {
    background: rgba(30, 41, 59, 0.5) !important;
    border-radius: 14px !important;
    font-weight: 600 !important;
    color: #e2e8f0 !important;
    border: 1px solid rgba(255,255,255,0.03) !important;
}
div[data-testid="stExpanderDetails"] {
    background: rgba(15, 23, 42, 0.3) !important;
    border-bottom-left-radius: 14px !important;
    border-bottom-right-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.03) !important;
    border-top: none !important;
}

/* Map container */
iframe {
    border-radius: 20px !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5) !important;
}

/* Divider */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent) !important;
    margin: 40px 0 !important;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}
::-webkit-scrollbar-track {
    background: #050814;
}
::-webkit-scrollbar-thumb {
    background: #1e293b;
    border-radius: 5px;
}
::-webkit-scrollbar-thumb:hover {
    background: #334155;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Hero Section
# -----------------------------
st.markdown("""
<div class="hero-wrapper">
    <div class="hero-title">JanDrishti AI</div>
    <div class="hero-subtitle">Elevating Citizen Voices to Infrastructure Intelligence</div>
    <div class="hero-description">
        Empowering communities across India. We transform your everyday infrastructural challenges 
        into structured, highly-accurate, and location-aware data, equipping policymakers 
        with the intelligence they need to act instantly.
    </div>
    <div class="badge-row">
        <span class="modern-badge">✨ Next-Gen AI Analysis</span>
        <span class="modern-badge">🎙️ Multi-lingual Voice</span>
        <span class="modern-badge">🛰️ Precision Mapping</span>
        <span class="modern-badge">🇮🇳 Built for India</span>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Submit Request
# -----------------------------
st.markdown('<div class="section-header">🗣️ Voice Your Concern</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-caption">Choose your preferred method to inform JanDrishti about infrastructural issues in your area.</div>',
    unsafe_allow_html=True
)

# Replacing the old radio button with native Streamlit tabs for a cleaner UI
tab1, tab2 = st.tabs(["⌨️ Text Submission", "🎙️ Voice Submission"])

with tab1:
    st.markdown("""
    <div class="glass-panel" style="margin-bottom: 15px; padding: 20px;">
        <h4 style="margin:0; color:#f8fafc; font-size: 16px;">Detailed Description</h4>
        <p style="margin:5px 0 0 0; color:#94a3b8; font-size: 14px;">
            Provide specific details about the issue, including landmarks and how it affects the community.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    text = st.text_area(
        "Citizen complaint",
        value=st.session_state.request_text,
        placeholder="Example: The main road near Shivaji Chowk in Pune is severely potholed after the recent rains, causing massive traffic blocks and accidents.",
        height=180,
        label_visibility="collapsed"
    )
    st.session_state.request_text = text

with tab2:
    st.markdown("""
    <div class="glass-panel" style="margin-bottom: 15px; padding: 20px;">
        <h4 style="margin:0; color:#f8fafc; font-size: 16px;">Speak Naturally</h4>
        <p style="margin:5px 0 0 0; color:#94a3b8; font-size: 14px;">
            Select your language and tap the microphone. Our AI will instantly transcribe and translate your concern.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_lang, col_mic = st.columns([1, 2])
    
    with col_lang:
        voice_language = st.selectbox(
            "Select Language",
            ["English", "Hindi", "Marathi"],
            help="Choose the language you are most comfortable speaking in."
        )

    language_codes = {
        "English": "en-IN",
        "Hindi": "hi-IN",
        "Marathi": "mr-IN",
    }

    with col_mic:
        st.write("") # spacing
        st.write("")
        try:
            voice_result = speech_to_text(
                language=language_codes[voice_language],
                start_prompt="🎙️ Tap to Start Recording",
                stop_prompt="⏹️ Tap to Stop",
                just_once=True,
                use_container_width=True,
            )
            if voice_result:
                st.session_state.voice_text = voice_result
                st.session_state.request_text = voice_result
        except Exception as e:
            st.error(f"Voice recorder encountered an issue: {e}")

    if st.session_state.voice_text:
        st.markdown("<br>", unsafe_allow_html=True)
        st.success("✅ **Transcription Captured**")
        st.info(f'"{st.session_state.voice_text}"')

# -----------------------------
# Location Data Gathering
# -----------------------------
st.write("")
st.markdown('<div class="section-header">📍 Pinpoint the Location</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-caption">Our AI extracts the location from your text, but providing it below guarantees precision.</div>',
    unsafe_allow_html=True
)

loc_col1, loc_col2 = st.columns([3, 2])

with loc_col1:
    location_input = st.text_input(
        "Manual Location Override (Optional)",
        placeholder="e.g., Kothrud, Pune, Maharashtra",
        help="Leave blank to let our AI auto-detect the location from your story."
    )

with loc_col2:
    use_precise_location = st.checkbox(
        "🎯 Use precise current location",
        value=False,
    )

    if use_precise_location:
        try:
            detected_location = streamlit_geolocation()
            if (
                isinstance(detected_location, dict)
                and detected_location.get("latitude") is not None
                and detected_location.get("longitude") is not None
            ):
                st.session_state.precise_location = {
                    "latitude": detected_location["latitude"],
                    "longitude": detected_location["longitude"],
                }
        except Exception:
            st.session_state.precise_location = None

        if st.session_state.precise_location:
            gps = st.session_state.precise_location
            st.success(
                f"✓ Coordinates captured: {float(gps['latitude']):.6f}, "
                f"{float(gps['longitude']):.6f}"
            )




# -----------------------------
# AI Analysis Execution
# -----------------------------
st.write("")
st.write("")
st.write("")

analyze_clicked = st.button(
    "🚀 Initiate AI Analysis",
    type="primary",
    use_container_width=True,
)

if analyze_clicked:
    request_text = st.session_state.request_text.strip()

    if not request_text:
        st.error("⚠️ Please provide a text description or record a voice note before analyzing.", icon="🚨")
        st.stop()

    with st.status("🧠 Initializing JanDrishti Neural Core...", expanded=True) as status:
        try:
            st.write("⏳ Parsing natural language logic...")
            result = analyze_request(request_text)
            st.write("✅ Contextual analysis generated.")

            if use_precise_location:
                gps = st.session_state.precise_location
                if not gps:
                    status.update(label="📍 Precise location required", state="error")
                    st.error("Allow browser location access, capture coordinates, then try again.")
                    st.stop()

                st.write("🛰️ Identifying locality, district, and state...")
                location_data = reverse_geocode_coordinates(
                    float(gps["latitude"]),
                    float(gps["longitude"]),
                )

                if location_data is None:
                    location_data = gps_fallback_data(gps)

                resolved_input = location_data["display_name"]
                location_source = "Precise Current Location"

            else:
                if location_input.strip():
                    resolved_input = location_input.strip()
                    location_source = "Manual Override"
                else:
                    resolved_input = result.location
                    location_source = "AI Extracted"

                if not resolved_input or resolved_input.strip().lower() == "unknown":
                    status.update(label="📍 Location mapping failed", state="error")
                    st.error("No valid location was detected. Please enter a location or use precise current location.")
                    st.stop()

                st.write(f"🛰️ Resolving spatial coordinates for: **{resolved_input}**...")
                location_data = geocode_location(resolved_input)

                if location_data is None:
                    status.update(label="❌ Geocoding Failed", state="error")
                    st.error("Could not map that location. Use precise current location for direct GPS coordinates.")
                    st.stop()

            location_data["input_location"] = resolved_input
            location_data["location_source"] = location_source

        
            st.write("💾 Committing structured intelligence to database...")
            save_request(result, request_text, location_data)

            status.update(label="✨ Analysis Complete & Stored Successfully!", state="complete")
            
            # -------------------------
            # Comprehensive Results UI
            # -------------------------
            st.markdown("---")
            st.markdown('<div class="section-header">📊 Intelligence Dossier</div>', unsafe_allow_html=True)
            st.write("")
            
            # Custom Metric Grid
            st.markdown(f"""
            <div class="ai-metric-grid">
                <div class="ai-metric">
                    <div class="metric-dot"></div>
                    <div class="ai-metric-label">Incident Category</div>
                    <div class="ai-metric-value">{result.category}</div>
                </div>
                <div class="ai-metric">
                    <div class="metric-dot" style="background: #f43f5e; box-shadow: 0 0 10px #f43f5e;"></div>
                    <div class="ai-metric-label">Severity Level</div>
                    <div class="ai-metric-value">{result.severity}</div>
                </div>
                <div class="ai-metric">
                    <div class="metric-dot" style="background: #f59e0b; box-shadow: 0 0 10px #f59e0b;"></div>
                    <div class="ai-metric-label">Required Urgency</div>
                    <div class="ai-metric-value">{result.urgency}</div>
                </div>
                <div class="ai-metric">
                    <div class="metric-dot" style="background: #8b5cf6; box-shadow: 0 0 10px #8b5cf6;"></div>
                    <div class="ai-metric-label">Estimated Impact</div>
                    <div class="ai-metric-value">{result.affected_population_estimate:,}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_a, col_b = st.columns([1.2, 1])

            with col_a:
                st.markdown("##### 🧠 Contextual Extraction")
                st.markdown(f"""
                <div class="glass-panel">
                    <div class="info-row"><span class="info-label">Input Lang</span><span class="info-value">{result.language}</span></div>
                    <div class="info-row"><span class="info-label">Core Problem</span><span class="info-value">{result.problem}</span></div>
                    <div class="info-row"><span class="info-label">Service Affected</span><span class="info-value">{result.affected_service}</span></div>
                    <div class="info-row"><span class="info-label">Brief Summary</span><span class="info-value">{result.summary}</span></div>
                </div>
                """, unsafe_allow_html=True)

            with col_b:
                st.markdown("##### 📍 Geographic Node")
                
                source_color = "#2dd4bf" if location_source == "AI Extracted" else "#8b5cf6"
                source_icon = "🤖" if location_source == "AI Extracted" else "✍️"
                
                st.markdown(f"""
                <div style="margin-bottom: 15px; padding: 10px 16px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; display: inline-flex; gap: 8px; align-items: center;">
                    <span>{source_icon}</span>
                    <span style="color: #94a3b8; font-size: 13px;">Source:</span>
                    <strong style="color: {source_color};">{location_source} ({resolved_input})</strong>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="glass-panel" style="padding: 24px;">
                    <div class="info-row"><span class="info-label">Locality / City</span><span class="info-value">{location_data.get('village', 'Unknown')}</span></div>
                    <div class="info-row"><span class="info-label">District</span><span class="info-value">{location_data.get('district', 'Unknown')}</span></div>
                    <div class="info-row"><span class="info-label">State Region</span><span class="info-value">{location_data.get('state', 'Unknown')}</span></div>
                </div>
                """, unsafe_allow_html=True)

            # Mapping
            latitude = location_data.get("latitude")
            longitude = location_data.get("longitude")

            if latitude is not None and longitude is not None:
                st.write("")
                st.markdown(f"##### 🗺️ Spatial Visualization <span style='font-size:14px; font-weight:normal; color:#64748b; margin-left: 10px;'>[{latitude:.6f}, {longitude:.6f}]</span>", unsafe_allow_html=True)
                # Map styled via CSS overrides earlier
                st.map({"latitude": [latitude], "longitude": [longitude]}, zoom=11)

            st.write("")
            with st.expander("📄 View Raw Transcription / Source Text", expanded=False):
                st.markdown(f"<div style='color: #e2e8f0; line-height: 1.6; font-size: 15px;'>{request_text}</div>", unsafe_allow_html=True)

            with st.expander("💻 Developer Mode: JSON Payload", expanded=False):
                st.json({
                    "metadata": {
                        "status": "success",
                        "timestamp": "auto-generated"
                    },
                    "ai_inference": result.model_dump(),
                    "spatial_data": location_data,
                })

        except Exception as e:
            status.update(label="❌ System Exception Intercepted", state="error")
            st.error("A critical error occurred while parsing the request stream.")
            st.exception(e)

# -----------------------------
# Sleek Footer
# -----------------------------
st.markdown("""
<div style="text-align: center; margin-top: 80px; padding: 40px 0; border-top: 1px solid rgba(255,255,255,0.05);">
    <div style="font-size: 18px; font-weight: 700; color: #e2e8f0; margin-bottom: 8px;">
        🇮🇳 JanDrishti AI
    </div>
    <div style="color: #64748b; font-size: 14px; line-height: 1.6;">
        Transforming citizen voices into structured civic intelligence.<br>
        Built for the future of India's infrastructure.
    </div>
</div>
""", unsafe_allow_html=True)
