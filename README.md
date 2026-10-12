# MCEIT Dashboard

Interactive dashboard for the Maximum Cost-Effective Intervention Threshold (MCEIT) analysis of bowel cancer screening promotion in Australia, based on the Policy1-Bowel microsimulation model.

**The Cancer Elimination Collaboration | The University of Sydney**

## What it does

- Calculates the MCEIT at three thresholds (cost-saving, WTP $30,000/LYS, WTP $50,000/LYS) for any participation increase (RR 1.0–1.6) using linear interpolation between modelled scenarios
- Shows the threshold in total, per eligible person, and per extra kit returned
- Compares a user-specified program cost against each threshold
- Plots literature-identified interventions against the threshold curves

## Run locally

```bash
pip install -r requirements.txt
streamlit run mceit_dashboard.py
```

## Deploy to Streamlit Community Cloud

1. Push this folder to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Click **New app**, select your repo and set the main file to `mceit_dashboard.py`
4. Click **Deploy** — your app will be live at a public URL within a minute

## Files

| File | Description |
|------|-------------|
| `mceit_dashboard.py` | Main Streamlit app |
| `requirements.txt` | Python dependencies |
| `mceit_figure.py` | Static matplotlib figure (for publication) |

## Methods

MCEIT = (C_comparator − C_scenario) + (E_scenario − E_comparator) × WTP

Thresholds derived from Policy1-Bowel microsimulation (Australia). Eligible population: 3,967,654 persons (NBCSP). Comparator kits returned: 1,349,188.
