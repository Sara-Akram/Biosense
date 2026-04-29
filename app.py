"""
app.py (v3.0)
-------------
BioSense — dark theme, premium executive-ready dashboard.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from data_generator import generate_bioreactor_data
from correlation import analyze_correlations, detect_correlated_drifts
from sklearn.ensemble import IsolationForest


# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="BioSense",
    page_icon="◆",
    layout="wide",
)

# ── Dark theme CSS ───────────────────────────────────────────
st.markdown("""
<style>
    /* Force dark background everywhere */
    .stApp, .main, [data-testid="stAppViewContainer"],
    [data-testid="stHeader"], [data-testid="stToolbar"] {
        background-color: #0a0a0f !important;
    }
    .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }

    /* Sidebar dark */
    [data-testid="stSidebar"] {
        background-color: #111118 !important;
        border-right: 1px solid #1e1e2a;
    }
    [data-testid="stSidebar"] * {
        color: #a0a0b8 !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #e0e0f0 !important;
    }

    /* Hide Streamlit developer toolbar/menu */
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    #MainMenu,
    header[data-testid="stHeader"],
    .stDeployButton {
        display: none !important;
        visibility: hidden !important;
    }

    /* Force ALL text bright on dark background */
    h1, h2, h3, p, span, label, div, li, a {
        color: #e0e0f0 !important;
    }
    /* Title */
    h1 {
        font-size: 2rem !important;
        font-weight: 300 !important;
        letter-spacing: 0.02em;
        color: #ffffff !important;
    }
    /* Section subheaders */
    [data-testid="stSubheader"] h2,
    [data-testid="stSubheader"] p,
    .stSubheader {
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        color: #7ab3d4 !important;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-top: 2rem;
    }
    /* Caption text */
    [data-testid="stCaption"] p,
    .stCaption p {
        color: #5a7a8f !important;
        font-size: 13px !important;
    }
    /* Markdown text */
    .stMarkdown p {
        color: #c0d0e0 !important;
    }

    /* Metric cards — frosted glass effect */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, rgba(30,40,60,0.6) 0%, rgba(20,28,45,0.8) 50%, rgba(15,22,38,0.6) 100%) !important;
        border: 1px solid rgba(56,138,221,0.2) !important;
        border-radius: 14px !important;
        padding: 1.4rem !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        box-shadow: 0 4px 24px rgba(0,0,0,0.3), inset 0 1px 0 rgba(56,138,221,0.08) !important;
    }
    [data-testid="stMetricLabel"] p {
        color: #7ab3d4 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.12em;
    }
    [data-testid="stMetricValue"] div {
        color: #ffffff !important;
        font-weight: 300 !important;
        font-size: 1.8rem !important;
        text-shadow: 0 0 20px rgba(255,255,255,0.1);
    }
    [data-testid="stMetricDelta"] div {
        color: #38bdf8 !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 1px solid #1e2a3d !important;
        gap: 0;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #4a6a8a !important;
        font-size: 0.85rem !important;
        font-weight: 400 !important;
        padding: 8px 20px !important;
    }
    .stTabs [aria-selected="true"] {
        color: #38bdf8 !important;
        background: transparent !important;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #38bdf8 !important;
        height: 2px !important;
    }
    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }

    /* Expander */
    [data-testid="stExpander"] {
        background: #111118 !important;
        border: 1px solid #1e1e2a !important;
        border-radius: 8px;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background: #111118 !important;
        border: 1px dashed #2a2a3d !important;
        border-radius: 8px;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border: 1px solid #1e1e2a !important;
        border-radius: 8px;
    }

    /* Download button */
    .stDownloadButton button {
        background: transparent !important;
        border: 1px solid #1e3a5f !important;
        color: #38bdf8 !important;
        border-radius: 8px;
    }
    .stDownloadButton button:hover {
        border-color: #38bdf8 !important;
        background: rgba(56,189,248,0.08) !important;
    }

    /* Radio buttons */
    [data-testid="stRadio"] label span {
        color: #a0a0b8 !important;
    }

    /* Caption text */
    .stCaption, [data-testid="stCaption"] p {
        color: #4a4a6a !important;
    }

    /* Divider */
    hr {
        border-color: #1e1e2a !important;
    }

    /* Select boxes and inputs */
    [data-baseweb="select"], [data-baseweb="input"] {
        background: #111118 !important;
        border-color: #2a2a3d !important;
    }

    /* Multiselect */
    [data-testid="stMultiSelect"] span {
        background: #0f2a4a !important;
        color: #38bdf8 !important;
    }

    /* Info/success/warning boxes */
    [data-testid="stInfo"], [data-testid="stSuccess"], [data-testid="stWarning"] {
        background: #111118 !important;
        border: 1px solid #2a2a3d !important;
        color: #a0a0b8 !important;
    }

    /* Slider — clean track and thumb */
    [data-testid="stSlider"] {
        padding: 0 4px;
    }
    [data-testid="stSlider"] [data-baseweb="slider"] {
        margin-top: 8px;
    }
    [data-testid="stSlider"] div[role="slider"] {
        background: #38bdf8 !important;
        border: 2px solid #0a0a0f !important;
        width: 16px !important;
        height: 16px !important;
        box-shadow: 0 0 6px rgba(56,189,248,0.4) !important;
    }
    [data-testid="stSlider"] [data-testid="stTickBar"] {
        color: #4a6a8a !important;
        font-size: 11px !important;
    }
