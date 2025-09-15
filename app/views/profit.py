import streamlit as st
import pandas as pd
import plotly.express as px
from theme import CHANNEL_COLORS  # For consistency if channel splits are added later

from metrics import compute_blended_kpis
import io


def _apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    out = df.copy()
    date_range = filters.get("date_range") or []
    if len(date_range) == 2:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        out = out[(out["date"] >= start) & (out["date"] <= end)]
    return out


essential_cols = [
    "contribution_after_ads",
    "profit_roas",
    "gross_margin_pct",
]


def _rolling(df: pd.DataFrame, cols: list[str], window: int) -> pd.DataFrame:
    if df.empty or window <= 1:
        return df
    out = df.sort_values("date").copy()
    for c in cols:
        if c in out.columns:
            out[c] = out[c].rolling(window, min_periods=1).mean()
    return out


def render(filters: dict):
    st.subheader("Profit & Contribution")

    if "marketing_daily" not in st.session_state or "business_df" not in st.session_state:
        st.info("Data not loaded yet. Visit Executive Summary first or reload.")
        return

    m_daily = st.session_state["marketing_daily"]
    b_df = st.session_state["business_df"]

    # Apply date filters
    m_daily = _apply_filters(m_daily, filters)
    b_df = _apply_filters(b_df, filters)

    blended = compute_blended_kpis(m_daily, b_df)
    if blended is None or blended.empty:
        st.warning("No data for selected date range.")
        return

    st.sidebar.markdown("### Profit options")
    rolling = st.sidebar.checkbox("7-day rolling average", value=True)
    lag_days = st.sidebar.selectbox("Lag business metrics (days)", options=[0, 1, 2, 3], index=0)
    targets = (filters or {}).get("targets", {})

    df = blended.copy().sort_values("date")
    if lag_days:
        # Lag gross-profit-derived metrics by shifting total_revenue and gross_profit together
        df["gross_profit"] = df["gross_margin_pct"] * df["total_revenue"]
        df["total_revenue"] = df["total_revenue"].shift(lag_days)
        df["gross_profit"] = df["gross_profit"].shift(lag_days)
        # recompute contribution & profit roas
        df["contribution_after_ads"] = (df["gross_profit"] - df["spend"]).fillna(0)
        df["profit_roas"] = (df["gross_profit"] / df["spend"]).replace([float("inf"), -float("inf")], 0).fillna(0)

    if rolling:
        df = _rolling(df, ["contribution_after_ads", "profit_roas"], window=7)

    # KPIs
    total_contrib = float(df["contribution_after_ads"].sum())
    avg_profit_roas = float(df["profit_roas"].replace([float("inf"), -float("inf")], 0).fillna(0).mean())
    avg_gm = float(df["gross_margin_pct"].replace([float("inf"), -float("inf")], 0).fillna(0).mean())

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Contribution after ads (sum)", f"${total_contrib:,.0f}")
    with c2:
        t = targets.get("profit_roas")
        if t:
            st.metric("Avg Profit ROAS", f"{avg_profit_roas:,.2f}", delta=f"{(avg_profit_roas - t):+.2f}")
        else:
            st.metric("Avg Profit ROAS", f"{avg_profit_roas:,.2f}")
    with c3:
        st.metric("Avg Gross Margin %", f"{avg_gm*100:,.1f}%")

    # Trends
    c1, c2 = st.columns(2)
    with c1:
        fig = px.line(df, x="date", y="contribution_after_ads", title="Contribution after ads over time", template=px.defaults.template)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        
    with c2:
        fig = px.line(df, x="date", y="profit_roas", title="Profit ROAS over time", template=px.defaults.template)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        

    st.caption("Contribution after ads = Gross Profit − Total Ad Spend. Profit ROAS = Gross Profit / Total Ad Spend.")

    # Top/Bottom days by contribution
    st.markdown("### Top/Bottom days by Contribution")
    top_n = st.slider("Show top/bottom N days", min_value=3, max_value=15, value=5)
    day_tbl = df[["date", "contribution_after_ads", "profit_roas"]].dropna().copy()
    left, right = st.columns(2)
    with left:
        st.write("Top days")
        st.dataframe(day_tbl.sort_values("contribution_after_ads", ascending=False).head(top_n), use_container_width=True)
    with right:
        st.write("Bottom days")
        st.dataframe(day_tbl.sort_values("contribution_after_ads", ascending=True).head(top_n), use_container_width=True)

    with st.expander("Metrics & Interpretation", expanded=False):
        st.markdown('<style>.metrics-header {font-size: 18px !important; font-weight: 500 !important;}</style>', unsafe_allow_html=True)
        st.write(
            """
            - Contribution after ads = Gross Profit − Ad Spend; this approximates contribution margin after marketing.
            - Profit ROAS = Gross Profit / Ad Spend; useful when revenue ROAS is misleading due to COGS shifts.
            - Use rolling averages to smooth volatility; use Lag to align revenue/gross profit timing to spend.
            - Top/Bottom days help spot anomalies, promos, or tracking issues worth investigating.
            
            """
        )
