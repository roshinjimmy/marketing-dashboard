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

Data files are expected at `data/` relative to the repo root. You can also point to a custom folder by setting an environment variable before running:

```bash
export DATA_DIR=/absolute/path/to/your/data
streamlit run app/main.py
```

## Deployment (Streamlit Cloud)

1) Push this repo to GitHub
2) In Streamlit Cloud, create a new app pointing to `app/main.py`
3) Select Python 3.12 (or Default if it picks 3.12 automatically)
4) The platform will use `requirements.txt` to install dependencies

Live app: https://marketing-dashboard-lifesight.streamlit.app/

## Screenshots

Place a few representative screenshots in `docs/screenshots/` for quick review:

- `docs/screenshots/summary.png` – Executive Summary (KPIs + channel breakdown)
- `docs/screenshots/trends.png` – Trends (Spend vs Revenue; MER & Blended CAC)
- `docs/screenshots/profit.png` – Profit (Contribution & Profit ROAS)
- `docs/screenshots/geo_tactic.png` – Geo & Tactic (bars or map)
- `docs/screenshots/data_quality.png` – Data Quality (coverage, reconciliation, outliers)

Tips:
- In Streamlit, use the menu → "Settings → Enable wide mode" for better captures.
- Prefer 125% zoom and hide the sidebar if the focus is on charts.
- Name files exactly as above so they render consistently in PRs and READMEs.

## Project structure

- `app/` – Streamlit app
	- `main.py` – entry point and routing
	- `data.py` – data loading and normalization
	- `metrics.py` – derived metrics
	- `views/` – pages
		- `summary.py`, `drilldown.py`
- `data/` – CSV inputs (Facebook, Google, TikTok, business)
- `docs/plan.md` – detailed plan and scope
- `requirements.txt` – pinned dependencies