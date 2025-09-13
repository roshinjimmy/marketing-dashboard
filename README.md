# marketing-dashboard

A quick Streamlit dashboard for the Marketing Intelligence assessment.

## Local setup

1) Create a virtual environment (Python 3.10+) and activate it
2) Install requirements
3) Run the Streamlit app

Linux/macOS example:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/main.py
```

Data files are expected at `Marketing Intelligence Dashboard/` relative to the repo root.

## Deployment (Streamlit Cloud)

1) Push this repo to GitHub
2) In Streamlit Cloud, create a new app pointing to `app/main.py`
3) Select Python 3.12 (or Default if it picks 3.12 automatically)
4) The platform will use `requirements.txt` to install dependencies

Live app: https://marketing-dashboard-lifesight.streamlit.app/

## Screenshots

Add a couple of representative screenshots for quick review:

- Executive Summary (KPIs + channel breakdown)
- Trends (Spend vs Revenue; MER & Blended CAC)
- Profit (Contribution & Profit ROAS)
- Data Quality (coverage, reconciliation, outliers)

## Project structure

- `app/` – Streamlit app
	- `main.py` – entry point and routing
	- `data.py` – data loading and normalization
	- `metrics.py` – derived metrics
	- `views/` – pages
		- `summary.py`, `drilldown.py`
- `Marketing Intelligence Dashboard/` – CSV inputs (Facebook, Google, TikTok, business)
- `docs/plan.md` – detailed plan and scope
- `requirements.txt` – pinned dependencies