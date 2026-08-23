import html

import streamlit as st
from dotenv import load_dotenv
from streamlit_geolocation import streamlit_geolocation
from streamlit_mic_recorder import speech_to_text

from ai.extractor import analyze_request
from database.database import create_table, save_request
from utils.geocoding import geocode_location, reverse_geocode_coordinates


load_dotenv()
create_table()

st.set_page_config(
    page_title="JanDrishti AI",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

for key, default_value in {
    "request_text": "",
    "voice_text": "",
    "precise_location": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default_value


def safe_text(value, fallback="Unknown"):
    if value is None or str(value).strip() == "":
        value = fallback
    return html.escape(str(value))


def model_to_dict(result):
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return vars(result)


def population_display(value):
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return safe_text(value, "Not available")


def gps_fallback_data(gps_data):
    """Save GPS coordinates even if reverse geocoding is temporarily unavailable."""
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


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', system-ui, sans-serif !important;
    }

    .stApp {
        background-color: #050814;
        background-image:
            radial-gradient(circle at 15% 50%, rgba(45,212,191,.05), transparent 25%),
            radial-gradient(circle at 85% 30%, rgba(99,102,241,.05), transparent 25%);
        color: #f8fafc;
    }

    /* Permanently hide Streamlit sidebar and menu controls. */
    [data-testid="stSidebar"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"],
    button[aria-label="Open sidebar"],
    button[title="Open sidebar"],
    #MainMenu, footer, header,
    [data-testid="stToolbar"],
    [data-testid="stStatusWidget"] {
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
    }

    .block-container {
        max-width: 1320px !important;
        padding-top: 2.5rem !important;
        padding-bottom: 3rem !important;
    }

    @keyframes pulseGlow {
        0% { box-shadow: 0 0 0 0 rgba(45,212,191,.4); }
        70% { box-shadow: 0 0 0 15px rgba(45,212,191,0); }
        100% { box-shadow: 0 0 0 0 rgba(45,212,191,0); }
    }

    @keyframes gradientText {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .hero-wrapper {
        position: relative;
        overflow: hidden;
        padding: 60px 70px;
        margin-bottom: 50px;
        border: 1px solid rgba(255,255,255,.06);
        border-radius: 32px;
        background: rgba(15,23,42,.45);
        box-shadow: 0 30px 60px -10px rgba(0,0,0,.5);
    }

    .hero-wrapper::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -20%;
        width: 60%;
        height: 200%;
        background: radial-gradient(circle, rgba(45,212,191,.15), transparent 60%);
        transform: rotate(15deg);
    }

    .hero-title {
        position: relative;
        font-size: 64px;
        font-weight: 800;
        letter-spacing: -2px;
        background: linear-gradient(300deg, #2dd4bf, #6366f1, #2dd4bf);
        background-size: 200% auto;
        color: transparent;
        -webkit-background-clip: text;
        background-clip: text;
        animation: gradientText 6s linear infinite;
    }

    .hero-subtitle {
        position: relative;
        margin: 15px 0 20px;
        font-size: 24px;
        font-weight: 500;
        color: #e2e8f0;
    }

    .hero-description {
        position: relative;
        max-width: 700px;
        margin-bottom: 30px;
        color: #94a3b8;
        font-size: 17px;
        line-height: 1.8;
    }

    .badge-row { position: relative; display: flex; flex-wrap: wrap; gap: 12px; }

    .modern-badge {
        padding: 8px 18px;
        border: 1px solid rgba(255,255,255,.08);
        border-radius: 12px;
        background: rgba(255,255,255,.03);
        color: #cbd5e1;
        font-size: 13px;
        font-weight: 600;
    }

    .section-header {
        margin-top: 25px;
        margin-bottom: 8px;
        color: #fff;
        font-size: 28px;
        font-weight: 700;
    }

    .section-caption {
        margin-bottom: 25px;
        color: #64748b;
        font-size: 15px;
        line-height: 1.6;
    }

    .glass-panel {
        padding: 25px;
        border: 1px solid rgba(255,255,255,.06);
        border-radius: 24px;
        background: rgba(15,23,42,.55);
        box-shadow: 0 10px 30px -10px rgba(0,0,0,.5);
    }

    .ai-metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin-bottom: 30px;
    }

    .ai-metric {
        position: relative;
        padding: 24px;
        border: 1px solid rgba(255,255,255,.06);
        border-radius: 20px;
        background: linear-gradient(145deg, rgba(30,41,59,.7), rgba(15,23,42,.9));
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
    }

    .ai-metric-label {
        color: #94a3b8;
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    .ai-metric-value {
        margin-top: 8px;
        color: #fff;
        font-size: 24px;
        font-weight: 800;
        overflow-wrap: anywhere;
    }

    .info-row {
        display: flex;
        gap: 16px;
        padding: 14px 0;
        border-bottom: 1px solid rgba(255,255,255,.05);
        line-height: 1.6;
    }

    .info-row:last-child { border-bottom: none; }

    .info-label {
        min-width: 140px;
        color: #64748b;
        font-weight: 600;
    }

    .info-value {
        color: #f1f5f9;
        font-weight: 500;
        overflow-wrap: anywhere;
    }

    div[data-testid="stTabs"] button {
        border: none !important;
        border-bottom: 2px solid transparent !important;
        background: transparent !important;
        color: #64748b !important;
        font-size: 16px !important;
        font-weight: 600 !important;
    }

    div[data-testid="stTabs"] button[aria-selected="true"] {
        border-bottom-color: #2dd4bf !important;
        color: #2dd4bf !important;
    }

    .stButton > button[kind="primary"] {
        border: none !important;
        border-radius: 16px !important;
        background: linear-gradient(135deg, #0d9488, #3b82f6) !important;
        color: #fff !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        padding: 1.1rem 2rem !important;
        animation: pulseGlow 3s infinite;
    }

    .stTextArea textarea, .stTextInput input, .stSelectbox > div > div {
        border: 1px solid rgba(255,255,255,.12) !important;
        border-radius: 16px !important;
        background: rgba(15,23,42,.5) !important;
        color: #f8fafc !important;
    }

    iframe {
        border: 1px solid rgba(255,255,255,.1) !important;
        border-radius: 20px !important;
    }

    @media (max-width: 768px) {
        .block-container { padding: 1.2rem !important; }
        .hero-wrapper { padding: 35px 28px; }
        .hero-title { font-size: 42px; }
        .hero-subtitle { font-size: 19px; }
        .info-row { flex-direction: column; gap: 4px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-wrapper">
        <div class="hero-title">JanDrishti AI</div>
        <div class="hero-subtitle">Elevating Citizen Voices to Infrastructure Intelligence</div>
        <div class="hero-description">
            Transforming citizen concerns into structured and location-aware
            intelligence for faster infrastructure action.
        </div>
        <div class="badge-row">
            <span class="modern-badge">✨ Next-Gen AI Analysis</span>
            <span class="modern-badge">🎙️ Multi-lingual Voice</span>
            <span class="modern-badge">🛰️ Precision Mapping</span>
            <span class="modern-badge">🇮🇳 Built for India</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-header">🗣️ Voice Your Concern</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-caption">Describe the issue using text or voice.</div>',
    unsafe_allow_html=True,
)

text_tab, voice_tab = st.tabs(["⌨️ Text Submission", "🎙️ Voice Submission"])

with text_tab:
    st.markdown(
        """
        <div class="glass-panel" style="margin-bottom:15px; padding:20px;">
            <h4 style="margin:0; color:#f8fafc;">Detailed Description</h4>
            <p style="margin:5px 0 0; color:#94a3b8;">
                Include the issue, nearby landmarks, and impact on your community.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.session_state.request_text = st.text_area(
        "Citizen complaint",
        value=st.session_state.request_text,
        placeholder=(
            "Example: The main road near Shivaji Chowk in Pune is severely "
            "potholed after the rains, causing traffic and accidents."
        ),
        height=180,
        label_visibility="collapsed",
    )

with voice_tab:
    language_codes = {
        "English": "en-IN",
        "Hindi": "hi-IN",
        "Marathi": "mr-IN",
    }

    left_col, right_col = st.columns([1, 2])

    with left_col:
        voice_language = st.selectbox("Select Language", list(language_codes))

    with right_col:
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

        except Exception as error:
            st.error(f"Voice recorder encountered an issue: {error}")

    if st.session_state.voice_text:
        st.success("✅ Transcription Captured")
        st.info(f'"{st.session_state.voice_text}"')

st.markdown('<div class="section-header">📍 Pinpoint the Location</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="section-caption">
        Use precise current location for GPS coordinates and automatic district/state,
        or enter a location manually.
    </div>
    """,
    unsafe_allow_html=True,
)

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
                "accuracy": detected_location.get("accuracy"),
            }

    except Exception:
        st.session_state.precise_location = None

    if st.session_state.precise_location:
        gps = st.session_state.precise_location
        st.success(
            f"✓ Coordinates captured: {float(gps['latitude']):.6f}, "
            f"{float(gps['longitude']):.6f}"
        )

location_input = st.text_input(
    "Manual Location Override (Optional)",
    placeholder="e.g., Kothrud, Pune, Maharashtra",
    disabled=use_precise_location,
)

st.write("")
analyze_clicked = st.button(
    "🚀 Initiate AI Analysis",
    type="primary",
    use_container_width=True,
)

if analyze_clicked:
    request_text = st.session_state.request_text.strip()

    if not request_text:
        st.error("⚠️ Please provide a text description or record a voice note first.")
        st.stop()

    with st.status("🧠 Initializing JanDrishti Neural Core...", expanded=True) as status:
        try:
            st.write("⏳ Parsing the concern...")
            result = analyze_request(request_text)
            st.write("✅ Contextual analysis generated.")

            # Precise GPS: GPS coordinates → reverse geocoding → locality/district/state.
            if use_precise_location:
                gps = st.session_state.precise_location

                if not gps:
                    status.update(label="📍 Precise location required", state="error")
                    st.error(
                        "Allow browser location access, capture coordinates, "
                        "then start analysis again."
                    )
                    st.stop()

                latitude = float(gps["latitude"])
                longitude = float(gps["longitude"])

                st.write("🛰️ Identifying locality, district, and state...")
                location_data = reverse_geocode_coordinates(latitude, longitude)

                # Do not fail complaint submission when reverse geocoding is unavailable.
                if location_data is None:
                    location_data = gps_fallback_data(gps)

                resolved_input = location_data["display_name"]
                location_source = "Precise Current Location"

            # Manual / AI location: place name → geocoding.
            else:
                if location_input.strip():
                    resolved_input = location_input.strip()
                    location_source = "Manual Override"
                else:
                    resolved_input = str(getattr(result, "location", "")).strip()
                    location_source = "AI Extracted"

                if not resolved_input or resolved_input.lower() == "unknown":
                    status.update(label="📍 Location required", state="error")
                    st.error(
                        "No valid location was detected. Enter a location manually "
                        "or use precise current location."
                    )
                    st.stop()

                st.write(f"🛰️ Resolving spatial coordinates for: **{resolved_input}**")
                location_data = geocode_location(resolved_input)

                if location_data is None:
                    status.update(label="❌ Geocoding Failed", state="error")
                    st.error(
                        "Could not map that location. Use precise current location "
                        "for direct GPS coordinates."
                    )
                    st.stop()

            location_data["input_location"] = resolved_input
            location_data["location_source"] = location_source

            st.write("💾 Saving structured intelligence...")
            save_request(result, request_text, location_data)

            status.update(
                label="✨ Analysis Complete & Stored Successfully!",
                state="complete",
            )

            st.markdown("---")
            st.markdown(
                '<div class="section-header">📊 Intelligence Dossier</div>',
                unsafe_allow_html=True,
            )

            category = safe_text(getattr(result, "category", None))
            severity = safe_text(getattr(result, "severity", None))
            urgency = safe_text(getattr(result, "urgency", None))
            population = population_display(
                getattr(result, "affected_population_estimate", None)
            )

            st.markdown(
                f"""
                <div class="ai-metric-grid">
                    <div class="ai-metric">
                        <div class="metric-dot"></div>
                        <div class="ai-metric-label">Incident Category</div>
                        <div class="ai-metric-value">{category}</div>
                    </div>
                    <div class="ai-metric">
                        <div class="metric-dot" style="background:#f43f5e; box-shadow:0 0 10px #f43f5e;"></div>
                        <div class="ai-metric-label">Severity Level</div>
                        <div class="ai-metric-value">{severity}</div>
                    </div>
                    <div class="ai-metric">
                        <div class="metric-dot" style="background:#f59e0b; box-shadow:0 0 10px #f59e0b;"></div>
                        <div class="ai-metric-label">Required Urgency</div>
                        <div class="ai-metric-value">{urgency}</div>
                    </div>
                    <div class="ai-metric">
                        <div class="metric-dot" style="background:#8b5cf6; box-shadow:0 0 10px #8b5cf6;"></div>
                        <div class="ai-metric-label">Estimated Impact</div>
                        <div class="ai-metric-value">{population}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            details_col, location_col = st.columns([1.2, 1])

            with details_col:
                st.markdown("##### 🧠 Contextual Extraction")
                st.markdown(
                    f"""
                    <div class="glass-panel">
                        <div class="info-row"><span class="info-label">Input Language</span><span class="info-value">{safe_text(getattr(result, "language", None))}</span></div>
                        <div class="info-row"><span class="info-label">Core Problem</span><span class="info-value">{safe_text(getattr(result, "problem", None))}</span></div>
                        <div class="info-row"><span class="info-label">Service Affected</span><span class="info-value">{safe_text(getattr(result, "affected_service", None))}</span></div>
                        <div class="info-row"><span class="info-label">Brief Summary</span><span class="info-value">{safe_text(getattr(result, "summary", None))}</span></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with location_col:
                st.markdown("##### 📍 Geographic Node")

                source_styles = {
                    "Precise Current Location": ("🎯", "#2dd4bf"),
                    "Manual Override": ("✍️", "#8b5cf6"),
                    "AI Extracted": ("🤖", "#60a5fa"),
                }
                source_icon, source_color = source_styles.get(
                    location_source,
                    ("📍", "#2dd4bf"),
                )

                st.markdown(
                    f"""
                    <div style="margin-bottom:15px; padding:10px 16px; background:rgba(255,255,255,.03); border:1px solid rgba(255,255,255,.05); border-radius:12px;">
                        <span>{source_icon}</span>
                        <span style="color:#94a3b8; font-size:13px;"> Source:</span>
                        <strong style="color:{source_color};"> {safe_text(location_source)}</strong>
                    </div>
                    <div class="glass-panel">
                        <div class="info-row"><span class="info-label">Locality / City</span><span class="info-value">{safe_text(location_data.get("village"))}</span></div>
                        <div class="info-row"><span class="info-label">District</span><span class="info-value">{safe_text(location_data.get("district"))}</span></div>
                        <div class="info-row"><span class="info-label">State Region</span><span class="info-value">{safe_text(location_data.get("state"))}</span></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            latitude = location_data.get("latitude")
            longitude = location_data.get("longitude")

            if latitude is not None and longitude is not None:
                st.markdown(
                    f"""
                    ##### 🗺️ Spatial Visualization
                    <span style="font-size:14px; font-weight:normal; color:#64748b;">
                        [{float(latitude):.6f}, {float(longitude):.6f}]
                    </span>
                    """,
                    unsafe_allow_html=True,
                )

                st.map(
                    {
                        "latitude": [float(latitude)],
                        "longitude": [float(longitude)],
                    },
                    zoom=15,
                )

            with st.expander("📄 View Raw Transcription / Source Text"):
                st.markdown(
                    f"<div style='color:#e2e8f0; line-height:1.6;'>{safe_text(request_text)}</div>",
                    unsafe_allow_html=True,
                )

            with st.expander("💻 Developer Mode: JSON Payload"):
                st.json(
                    {
                        "metadata": {"status": "success"},
                        "ai_inference": model_to_dict(result),
                        "spatial_data": location_data,
                    }
                )

        except Exception as error:
            status.update(label="❌ System Exception Intercepted", state="error")
            st.error("A critical error occurred while processing the request.")
            st.exception(error)

st.markdown(
    """
    <div style="text-align:center; margin-top:80px; padding:40px 0; border-top:1px solid rgba(255,255,255,.05);">
        <div style="font-size:18px; font-weight:700; color:#e2e8f0; margin-bottom:8px;">
            🇮🇳 JanDrishti AI
        </div>
        <div style="color:#64748b; font-size:14px; line-height:1.6;">
            Transforming citizen voices into structured civic intelligence.<br>
            Built for the future of India's infrastructure.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
