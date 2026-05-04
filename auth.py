"""
auth.py
-------
BioSense Google OAuth login.

Flow:
1. User clicks "Sign in with Google"
2. Redirected to Google login
3. Google sends back a code to our redirect URI
4. We exchange the code for user info
5. Check if email is in allowed_users list
6. If yes — log them in
"""

import streamlit as st
import requests
import urllib.parse


def get_google_auth_url() -> str:
    """Build the Google OAuth URL to redirect the user to."""
    client_id = st.secrets["google_oauth"]["client_id"]
    redirect_uri = st.secrets["google_oauth"]["redirect_uri"]

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
    }
    base = "https://accounts.google.com/o/oauth2/v2/auth"
    return base + "?" + urllib.parse.urlencode(params)


def exchange_code_for_user(code: str) -> dict | None:
    """
    Exchange the OAuth code Google sent us for actual user info.
    Returns user dict or None if it fails.
    """
    client_id = st.secrets["google_oauth"]["client_id"]
    client_secret = st.secrets["google_oauth"]["client_secret"]
    redirect_uri = st.secrets["google_oauth"]["redirect_uri"]

    # Step 1 — get access token
    token_resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        },
        timeout=10,
    )

    if not token_resp.ok:
        return None

    access_token = token_resp.json().get("access_token")
    if not access_token:
        return None

    # Step 2 — get user info using the token
    user_resp = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )

    if not user_resp.ok:
        return None

    return user_resp.json()  # has email, name, picture


def is_allowed(email: str) -> bool:
    """Check if this email is in the approved list."""
    try:
        allowed = st.secrets["allowed_users"]["emails"]
        return email.lower() in [e.lower() for e in allowed]
    except Exception:
        return False


def is_logged_in() -> bool:
    return st.session_state.get("auth_user") is not None


def get_current_user() -> dict | None:
    return st.session_state.get("auth_user")


def logout():
    st.session_state.auth_user = None
    st.session_state.tour_done = False
    st.session_state.tour_step = 0
    st.rerun()


def handle_oauth_callback():
    """
    Called on every page load. If Google sent back a ?code=,
    we exchange it, check the email, and log the user in.
    """
    params = st.query_params
    code = params.get("code")
    error = params.get("error")

    if error:
        st.session_state.auth_error = "Google sign-in was cancelled. Please try again."
        st.query_params.clear()
        return

    if code and not is_logged_in():
        with st.spinner("Signing you in..."):
            user_info = exchange_code_for_user(code)

        # Clear the code from the URL immediately
        st.query_params.clear()

        if not user_info:
            st.session_state.auth_error = "Could not retrieve your Google account info. Please try again."
            return

        email = user_info.get("email", "")

        if not is_allowed(email):
            st.session_state.auth_error = f"{email} doesn't have access to BioSense. Request access from Sara."
            return

        # Logged in
        st.session_state.auth_user = {
            "email": email,
            "name": user_info.get("name", email.split("@")[0].title()),
            "picture": user_info.get("picture", ""),
        }
        st.session_state.auth_error = ""
        st.session_state.tour_done = False
        st.session_state.tour_step = 0
        st.rerun()


