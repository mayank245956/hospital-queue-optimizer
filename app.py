"""
Hospital Queue & Waiting Time Optimizer
========================================
A complete Streamlit dashboard built on M/M/c queueing theory.
All logic is self-contained in this single file.

Run:
    pip install streamlit pandas numpy matplotlib
    streamlit run app.py
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from math import factorial, ceil
from dataclasses import dataclass

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Hospital Queue Optimizer",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    /* ── Base ── */
    .main { background-color: #0a0e1a; }
    .block-container { padding: 1.5rem 2rem 2rem 2rem; max-width: 1400px; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1628 0%, #0a0e1a 100%);
        border-right: 1px solid #1e2d4a;
    }
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #7eb8f7 !important;
    }

    /* ── KPI Cards ── */
    .kpi-card {
        background: linear-gradient(135deg, #0d1628 0%, #111d35 100%);
        border: 1px solid #1e2d4a;
        border-radius: 14px;
        padding: 1.2rem 1rem;
        text-align: center;
        transition: border-color 0.2s;
    }
    .kpi-card:hover { border-color: #3a7bd5; }
    .kpi-label {
        font-size: 11px;
        color: #4a6a9a;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        line-height: 1.1;
        margin-bottom: 4px;
    }
    .kpi-sub {
        font-size: 11px;
        color: #3a5a7a;
    }
    .kpi-blue  .kpi-value { color: #4da6ff; }
    .kpi-green .kpi-value { color: #4ade80; }
    .kpi-amber .kpi-value { color: #fbbf24; }
    .kpi-red   .kpi-value { color: #f87171; }
    .kpi-teal  .kpi-value { color: #2dd4bf; }
    .kpi-gold  .kpi-value { color: #f59e0b; }

    /* ── Insight Boxes ── */
    .insight {
        padding: 0.75rem 1rem 0.75rem 1.2rem;
        border-radius: 10px;
        font-size: 13.5px;
        line-height: 1.6;
        margin-bottom: 0.6rem;
        border-left: 4px solid;
    }
    .ins-danger  { background:#1f0a0a; border-color:#ef4444; color:#fca5a5; }
    .ins-warning { background:#1f1408; border-color:#f59e0b; color:#fcd34d; }
    .ins-success { background:#071f0e; border-color:#22c55e; color:#86efac; }
    .ins-info    { background:#071428; border-color:#3b82f6; color:#93c5fd; }
    .ins-purple  { background:#110a1f; border-color:#a855f7; color:#d8b4fe; }

    /* ── Section Headers ── */
    .section-header {
        font-size: 13px;
        font-weight: 700;
        color: #3a7bd5;
        text-transform: uppercase;
        letter-spacing: 2px;
        border-bottom: 1px solid #1e2d4a;
        padding-bottom: 8px;
        margin: 1.5rem 0 1rem 0;
    }

    /* ── Conclusion Table ── */
    .conclude-table {
        background: #0d1628;
        border: 1px solid #1e2d4a;
        border-radius: 12px;
        overflow: hidden;
        width: 100%;
    }
    .conclude-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 16px;
        border-bottom: 1px solid #131f35;
        font-size: 13.5px;
    }
    .conclude-row:last-child { border-bottom: none; font-weight: 700; }
    .conclude-row .clabel { color: #4a6a9a; }
    .conclude-row .cvalue { color: #e2e8f0; text-align: right; }
    .conclude-row.highlight { background: #0f1e38; }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid #1e2d4a; }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #4a6a9a;
        border: none;
        padding: 8px 20px;
        border-radius: 8px 8px 0 0;
        font-size: 13px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background: #0d1628 !important;
        color: #4da6ff !important;
        border-bottom: 2px solid #4da6ff !important;
    }

    /* ── Metric delta overrides ── */
    [data-testid="stMetricDelta"] { font-size: 12px; }

    /* ── Expander ── */
    [data-testid="stExpander"] {
        background: #0d1628;
        border: 1px solid #1e2d4a;
        border-radius: 10px;
    }

    /* ── Slider labels ── */
    .stSlider [data-testid="stWidgetLabel"] { color: #7eb8f7; font-size: 13px; }

    /* ── Page title ── */
    .page-title {
        font-size: 32px;
        font-weight: 800;
        background: linear-gradient(135deg, #4da6ff 0%, #2dd4bf 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 4px;
    }
    .page-subtitle { color: #4a6a9a; font-size: 14px; margin-bottom: 1.5rem; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# QUEUEING MATH  (M/M/c model)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class QueueResult:
    c: int
    rho: float          # utilization per server  (must be < 1)
    Pq: float           # probability a patient waits
    Wq_min: float       # avg wait in queue   (minutes)
    Lq: float           # avg queue length    (patients)
    W_min: float        # avg time in system  (minutes)
    L: float            # avg patients in system
    stable: bool


def erlang_c(c: int, lam: float, mu: float) -> float:
    """Erlang C formula — P(arriving patient must wait)."""
    a = lam / mu
    rho = a / c
    if rho >= 1.0:
        return 1.0
    numerator = (a ** c / factorial(c)) * (1.0 / (1.0 - rho))
    total = sum(a ** n / factorial(n) for n in range(c)) + numerator
    return numerator / total


def mmc(lam: float, mu: float, c: int) -> QueueResult:
    """All M/M/c performance metrics."""
    rho = lam / (c * mu)
    if rho >= 1.0:
        return QueueResult(c=c, rho=rho, Pq=1.0,
                           Wq_min=float("inf"), Lq=float("inf"),
                           W_min=float("inf"), L=float("inf"),
                           stable=False)
    Pq = erlang_c(c, lam, mu)
    Wq  = Pq / (c * mu - lam)          # hours
    Lq  = lam * Wq
    W   = Wq + 1.0 / mu
    L   = lam * W
    return QueueResult(
        c=c, rho=round(rho, 4), Pq=round(Pq, 4),
        Wq_min=round(Wq * 60, 2), Lq=round(Lq, 3),
        W_min=round(W * 60, 2), L=round(L, 3),
        stable=True,
    )


def build_cost_table(lam, mu, doc_cost, wait_cost, max_c=20) -> pd.DataFrame:
    rows = []
    for c in range(1, max_c + 1):
        m = mmc(lam, mu, c)
        if m.stable:
            dc = c * doc_cost
            wc = m.Lq * wait_cost
            tc = dc + wc
        else:
            dc = c * doc_cost
            wc = None
            tc = None
        rows.append({
            "Doctors": c, "ρ Utilization": m.rho,
            "P(wait)": m.Pq,
            "Avg Wait (min)": m.Wq_min if m.stable else None,
            "Queue Length (Lq)": m.Lq if m.stable else None,
            "Time in System (min)": m.W_min if m.stable else None,
            "Doctor Cost (₹/hr)": dc,
            "Wait Cost (₹/hr)": wc,
            "Total Cost (₹/hr)": tc,
            "Stable": m.stable,
        })
    return pd.DataFrame(rows)


def find_optimal(lam, mu, doc_cost, wait_cost, max_c=20):
    df = build_cost_table(lam, mu, doc_cost, wait_cost, max_c)
    stable = df[df["Stable"] & df["Total Cost (₹/hr)"].notna()]
    if stable.empty:
        return None, df
    opt_idx = stable["Total Cost (₹/hr)"].idxmin()
    return int(stable.loc[opt_idx, "Doctors"]), df


# ─────────────────────────────────────────────────────────────────────────────
# MATPLOTLIB CHARTS
# ─────────────────────────────────────────────────────────────────────────────

DARK_BG  = "#0a0e1a"
CARD_BG  = "#0d1628"
GRID_C   = "#1a2a42"
TEXT_C   = "#8aa5c8"
BLUE     = "#4da6ff"
ORANGE   = "#f97316"
GREEN    = "#4ade80"
GOLD     = "#f59e0b"
RED      = "#f87171"
TEAL     = "#2dd4bf"


def _base_fig(w=8, h=4):
    fig, ax = plt.subplots(figsize=(w, h), facecolor=DARK_BG)
    ax.set_facecolor(CARD_BG)
    ax.tick_params(colors=TEXT_C, labelsize=9)
    ax.xaxis.label.set_color(TEXT_C)
    ax.yaxis.label.set_color(TEXT_C)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_C)
    ax.grid(True, axis="y", color=GRID_C, linewidth=0.5)
    return fig, ax


def chart_wait_vs_doctors(df, opt_c, current_c):
    fig, ax = _base_fig(8, 3.5)
    stable = df[df["Stable"]].dropna(subset=["Avg Wait (min)"])
    ax.plot(stable["Doctors"], stable["Avg Wait (min)"],
            color=BLUE, linewidth=2.5, marker="o", markersize=6,
            markerfacecolor=DARK_BG, markeredgewidth=2)
    ax.axvline(opt_c, color=GOLD, linestyle="--", linewidth=1.5,
               label=f"Optimal: {opt_c} doctors")
    ax.axvline(current_c, color=TEAL, linestyle=":", linewidth=1.5,
               label=f"Current: {current_c} doctors")
    ax.set_xlabel("Number of Doctors", fontsize=10)
    ax.set_ylabel("Avg Wait Time (minutes)", fontsize=10)
    ax.set_title("Avg Patient Wait Time vs Doctor Count", color="#c8d8f0",
                 fontsize=12, fontweight="bold", pad=12)
    ax.legend(facecolor=CARD_BG, edgecolor=GRID_C,
              labelcolor=TEXT_C, fontsize=9)
    fig.tight_layout(pad=1.5)
    return fig


def chart_utilization(df, opt_c, current_c):
    fig, ax = _base_fig(8, 3.5)
    colors = []
    for rho in df["ρ Utilization"]:
        if rho >= 1.0: colors.append(RED)
        elif rho >= 0.85: colors.append(ORANGE)
        else: colors.append(BLUE)
    ax.bar(df["Doctors"], df["ρ Utilization"].clip(upper=1.05),
           color=colors, edgecolor=DARK_BG, linewidth=0.5, width=0.65)
    ax.axhline(0.85, color=ORANGE, linestyle="--", linewidth=1.2,
               label="Warning: 85%")
    ax.axhline(1.0, color=RED, linestyle="--", linewidth=1.2,
               label="Unstable: 100%")
    ax.axvline(opt_c, color=GOLD, linestyle="--", linewidth=1.5,
               label=f"Optimal: {opt_c}")
    ax.axvline(current_c, color=TEAL, linestyle=":", linewidth=1.5,
               label=f"Current: {current_c}")
    ax.set_ylim(0, 1.2)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1))
    ax.set_xlabel("Number of Doctors", fontsize=10)
    ax.set_ylabel("Utilization ρ", fontsize=10)
    ax.set_title("Doctor Utilization vs Doctor Count", color="#c8d8f0",
                 fontsize=12, fontweight="bold", pad=12)
    ax.legend(facecolor=CARD_BG, edgecolor=GRID_C,
              labelcolor=TEXT_C, fontsize=9)
    fig.tight_layout(pad=1.5)
    return fig


def chart_cost_breakdown(df, opt_c, current_c):
    fig, ax = _base_fig(8, 3.5)
    stable = df[df["Stable"]].dropna(subset=["Total Cost (₹/hr)"])
    ax.bar(stable["Doctors"], stable["Doctor Cost (₹/hr)"],
           label="Doctor salary", color=BLUE,
           edgecolor=DARK_BG, linewidth=0.5, width=0.65)
    ax.bar(stable["Doctors"], stable["Wait Cost (₹/hr)"],
           bottom=stable["Doctor Cost (₹/hr)"],
           label="Patient wait cost", color=ORANGE,
           edgecolor=DARK_BG, linewidth=0.5, width=0.65)
    ax.plot(stable["Doctors"], stable["Total Cost (₹/hr)"],
            color=GOLD, linewidth=2.5, marker="D", markersize=5,
            markerfacecolor=DARK_BG, markeredgewidth=2,
            label="Total cost", zorder=5)
    ax.axvline(opt_c, color=GOLD, linestyle="--", linewidth=1.5,
               label=f"Optimal: {opt_c}")
    ax.axvline(current_c, color=TEAL, linestyle=":", linewidth=1.5,
               label=f"Current: {current_c}")
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"₹{int(x):,}"))
    ax.set_xlabel("Number of Doctors", fontsize=10)
    ax.set_ylabel("Cost per Hour (₹)", fontsize=10)
    ax.set_title("Cost Breakdown vs Doctor Count", color="#c8d8f0",
                 fontsize=12, fontweight="bold", pad=12)
    ax.legend(facecolor=CARD_BG, edgecolor=GRID_C,
              labelcolor=TEXT_C, fontsize=9)
    fig.tight_layout(pad=1.5)
    return fig


def chart_queue_length(df, opt_c, current_c):
    fig, ax = _base_fig(8, 3.5)
    stable = df[df["Stable"]].dropna(subset=["Queue Length (Lq)"])
    ax.fill_between(stable["Doctors"], stable["Queue Length (Lq)"],
                    alpha=0.2, color=TEAL)
    ax.plot(stable["Doctors"], stable["Queue Length (Lq)"],
            color=TEAL, linewidth=2.5, marker="s", markersize=6,
            markerfacecolor=DARK_BG, markeredgewidth=2)
    ax.axvline(opt_c, color=GOLD, linestyle="--", linewidth=1.5,
               label=f"Optimal: {opt_c} doctors")
    ax.axvline(current_c, color=TEAL, linestyle=":", linewidth=1.5,
               label=f"Current: {current_c} doctors")
    ax.set_xlabel("Number of Doctors", fontsize=10)
    ax.set_ylabel("Avg Patients in Queue", fontsize=10)
    ax.set_title("Queue Length vs Doctor Count", color="#c8d8f0",
                 fontsize=12, fontweight="bold", pad=12)
    ax.legend(facecolor=CARD_BG, edgecolor=GRID_C,
              labelcolor=TEXT_C, fontsize=9)
    fig.tight_layout(pad=1.5)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# HELPER: format rupees
# ─────────────────────────────────────────────────────────────────────────────

def rs(n):
    if n is None or not np.isfinite(n):
        return "∞"
    return f"₹{int(n):,}"


def fmt(n, d=1):
    if n is None or not np.isfinite(n):
        return "∞"
    return f"{n:.{d}f}"


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🏥 Hospital Queue\nOptimizer")
    st.markdown("---")

    st.markdown("### 📥 Patient Flow")
    lam = st.slider(
        "Patients arriving per hour (λ)",
        min_value=1, max_value=60, value=12, step=1,
        help="How many patients walk into OPD per hour on average."
    )
    mu = st.slider(
        "Patients one doctor handles per hour (µ)",
        min_value=1, max_value=20, value=5, step=1,
        help="How many patients a single doctor can finish in one hour."
    )
    c = st.slider(
        "Number of doctors on duty (c)",
        min_value=1, max_value=25, value=3, step=1,
        help="Total doctors available simultaneously at the OPD."
    )

    st.markdown("---")
    st.markdown("### 💰 Cost Parameters (₹/hr)")
    doc_cost = st.number_input(
        "Doctor salary per hour (₹)",
        min_value=100, max_value=20000, value=1500, step=100,
        help="Average hourly cost of one doctor (salary + overhead)."
    )
    wait_cost = st.number_input(
        "Cost when 1 patient waits 1 hour (₹)",
        min_value=10, max_value=5000, value=200, step=50,
        help="The indirect cost per patient-hour of waiting (lost wages, dissatisfaction, etc.)."
    )

    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    max_c = st.slider("Max doctors to analyse", 5, 30, 20, 1)
    show_sim = st.checkbox("Show simulation tab", value=True)
    show_table = st.checkbox("Show full data table", value=True)

    st.markdown("---")
    min_needed = ceil(lam / mu) + 1
    st.markdown(f"""
    **Quick reference**
    - Min doctors for stability: **{min_needed}**
    - Avg inter-arrival: **{60/lam:.1f} min**
    - Avg service time: **{60/mu:.1f} min**
    """)


# ─────────────────────────────────────────────────────────────────────────────
# COMPUTE
# ─────────────────────────────────────────────────────────────────────────────

m = mmc(lam, mu, c)
opt_c, df_costs = find_optimal(lam, mu, doc_cost, wait_cost, max_c)

current_doc_cost  = c * doc_cost
current_wait_cost = m.Lq * wait_cost if m.stable and np.isfinite(m.Lq) else float("inf")
current_total     = current_doc_cost + current_wait_cost if np.isfinite(current_wait_cost) else float("inf")

opt_row = None
opt_total = None
if opt_c:
    opt_row = df_costs[df_costs["Doctors"] == opt_c].iloc[0]
    opt_total = opt_row["Total Cost (₹/hr)"]


# ─────────────────────────────────────────────────────────────────────────────
# PAGE HEADER
# ─────────────────────────────────────────────────────────────────────────────

st.markdown('<div class="page-title">🏥 Hospital Queue Optimizer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">M/M/c Queueing Theory · Erlang C Formula · Cost Optimization · All costs in Indian Rupees (₹)</div>',
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────────────────────
# WHAT IS THIS MODEL?  (collapsible explainer)
# ─────────────────────────────────────────────────────────────────────────────

with st.expander("📖 What is this model? How does it work? (click to read)", expanded=False):
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        st.markdown("""
**The real-world problem:**
A hospital OPD has patients arriving throughout the day.
If there are too few doctors → patients wait a long time → poor service.
If there are too many doctors → high salary cost → wasteful.
**This model finds the exact right number of doctors.**

