"""
alerts.py
---------
Email alert system for BioSense using Resend.
Sends alerts when anomalies or correlated drifts are detected.
"""

import resend
from datetime import datetime


def send_alert(
    api_key: str,
    to_email: str,
    from_email: str,
    alert_type: str,
    severity: str,
    parameter: str,
    message: str,
    value: float = None,
    recommendation: str = None,
    dashboard_url: str = "http://localhost:8501",
):
    """
    Send a single anomaly alert email via Resend.

    Parameters:
        api_key       — your Resend API key
        to_email      — recipient email address
        from_email    — sender address (must be verified in Resend)
        alert_type    — "Anomaly" or "Correlated drift"
        severity      — "critical", "warning", or "info"
        parameter     — which sensor/parameter triggered the alert
        message       — description of what happened
        value         — the actual sensor reading (optional)
        recommendation — what to do about it (optional)
        dashboard_url — link to the BioSense dashboard
    """
    resend.api_key = api_key

    # Color and emoji based on severity
    if severity == "critical":
        color = "#ef4444"
        emoji = "🔴"
        header_bg = "#1a0a0a"
        border = "#ef4444"
    elif severity == "warning":
        color = "#fbbf24"
        emoji = "🟡"
        header_bg = "#1a1500"
        border = "#fbbf24"
    else:
        color = "#38bdf8"
        emoji = "🔵"
        header_bg = "#0a1520"
        border = "#38bdf8"

    now = datetime.now().strftime("%B %d, %Y at %H:%M")

    value_row = f"""
    <tr>
      <td style="padding:8px 0;color:#8fafc8;font-size:13px;border-bottom:1px solid #1e2a3d">Sensor value</td>
      <td style="padding:8px 0;color:#e0e0f0;font-size:13px;border-bottom:1px solid #1e2a3d;text-align:right;font-weight:500">{value}</td>
    </tr>""" if value is not None else ""

    rec_block = f"""
    <div style="margin-top:20px;padding:14px 16px;background:#0f1e30;border-radius:8px;border:1px solid rgba(56,189,248,0.2)">
      <p style="margin:0 0 4px;font-size:11px;text-transform:uppercase;letter-spacing:0.1em;color:#38bdf8">Recommended action</p>
      <p style="margin:0;font-size:14px;color:#c0d0e0">{recommendation}</p>
    </div>""" if recommendation else ""

    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="margin:0;padding:0;background:#0a0a0f;font-family:system-ui,-apple-system,sans-serif">
      <div style="max-width:560px;margin:0 auto;padding:24px 16px">

        <!-- Header -->
        <div style="background:{header_bg};border:1px solid {border};border-radius:12px;overflow:hidden;margin-bottom:0">
          <div style="padding:20px 24px;border-bottom:1px solid {border}">
            <div style="display:flex;align-items:center;gap:12px">
              <span style="font-size:22px">{emoji}</span>
              <div>
                <p style="margin:0;font-size:11px;text-transform:uppercase;letter-spacing:0.12em;color:{color}">
                  BioSense {severity.upper()} ALERT
                </p>
                <p style="margin:4px 0 0;font-size:18px;font-weight:500;color:#e0e0f0">{alert_type} detected</p>
              </div>
            </div>
          </div>

          <!-- Details -->
          <div style="padding:20px 24px">
            <table style="width:100%;border-collapse:collapse">
              <tr>
                <td style="padding:8px 0;color:#8fafc8;font-size:13px;border-bottom:1px solid #1e2a3d">Time</td>
                <td style="padding:8px 0;color:#e0e0f0;font-size:13px;border-bottom:1px solid #1e2a3d;text-align:right">{now}</td>
              </tr>
              <tr>
                <td style="padding:8px 0;color:#8fafc8;font-size:13px;border-bottom:1px solid #1e2a3d">Parameter</td>
                <td style="padding:8px 0;color:#e0e0f0;font-size:13px;border-bottom:1px solid #1e2a3d;text-align:right;font-weight:500">{parameter}</td>
              </tr>
              {value_row}
              <tr>
                <td colspan="2" style="padding:12px 0 0">
                  <p style="margin:0;font-size:14px;color:#c0d0e0;line-height:1.6">{message}</p>
                </td>
              </tr>
            </table>

            {rec_block}

            <!-- CTA -->
            <div style="margin-top:24px;text-align:center">
              <a href="{dashboard_url}"
                 style="display:inline-block;padding:12px 28px;background:#1a3a5c;
                        border:1px solid #38bdf8;border-radius:8px;
                        color:#38bdf8;text-decoration:none;font-size:14px">
                View dashboard →
              </a>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <p style="text-align:center;margin-top:16px;font-size:11px;color:#2a3a4a">
          BioSense · Predictive Lab Analytics · This is an automated alert
        </p>
      </div>
    </body>
    </html>
    """

    subject_prefix = {"critical": "🔴 CRITICAL", "warning": "🟡 WARNING", "info": "🔵 INFO"}.get(severity, "")
    subject = f"{subject_prefix} BioSense: {parameter} — {alert_type}"

    try:
        response = resend.Emails.send({
            "from": from_email,
            "to": [to_email],
            "subject": subject,
            "html": html,
        })
        return {"success": True, "id": response.get("id")}
    except Exception as e:
        return {"success": False, "error": str(e)}


def send_anomaly_alerts(api_key, to_email, from_email, df, sensor_cols, drift_events, sensor_display, dashboard_url="http://localhost:8501"):
    """
    Check for anomalies and correlated drifts and send alerts.
    Called after each detection run.

    Returns list of sent alert results.
    """
    sent = []

    # --- Critical anomaly alerts ---
    anom_rows = df[df["detected_anomaly"] == 1]
    if len(anom_rows) > 0:
        # Find worst parameter
        worst_param = None
        worst_z = 0
        latest_anom = anom_rows.iloc[-1]

        for c in sensor_cols:
            m, s = df[c].mean(), df[c].std()
            z = abs((latest_anom[c] - m) / (s + 1e-8))
            if z > worst_z:
                worst_z = z
                worst_param = c

        if worst_param and worst_z > 3:
            label = sensor_display.get(worst_param, {}).get("label", worst_param)
            val = round(latest_anom[worst_param], 2)
            unit = sensor_display.get(worst_param, {}).get("unit", "")
            severity = "critical" if worst_z > 5 else "warning"

            rec_map = {
                "temperature_c": "Check heating/cooling system and inspect door seals immediately.",
                "ph": "Check CO₂ supply, media composition, and cell viability.",
                "dissolved_oxygen_pct": "Inspect agitation system, sparger, and dissolved oxygen probe calibration.",
            }
            recommendation = rec_map.get(worst_param, "Inspect equipment and review recent operational changes.")

            result = send_alert(
                api_key=api_key,
                to_email=to_email,
                from_email=from_email,
                alert_type="Anomaly detected",
                severity=severity,
                parameter=f"{label}",
                message=f"{label} is showing anomalous behavior. Current reading: {val} {unit}. The ML model flagged this as {worst_z:.1f} standard deviations from normal — significantly outside expected range.",
                value=f"{val} {unit}",
                recommendation=recommendation,
                dashboard_url=dashboard_url,
            )
            sent.append(result)

    # --- Correlated drift alerts ---
    for ev in drift_events:
        if ev.get("severity") in ("high", "medium"):
            result = send_alert(
                api_key=api_key,
                to_email=to_email,
                from_email=from_email,
                alert_type="Correlated drift",
                severity="critical" if ev["severity"] == "high" else "warning",
                parameter=ev["parameters"],
                message=ev["message"],
                value=None,
                recommendation=f"Multiple sensors drifting together suggests a single root cause. Inspect the equipment or environment for systemic issues affecting {ev['parameters']}.",
                dashboard_url=dashboard_url,
            )
            sent.append(result)

    return sent


if __name__ == "__main__":
    # Quick test — sends a test email
    import os
    api_key = input("Enter your Resend API key: ")
    to_email = input("Enter your email address: ")

    result = send_alert(
        api_key=api_key,
        to_email=to_email,
        from_email="onboarding@resend.dev",
        alert_type="Test alert",
        severity="warning",
        parameter="Temperature",
        message="This is a test alert from BioSense. Your email alert system is working correctly.",
        value="-77.2 °C",
        recommendation="No action needed — this is just a test.",
    )
    print(result)
