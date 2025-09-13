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
    st.subheader("Geo & Tactic")
    if "marketing_df" not in st.session_state:
        st.info("Data not loaded yet. Visit Executive Summary first or reload.")
        return

    df = st.session_state["marketing_df"]
    df = _apply_filters(df, filters)
    if df.empty:
        st.warning("No data for selected filters.")
        return

    # By state
    st.markdown("### By state")
    state_grp = df.groupby("state", as_index=False).agg({"spend": "sum", "attributed_revenue": "sum"})
    state_grp["roas"] = state_grp.apply(lambda r: (r["attributed_revenue"] / r["spend"]) if r["spend"] else 0.0, axis=1)
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(state_grp.sort_values("spend", ascending=False).head(20), x="state", y="spend", title="Top states by spend")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.bar(state_grp.sort_values("roas", ascending=False).head(20), x="state", y="roas", title="Top states by ROAS")
        st.plotly_chart(fig, use_container_width=True)

    # By tactic
    st.markdown("### By tactic")
    tactic_grp = df.groupby(["channel", "tactic"], as_index=False).agg({"spend": "sum", "attributed_revenue": "sum"})
    tactic_grp["roas"] = tactic_grp.apply(lambda r: (r["attributed_revenue"] / r["spend"]) if r["spend"] else 0.0, axis=1)
    fig = px.bar(
        tactic_grp.sort_values("spend", ascending=False),
        x="tactic",
        y="spend",
        color="channel",
        barmode="group",
        title="Spend by tactic and channel",
        color_discrete_map=CHANNEL_COLORS,
    )
    st.plotly_chart(fig, use_container_width=True)