---
**How it works (M/M/c model):**
- Patients arrive randomly — modeled as a **Poisson process** with rate λ
- Each doctor takes a random amount of time — modeled as **Exponential distribution** with rate µ
- With c doctors running in parallel, we use the **Erlang C formula** to compute exact waiting times

---
**Key formula:**
`ρ = λ / (c × µ)`  → must be < 1 for the system to be stable
`Wq = Pq / (c×µ − λ)` → avg wait time in queue (hours)
`Lq = λ × Wq` → avg patients sitting in queue
        """)
    with col_e2:
        st.markdown("""
**What each term means in plain words:**

| Symbol | Plain meaning |
|--------|--------------|
| λ (lambda) | Patients arriving per hour |
| µ (mu) | Patients one doctor finishes per hour |
| c | Number of doctors on duty |
| ρ (rho) | How busy the doctors are (keep < 85%) |
| Pq | Chance that you'll have to wait at all |
| Wq | How long you wait before the doctor sees you |
| Lq | How many people are sitting in the waiting area |
| W | Total time: waiting + treatment |

---
**How to reach a conclusion:**
1. Check **System Status** — must be Stable
2. Keep **Utilization ρ** between 60–80%
3. Check **Avg Wait** — under 10 min is good
4. Find **Optimal Doctors** — minimum cost point
5. Read the **Conclusion** section at the bottom
        """)


# ─────────────────────────────────────────────────────────────────────────────
# KPI CARDS  (row 1)
# ─────────────────────────────────────────────────────────────────────────────

st.markdown('<div class="section-header">Current System Performance</div>',
            unsafe_allow_html=True)
st.markdown(f"**{c} doctor{'s' if c != 1 else ''} on duty** · "
            f"λ = {lam} patients/hr · µ = {mu} patients/hr per doctor")

# Status colour
if not m.stable:
    rho_color = "kpi-red"
    rho_label = "UNSTABLE"
elif m.rho > 0.85:
    rho_color = "kpi-amber"
    rho_label = "HIGH"
else:
    rho_color = "kpi-green"
    rho_label = "HEALTHY"

wq_color = "kpi-red" if not m.stable or (m.stable and m.Wq_min > 30) else (
           "kpi-amber" if m.Wq_min > 10 else "kpi-green")

k1, k2, k3, k4, k5, k6 = st.columns(6)

def kpi(col, label, value, sub, color):
    col.markdown(
        f'<div class="kpi-card {color}">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-sub">{sub}</div>'
        f'</div>', unsafe_allow_html=True
    )

kpi(k1, "Utilization ρ",
    f"{m.rho*100:.1f}%", rho_label, rho_color)
kpi(k2, "Avg Wait in Queue",
    fmt(m.Wq_min) + " min" if m.stable else "∞",
    "before doctor sees you", wq_color)
kpi(k3, "Avg Queue Length",
    fmt(m.Lq) if m.stable else "∞",
    "patients waiting now", "kpi-blue")
kpi(k4, "Time in System",
    fmt(m.W_min) + " min" if m.stable else "∞",
    "wait + treatment", "kpi-teal")
kpi(k5, "Total Cost / hr",
    rs(current_total),
    "doctor + wait cost", "kpi-gold")
kpi(k6, "Optimal Doctors",
    str(opt_c) if opt_c else "N/A",
    f"min cost: {rs(opt_total)}/hr" if opt_total else "—",
    "kpi-purple" if opt_c and opt_c != c else "kpi-green")

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# INSIGHTS
# ─────────────────────────────────────────────────────────────────────────────

st.markdown('<div class="section-header">System Insights & Recommendations</div>',
            unsafe_allow_html=True)

ins_col1, ins_col2 = st.columns(2)

def ins(col, msg, kind):
    col.markdown(f'<div class="insight ins-{kind}">{msg}</div>',
                 unsafe_allow_html=True)

with ins_col1:
    if not m.stable:
        ins(ins_col1,
            f"🚨 <b>SYSTEM UNSTABLE</b> — Patients arrive at {lam}/hr but {c} doctors can only handle "
            f"{c*mu}/hr total. Queue grows without end. "
            f"You need at least <b>{ceil(lam/mu)+1} doctors</b> for stability.",
            "danger")
    elif m.rho > 0.9:
        ins(ins_col1,
            f"⚠️ Doctors are <b>{m.rho*100:.0f}% busy</b> — dangerously high. "
            "Any unexpected surge will create a massive backlog immediately.",
            "warning")
    elif m.rho > 0.85:
        ins(ins_col1,
            f"⚠️ Utilization is <b>{m.rho*100:.0f}%</b> — above the recommended 85% threshold. "
            "Consider adding 1 more doctor during peak hours.",
            "warning")
    else:
        ins(ins_col1,
            f"✅ System is stable and healthy. Doctors are <b>{m.rho*100:.0f}% busy</b> "
            "— good workload with room for surge capacity.",
            "success")

    if m.stable and m.Wq_min > 30:
        ins(ins_col1,
            f"🕐 Average wait of <b>{m.Wq_min:.1f} minutes</b> is very high. "
            "Patients spend more time waiting than being treated.",
            "warning")
    elif m.stable and m.Wq_min <= 10:
        ins(ins_col1,
            f"✅ Excellent wait time of <b>{m.Wq_min:.1f} minutes</b>. "
            "Patients are seen quickly.",
            "success")

    prob_pct = m.Pq * 100
    if m.stable:
        ins(ins_col1,
            f"ℹ️ <b>{prob_pct:.0f}% of patients</b> will have to wait in queue. "
            f"The rest go straight to a doctor.",
            "info")

with ins_col2:
    if opt_c and m.stable:
        if c < opt_c:
            savings = current_total - opt_total if np.isfinite(current_total) else 0
            ins(ins_col2,
                f"💡 Adding <b>{opt_c - c} more doctor(s)</b> (total: {opt_c}) would "
                f"reduce total cost by <b>{rs(savings)}/hr</b> by cutting patient waiting cost.",
                "info")
        elif c > opt_c:
            savings = current_total - opt_total
            ins(ins_col2,
                f"💡 You have <b>{c - opt_c} extra doctor(s)</b> beyond optimal. "
                f"Reducing to {opt_c} doctors saves <b>{rs(savings)}/hr</b> in salary cost.",
                "info")
        else:
            ins(ins_col2,
                f"🏆 You are already at the <b>optimal doctor count ({c})</b>! "
                f"Total cost is minimized at <b>{rs(current_total)}/hr</b>.",
                "success")

    if opt_c and opt_row is not None:
        ins(ins_col2,
            f"📊 At optimal {opt_c} doctors: avg wait = <b>{fmt(opt_row['Avg Wait (min)'])} min</b>, "
            f"utilization = <b>{opt_row['ρ Utilization']*100:.0f}%</b>, "
            f"total cost = <b>{rs(opt_total)}/hr</b>.",
            "purple")

    per_patient_cost = (current_total / lam) if lam > 0 and np.isfinite(current_total) else None
    if per_patient_cost:
        ins(ins_col2,
            f"🧮 Cost per patient served: <b>{rs(per_patient_cost)}</b> "
            f"({c} doctors handling {lam} patients/hr).",
            "info")


# ─────────────────────────────────────────────────────────────────────────────
# CHARTS  (tabs)
# ─────────────────────────────────────────────────────────────────────────────

st.markdown('<div class="section-header">Analysis Charts</div>',
            unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "⏱ Wait Time", "📊 Utilization", "💰 Cost Breakdown", "👥 Queue Length"
])

if opt_c:
    with tab1:
        st.pyplot(chart_wait_vs_doctors(df_costs, opt_c, c), use_container_width=True)
        st.caption(
            "Blue line = avg patient wait. "
            "Gold dashed = optimal doctor count (min cost). "
            "Teal dotted = current setting. "
            "Wait time falls sharply as doctors increase, then flattens."
        )

    with tab2:
        st.pyplot(chart_utilization(df_costs, opt_c, c), use_container_width=True)
        st.caption(
            "Blue bars = healthy (<85%). Orange = high (85–99%). Red = unstable (≥100%). "
            "Target: keep utilization between 60–80% for reliable service."
        )

    with tab3:
        st.pyplot(chart_cost_breakdown(df_costs, opt_c, c), use_container_width=True)
        st.caption(
            "Blue = doctor salary cost (goes up as you add doctors). "
            "Orange = patient waiting cost (goes down as you add doctors). "
            "Gold line = total cost — the bottom of this curve is the optimal point."
        )

    with tab4:
        st.pyplot(chart_queue_length(df_costs, opt_c, c), use_container_width=True)
        st.caption(
            "How many patients are sitting in the waiting area on average. "
            "Ideally this should be under 2–3 patients for a smooth OPD."
        )


# ─────────────────────────────────────────────────────────────────────────────
# SIMULATION TAB
# ─────────────────────────────────────────────────────────────────────────────

if show_sim:
    st.markdown('<div class="section-header">Discrete-Event Simulation</div>',
                unsafe_allow_html=True)

    with st.expander("▶ Run simulation to validate theory", expanded=False):
        sim_hours = st.slider("Simulation window (hours)", 1, 24, 8)
        run_btn = st.button("Run Simulation")

        if run_btn:
            # Simple event-driven simulation
            rng = np.random.default_rng(42)
            lam_min = lam / 60.0
            mu_min  = mu  / 60.0
            duration = sim_hours * 60.0

            arrivals = []
            t = 0.0
            while t < duration:
                t += rng.exponential(1.0 / lam_min)
                if t < duration:
                    arrivals.append(t)

            service_times = rng.exponential(1.0 / mu_min, size=len(arrivals))
            finish_times  = np.zeros(c)
            wait_times    = []

            for i, arr in enumerate(arrivals):
                earliest_free = np.min(finish_times)
                start = max(arr, earliest_free)
                wait  = start - arr
                wait_times.append(wait)
                doc_idx = np.argmin(finish_times)
                finish_times[doc_idx] = start + service_times[i]

            wait_arr = np.array(wait_times)
            sim_avg  = wait_arr.mean()
            sim_max  = wait_arr.max()
            pct_waited = (wait_arr > 0.5).mean() * 100

            sc1, sc2, sc3, sc4 = st.columns(4)
            sc1.metric("Patients simulated", f"{len(arrivals):,}")
            sc2.metric("Sim avg wait", f"{sim_avg:.1f} min",
                       delta=f"Theory: {fmt(m.Wq_min)} min" if m.stable else "Theory: ∞")
            sc3.metric("Max wait seen", f"{sim_max:.1f} min")
            sc4.metric("% who waited", f"{pct_waited:.1f}%",
                       delta=f"Theory: {m.Pq*100:.0f}%" if m.stable else None)

            fig, ax = _base_fig(10, 3.5)
            ax.hist(wait_arr, bins=50, color=BLUE, edgecolor=DARK_BG,
                    linewidth=0.3, alpha=0.85)
            ax.axvline(sim_avg, color=GOLD, linewidth=2,
                       label=f"Sim mean: {sim_avg:.1f} min")
            if m.stable:
                ax.axvline(m.Wq_min, color=TEAL, linewidth=2,
                           linestyle="--",
                           label=f"Theory: {m.Wq_min:.1f} min")
            ax.set_xlabel("Wait time (minutes)", fontsize=10)
            ax.set_ylabel("Number of patients", fontsize=10)
            ax.set_title("Distribution of Patient Wait Times (Simulation)",
                         color="#c8d8f0", fontsize=12, fontweight="bold")
            ax.legend(facecolor=CARD_BG, edgecolor=GRID_C,
                      labelcolor=TEXT_C, fontsize=9)
            fig.tight_layout()
            st.pyplot(fig, use_container_width=True)

            if m.stable and abs(sim_avg - m.Wq_min) < 2:
                st.success(
                    f"Theory and simulation agree closely "
                    f"(difference = {abs(sim_avg - m.Wq_min):.2f} min). "
                    "The M/M/c model is accurate for this setting."
                )
            else:
                st.info(
                    "Some variance between theory and simulation is normal. "
                    "Run a longer simulation (e.g. 24 hours) for closer agreement."
                )


# ─────────────────────────────────────────────────────────────────────────────
# PEAK vs NORMAL SCENARIO COMPARISON
# ─────────────────────────────────────────────────────────────────────────────

st.markdown('<div class="section-header">Peak vs Normal Scenario Comparison</div>',
            unsafe_allow_html=True)

peak_col, normal_col = st.columns([1, 2])
with peak_col:
    peak_mult = st.slider(
        "Peak-hour arrival multiplier", 1.1, 4.0, 1.5, 0.1,
        help="During peak hours (morning rush, post-lunch) arrivals can be 1.5–3× normal."
    )

lam_peak  = lam * peak_mult
m_normal  = mmc(lam, mu, c)
m_peak    = mmc(lam_peak, mu, c)
opt_peak, _ = find_optimal(lam_peak, mu, doc_cost, wait_cost, max_c)

nc1, nc2, nc3 = st.columns(3)

def scenario_block(col, title, m_val, lam_val, color):
    col.markdown(f"**{title}**  —  λ = {lam_val:.1f} pts/hr")
    col.markdown(
        f'<div class="kpi-card {color}" style="margin-bottom:8px">'
        f'<div class="kpi-label">Utilization</div>'
        f'<div class="kpi-value">{m_val.rho*100:.1f}%</div>'
        f'<div class="kpi-sub">{"UNSTABLE" if not m_val.stable else "OK" if m_val.rho < 0.85 else "HIGH"}</div>'
        f'</div>', unsafe_allow_html=True
    )
    col.markdown(
        f'<div class="kpi-card {color}">'
        f'<div class="kpi-label">Avg Wait</div>'
        f'<div class="kpi-value">{fmt(m_val.Wq_min) + " min" if m_val.stable else "∞"}</div>'
        f'<div class="kpi-sub">in queue</div>'
        f'</div>', unsafe_allow_html=True
    )

scenario_block(nc1, "Normal Hours", m_normal, lam,
               "kpi-green" if m_normal.rho < 0.85 else "kpi-amber")
scenario_block(nc2, f"Peak Hours (×{peak_mult})", m_peak, lam_peak,
               "kpi-red" if not m_peak.stable or m_peak.rho > 0.9 else "kpi-amber")

with nc3:
    st.markdown("**Recommendation**")
    if not m_peak.stable:
        st.error(
            f"During peak hours, {c} doctors cannot handle {lam_peak:.0f} pts/hr. "
            f"You need **at least {ceil(lam_peak/mu)+1} doctors** during peak."
        )
    elif m_peak.rho > 0.85:
        st.warning(
            f"Peak load pushes utilization to {m_peak.rho*100:.0f}%. "
            f"Consider adding {(opt_peak or c+1) - c} extra doctor(s) during peak hours."
        )
    else:
        st.success(
            f"Current {c} doctors can handle peak load of {lam_peak:.0f} pts/hr "
            f"with {m_peak.rho*100:.0f}% utilization."
        )
    if opt_peak:
        st.info(f"Optimal doctors for peak hours: **{opt_peak}** (vs {opt_c} normally)")


# ─────────────────────────────────────────────────────────────────────────────
# FULL DATA TABLE
# ─────────────────────────────────────────────────────────────────────────────

if show_table:
    with st.expander("📋 Full Performance & Cost Table (all doctor counts)", expanded=False):
        display_df = df_costs.copy()
        display_df["ρ Utilization"] = display_df["ρ Utilization"].apply(
            lambda x: f"{x*100:.1f}%" if pd.notna(x) else "—"
        )
        display_df["P(wait)"] = display_df["P(wait)"].apply(
            lambda x: f"{x*100:.1f}%" if pd.notna(x) else "—"
        )
        for col_name in ["Avg Wait (min)", "Queue Length (Lq)", "Time in System (min)"]:
            display_df[col_name] = display_df[col_name].apply(
                lambda x: f"{x:.2f}" if pd.notna(x) else "Unstable"
            )
        for col_name in ["Doctor Cost (₹/hr)", "Wait Cost (₹/hr)", "Total Cost (₹/hr)"]:
            display_df[col_name] = display_df[col_name].apply(
                lambda x: f"₹{x:,.0f}" if pd.notna(x) else "—"
            )
        display_df["Stable"] = display_df["Stable"].apply(lambda x: "✅" if x else "❌")

        def highlight_rows(row):
            if row["Doctors"] == opt_c:
                return ["background-color: #0f2a1a; color: #86efac"] * len(row)
            if row["Doctors"] == c:
                return ["background-color: #0a1a2e; color: #93c5fd"] * len(row)
            return [""] * len(row)

        st.dataframe(
            display_df.style.apply(highlight_rows, axis=1),
            use_container_width=True,
            hide_index=True,
        )
        st.caption("🟢 Green row = optimal (min cost) · 🔵 Blue row = current setting")


# ─────────────────────────────────────────────────────────────────────────────
# CONCLUSION  (the final answer section)
# ─────────────────────────────────────────────────────────────────────────────

st.markdown('<div class="section-header">Conclusion — What This Means for Your Hospital</div>',
            unsafe_allow_html=True)

def conclude_row(label, value, highlight=False):
    cls = "conclude-row highlight" if highlight else "conclude-row"
    return (f'<div class="{cls}">'
            f'<span class="clabel">{label}</span>'
            f'<span class="cvalue">{value}</span>'
            f'</div>')

rows_html = "".join([
    conclude_row("Patients arriving at OPD",
                 f"{lam} per hour  (1 every {60/lam:.0f} minutes)"),
    conclude_row("Each doctor handles",
                 f"{mu} patients/hr  ({60/mu:.0f} min per patient)"),
    conclude_row("Doctors currently on duty", str(c)),
    conclude_row("Minimum doctors needed (for stability)",
                 str(ceil(lam / mu) + 1)),
    conclude_row("Doctor utilization",
                 f"{m.rho*100:.1f}%  —  "
                 + ("OVERLOADED ❌" if not m.stable else
                    "HIGH ⚠️" if m.rho > 0.85 else "HEALTHY ✅")),
    conclude_row("Probability a patient waits",
                 f"{m.Pq*100:.0f}%" if m.stable else "100% (unstable)"),
    conclude_row("Average wait before doctor",
                 f"{fmt(m.Wq_min)} minutes" if m.stable else "Infinite (queue never clears)"),
    conclude_row("Average time in OPD (wait + treatment)",
                 f"{fmt(m.W_min)} minutes" if m.stable else "∞"),
    conclude_row("Average patients waiting right now",
                 f"{fmt(m.Lq)} patients" if m.stable else "∞"),
    conclude_row("Doctor salary cost",
                 f"{rs(current_doc_cost)} / hour  "
                 f"({rs(current_doc_cost * 8)} for 8-hr shift)"),
    conclude_row("Patient waiting cost",
                 f"{rs(current_wait_cost)} / hour" if np.isfinite(current_wait_cost) else "∞"),
    conclude_row("Total operational cost",
                 f"{rs(current_total)} / hour  "
                 f"({rs(current_total * 8) if np.isfinite(current_total) else '∞'} for 8-hr shift)"),
    conclude_row("Cost-optimal doctor count",
                 f"{opt_c} doctors  (total cost {rs(opt_total)}/hr)"
                 if opt_c else "N/A", highlight=True),
])

if opt_c and np.isfinite(current_total) and opt_total:
    diff = current_total - opt_total
    rows_html += conclude_row(
        "Savings by switching to optimal",
        f"{rs(diff)}/hr  ({rs(diff*8)} per 8-hr shift)"
        if diff > 0 else "Already at optimal cost",
        highlight=True
    )

st.markdown(
    f'<div class="conclude-table">{rows_html}</div>',
    unsafe_allow_html=True,
)

# Final plain-English verdict
st.markdown("<br>", unsafe_allow_html=True)
if not m.stable:
    st.error(
        f"**Verdict:** The OPD is overloaded with {c} doctors. "
        f"You must add at least {ceil(lam/mu)+1 - c} more doctor(s) immediately. "
        "Patients are accumulating faster than they can be served."
    )
elif m.rho > 0.85:
    st.warning(
        f"**Verdict:** The OPD is running too hot ({m.rho*100:.0f}% busy). "
        f"Patients wait an average of {m.Wq_min:.1f} minutes. "
        f"The optimal setup is {opt_c} doctors at {rs(opt_total)}/hr total cost."
    )
else:
    st.success(
        f"**Verdict:** The OPD is running well with {c} doctors "
        f"({m.rho*100:.0f}% utilization, {m.Wq_min:.1f} min avg wait). "
        + (f"The cost-optimal count is {opt_c} doctors — saving {rs(current_total - opt_total)}/hr."
           if opt_c and opt_c != c and np.isfinite(current_total)
           else "You are already at the optimal doctor count.")
    )

st.markdown("---")
st.caption(
    "Model: M/M/c queue · Erlang C formula · Cost = doctor salaries + patient waiting cost · "
    "All amounts in Indian Rupees (₹) · "
    "Adjust sliders in the sidebar to update all results in real time."
)
