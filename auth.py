"""
auth.py
-------
BioSense login using Supabase Auth.
Sessions persist across refreshes via Supabase's built-in token system.

Streamlit secrets format:
[supabase]
url = "https://xxxx.supabase.co"
anon_key = "eyJ..."

[users]
"sara@gmail.com" = { role = "admin", name = "Sara" }
"maria@atek.com" = { role = "client", name = "Maria Fernanda" }
"""

import streamlit as st
from supabase import create_client


def get_supabase():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["anon_key"]
    return create_client(url, key)


def get_user_role(email: str) -> str:
    try:
        users = st.secrets.get("users", {})
        entry = users.get(email.lower(), {})
        return entry.get("role", "client")
    except Exception:
        return "client"


def get_user_name(email: str) -> str:
    try:
        users = st.secrets.get("users", {})
        entry = users.get(email.lower(), {})
        return entry.get("name", email.split("@")[0].title())
    except Exception:
        return email.split("@")[0].title()


def inject_token_bridge():
    """
    Inject JS that:
    1. On load — reads tokens from localStorage and puts them in the URL as query params
    2. After login — saves tokens from query params to localStorage
    This bridges localStorage (survives refresh) with Streamlit (reads query params).
    """
    st.markdown("""
    <script>
    (function() {
        const ACCESS_KEY = 'bs_access_token';
        const REFRESH_KEY = 'bs_refresh_token';

        // If tokens in localStorage but not in URL, inject them into URL
        const access = localStorage.getItem(ACCESS_KEY);
        const refresh = localStorage.getItem(REFRESH_KEY);
        const params = new URLSearchParams(window.parent.location.search);

        if (access && refresh && !params.get('bs_access') && !params.get('bs_refresh')) {
            params.set('bs_access', access);
            params.set('bs_refresh', refresh);
            const newUrl = window.parent.location.pathname + '?' + params.toString();
            window.parent.history.replaceState({}, '', newUrl);
            window.parent.location.reload();
        }
    })();
    </script>
    """, unsafe_allow_html=True)


def save_tokens_to_browser(access_token: str, refresh_token: str):
    """Save tokens to localStorage via JS injection."""
    st.markdown(f"""
    <script>
    (function() {{
        localStorage.setItem('bs_access_token', '{access_token}');
        localStorage.setItem('bs_refresh_token', '{refresh_token}');
    }})();
    </script>
    """, unsafe_allow_html=True)


def clear_tokens_from_browser():
    """Remove tokens from localStorage on logout."""
    st.markdown("""
    <script>
    (function() {
        localStorage.removeItem('bs_access_token');
        localStorage.removeItem('bs_refresh_token');
    })();
    </script>
    """, unsafe_allow_html=True)


def is_logged_in() -> bool:
    """Check session state, then URL params (restored from localStorage on refresh)."""
    # Already in session state
    if st.session_state.get("auth_user"):
        return True

    # Check URL params — set by the JS bridge from localStorage
    params = st.query_params
    access = params.get("bs_access")
    refresh = params.get("bs_refresh")

    if access and refresh:
        try:
            sb = get_supabase()
            result = sb.auth.set_session(access, refresh)
            if result and result.user:
                email = result.user.email
                st.session_state.auth_user = {
                    "email": email,
                    "name": get_user_name(email),
                    "picture": "",
                    "role": get_user_role(email),
                }
                st.session_state.sb_access_token = result.session.access_token
                st.session_state.sb_refresh_token = result.session.refresh_token
                # Clean tokens from URL
                st.query_params.clear()
                return True
        except Exception:
            pass

    return False


def get_current_user():
    return st.session_state.get("auth_user")


def logout():
    try:
        sb = get_supabase()
        sb.auth.sign_out()
    except Exception:
        pass
    clear_tokens_from_browser()
    st.session_state.auth_user = None
    st.session_state.sb_access_token = None
    st.session_state.sb_refresh_token = None
    st.session_state.tour_done = False
    st.session_state.tour_step = 0
    st.rerun()


