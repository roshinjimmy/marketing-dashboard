import streamlit as st
import pandas as pd
import plotly.express as px
from theme import CHANNEL_COLORS


def _apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
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


def render(filters: dict):
    st.subheader("Drilldown")
    st.caption("Explore performance by channel, tactic, state, and campaign")

    # Expect marketing data injected via session_state by main
    if "marketing_df" not in st.session_state:
        st.info("Data not loaded yet. Visit Executive Summary first or reload.")
        return

    df = st.session_state["marketing_df"]
    df = _apply_filters(df, filters)
    if df is None or df.empty:
        st.warning("No data for selected filters.")
        return

    # Channel bar charts
    ch = df.groupby("channel", as_index=False).agg({
        "spend": "sum",
        "attributed_revenue": "sum",
        "impressions": "sum",
        "clicks": "sum",
    })
    ch["roas"] = ch.apply(lambda r: (r["attributed_revenue"] / r["spend"]) if r["spend"] else 0.0, axis=1)

    c1, c2 = st.columns(2)
    with c1:
        df_sorted = ch.sort_values("spend", ascending=False)
        fig = px.bar(df_sorted, x="channel", y="spend", title="Spend by channel", template=px.defaults.template)
        fig.update_traces(marker_color=[CHANNEL_COLORS.get(c, "#888888") for c in df_sorted["channel"]])
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        
    with c2:
        df_sorted = ch.sort_values("roas", ascending=False)
        fig = px.bar(df_sorted, x="channel", y="roas", title="Attributed ROAS by channel", template=px.defaults.template)
        fig.update_traces(marker_color=[CHANNEL_COLORS.get(c, "#888888") for c in df_sorted["channel"]])
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        

    # Campaign table
    st.markdown("### Campaigns")
    camp = df.groupby(["channel", "tactic", "state", "campaign"], as_index=False).agg({
        "impressions": "sum",
        "clicks": "sum",
        "spend": "sum",
        "attributed_revenue": "sum",
    })
    camp["ctr"] = camp.apply(lambda r: (r["clicks"] / r["impressions"]) if r["impressions"] else 0.0, axis=1)
    camp["cpc"] = camp.apply(lambda r: (r["spend"] / r["clicks"]) if r["clicks"] else 0.0, axis=1)
    camp["cpm"] = camp.apply(lambda r: (1000 * r["spend"] / r["impressions"]) if r["impressions"] else 0.0, axis=1)
    camp["roas"] = camp.apply(lambda r: (r["attributed_revenue"] / r["spend"]) if r["spend"] else 0.0, axis=1)
    st.dataframe(
        camp.sort_values(["channel", "spend"], ascending=[True, False])
        .rename(columns={
            "channel": "Channel",
            "tactic": "Tactic",
            "state": "State",
            "campaign": "Campaign",
            "impressions": "Impr.",
            "clicks": "Clicks",
            "spend": "Spend",
            "attributed_revenue": "Attr. Rev.",
            "ctr": "CTR",
            "cpc": "CPC",
            "cpm": "CPM",
            "roas": "ROAS",
        }),
        use_container_width=True,
    )
    with st.expander("Metrics & Interpretation", expanded=False):
        st.markdown('<style>.metrics-header {font-size: 18px !important; font-weight: 500 !important;}</style>', unsafe_allow_html=True)
        st.write("""
        Metrics
        - CTR = Clicks / Impressions
        - CPC = Spend / Clicks
        - CPM = 1000 * Spend / Impressions
        - Attributed ROAS = Attributed Revenue / Spend (platform attribution)

        How to interpret
        - Start with the Channel bars to see where budget concentrates and which channels return the most (Attributed ROAS).
        - Use the Campaigns table to drill into tactics, states, or campaigns driving performance shifts.
        - CTR, CPC, CPM help diagnose whether issues are from funnel top (impressions/CTR), mid (CPC), or bottom (ROAS).
        
        """)
    # Export note removed; exports not available.
