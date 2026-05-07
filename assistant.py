"""
assistant.py
------------
BioSense virtual assistant — FAQ-based.

Matches user questions against keyword groups and returns pre-written answers.
No API calls, no costs, instant responses.
"""

# Each FAQ entry: keywords (any match triggers it) + the answer
FAQ = [
    {
        "keywords": ["upload", "csv", "file", "import", "data file", "my data"],
        "answer": "Click the 'Upload CSV' button at the top. Your CSV needs a timestamp column (named 'time', 'date', or 'timestamp') and at least 2 numeric sensor columns. You can upload multiple files at once — each one is treated as a separate device and shown side by side.",
    },
    {
        "keywords": ["anomaly score", "what is score", "score mean", "decision function", "isolation"],
        "answer": "The anomaly score comes from the Isolation Forest ML model. Positive values = normal. Near zero = borderline. Negative values = anomaly. The more negative the score, the more confident the model is that something is wrong.",
    },
    {
        "keywords": ["sensitivity", "false alarm", "too many alerts", "too few", "tune model"],
        "answer": "ML Sensitivity controls how much of your data is flagged. Lower (0.01) = fewer false alarms but might miss subtle issues. Higher (0.10) = catches more but more false positives. 0.02 is a good default for most lab environments. Adjust it in the ☰ settings panel.",
    },
    {
        "keywords": ["correlation", "correlated drift", "what is correlation", "sensors together", "linked"],
        "answer": "Correlation analysis finds when two sensors are moving together. If temperature AND humidity drift at the same time, that's usually one root cause (like an HVAC failure) — not two separate problems. Most monitoring systems miss this. Check the correlation timeline on the right side of the dashboard.",
    },
    {
        "keywords": ["confidence", "confidence score", "how confident", "trust"],
        "answer": "Confidence is derived from the anomaly score. 80%+ = critical (act now), 55-80% = warning (investigate), under 55% = info (monitor). It tells you how sure the ML model is that the reading is genuinely abnormal.",
    },
    {
        "keywords": ["predictive", "maintenance window", "threshold breach", "when will", "forecast", "predict"],
        "answer": "The Predictive Maintenance Window estimates when a sensor will cross its normal range based on the current drift rate. Red = act within 2 hours, yellow = act today, blue = monitor. It uses the drift velocity over the last 20% of readings to extrapolate forward.",
    },
    {
        "keywords": ["email", "alert", "notification", "send email", "resend", "notify"],
        "answer": "Open the ☰ settings panel on the right side. Toggle 'Enable email alerts' on, paste your Resend API key, and add the email to send to. Get a free Resend key at resend.com — they give 100 emails/day free. Click 'Send Test Email' to verify it works.",
    },
    {
        "keywords": ["audit", "fda", "21 cfr", "compliance", "gxp", "regulatory", "validation"],
        "answer": "The Event Log at the bottom is your audit trail. Every anomaly is timestamped and includes the parameter name, severity, z-score, and detection method. Export it as CSV with the download button. The format is designed to align with FDA 21 CFR Part 11 expectations for electronic records.",
    },
    {
        "keywords": ["spike", "drift", "dropout", "anomaly type", "kind of anomaly"],
        "answer": "Spike = sudden jump (door opening, glitch). Drift = slow creep over time (developing equipment issue). Dropout = values near zero (sensor disconnect, cable fault). Elevated = sustained out-of-range without a sharp spike. The system auto-detects which type each anomaly is.",
    },
    {
        "keywords": ["normal range", "band", "shaded area", "blue zone"],
        "answer": "The shaded band on each chart is the normal operating range — calculated as the mean ± 2 standard deviations. About 95% of normal readings should fall inside it. Anything outside is statistically unusual and gets flagged.",
    },
    {
        "keywords": ["heatmap", "color", "red blue", "correlation matrix"],
        "answer": "On the correlation heatmap: red = sensors moving together (positive correlation), blue = sensors moving opposite (negative correlation), grey = no relationship. Strong red or blue between two sensors suggests they share a root cause when something goes wrong.",
    },
    {
        "keywords": ["multiple", "compare", "equipment", "devices", "side by side"],
        "answer": "Upload multiple CSV files at once and BioSense compares them side by side. Each device gets a health score (0-100) based on anomaly count. Green = healthy, yellow = watch, red = critical. Click any device to drill into its detailed analysis.",
    },
    {
        "keywords": ["health score", "health", "score 100", "rating"],
        "answer": "The health score is a quick overall rating per device. 100 = no anomalies. Lower scores mean more anomalies were detected. It's calculated as 100 minus (anomaly percentage × 300), capped between 0 and 100.",
    },
    {
        "keywords": ["window", "monitoring window", "hours", "time range", "how long"],
        "answer": "Monitoring Window controls how many hours of simulated data to generate (6-48 hours). Only applies to the Simulated Demo mode. For uploaded CSV, the window is whatever date range your file covers.",
    },
    {
        "keywords": ["correlation window", "rolling window", "5 min"],
        "answer": "Correlation Window is the rolling window size (in minutes) used to calculate how sensor relationships change over time. Smaller windows (5 min) react faster but are noisier. Larger (60 min) are smoother but slower to detect shifts. 15 minutes is the default.",
    },
    {
        "keywords": ["z-score", "z score", "standard deviation", "sigma"],
        "answer": "Z-score measures how far a reading is from normal in standard deviations. Z = 2 means 2 standard deviations away (about 5% of normal data). Z = 3+ is rare. Z = 5+ is almost certainly an anomaly. BioSense flags readings with z > 3 as statistically unusual.",
    },
    {
        "keywords": ["help", "how do i", "how to", "getting started", "start"],
        "answer": "Quick start: 1) Click 'Simulated Demo' to see how it works with built-in data, or 'Upload CSV' to use your own. 2) Watch the sensor charts — anomalies show as red diamonds. 3) Read the explanation cards under each chart. 4) Adjust ML sensitivity in the ☰ settings if you get too many or too few alerts. 5) Export the Event Log when you're done.",
    },
    {
        "keywords": ["cost", "price", "pricing", "how much", "subscription"],
        "answer": "BioSense pricing: Starter $79/month, Professional $199/month, Enterprise custom. White-label licensing available at $5-15 per sensor per month for monitoring system vendors who want AI capabilities. Contact sara.akram for a demo.",
    },
    {
        "keywords": ["who built", "who made", "creator", "founder", "sara"],
        "answer": "BioSense was built by Sara Akram, a biochemistry graduate based in Winnipeg, Canada. It's designed as the AI intelligence layer for existing pharma/biotech monitoring systems like ATEK and PolySense.",
    },
]


def find_faq_match(question: str):
    """
    Try to match user question to an FAQ entry.

    Matching: count how many keywords from each FAQ entry appear in the question.
    Best match wins (must have at least 1 match).
    Returns the answer string if matched, None otherwise.
    """
    q = question.lower().strip()
    if not q:
        return None

    best_score = 0
    best_answer = None

    for entry in FAQ:
        score = sum(1 for kw in entry["keywords"] if kw in q)
        if score > best_score:
            best_score = score
            best_answer = entry["answer"]

    return best_answer if best_score > 0 else None


def get_response(question: str) -> str:
    """Main entry point — returns answer string for any user question."""
    answer = find_faq_match(question)
    if answer:
        return answer

    return (
        "I don't have a specific answer for that yet. Try asking about: "
        "uploading data, anomaly scores, ML sensitivity, correlation analysis, "
        "email alerts, the audit trail, or how to get started. "
        "For anything else, you can email sara.akram or check the README on GitHub."
    )


SUGGESTED_QUESTIONS = [
    "How do I upload my data?",
    "What does the anomaly score mean?",
    "How do I set up email alerts?",
    "What's the difference between spike and drift?",
    "How does correlation analysis work?",
]
