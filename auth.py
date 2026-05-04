"""
auth.py
-------
BioSense login system — splash screen + credential gate.

Secrets format (Streamlit Cloud → App settings → Secrets):

[users]
"maria@atek.com" = { password = "atek2024", name = "Maria Fernanda", role = "client" }
"matthew@polysense.com" = { password = "poly2024", name = "Matthew Gale", role = "client" }
"sara@biosense.app" = { password = "yourpassword", name = "Sara", role = "admin" }
"""

import streamlit as st
import hashlib


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def check_credentials(email: str, password: str):
    try:
        users = st.secrets.get("users", {})
    except Exception:
        return None

    email = email.strip().lower()
    user = users.get(email)
    if not user:
        return None

    stored_pw = user.get("password", "")
    if stored_pw == password or stored_pw == hash_password(password):
        return {
            "email": email,
            "name": user.get("name", email.split("@")[0].title()),
            "role": user.get("role", "viewer"),
        }
    return None


def is_logged_in() -> bool:
    return st.session_state.get("auth_user") is not None


def get_current_user():
    return st.session_state.get("auth_user")


def logout():
    st.session_state.auth_user = None
    st.session_state.tour_done = False
    st.session_state.tour_step = 0
    st.rerun()


def render_login_page():
    """Full-page splash + login. Option B orb with waveform background."""

    st.markdown("""
    <style>
    #MainMenu, header, footer, [data-testid="stToolbar"],
    [data-testid="stSidebar"], [data-testid="collapsedControl"],
    [data-testid="stDecoration"] {
        display: none !important;
    }
    .stApp, [data-testid="stAppViewContainer"] {
        background: #07080f !important;
    }
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    /* Splash wrapper */
    .splash {
        position: fixed;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #07080f;
        overflow: hidden;
        z-index: 0;
    }

    /* Waveform SVG background */
    .wave-bg {
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        opacity: 0.18;
    }

    /* Orb glow */
    .orb {
        position: absolute;
        width: 520px;
        height: 520px;
        border-radius: 50%;
        background: radial-gradient(circle,
            rgba(56,189,248,0.22) 0%,
            rgba(167,139,250,0.10) 45%,
            transparent 70%);
        filter: blur(48px);
        animation: orbPulse 6s ease-in-out infinite;
        pointer-events: none;
    }
    @keyframes orbPulse {
        0%,100% { transform: scale(1); opacity: 1; }
        50%      { transform: scale(1.08); opacity: 0.75; }
    }

    /* Second smaller orb for depth */
    .orb2 {
        position: absolute;
        width: 280px;
        height: 280px;
        border-radius: 50%;
        background: radial-gradient(circle,
            rgba(167,139,250,0.18) 0%,
            transparent 65%);
        filter: blur(36px);
        transform: translate(80px, 60px);
        animation: orbPulse2 8s ease-in-out infinite;
        pointer-events: none;
    }
    @keyframes orbPulse2 {
        0%,100% { transform: translate(80px,60px) scale(1); opacity: 0.7; }
        50%      { transform: translate(60px,80px) scale(1.1); opacity: 1; }
    }

    /* Waveform line animation */
    @keyframes waveDraw {
        from { stroke-dashoffset: 2000; }
        to   { stroke-dashoffset: 0; }
    }
    @keyframes waveFlow {
        from { transform: translateX(0); }
        to   { transform: translateX(-50%); }
    }

    /* Logo */
    @keyframes shimmer {
        0%   { background-position: 0% center; }
        100% { background-position: 400% center; }
    }
    @keyframes diamondPulse {
        0%,100% { opacity: 1; transform: scale(1); }
        50%     { opacity: 0.45; transform: scale(1.12); }
    }
    .splash-diamond {
        font-size: 3rem;
        color: #a78bfa;
        display: block;
        margin-bottom: 10px;
        animation: diamondPulse 5s ease-in-out infinite;
    }
    .splash-title {
        font-size: 3rem;
        font-weight: 300;
        letter-spacing: 0.06em;
        background: linear-gradient(90deg,
            #e0e0f0 0%, #e0e0f0 10%,
            #38bdf8 28%, #a78bfa 50%,
            #38bdf8 72%, #e0e0f0 90%, #e0e0f0 100%);
        background-size: 400% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 8s ease-in-out infinite;
        font-family: system-ui, -apple-system, sans-serif;
    }
    .splash-sub {
        font-size: 11px;
        color: #4a6a8a;
        text-transform: uppercase;
        letter-spacing: 0.22em;
        margin-top: 8px;
        font-family: system-ui, -apple-system, sans-serif;
    }
    .splash-divider {
        width: 48px;
        height: 1px;
        background: linear-gradient(90deg, transparent, #38bdf8, transparent);
        margin: 20px auto;
    }

    /* Login card */
    .login-card {
        position: relative;
        background: linear-gradient(145deg,
            rgba(12,18,30,0.92) 0%,
            rgba(10,14,24,0.95) 100%);
        border: 1px solid rgba(56,189,248,0.2);
        border-radius: 18px;
        padding: 36px 32px 28px;
        width: 100%;
        max-width: 380px;
        box-shadow:
            0 24px 64px rgba(0,0,0,0.6),
            0 0 0 1px rgba(56,189,248,0.06),
            inset 0 1px 0 rgba(56,189,248,0.08);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        text-align: center;
        z-index: 1;
    }

    /* Streamlit input styling on login page */
    .login-card input {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(56,189,248,0.15) !important;
        border-radius: 8px !important;
        color: #e0e0f0 !important;
        font-size: 14px !important;
    }
    .login-card input:focus {
        border-color: rgba(56,189,248,0.4) !important;
        box-shadow: 0 0 0 2px rgba(56,189,248,0.08) !important;
    }

    /* Primary button */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #1a4a7a, #1e3a5f) !important;
        border: 1px solid rgba(56,189,248,0.35) !important;
        color: #38bdf8 !important;
        border-radius: 10px !important;
        font-size: 14px !important;
        padding: 10px !important;
        letter-spacing: 0.04em !important;
        transition: all 0.2s !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #1e5a94, #244870) !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 0 16px rgba(56,189,248,0.2) !important;
    }
    </style>

    <!-- Splash background: waveform + orbs -->
    <div class="splash">
      <div class="orb"></div>
      <div class="orb2"></div>

      <!-- Animated waveform SVG — two copies side by side for seamless scroll -->
      <svg class="wave-bg" viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice"
           xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="wg1" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%"   stop-color="#38bdf8" stop-opacity="0"/>
            <stop offset="20%"  stop-color="#38bdf8" stop-opacity="1"/>
            <stop offset="80%"  stop-color="#a78bfa" stop-opacity="1"/>
            <stop offset="100%" stop-color="#a78bfa" stop-opacity="0"/>
          </linearGradient>
          <linearGradient id="wg2" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%"   stop-color="#a78bfa" stop-opacity="0"/>
            <stop offset="20%"  stop-color="#a78bfa" stop-opacity="0.6"/>
            <stop offset="80%"  stop-color="#34d399" stop-opacity="0.6"/>
            <stop offset="100%" stop-color="#34d399" stop-opacity="0"/>
          </linearGradient>
        </defs>
        <!-- Main waveform line -->
        <path d="M-100,450 L80,450 L100,420 L120,390 L140,450 L180,450
                 L200,410 L220,370 L240,310 L260,380 L280,420 L300,450
                 L340,450 L360,430 L380,395 L400,450 L440,450
                 L460,400 L480,340 L500,280 L520,200 L540,300 L560,380 L580,430 L600,450
                 L640,450 L660,420 L680,390 L700,360 L720,400 L740,440 L760,450
                 L800,450 L820,410 L840,370 L860,420 L880,450
                 L920,450 L940,430 L960,380 L980,320 L1000,390 L1020,430 L1040,450
                 L1080,450 L1100,420 L1120,400 L1140,450 L1180,450
                 L1200,410 L1220,360 L1240,310 L1260,370 L1280,420 L1300,450
                 L1440,450 L1540,450"
              fill="none" stroke="url(#wg1)" stroke-width="1.5"
              stroke-dasharray="2000" stroke-dashoffset="2000"
              style="animation: waveDraw 3s ease-out 0.3s forwards"/>
        <!-- Secondary softer line offset vertically -->
        <path d="M-100,490 L80,490 L110,460 L130,430 L150,490 L190,490
                 L210,450 L230,410 L250,370 L270,440 L290,480 L310,490
                 L350,490 L370,465 L390,440 L420,490 L460,490
                 L480,445 L500,390 L520,340 L540,260 L560,350 L580,420 L600,470 L620,490
                 L660,490 L680,460 L700,430 L720,400 L740,445 L760,480 L780,490
                 L820,490 L840,450 L860,420 L880,465 L910,490
                 L950,490 L970,465 L990,420 L1010,360 L1030,430 L1050,475 L1070,490
                 L1110,490 L1130,455 L1150,430 L1170,490
                 L1220,490 L1250,445 L1270,390 L1300,450 L1330,480 L1360,490 L1440,490"
              fill="none" stroke="url(#wg2)" stroke-width="1"
              stroke-dasharray="2000" stroke-dashoffset="2000"
              style="animation: waveDraw 3.5s ease-out 0.8s forwards; opacity:0.5"/>
      </svg>
    </div>
    """, unsafe_allow_html=True)

    # Centered login card using Streamlit columns
    _, col, _ = st.columns([1, 1.4, 1])

    with col:
        # Logo section
        st.markdown("""
        <div style="text-align:center; padding-top: 80px; margin-bottom: 32px; position:relative; z-index:2;">
          <span class="splash-diamond">◆</span>
          <div class="splash-title">BioSense</div>
          <div class="splash-sub">Predictive Lab Analytics</div>
          <div class="splash-divider"></div>
        </div>
        """, unsafe_allow_html=True)

        # Login form
        st.markdown("""
        <div style="position:relative;z-index:2;
            background:linear-gradient(145deg,rgba(12,18,30,0.92),rgba(10,14,24,0.95));
            border:1px solid rgba(56,189,248,0.2);border-radius:18px;
            padding:28px 24px 8px;
            box-shadow:0 24px 64px rgba(0,0,0,0.6),inset 0 1px 0 rgba(56,189,248,0.08);
            backdrop-filter:blur(20px);">
          <p style="font-size:10px;text-transform:uppercase;letter-spacing:0.18em;
              color:#38bdf8;margin:0 0 20px;text-align:center">
            Sign in to your account
          </p>
        </div>
        """, unsafe_allow_html=True)

        email = st.text_input(
            "Email address",
            placeholder="you@company.com",
            key="login_email",
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="••••••••",
            key="login_password",
        )

        if "login_error" not in st.session_state:
            st.session_state.login_error = ""

        if st.button("Sign in →", use_container_width=True, type="primary", key="login_btn"):
            if not email or not password:
                st.session_state.login_error = "Enter your email and password."
            else:
                user = check_credentials(email, password)
                if user:
                    st.session_state.auth_user = user
                    st.session_state.login_error = ""
                    st.session_state.tour_done = False
                    st.session_state.tour_step = 0
                    st.rerun()
                else:
                    st.session_state.login_error = "Incorrect email or password."

        if st.session_state.login_error:
            st.markdown(f"""
            <div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.3);
                border-radius:8px;padding:10px 14px;margin-top:8px;
                font-size:13px;color:#ef4444;text-align:center">
              {st.session_state.login_error}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <p style="text-align:center;font-size:11px;color:#2a3a4a;margin-top:20px;padding-bottom:40px">
          Need access? Contact sara@biosense.app
        </p>
        """, unsafe_allow_html=True)