</style>
""", unsafe_allow_html=True)


# ── Chart theme (dark) ───────────────────────────────────────
CHART_BG = "#0a0a0f"
CHART_GRID = "rgba(255,255,255,0.04)"
CHART_TEXT = "#4a7a9f"
CHART_COLORS = ["#38bdf8", "#06b6d4", "#0ea5e9", "#67e8f9", "#22d3ee", "#7dd3fc"]
ANOMALY_COLOR = "#ef4444"
NORMAL_BAND = "rgba(56,189,248,0.05)"
NORMAL_BORDER = "rgba(56,189,248,0.12)"


def dark_layout(height=280):
    return dict(
        height=height,
        margin=dict(l=0, r=0, t=30, b=0),
        showlegend=False,
        hovermode="x unified",
        plot_bgcolor=CHART_BG,
        paper_bgcolor=CHART_BG,
        yaxis=dict(gridcolor=CHART_GRID, tickfont=dict(color=CHART_TEXT, size=11), title_font=dict(color=CHART_TEXT, size=12)),
        xaxis=dict(gridcolor=CHART_GRID, tickfont=dict(color=CHART_TEXT, size=11)),
        font=dict(color="#e0e0f0"),
    )


# ── Header ───────────────────────────────────────────────────
st.markdown("<h1 style='margin-bottom:0'>◆ BioSense</h1>", unsafe_allow_html=True)
st.caption("Predictive anomaly detection  ·  Multi-parameter correlation  ·  Audit trail")


# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Data source")
    data_source = st.radio(
        "Source",
        ["Upload CSV", "Simulated demo data"],
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("### Detection settings")

    sensitivity = st.slider(
        "ML sensitivity", min_value=0.01, max_value=0.10, value=0.02, step=0.01,
        help="Lower = fewer false alarms"
    )
    correlation_window = st.slider(
        "Correlation window (min)", min_value=5, max_value=60, value=15, step=5,
        help="Rolling window for correlation analysis"
    )

    st.divider()
    st.markdown("### Alert settings")

    alerts_enabled = st.toggle("Enable email alerts", value=False)

    if alerts_enabled:
        resend_api_key = st.text_input(
            "Resend API key",
            type="password",
            placeholder="re_xxxxxxxxxxxx",
            help="Get your free API key at resend.com"
        )
        alert_email = st.text_input(
            "Send alerts to",
            placeholder="lab@yourcompany.com",
        )
        from_email = st.text_input(
            "Send alerts from",
            value="onboarding@resend.dev",
            help="Use onboarding@resend.dev for testing. Add your own domain in Resend for production."
        )
        alert_severity = st.selectbox(
            "Minimum severity to alert",
            ["critical only", "warning and above", "all"],
            index=1,
        )

        if st.button("Send test email"):
            if resend_api_key and alert_email:
                from alerts import send_alert
                with st.spinner("Sending..."):
                    result = send_alert(
                        api_key=resend_api_key,
                        to_email=alert_email,
                        from_email=from_email,
                        alert_type="Test alert",
                        severity="warning",
                        parameter="Temperature",
                        message="This is a test alert from BioSense. Your email alert system is working correctly.",
                        value="-77.2 °C",
                        recommendation="No action needed — this is just a test.",
                    )
                if result.get("success"):
                    st.success("Test email sent!")
                else:
                    st.error(f"Failed: {result.get('error')}")
            else:
                st.warning("Enter your API key and email address first")
    else:
        resend_api_key = None
        alert_email = None
        from_email = "onboarding@resend.dev"
        alert_severity = "warning and above"

    st.divider()
    st.markdown("<div style='text-align:center;margin-top:2rem'>"
                "<span style='color:#4a4a6a;font-size:12px'>BioSense v3.0</span><br>"
                "<span style='color:#3a3a5a;font-size:11px'>by Sara Akram</span>"
                "</div>", unsafe_allow_html=True)


# ── Data loading ─────────────────────────────────────────────
df = None
sensor_cols = None

if data_source == "Upload CSV":
    st.subheader("Upload data")
    st.markdown("<p style='color:#6060a0;font-size:14px'>CSV with a timestamp column and 2+ numeric sensor columns</p>", unsafe_allow_html=True)

    with st.expander("Example CSV format"):
        example = pd.DataFrame({
            "timestamp": ["2026-04-17 08:00", "2026-04-17 08:01", "2026-04-17 08:02"],
            "temperature": [37.0, 37.1, 37.0],
            "humidity": [45.2, 45.1, 45.3],
            "pressure": [101.3, 101.3, 101.2],
        })
        st.dataframe(example, use_container_width=True)

    uploaded_file = st.file_uploader("", type=["csv"], label_visibility="collapsed")

    if uploaded_file is not None:
        try:
            raw_df = pd.read_csv(uploaded_file)
            st.success(f"{len(raw_df)} rows loaded")

            all_cols = list(raw_df.columns)
            timestamp_col = st.selectbox("Timestamp column", all_cols, index=0)

            numeric_candidates = [
                c for c in all_cols
                if c != timestamp_col and pd.to_numeric(raw_df[c], errors='coerce').notna().mean() > 0.8
            ]

            selected_sensors = st.multiselect(
                "Sensor columns (select 2+)",
                numeric_candidates if numeric_candidates else [c for c in all_cols if c != timestamp_col],
                default=numeric_candidates[:3] if len(numeric_candidates) >= 2 else [],
            )

            if len(selected_sensors) >= 2:
                df = raw_df[[timestamp_col] + selected_sensors].copy()
                df.columns = ["timestamp"] + selected_sensors
                df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
                for col in selected_sensors:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                df = df.dropna().sort_values("timestamp").reset_index(drop=True)
                sensor_cols = selected_sensors
            elif len(selected_sensors) == 1:
                st.warning("Select at least 2 sensor columns")
        except Exception as e:
            st.error(f"Could not read file: {e}")

else:
    hours = st.sidebar.slider("Monitoring window (hours)", 6, 48, 24)

    @st.cache_data
    def load_demo(hours):
        return generate_bioreactor_data(hours=hours)

    df = load_demo(hours)
    sensor_cols = ["temperature_c", "ph", "dissolved_oxygen_pct"]


# ── Analysis ─────────────────────────────────────────────────
if df is not None and sensor_cols is not None:

    features = df[sensor_cols].values
    model = IsolationForest(contamination=sensitivity, random_state=42, n_estimators=100)
    predictions = model.fit_predict(features)
    scores = model.decision_function(features)

    df["ml_anomaly"] = (predictions == -1).astype(int)
    df["anomaly_score"] = np.round(scores, 4)

    z_scores_all = np.abs((features - features.mean(axis=0)) / (features.std(axis=0) + 1e-8))
    df["zscore_anomaly"] = (z_scores_all.max(axis=1) > 3).astype(int)

    df["raw_flag"] = ((df["ml_anomaly"] == 1) | (df["zscore_anomaly"] == 1)).astype(int)
    df["detected_anomaly"] = 0
    flags = df["raw_flag"].values
    count = 0
    streak_start = 0
    for i in range(len(flags)):
        if flags[i] == 1:
            if count == 0:
                streak_start = i
            count += 1
        else:
            if count >= 3:
                df.iloc[streak_start:i, df.columns.get_loc("detected_anomaly")] = 1
            count = 0
    if count >= 3:
        df.iloc[streak_start:len(flags), df.columns.get_loc("detected_anomaly")] = 1

    corr_results = analyze_correlations(df, sensor_cols, correlation_window)
    drift_events = detect_correlated_drifts(df, sensor_cols, correlation_window)

    # ── Send alerts if enabled ───────────────────────────────
    if alerts_enabled and resend_api_key and alert_email:
        if df["detected_anomaly"].sum() > 0 or len(drift_events) > 0:
            from alerts import send_anomaly_alerts
            with st.spinner("Sending alerts..."):
                results = send_anomaly_alerts(
                    api_key=resend_api_key,
                    to_email=alert_email,
                    from_email=from_email,
                    df=df,
                    sensor_cols=sensor_cols,
                    drift_events=drift_events,
                    sensor_display=sensor_display if "sensor_display" in dir() else {},
                )
            sent_ok = sum(1 for r in results if r.get("success"))
            if sent_ok > 0:
                st.toast(f"📧 {sent_ok} alert email(s) sent to {alert_email}", icon="✅")

    # ── Metric cards ─────────────────────────────────────────
    metric_cols = st.columns(min(len(sensor_cols) + 1, 4))
    latest = df.iloc[-1]

    sensor_labels = {
        "temperature_c": "Temperature",
        "ph": "pH level",
        "dissolved_oxygen_pct": "Dissolved O₂",
    }

    for i, col_name in enumerate(sensor_cols[:3]):
        with metric_cols[i]:
            label = sensor_labels.get(col_name, col_name.replace("_", " ").title())
            val = latest[col_name]
            unit = " °C" if "temp" in col_name.lower() else (" %" if "oxygen" in col_name.lower() or "do" in col_name.lower() else "")
            st.metric(label, f"{val:.2f}{unit}")

    with metric_cols[min(len(sensor_cols), 3)]:
        total_anomalies = int(df["detected_anomaly"].sum())
        st.metric("Anomalies", total_anomalies, delta=f"{len(drift_events)} correlated", delta_color="inverse")

    # ── Sensor charts ────────────────────────────────────────
    st.subheader("Sensor readings")

    # Clean labels and distinct colors per sensor
    sensor_display = {
        "temperature_c": {"label": "Temperature", "unit": "°C", "color": "#38bdf8", "band_fill": "rgba(56,189,248,0.15)", "band_border": "rgba(56,189,248,0.4)"},
        "ph": {"label": "pH", "unit": "", "color": "#34d399", "band_fill": "rgba(52,211,153,0.15)", "band_border": "rgba(52,211,153,0.4)"},
        "dissolved_oxygen_pct": {"label": "Dissolved O₂", "unit": "%", "color": "#fbbf24", "band_fill": "rgba(251,191,36,0.15)", "band_border": "rgba(251,191,36,0.4)"},
    }

    # Fallback colors for uploaded CSV columns
    fallback_colors = [
        {"color": "#38bdf8", "band_fill": "rgba(56,189,248,0.15)", "band_border": "rgba(56,189,248,0.4)"},
        {"color": "#34d399", "band_fill": "rgba(52,211,153,0.15)", "band_border": "rgba(52,211,153,0.4)"},
        {"color": "#fbbf24", "band_fill": "rgba(251,191,36,0.15)", "band_border": "rgba(251,191,36,0.4)"},
        {"color": "#f472b6", "band_fill": "rgba(244,114,182,0.15)", "band_border": "rgba(244,114,182,0.4)"},
        {"color": "#a78bfa", "band_fill": "rgba(167,139,250,0.15)", "band_border": "rgba(167,139,250,0.4)"},
    ]

    # Build clean tab names
    tab_names = []
    for col_name in sensor_cols:
        if col_name in sensor_display:
            tab_names.append(sensor_display[col_name]["label"])
        else:
            tab_names.append(col_name.replace("_", " ").title())

    tabs = st.tabs(tab_names)
    for i, col_name in enumerate(sensor_cols):
        with tabs[i]:
            fig = go.Figure()

            # Get color config for this sensor
            if col_name in sensor_display:
                cfg = sensor_display[col_name]
            else:
                cfg = fallback_colors[i % len(fallback_colors)]
                cfg["label"] = col_name.replace("_", " ").title()
                cfg["unit"] = ""

            display_label = sensor_display.get(col_name, {}).get("label", col_name.replace("_", " ").title())
            display_unit = sensor_display.get(col_name, {}).get("unit", "")

            # Data line
            fig.add_trace(go.Scatter(
                x=df["timestamp"], y=df[col_name], mode="lines",
                name=display_label, line=dict(color=cfg["color"], width=1.5),
                hovertemplate=f"{display_label}: %{{y:.2f}} {display_unit}<extra></extra>",
            ))

            # Anomaly markers
            anom = df[df["detected_anomaly"] == 1]
            if len(anom) > 0:
                fig.add_trace(go.Scatter(
                    x=anom["timestamp"], y=anom[col_name], mode="markers",
                    name="Anomaly", marker=dict(color=ANOMALY_COLOR, size=6, symbol="diamond"),
                ))

            # Normal range band — brighter and more visible
            mean_v = df[col_name].mean()
            std_v = df[col_name].std()
            fig.add_hrect(
                y0=mean_v - 2 * std_v, y1=mean_v + 2 * std_v,
                fillcolor=cfg["band_fill"],
                line=dict(width=0.8, color=cfg["band_border"], dash="dot"),
                annotation_text="Normal range",
                annotation_position="top left",
                annotation_font_size=11,
                annotation_font_color=cfg["band_border"],
            )

            # Clean axis label with unit — no rotated title, just tick labels
            fig.update_layout(
                height=280,
                margin=dict(l=10, r=10, t=30, b=0),
                showlegend=False,
                hovermode="x unified",
                plot_bgcolor=CHART_BG,
                paper_bgcolor=CHART_BG,
                yaxis=dict(
                    gridcolor="rgba(255,255,255,0.06)",
                    tickfont=dict(color="#8fafc8", size=12),
                    title=None,
                    showgrid=True,
                ),
                xaxis=dict(
                    gridcolor="rgba(255,255,255,0.04)",
                    tickfont=dict(color="#8fafc8", size=11),
                ),
                font=dict(color="#e0e0f0"),
            )
            st.plotly_chart(fig, use_container_width=True)

    # ── ML anomaly score ─────────────────────────────────────
    st.subheader("Anomaly score")
    fig_s = go.Figure()
    fig_s.add_trace(go.Scatter(
        x=df["timestamp"], y=df["anomaly_score"], mode="lines",
        line=dict(color="#1e6091", width=1),
        fill="tozeroy", fillcolor="rgba(56,189,248,0.03)",
    ))
    ml_f = df[df["ml_anomaly"] == 1]
    fig_s.add_trace(go.Scatter(
        x=ml_f["timestamp"], y=ml_f["anomaly_score"], mode="markers",
        marker=dict(color=ANOMALY_COLOR, size=5, symbol="diamond"),
    ))
    layout_s = dark_layout(180)
    layout_s["yaxis"]["title"] = "Score"
    layout_s["yaxis"]["tickfont"] = dict(color="#8fafc8", size=12)
    layout_s["yaxis"]["title_font"] = dict(color="#8fafc8", size=13)
    layout_s["xaxis"]["tickfont"] = dict(color="#8fafc8", size=11)
    fig_s.update_layout(**layout_s)
    st.plotly_chart(fig_s, use_container_width=True)

    # ── Correlation section ──────────────────────────────────
    st.subheader("Correlation analysis")
    st.caption("Shows when sensor relationships changed — sudden shifts indicate a single root cause affecting multiple sensors")

    col_a, col_b = st.columns(2)

    with col_a:
        corr_matrix = corr_results["correlation_matrix"]
        heatmap_labels = [sensor_display.get(c, {}).get("label", c.replace("_", " ").title()) for c in sensor_cols]
        fig_h = go.Figure(data=go.Heatmap(
            z=corr_matrix, x=heatmap_labels, y=heatmap_labels,
            colorscale=[[0, "#0c4a6e"], [0.5, "#0f1520"], [1, "#ef4444"]],
            zmin=-1, zmax=1, text=np.round(corr_matrix, 2), texttemplate="%{text}",
            textfont=dict(size=12, color="#e0e0f0"),
        ))
        fig_h.update_layout(
            height=300, margin=dict(l=0, r=0, t=10, b=0),
            plot_bgcolor=CHART_BG, paper_bgcolor=CHART_BG,
            font=dict(color="#e0e0f0"),
            xaxis=dict(tickfont=dict(color="#8fafc8", size=11)),
            yaxis=dict(tickfont=dict(color="#8fafc8", size=11)),
        )
        st.plotly_chart(fig_h, use_container_width=True)
        st.caption("Red = moving together · Blue = moving opposite · Grey = no relationship")

        # Existing drift events below heatmap
        if drift_events:
            for ev in drift_events[:4]:
                sev_color = "#ef4444" if ev["severity"] == "high" else "#f59e0b"
                st.markdown(
                    f"<div style='padding:10px 14px;margin:6px 0;border-radius:8px;"
                    f"border-left:3px solid {sev_color};background:#111118;"
                    f"border:1px solid #1e1e2a;border-left:3px solid {sev_color}'>"
                    f"<strong style='color:#e0e0f0;font-size:14px'>{ev['parameters']}</strong><br>"
                    f"<span style='font-size:13px;color:#8888aa'>{ev['message']}</span><br>"
                    f"<span style='font-size:11px;color:#4a4a6a'>{ev['time_range']}</span></div>",
                    unsafe_allow_html=True,
                )
        else:
            st.markdown("<div style='padding:16px;text-align:center;color:#4a4a6a;font-size:13px'>No correlated drifts detected</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown("<p style='font-size:12px;color:#4a7a9f;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:12px'>When did sensor relationships change?</p>", unsafe_allow_html=True)

        # Build correlation change timeline
        pair_idx = 0
        timeline_events = []
        pair_colors_map = ["#38bdf8", "#34d399", "#fbbf24", "#f472b6"]

        for i in range(len(sensor_cols)):
            for j in range(i + 1, len(sensor_cols)):
                if pair_idx >= 4:
                    break
                col_i = sensor_cols[i]
                col_j = sensor_cols[j]
                label_a = sensor_display.get(col_i, {}).get("label", col_i.replace("_", " ").title())
                label_b = sensor_display.get(col_j, {}).get("label", col_j.replace("_", " ").title())
                color = pair_colors_map[pair_idx]

                rc = df[col_i].rolling(window=correlation_window, min_periods=5).corr(df[col_j])

                # Detect crossings of ±0.5 threshold
                prev_state = "independent"
                for k in range(len(rc)):
                    curr = rc.iloc[k]
                    if np.isnan(curr):
                        continue
                    if curr > 0.5:
                        curr_state = "linked"
                    elif curr < -0.5:
                        curr_state = "opposed"
                    else:
                        curr_state = "independent"

                    if curr_state != prev_state and prev_state is not None:
                        ts = df["timestamp"].iloc[k]

                        if curr_state == "linked":
                            msg = f"{label_a} + {label_b} started moving together"
                            why = f"Connection strength jumped to {curr:.0%} — check for shared root cause"
                            sev = "high"
                        elif curr_state == "opposed":
                            msg = f"{label_a} rising while {label_b} dropping (or vice versa)"
                            why = f"Inverse relationship detected — one sensor compensating for another"
                            sev = "medium"
                        else:
                            msg = f"{label_a} + {label_b} became independent again"
                            why = "Sensors returned to normal independent behavior"
                            sev = "ok"

                        timeline_events.append({
                            "timestamp": ts,
                            "message": msg,
                            "why": why,
                            "severity": sev,
                            "color": color,
                            "pair": f"{label_a} + {label_b}",
                        })

                    prev_state = curr_state
                pair_idx += 1

        # Sort by time, most recent first
        timeline_events.sort(key=lambda x: x["timestamp"], reverse=True)

        if timeline_events:
            def render_tl_event(ev):
                if ev["severity"] == "high":
                    dot_color = "#ef4444"
                    glow = "box-shadow:0 0 6px rgba(239,68,68,0.4)"
                elif ev["severity"] == "medium":
                    dot_color = "#fbbf24"
                    glow = ""
                else:
                    dot_color = "#34d399"
                    glow = ""
                ts_str = ev["timestamp"].strftime("%H:%M  %b %d") if hasattr(ev["timestamp"], "strftime") else str(ev["timestamp"])[:16]
                return f"""
                <div style='position:relative;padding:10px 0 10px 16px;border-bottom:1px solid rgba(56,138,221,0.07)'>
                  <div style='position:absolute;left:-25px;top:16px;width:8px;height:8px;
                    border-radius:50%;background:{dot_color};{glow}'></div>
                  <div style='font-size:11px;color:#4a6a8a;font-family:monospace;margin-bottom:3px'>{ts_str}</div>
                  <div style='font-size:13px;color:#c0d0e0;margin-bottom:3px;font-weight:500'>{ev['message']}</div>
                  <div style='font-size:12px;color:#5a7a8f;line-height:1.4'>{ev['why']}</div>
                </div>"""

            # Show latest 3 pinned at the top
            pinned_html = "<div style='position:relative;padding-left:20px;border-left:1px solid rgba(56,138,221,0.15)'>"
            for ev in timeline_events[:3]:
                pinned_html += render_tl_event(ev)
            pinned_html += "</div>"
            st.markdown(pinned_html, unsafe_allow_html=True)

            # Remaining events in a scrollable box
            if len(timeline_events) > 3:
                scroll_html = "<div style='position:relative;padding-left:20px;border-left:1px solid rgba(56,138,221,0.1);max-height:260px;overflow-y:auto;margin-top:4px;padding-right:4px'>"
                for ev in timeline_events[3:]:
                    scroll_html += render_tl_event(ev)
                scroll_html += "</div>"
                st.markdown(f"<p style='font-size:11px;color:#3a5a7a;margin:8px 0 4px'>Earlier events — scroll to see more</p>", unsafe_allow_html=True)
                st.markdown(scroll_html, unsafe_allow_html=True)
        else:
            st.markdown("<div style='padding:16px;text-align:center;color:#4a4a6a;font-size:13px'>No correlation changes detected in this window</div>", unsafe_allow_html=True)

    # Rolling correlation
    if len(sensor_cols) >= 2:
        fig_r = go.Figure()
        pair_colors = ["#38bdf8", "#34d399", "#fbbf24", "#f472b6"]
        idx = 0
        for i in range(len(sensor_cols)):
            for j in range(i + 1, min(len(sensor_cols), i + 4)):
                if idx >= 4:
                    break
                label_a = sensor_display.get(sensor_cols[i], {}).get("label", sensor_cols[i].replace("_", " ").title())
                label_b = sensor_display.get(sensor_cols[j], {}).get("label", sensor_cols[j].replace("_", " ").title())
                pair = f"{label_a} vs {label_b}"
                rc = df[sensor_cols[i]].rolling(window=correlation_window, min_periods=5).corr(df[sensor_cols[j]])
                fig_r.add_trace(go.Scatter(
                    x=df["timestamp"], y=rc, mode="lines",
                    name=pair, line=dict(color=pair_colors[idx], width=1.5),
                ))
                idx += 1

        fig_r.add_hline(y=0.7, line_dash="dot", line_color="rgba(239,68,68,0.3)", line_width=1)
        fig_r.add_hline(y=-0.7, line_dash="dot", line_color="rgba(59,130,246,0.3)", line_width=1)

        layout_r = dark_layout(220)
        layout_r["showlegend"] = True
        layout_r["legend"] = dict(orientation="h", yanchor="bottom", y=1.02, font=dict(color="#8fafc8", size=11))
        layout_r["yaxis"]["title"] = "Correlation"
        layout_r["yaxis"]["range"] = [-1.1, 1.1]
        layout_r["yaxis"]["tickfont"] = dict(color="#8fafc8", size=12)
        layout_r["yaxis"]["title_font"] = dict(color="#8fafc8", size=13)
        layout_r["xaxis"]["tickfont"] = dict(color="#8fafc8", size=11)
        fig_r.update_layout(**layout_r)
        st.plotly_chart(fig_r, use_container_width=True)

    # ── Event log ────────────────────────────────────────────
    st.subheader("Event log")
    events = []
    anom_rows = df[df["detected_anomaly"] == 1]
    for _, row in anom_rows.iterrows():
        zs = {}
        for c in sensor_cols:
            m, s = df[c].mean(), df[c].std()
            zs[c] = abs((row[c] - m) / (s + 1e-8))
        worst = max(zs, key=zs.get)
        events.append({
            "timestamp": row["timestamp"], "type": "Anomaly",
            "severity": "critical" if zs[worst] > 4 else "warning",
            "parameter": worst, "message": f"{worst} = {row[worst]:.2f} (z: {zs[worst]:.1f})",
            "method": "ML + statistical",
        })
    for ev in drift_events:
        events.append({
            "timestamp": ev.get("start_time", ""), "type": "Correlated drift",
            "severity": ev["severity"], "parameter": ev["parameters"],
            "message": ev["message"], "method": "correlation",
        })

    if events:
        ev_df = pd.DataFrame(events).sort_values("timestamp", ascending=False).head(100)
        st.dataframe(ev_df, use_container_width=True, height=350)
        st.download_button("Export event log", ev_df.to_csv(index=False), "biosense_events.csv", "text/csv")
    else:
        st.markdown("<div style='padding:20px;text-align:center;color:#4a4a6a'>No events detected</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("<div style='text-align:center;padding:1rem 0'>"
                "<span style='color:#2a2a3d;font-size:12px'>◆ BioSense v3.0</span>"
                "</div>", unsafe_allow_html=True)

else:
    if data_source == "Upload CSV":
        st.markdown("<div style='padding:60px 20px;text-align:center'>"
                    "<p style='color:#4a4a6a;font-size:16px'>Upload a CSV to begin analysis</p>"
                    "</div>", unsafe_allow_html=True)