def render_login_page():
    """Full splash screen + Google sign-in button."""

    # Initialize error state
    if "auth_error" not in st.session_state:
        st.session_state.auth_error = ""

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

    /* Orb glow */
    @keyframes orbPulse {
        0%,100% { transform: scale(1); opacity: 1; }
        50%      { transform: scale(1.08); opacity: 0.75; }
    }
    @keyframes orbPulse2 {
        0%,100% { transform: translate(80px,60px) scale(1); opacity:0.7; }
        50%      { transform: translate(60px,80px) scale(1.1); opacity:1; }
    }

    /* Waveform draw */
    @keyframes waveDraw {
        from { stroke-dashoffset: 2400; }
        to   { stroke-dashoffset: 0; }
    }

    /* Logo shimmer */
    @keyframes shimmer {
        0%   { background-position: 0% center; }
        100% { background-position: 400% center; }
    }
    @keyframes diamondPulse {
        0%,100% { opacity:1; transform:scale(1); }
        50%     { opacity:0.45; transform:scale(1.12); }
    }

    /* Login card slide up */
    @keyframes slideUp {
        from { opacity:0; transform: translateY(40px); }
        to   { opacity:1; transform: translateY(0); }
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
    .login-card {
        animation: slideUp 0.7s ease-out 1.8s both;
        background: linear-gradient(145deg,
            rgba(12,18,30,0.94) 0%,
            rgba(10,14,24,0.97) 100%);
        border: 1px solid rgba(56,189,248,0.2);
        border-radius: 18px;
        padding: 32px 28px;
        box-shadow:
            0 24px 64px rgba(0,0,0,0.6),
            inset 0 1px 0 rgba(56,189,248,0.08);
        backdrop-filter: blur(20px);
    }
    .google-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        width: 100%;
        padding: 13px 20px;
        background: #ffffff;
        border: none;
        border-radius: 10px;
        font-size: 15px;
        font-weight: 500;
        color: #1a1a2e;
        cursor: pointer;
        text-decoration: none;
        transition: all 0.2s;
        box-shadow: 0 2px 12px rgba(0,0,0,0.3);
        margin-top: 8px;
    }
    .google-btn:hover {
        background: #f5f5f5;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        transform: translateY(-1px);
    }
    .google-logo {
        width: 20px;
        height: 20px;
    }
    </style>

    <!-- Background: orbs + waveform -->
    <div style="position:fixed;inset:0;background:#07080f;z-index:0;overflow:hidden;pointer-events:none">

      <!-- Orb 1 -->
      <div style="position:absolute;width:540px;height:540px;border-radius:50%;
          background:radial-gradient(circle,rgba(56,189,248,0.2) 0%,rgba(167,139,250,0.08) 45%,transparent 70%);
          filter:blur(52px);top:50%;left:50%;transform:translate(-50%,-50%);
          animation:orbPulse 6s ease-in-out infinite"></div>

      <!-- Orb 2 -->
      <div style="position:absolute;width:300px;height:300px;border-radius:50%;
          background:radial-gradient(circle,rgba(167,139,250,0.16) 0%,transparent 65%);
          filter:blur(40px);top:calc(50% - 80px);left:calc(50% + 60px);
          animation:orbPulse2 8s ease-in-out infinite"></div>

      <!-- Waveform SVG -->
      <svg style="position:absolute;inset:0;width:100%;height:100%;opacity:0.15"
           viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice">
        <defs>
          <linearGradient id="wg1" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%"   stop-color="#38bdf8" stop-opacity="0"/>
            <stop offset="20%"  stop-color="#38bdf8" stop-opacity="1"/>
            <stop offset="80%"  stop-color="#a78bfa" stop-opacity="1"/>
            <stop offset="100%" stop-color="#a78bfa" stop-opacity="0"/>
          </linearGradient>
          <linearGradient id="wg2" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%"   stop-color="#a78bfa" stop-opacity="0"/>
            <stop offset="25%"  stop-color="#34d399" stop-opacity="0.5"/>
            <stop offset="75%"  stop-color="#38bdf8" stop-opacity="0.5"/>
            <stop offset="100%" stop-color="#38bdf8" stop-opacity="0"/>
          </linearGradient>
        </defs>
        <path d="M-100,450 L80,450 L100,420 L120,390 L140,450 L180,450
                 L200,410 L220,370 L240,310 L260,380 L280,420 L300,450
                 L340,450 L360,430 L380,395 L400,450 L440,450
                 L460,400 L480,340 L500,280 L520,200 L540,300 L560,380 L580,430 L600,450
                 L640,450 L660,420 L680,390 L700,360 L720,400 L740,440 L760,450
                 L800,450 L820,410 L840,370 L860,420 L880,450
                 L920,450 L940,430 L960,380 L980,320 L1000,390 L1020,430 L1040,450
                 L1080,450 L1100,420 L1120,400 L1140,450 L1180,450
                 L1200,410 L1220,360 L1240,310 L1260,370 L1280,420 L1300,450 L1540,450"
              fill="none" stroke="url(#wg1)" stroke-width="1.5"
              stroke-dasharray="2400" stroke-dashoffset="2400"
              style="animation:waveDraw 3s ease-out 0.2s forwards"/>
        <path d="M-100,480 L100,480 L130,450 L160,410 L180,480 L220,480
                 L250,440 L280,390 L310,340 L340,410 L370,465 L400,480
                 L440,480 L470,450 L500,400 L530,350 L560,270 L590,360 L620,430 L650,475 L680,480
                 L720,480 L750,445 L780,410 L810,455 L840,478 L870,480
                 L910,480 L940,445 L970,400 L1000,350 L1030,420 L1060,468 L1090,480
                 L1130,480 L1160,448 L1190,415 L1220,460 L1260,480
                 L1300,480 L1330,440 L1360,390 L1400,450 L1440,480"
              fill="none" stroke="url(#wg2)" stroke-width="1"
              stroke-dasharray="2400" stroke-dashoffset="2400"
              style="animation:waveDraw 3.8s ease-out 0.6s forwards;opacity:0.5"/>
      </svg>
    </div>
    """, unsafe_allow_html=True)

    # Centered content
    _, col, _ = st.columns([1, 1.2, 1])

    with col:
        # Logo — fades in first
        st.markdown("""
        <div style="text-align:center;padding-top:100px;margin-bottom:36px;
            position:relative;z-index:2;
            animation:slideUp 0.6s ease-out 0.5s both;">
          <span class="splash-diamond">◆</span>
          <div class="splash-title">BioSense</div>
          <div class="splash-sub">Predictive Lab Analytics</div>
          <div class="splash-divider"></div>
        </div>
        """, unsafe_allow_html=True)

        # Login card — slides up after logo
        st.markdown('<div class="login-card" style="position:relative;z-index:2">', unsafe_allow_html=True)

        st.markdown("""
        <p style="font-size:10px;text-transform:uppercase;letter-spacing:0.18em;
            color:#38bdf8;margin:0 0 20px;text-align:center">
          Sign in to continue
        </p>
        """, unsafe_allow_html=True)

        # Google sign-in button
        auth_url = get_google_auth_url()
        st.markdown(f"""
        <a href="{auth_url}" class="google-btn">
          <svg class="google-logo" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          Continue with Google
        </a>
        """, unsafe_allow_html=True)

        # Error message
        if st.session_state.auth_error:
            st.markdown(f"""
            <div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.3);
                border-radius:8px;padding:10px 14px;margin-top:14px;
                font-size:13px;color:#ef4444;text-align:center;line-height:1.5">
              {st.session_state.auth_error}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <p style="text-align:center;font-size:11px;color:#1e2a3a;margin-top:20px">
          Access is by invite only
        </p>
        </div>
        """, unsafe_allow_html=True)
