"""
MCEIT Cost-Effectiveness Dashboard
Bowel cancer screening promotion · Policy1-Bowel microsimulation (Australia)

Run with:
    pip install streamlit plotly
    streamlit run mceit_dashboard.py
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MCEIT Dashboard",
    page_icon="📈",
    layout="wide",
)

# ── Data ──────────────────────────────────────────────────────────────────────
RR_PTS = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6]

T50   = [0, 63_172_987, 127_195_560, 188_582_841,
         367_687_657, 710_271_010, 1_063_034_759]
T30   = [0, 40_273_768, 81_291_157, 120_531_525,
         239_442_496, 467_258_824, 703_543_359]
TSAVE = [0, 5_924_940, 12_434_553, 18_454_552,
         47_074_756, 102_740_544, 164_306_259]

ELIGIBLE_POP      = 3_967_654   # eligible persons in the modelled population (Policy1-Bowel)
COMPARATOR_KITS   = 1_349_188.347606  # kits returned in the comparator scenario

LITERATURE = [
    # ("GP endorsement",                    1.01,  6_686_872),
    ("Patient reminder(multiple methods)", 1.07,  1_003_334),
    ("Patient navigation",                1.16, 380_023_523),
    ("Patient reminder(phone call)",     1.30, 24_480_274),
]

# ── Helpers ───────────────────────────────────────────────────────────────────
def interp(rr: float, data: list) -> float:
    """Linear interpolation between modelled RR scenarios."""
    rr = max(RR_PTS[0], min(RR_PTS[-1], rr))
    for i in range(len(RR_PTS) - 1):
        if RR_PTS[i] <= rr <= RR_PTS[i + 1]:
            t = (rr - RR_PTS[i]) / (RR_PTS[i + 1] - RR_PTS[i])
            return data[i] + t * (data[i + 1] - data[i])
    return data[-1]


def fmt_aud(v: float) -> str:
    if v is None or np.isnan(v):
        return "—"
    if abs(v) >= 1e9:
        return f"${v/1e9:.2f}B"
    if abs(v) >= 1e6:
        return f"${v/1e6:.1f}M"
    return f"${v:,.0f}"


def verdict(cost: float, threshold: float):
    """Return (label, delta_pct, colour) relative to threshold."""
    if threshold <= 0:
        return "N/A — no cost saving", None, "gray"
    if cost <= threshold:
        pct = (threshold - cost) / threshold * 100
        return f"✅  Cost-effective  (headroom {pct:.0f}%)", pct, "green"
    else:
        pct = (cost - threshold) / threshold * 100
        return f"❌  Exceeds threshold  (over by {pct:.0f}%)", -pct, "red"


# ── Smooth curves for Plotly ──────────────────────────────────────────────────
RR_SMOOTH = np.linspace(1.0, 1.6, 120)
smooth50   = [round(interp(r, T50)   / 1e6, 2) for r in RR_SMOOTH]
smooth30   = [round(interp(r, T30)   / 1e6, 2) for r in RR_SMOOTH]
smoothSave = [round(interp(r, TSAVE) / 1e6, 2) for r in RR_SMOOTH]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("MCEIT Calculator")
    st.caption("The Cancer Elimination Collaboration | The University of Sydney")
    st.divider()

    st.subheader("Your intervention")

    rr = st.slider(
        "Participation increase (relative to comparator)",
        min_value=1.00, max_value=1.60, value=1.20, step=0.01,
        format="%.2f×",
    )

    cost_m = st.number_input(
        "Intervention cost (AUD, millions)",
        min_value=0.0, value=50.0, step=1.0, format="%.2f",
    )
    cost = cost_m * 1e6

    _ek_sb = (rr - 1.0) * COMPARATOR_KITS
    _cpp   = cost / ELIGIBLE_POP
    _cpk   = cost / _ek_sb if _ek_sb > 0 else None
    kit_str = f"${_cpk:.2f}" if _cpk is not None else "N/A (RR = 1.0)"
    st.caption("Equivalent to:")
    st.caption(f"  ${_cpp:.2f} per eligible person")
    st.caption(f"  {kit_str} per extra kit")

    st.divider()
    st.subheader("Load a literature example")

    for name, lit_rr, lit_cost in LITERATURE:
        if st.button(f"{name}\n({lit_rr:.2f}× · {fmt_aud(lit_cost)})",
                     use_container_width=True):
            # Streamlit re-runs on click; we use query params to pass values
            st.session_state["rr"]   = lit_rr
            st.session_state["cost"] = lit_cost / 1e6
            st.rerun()

# Restore preset if clicked
if "rr" in st.session_state:
    rr     = st.session_state.pop("rr")
    cost_m = st.session_state.pop("cost")
    cost   = cost_m * 1e6


# ── Interpolated thresholds ────────────────────────────────────────────────────
t50   = interp(rr, T50)
t30   = interp(rr, T30)
tSave = interp(rr, TSAVE)

# ── Derived quantities ────────────────────────────────────────────────────────
extra_kits      = (rr - 1.0) * COMPARATOR_KITS
cost_per_person = cost / ELIGIBLE_POP
cost_per_kit    = cost / extra_kits if extra_kits > 0 else None

# ── Header ────────────────────────────────────────────────────────────────────
st.title("Maximum Cost-Effective Intervention Threshold")
st.caption("Bowel cancer screening promotion · Policy1-Bowel microsimulation · Australia")

# ══ SECTION 1: Thresholds ════════════════════════════════════════════════════
st.subheader("Maximum cost-effective thresholds")
st.caption(f"At participation increase RR = {rr:.2f}×")

c1, c2, c3 = st.columns(3)

def threshold_tile(col, label, value, help_text, ek, cost):
    with col:
        st.metric(label=label, value=fmt_aud(value), help=help_text)
        st.caption(f"Per eligible person: {fmt_aud(value / ELIGIBLE_POP)}")
        if ek > 0:
            st.caption(f"Per extra kit returned: {fmt_aud(value / ek)}")
        else:
            st.caption("Per extra kit: N/A (RR = 1.0)")
        # verdict badge
        if value <= 0:
            badge, col_ = "— N/A", "gray"
        elif cost <= value:
            badge, col_ = "✅  Cost-effective", "green"
        else:
            badge, col_ = "❌  Exceeds threshold", "red"
        st.markdown(
            f"<span style='color:{col_};font-weight:600;font-size:13px'>{badge}</span>",
            unsafe_allow_html=True,
        )

if tSave > 0:
    threshold_tile(c1, "Cost-saving threshold", tSave,
                   "Net program cost difference only; no health benefit component.",
                   extra_kits, cost)
else:
    with c1:
        st.metric(label="Cost-saving threshold", value="$0",
                  help="No cost saving at this participation level.")
        st.caption("Per eligible person: —")
        st.caption("Per extra kit returned: —")
        st.markdown("<span style='color:gray;font-weight:600;font-size:13px'>— N/A</span>",
                    unsafe_allow_html=True)

threshold_tile(c2, "MCEIT — WTP $30,000/LYS", t30,
               "MCEIT including health gains valued at $30,000 per life-year saved.",
               extra_kits, cost)
threshold_tile(c3, "MCEIT — WTP $50,000/LYS", t50,
               "MCEIT including health gains valued at $50,000 per life-year saved.",
               extra_kits, cost)

# st.caption(
#     f"Eligible population: {ELIGIBLE_POP:,} persons · "
#     f"Comparator kits: {COMPARATOR_KITS:,.0f} (Policy1-Bowel modelled population, NBCSP)"
# )

st.divider()

# ── Plotly chart ──────────────────────────────────────────────────────────────
fig = go.Figure()

# Shaded zone: between cost-saving and $30k
fig.add_trace(go.Scatter(
    x=list(RR_SMOOTH) + list(RR_SMOOTH[::-1]),
    y=smoothSave + smooth30[::-1],
    fill="toself",
    fillcolor="rgba(74,158,106,0.10)",
    line=dict(width=0),
    hoverinfo="skip",
    showlegend=False,
    name="_fill_30",
))

# Shaded zone: between $30k and $50k
fig.add_trace(go.Scatter(
    x=list(RR_SMOOTH) + list(RR_SMOOTH[::-1]),
    y=smooth30 + smooth50[::-1],
    fill="toself",
    fillcolor="rgba(91,138,245,0.10)",
    line=dict(width=0),
    hoverinfo="skip",
    showlegend=False,
    name="_fill_50",
))

# Cost-saving line
fig.add_trace(go.Scatter(
    x=RR_SMOOTH, y=smoothSave,
    mode="lines",
    name="Cost-saving threshold",
    line=dict(color="#35D0A0", width=2, dash="solid"),
    hovertemplate="Cost-saving: $%{y:.2f}M<extra></extra>",
))

# $30k line
fig.add_trace(go.Scatter(
    x=RR_SMOOTH, y=smooth30,
    mode="lines",
    name="MCEIT at $30,000/LYS",
    line=dict(color="#84B0FF", width=2, dash="dot"),
    hovertemplate="$30k/LYS: $%{y:.2f}M<extra></extra>",
))

# $50k line
fig.add_trace(go.Scatter(
    x=RR_SMOOTH, y=smooth50,
    mode="lines",
    name="MCEIT at $50,000/LYS",
    line=dict(color="#5B8AF5", width=2.5, dash="dash"),
    hovertemplate="$50k/LYS: $%{y:.2f}M<extra></extra>",
))

# Literature interventions (grey diamonds)
for name, lit_rr, lit_cost in LITERATURE:
    fig.add_trace(go.Scatter(
        x=[lit_rr], y=[lit_cost / 1e6],
        mode="markers+text",
        name=name,
        marker=dict(symbol="diamond", size=9, color="#888888",
                    line=dict(color="white", width=1.5)),
        text=[name.split(" (")[0]],
        textposition="top right",
        textfont=dict(size=10, color="#888888"),
        showlegend=True,
    ))

# User's intervention point
fig.add_trace(go.Scatter(
    x=[rr], y=[cost / 1e6],
    mode="markers",
    name="Your intervention",
    marker=dict(
        symbol="circle", size=14,
        color="#FF6B35",
        line=dict(color="white", width=2),
    ),
    hovertemplate=(
        f"<b>Your intervention</b><br>"
        f"RR: {rr:.2f}×<br>"
        f"Cost: ${cost/1e6:.2f}M<extra></extra>"
    ),
))

# Vertical line at current RR
fig.add_vline(
    x=rr, line_width=1, line_dash="dot", line_color="rgba(180,180,180,0.5)",
)

fig.update_layout(
    height=480,
    xaxis=dict(
        title="Participation increase (relative to comparator)",
        tickvals=RR_PTS,
        ticktext=[f"{r:.1f}×" for r in RR_PTS],
        range=[0.97, 1.63],
        gridcolor="rgba(100,100,100,0.15)",
        zeroline=False,
    ),
    yaxis=dict(
        title="Threshold (AUD, millions)",
        tickprefix="$",
        ticksuffix="M",
        gridcolor="rgba(100,100,100,0.15)",
        zeroline=False,
        rangemode="tozero",
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom", y=1.02,
        xanchor="left", x=0,
        font=dict(size=11),
    ),
    margin=dict(l=60, r=20, t=50, b=50),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    hovermode="x unified",
)

st.plotly_chart(fig, use_container_width=True)

# ── Footnote ──────────────────────────────────────────────────────────────────
# st.caption("**MCEIT** = (C_comparator − C_scenario) + (E_scenario − E_comparator) × WTP.")
st.caption("Thresholds derived from Policy1-Bowel microsimulation (Australia).")
st.caption("Linear interpolation applied between modelled participation scenarios (RR 1.0–1.6).")
# st.caption("Eligible population: 3,967,654 persons · Comparator kits: 1,349,188 (Policy1-Bowel modelled population, NBCSP)")
# st.caption("Cost-saving threshold reflects net program cost difference only (no health benefit component).")
# st.caption(f"Per eligible person = total MCEIT ÷ {ELIGIBLE_POP:,} eligible persons.")
# st.caption(f"Per extra kit = total MCEIT ÷ (RR − 1) × {COMPARATOR_KITS:,.0f} comparator kits (Policy1-Bowel modelled population, NBCSP).")
