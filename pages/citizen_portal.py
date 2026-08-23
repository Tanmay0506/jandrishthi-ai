import html

import streamlit as st
from dotenv import load_dotenv
from streamlit_mic_recorder import speech_to_text

from ai.extractor import analyze_request
from database.database import create_table, save_request
from utils.geocoding import geocode_location


load_dotenv()
create_table()

st.set_page_config(
    page_title="JanDrishti AI",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# Session state
# -----------------------------
for key, default_value in {
    "request_text": "",
    "voice_text": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default_value


def safe_text(value, fallback="Unknown"):
    """Safely render text values inside custom HTML."""
    if value is None or str(value).strip() == "":
        value = fallback
    return html.escape(str(value))


def model_to_dict(result):
    """Support Pydantic v1 and v2 models."""
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return vars(result)


def population_display(value):
    """Prevent formatting errors if the AI returns non-numeric data."""
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return safe_text(value, "Not available")


# -----------------------------
# Premium Dark CSS
# -----------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

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

    /* Permanently hide Streamlit menu, toolbar, and sidebar. */
    [data-testid="stSidebar"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"],
    button[aria-label="Open sidebar"],
    button[title="Open sidebar"],
    #MainMenu,
    footer,
    header,
    [data-testid="stToolbar"],
    [data-testid="stStatusWidget"] {
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
    }

    .block-container {
        padding-top: 2.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 1320px !important;
    }

    * {
        scroll-behavior: smooth;
    }

    ::selection {
        background: rgba(45, 212, 191, 0.3);
        color: #ffffff;
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
    }

    .hero-wrapper::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -20%;
        width: 60%;
        height: 200%;
        background: radial-gradient(circle, rgba(45, 212, 191, 0.15) 0%, transparent 60%);
        transform: rotate(15deg);
        pointer-events: none;
    }

    .hero-wrapper::after {
        content: '';
        position: absolute;
        bottom: -50%;
        right: -20%;
        width: 60%;
        height: 200%;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, transparent 60%);
        transform: rotate(-15deg);
        pointer-events: none;
    }

    .hero-title {
        position: relative;
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
        position: relative;
        font-size: 24px;
        font-weight: 500;
        color: #e2e8f0;
        margin-bottom: 25px;
    }

    .hero-description {
        position: relative;
        max-width: 700px;
        color: #94a3b8;
        font-size: 17px;
        line-height: 1.8;
        margin-bottom: 35px;
    }

    .badge-row {
        position: relative;
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
    }

    .modern-badge {
        display: inline-flex;
        align-items: center;
        padding: 8px 18px;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        color: #cbd5e1;
        font-size: 13.5px;
        font-weight: 600;
    }

    .section-header {
        font-size: 28px;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.5px;
        margin-top: 20px;
        margin-bottom: 8px;
    }

    .section-caption {
        color: #64748b;
        font-size: 15px;
        margin-bottom: 30px;
        line-height: 1.6;
    }

    .glass-panel {
        background: rgba(15, 23, 42, 0.5);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 24px;
        padding: 30px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    }

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
        position: relative;
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
        font-size: 13px;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .ai-metric-value {
        margin-top: 8px;
        font-size: 25px;
        font-weight: 800;
        color: #ffffff;
        overflow-wrap: anywhere;
    }

    .info-row {
        display: flex;
        align-items: flex-start;
        gap: 16px;
        padding: 14px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
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
        overflow-wrap: anywhere;
    }

    div[data-testid="stTabs"] button {
        background: transparent !important;
        border: none !important;
        color: #64748b !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
        border-bottom: 2px solid transparent !important;
    }

    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: #2dd4bf !important;
        border-bottom: 2px solid #2dd4bf !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #0d9488 0%, #3b82f6 100%) !important;
        color: #ffffff !important;
        border-radius: 16px !important;
        font-weight: 700 !important;
        font-size: 18px !important;
        padding: 1.15rem 2rem !important;
        border: none !important;
        animation: pulseGlow 3s infinite;
    }

    .stTextArea textarea,
    .stTextInput input,
    .stSelectbox > div > div {
        background-color: rgba(15, 23, 42, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        color: #f8fafc !important;
    }

    div[data-testid="stAlert"],
    div[data-testid="stExpanderDetails"] {
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        backdrop-filter: blur(10px);
    }

    iframe {
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.12), transparent) !important;
        margin: 40px 0 !important;
    }

    @media (max-width: 768px) {
        .block-container { padding: 1.2rem !important; }
        .hero-wrapper { padding: 36px 28px; }
        .hero-title { font-size: 42px; }
        .hero-subtitle { font-size: 19px; }
        .info-row { flex-direction: column; gap: 4px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Hero section
# -----------------------------
st.markdown(
    """
    <div class="hero-wrapper">
        <div class="hero-title">JanDrishti AI</div>
        <div class="hero-subtitle">Elevating Citizen Voices to Infrastructure Intelligence</div>
        <div class="hero-description">
            Empowering communities across India. We transform everyday infrastructure
            concerns into structured, location-aware intelligence for faster action.
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

# -----------------------------
# Complaint submission
# -----------------------------
st.markdown('<div class="section-header">🗣️ Voice Your Concern</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-caption">Describe the infrastructure issue by text or voice.</div>',
    unsafe_allow_html=True,
)

tab_text, tab_voice = st.tabs(["⌨️ Text Submission", "🎙️ Voice Submission"])

with tab_text:
    st.markdown(
        """
        <div class="glass-panel" style="margin-bottom:15px; padding:20px;">
            <h4 style="margin:0; color:#f8fafc;">Detailed Description</h4>
            <p style="margin:5px 0 0; color:#94a3b8;">
                Include the issue, nearby landmarks, and its impact on the community.
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

with tab_voice:
    st.markdown(
        """
        <div class="glass-panel" style="margin-bottom:15px; padding:20px;">
            <h4 style="margin:0; color:#f8fafc;">Speak Naturally</h4>
            <p style="margin:5px 0 0; color:#94a3b8;">
                Choose a language and record your concern. JanDrishti will transcribe it.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    language_codes = {
        "English": "en-IN",
        "Hindi": "hi-IN",
        "Marathi": "mr-IN",
    }

    language_col, mic_col = st.columns([1, 2])

    with language_col:
        voice_language = st.selectbox(
            "Select Language",
            list(language_codes),
        )

    with mic_col:
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

# -----------------------------
# Location input
# -----------------------------
st.markdown('<div class="section-header">📍 Pinpoint the Location</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="section-caption">
        Enter a location manually for maximum accuracy, or let JanDrishti
        extract the location from the complaint.
    </div>
    """,
    unsafe_allow_html=True,
)

location_input = st.text_input(
    "Manual Location Override (Optional)",
    placeholder="e.g., Kothrud, Pune, Maharashtra",
    help="Leave blank to let JanDrishti detect a location from your complaint.",
)

# -----------------------------
# AI analysis execution
# -----------------------------
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

            if location_input.strip():
                resolved_input = location_input.strip()
                location_source = "Manual Override"
            else:
                resolved_input = str(getattr(result, "location", "")).strip()
                location_source = "AI Extracted"

            if not resolved_input or resolved_input.lower() == "unknown":
                status.update(label="📍 Location required", state="error")
                st.error(
                    "No valid location was detected. Please enter a precise "
                    "location in the field above."
                )
                st.stop()

            st.write(f"🛰️ Resolving spatial coordinates for: **{resolved_input}**")
            location_data = geocode_location(resolved_input)

            if location_data is None:
                status.update(label="❌ Geocoding Failed", state="error")
                st.error(
                    f"Could not map '{resolved_input}'. Try a broader city or district."
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

            # -------------------------
            # Results UI
            # -------------------------
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

            details_col, geographic_col = st.columns([1.2, 1])

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

            with geographic_col:
                st.markdown("##### 📍 Geographic Node")

                source_icon = "✍️" if location_source == "Manual Override" else "🤖"
                source_color = "#8b5cf6" if location_source == "Manual Override" else "#2dd4bf"

                st.markdown(
                    f"""
                    <div style="margin-bottom:15px; padding:10px 16px; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.05); border-radius:12px;">
                        <span>{source_icon}</span>
                        <span style="color:#94a3b8; font-size:13px;"> Source:</span>
                        <strong style="color:{source_color};"> {safe_text(location_source)} — {safe_text(resolved_input)}</strong>
                    </div>
                    <div class="glass-panel" style="padding:24px;">
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
                    zoom=13,
                )

            with st.expander("📄 View Raw Transcription / Source Text", expanded=False):
                st.markdown(
                    f"<div style='color:#e2e8f0; line-height:1.6;'>{safe_text(request_text)}</div>",
                    unsafe_allow_html=True,
                )

            with st.expander("💻 Developer Mode: JSON Payload", expanded=False):
                st.json(
                    {
                        "metadata": {
                            "status": "success",
                            "timestamp": "auto-generated",
                        },
                        "ai_inference": model_to_dict(result),
                        "spatial_data": location_data,
                    }
                )

        except Exception as error:
            status.update(label="❌ System Exception Intercepted", state="error")
            st.error("A critical error occurred while processing the request.")
            st.exception(error)

# -----------------------------
# Footer
# -----------------------------
st.markdown(
    """
    <div style="text-align:center; margin-top:80px; padding:40px 0; border-top:1px solid rgba(255,255,255,0.05);">
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