def handle_oauth_callback():
    """No-op — kept for compatibility."""
    pass


def render_login_page():
    """Splash screen + email/password login via Supabase."""

    if "auth_error" not in st.session_state:
        st.session_state.auth_error = ""

    st.markdown("""
    <style>
    #MainMenu, header, footer, [data-testid="stToolbar"],
    [data-testid="stSidebar"], [data-testid="collapsedControl"],
    [data-testid="stDecoration"] { display: none !important; }
    .stApp, [data-testid="stAppViewContainer"] { background: #07080f !important; }
    .block-container { padding: 0 !important; max-width: 100% !important; }

    @keyframes orbPulse {
        0%,100% { transform: scale(1); opacity: 1; }
        50%      { transform: scale(1.08); opacity: 0.75; }
    }
    @keyframes waveDraw {
        from { stroke-dashoffset: 2400; }
        to   { stroke-dashoffset: 0; }
    }
    @keyframes shimmer {
        0%   { background-position: 0% center; }
        100% { background-position: 400% center; }
    }
    @keyframes diamondPulse {
        0%,100% { opacity:1; transform:scale(1); }
        50%     { opacity:0.45; transform:scale(1.12); }
    }
    .splash-logo { opacity: 1; }
    .splash-card {
        opacity: 0; transform: translateY(50px);
        transition: opacity 0.7s ease-out, transform 0.7s ease-out;
    }
    .splash-card.visible { opacity: 1; transform: translateY(0); }
    .splash-diamond {
        font-size: 4.5rem; color: #a78bfa; display: block;
        margin-bottom: 14px;
        animation: diamondPulse 5s ease-in-out infinite;
    }
    .splash-title {
        font-size: 4.5rem; font-weight: 300; letter-spacing: 0.06em;
        background: linear-gradient(90deg,#e0e0f0 0%,#e0e0f0 10%,#38bdf8 28%,
            #a78bfa 50%,#38bdf8 72%,#e0e0f0 90%,#e0e0f0 100%);
        background-size: 400% auto;
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 8s ease-in-out infinite;
        font-family: system-ui, -apple-system, sans-serif;
    }
    .splash-sub {
        font-size: 13px; color: #4a6a8a; text-transform: uppercase;
        letter-spacing: 0.22em; margin-top: 12px;
        font-family: system-ui, -apple-system, sans-serif;
    }
    .login-card {
        background: linear-gradient(145deg,rgba(12,18,30,0.94),rgba(10,14,24,0.97));
        border: 1px solid rgba(56,189,248,0.2); border-radius: 18px;
        padding: 32px 28px;
        box-shadow: 0 24px 64px rgba(0,0,0,0.6),inset 0 1px 0 rgba(56,189,248,0.08);
        backdrop-filter: blur(20px);
    }
    [data-testid="stTextInput"] input {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(56,189,248,0.15) !important;
        border-radius: 8px !important;
        color: #e0e0f0 !important;
        font-size: 14px !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #1a4a7a, #1e3a5f) !important;
        border: 1px solid rgba(56,189,248,0.35) !important;
        color: #38bdf8 !important;
        border-radius: 10px !important;
        font-size: 15px !important;
        padding: 11px !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #1e5a94, #244870) !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 0 16px rgba(56,189,248,0.2) !important;
    }
    </style>

    <div style="position:fixed;inset:0;background:#07080f;z-index:0;overflow:hidden;pointer-events:none">
      <div style="position:absolute;width:540px;height:540px;border-radius:50%;
          background:radial-gradient(circle,rgba(56,189,248,0.2) 0%,rgba(167,139,250,0.08) 45%,transparent 70%);
          filter:blur(52px);top:50%;left:50%;transform:translate(-50%,-50%);
          animation:orbPulse 6s ease-in-out infinite"></div>
      <div style="position:absolute;width:300px;height:300px;border-radius:50%;
          background:radial-gradient(circle,rgba(167,139,250,0.16) 0%,transparent 65%);
          filter:blur(40px);top:calc(50% - 80px);left:calc(50% + 60px);
          animation:orbPulse 8s ease-in-out infinite 1s"></div>
      <svg style="position:absolute;inset:0;width:100%;height:100%;opacity:0.15"
           viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice">
        <defs>
          <linearGradient id="wg1" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#38bdf8" stop-opacity="0"/>
            <stop offset="20%" stop-color="#38bdf8" stop-opacity="1"/>
            <stop offset="80%" stop-color="#a78bfa" stop-opacity="1"/>
            <stop offset="100%" stop-color="#a78bfa" stop-opacity="0"/>
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
      </svg>
    </div>

    <script>
    (function() {
        function run() {
            var card = window.parent.document.querySelector('.splash-card');
            if (!card) { setTimeout(run, 100); return; }
            setTimeout(function() { card.classList.add('visible'); }, 1400);
        }
        run();
    })();
    </script>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.2, 1])

    with col:
        st.markdown("""
        <div class="splash-logo" style="text-align:center;padding-top:80px;margin-bottom:0;
            position:relative;z-index:2;">
          <span class="splash-diamond">◆</span>
          <div class="splash-title">BioSense</div>
          <div class="splash-sub">Predictive Lab Analytics</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="splash-card login-card" style="position:relative;z-index:2;margin-top:4px">', unsafe_allow_html=True)

        st.markdown("""
        <p style="font-size:10px;text-transform:uppercase;letter-spacing:0.18em;
            color:#38bdf8;margin:0 0 16px;text-align:center">
          Sign in to continue
        </p>
        """, unsafe_allow_html=True)

        email = st.text_input("Email", placeholder="you@company.com",
                              key="login_email", label_visibility="collapsed")
        password = st.text_input("Password", type="password", placeholder="Password",
                                 key="login_password", label_visibility="collapsed")

        if st.button("Sign in →", use_container_width=True, type="primary", key="login_btn"):
            if not email or not password:
                st.session_state.auth_error = "Enter your email and password."
            else:
                try:
                    sb = get_supabase()
                    result = sb.auth.sign_in_with_password({
                        "email": email.strip().lower(),
                        "password": password,
                    })
                    if result.user:
                        user_email = result.user.email
                        st.session_state.auth_user = {
                            "email": user_email,
                            "name": get_user_name(user_email),
                            "picture": "",
                            "role": get_user_role(user_email),
                        }
                        access = result.session.access_token
                        refresh = result.session.refresh_token
                        st.session_state.sb_access_token = access
                        st.session_state.sb_refresh_token = refresh
                        st.session_state.auth_error = ""
                        st.session_state.tour_done = False
                        st.session_state.tour_step = 0
                        # Save to localStorage so session persists on refresh
                        save_tokens_to_browser(access, refresh)
                        st.rerun()
                    else:
                        st.session_state.auth_error = "Incorrect email or password."
                except Exception as e:
                    err = str(e).lower()
                    if "invalid" in err or "credentials" in err or "password" in err:
                        st.session_state.auth_error = "Incorrect email or password."
                    else:
                        st.session_state.auth_error = f"Login error: {str(e)[:100]}"

        if st.session_state.auth_error:
            st.markdown(f"""
            <div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.3);
                border-radius:8px;padding:10px 14px;margin-top:8px;
                font-size:13px;color:#ef4444;text-align:center">
              {st.session_state.auth_error}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <p style="text-align:center;font-size:11px;color:#2a3a4a;margin-top:16px;padding-bottom:8px">
          Access is by invite only
        </p>
        </div>
        <p style="text-align:center;font-size:11px;color:#2a3a4a;margin-top:16px">
          © 2026 BioSense. All rights reserved.
        </p>
        """, unsafe_allow_html=True)
