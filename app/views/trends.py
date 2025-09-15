import streamlit as st
import pandas as pd
import plotly.express as px
from theme import CHANNEL_COLORS

from metrics import compute_blended_kpis


def _apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    out = df.copy()
    date_range = filters.get("date_range") or []
    if len(date_range) == 2:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        out = out[(out["date"] >= start) & (out["date"] <= end)]
    return out


def _rolling(df: pd.DataFrame, cols: list[str], window: int) -> pd.DataFrame:
    if df.empty or window <= 1:
        return df
    out = df.copy()
    out = out.sort_values("date")
    for c in cols:
        if c in out.columns:
            out[c] = out[c].rolling(window, min_periods=1).mean()
    return out


def _apply_marketing_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    out = df.copy()
    channels = filters.get("channels") or []
    tactics = filters.get("tactics") or []
    states = filters.get("states") or []
    date_range = filters.get("date_range") or []
    if channels:
        out = out[out["channel"].isin(channels)]
    if tactics:
        out = out[out["tactic"].isin(tactics)]
    if states:
        out = out[out["state"].isin(states)]
    if len(date_range) == 2:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        out = out[(out["date"] >= start) & (out["date"] <= end)]
    return out


def _rolling_by_group(df: pd.DataFrame, group_col: str, cols: list[str], window: int) -> pd.DataFrame:
    if df.empty or window <= 1:
        return df
    def _roll(g: pd.DataFrame) -> pd.DataFrame:
        g = g.sort_values("date").copy()
        for c in cols:
            if c in g.columns:
                g[c] = g[c].rolling(window, min_periods=1).mean()
        return g
    out = df.groupby(group_col, group_keys=False).apply(_roll)
    return out.reset_index(drop=True)


def render(filters: dict):
    st.subheader("Trends")
    if "marketing_daily" not in st.session_state or "business_df" not in st.session_state:
        st.info("Data not loaded yet. Visit Executive Summary first or reload.")
        return

    m_daily = st.session_state["marketing_daily"]
    b_df = st.session_state["business_df"]

    # Apply date filter
    m_daily = _apply_filters(m_daily, filters)
    b_df = _apply_filters(b_df, filters)

    # Compute blended metrics joined by date
    blended = compute_blended_kpis(m_daily, b_df)
    if blended is None or blended.empty:
        st.warning("No data for selected date range.")
        return

    st.sidebar.markdown("### Trend options")
    rolling = st.sidebar.checkbox("7-day rolling average", value=True)
    lag_days = st.sidebar.selectbox("Lag business metrics (days)", options=[0, 1, 2, 3], index=0)
    show_channel_lines = st.sidebar.checkbox("Show per-channel time series", value=True)
    targets = (filters or {}).get("targets", {})

    # Optionally lag business metrics (revenue)
    df = blended.copy()
    if lag_days:
        df = df.sort_values("date")
        df["total_revenue"] = df["total_revenue"].shift(lag_days)
        # recompute MER with lagged revenue safely
        df["mer"] = (df["total_revenue"] / df["spend"]).fillna(0).replace([float("inf"), -float("inf")], 0)

    # Rolling averages for smoother trends
    if rolling:
        df = _rolling(df, ["spend", "total_revenue", "mer", "blended_cac"], window=7)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.line(df, x="date", y=["spend", "total_revenue"], title="Spend vs Total Revenue", template=px.defaults.template)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        
    with c2:
        fig = px.line(df, x="date", y=["mer", "blended_cac"], title="MER and Blended CAC", template=px.defaults.template)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        

    st.caption("Tip: Use the lag toggle to visualize delayed conversion effects.")

    # Optional: per-channel trends (Spend and Attributed ROAS)
    if show_channel_lines:
        if "marketing_df" in st.session_state:
            m_df = st.session_state["marketing_df"]
            m_df = _apply_marketing_filters(m_df, filters)
            if not m_df.empty:
                ch_ts = (
                    m_df.groupby(["date", "channel"], as_index=False)[["spend", "attributed_revenue"]]
                    .sum()
                    .sort_values(["channel", "date"]) 
                )
                ch_ts["roas"] = ch_ts.apply(lambda r: (r["attributed_revenue"] / r["spend"]) if r["spend"] else 0.0, axis=1)
                if rolling:
                    ch_ts = _rolling_by_group(ch_ts, "channel", ["spend", "roas"], window=7)

                st.markdown("### Per-channel trends")
                c1, c2 = st.columns(2)
                with c1:
                    fig = px.line(
                        ch_ts,
                        x="date",
                        y="spend",
                        color="channel",
                        title="Spend by channel over time",
                        color_discrete_map=CHANNEL_COLORS,
                        template=px.defaults.template,
                    )
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig, use_container_width=True)
                    # Exports are centralized in the Export center on the Executive Summary
                with c2:
                    fig = px.line(
                        ch_ts,
                        x="date",
                        y="roas",
                        color="channel",
                        title="Attributed ROAS by channel over time",
                        color_discrete_map=CHANNEL_COLORS,
                        template=px.defaults.template,
                    )
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig, use_container_width=True)
                    # Exports are centralized in the Export center on the Executive Summary

    # Small callouts
    max_rev_row = df.loc[df["total_revenue"].idxmax()] if not df.empty else None
    max_spend_row = df.loc[df["spend"].idxmax()] if not df.empty else None
    min_cac_row = df.loc[df["blended_cac"].idxmin()] if not df.empty else None

    c1, c2, c3 = st.columns(3)
    with c1:
        if max_rev_row is not None:
            st.metric("Max revenue day", f"{max_rev_row['date'].date()}", help=f"${max_rev_row['total_revenue']:,.0f}")
    with c2:
        if max_spend_row is not None:
            st.metric("Max spend day", f"{max_spend_row['date'].date()}", help=f"${max_spend_row['spend']:,.0f}")
    with c3:
        if min_cac_row is not None:
            st.metric("Min blended CAC day", f"{min_cac_row['date'].date()}", help=f"${min_cac_row['blended_cac']:,.2f}")

    with st.expander("Metrics & Interpretation", expanded=False):
        st.markdown('<style>.metrics-header {font-size: 18px !important; font-weight: 500 !important;}</style>', unsafe_allow_html=True)
        st.write(
            """
            - Spend vs Total Revenue shows the relationship between investment and top-line outcomes; consider enabling 7-day rolling averages for seasonality/noise.
            - MER and Blended CAC track efficiency: MER higher is better; CAC lower is better.
            - The Lag option shifts revenue to simulate delayed conversions; use it to test attribution lag hypotheses.
            - Per-channel trends help catch mix shifts: a channel with rising spend but falling ROAS may need attention.
            
            """
        )
