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
    # Determine top states and build a consistent color map
    top_spend = state_grp.sort_values("spend", ascending=False).head(20)
    top_roas = state_grp.sort_values("roas", ascending=False).head(20)
    top_states = pd.unique(pd.concat([top_spend["state"], top_roas["state"]], ignore_index=True))
    # Build a discrete color map that can cover up to a few dozen states
    palette = (
        px.colors.qualitative.Set2
        + px.colors.qualitative.Set1
        + px.colors.qualitative.Pastel
        + px.colors.qualitative.Safe
    )
    state_color_map = {s: palette[i % len(palette)] for i, s in enumerate(top_states)}
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(
            top_spend,
            x="state",
            y="spend",
            color="state",
            color_discrete_map=state_color_map,
            title="Top states by spend",
            template=px.defaults.template,
            category_orders={"state": list(top_states)},
        )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        fig.update_traces(hovertemplate="State: %{x}<br>Spend: $%{y:,}<extra></extra>")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        colA1, colA2 = st.columns([1,1])
        with colA1:
            st.download_button(
                "Download state spend (CSV)",
                data=top_spend.to_csv(index=False).encode("utf-8"),
                file_name="state_top_spend.csv",
                mime="text/csv",
            )
        with colA2:
            try:
                import plotly.io as pio
                img_bytes = fig.to_image(format="png")
                st.download_button(
                    "Download chart (PNG)",
                    data=img_bytes,
                    file_name="state_top_spend.png",
                    mime="image/png",
                )
            except Exception:
                pass
    with c2:
        fig = px.bar(
            top_roas,
            x="state",
            y="roas",
            color="state",
            color_discrete_map=state_color_map,
            title="Top states by ROAS",
            template=px.defaults.template,
            category_orders={"state": list(top_states)},
        )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        fig.update_traces(hovertemplate="State: %{x}<br>ROAS: %{y:.2f}<extra></extra>")
        fig.update_layout(legend_title_text="State")
        st.plotly_chart(fig, use_container_width=True)
        colB1, colB2 = st.columns([1,1])
        with colB1:
            st.download_button(
                "Download state ROAS (CSV)",
                data=top_roas.to_csv(index=False).encode("utf-8"),
                file_name="state_top_roas.csv",
                mime="text/csv",
            )
        with colB2:
            try:
                import plotly.io as pio
                img_bytes = fig.to_image(format="png")
                st.download_button(
                    "Download chart (PNG)",
                    data=img_bytes,
                    file_name="state_top_roas.png",
                    mime="image/png",
                )
            except Exception:
                pass

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
        template=px.defaults.template,
    )
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_traces(hovertemplate="Tactic: %{x}<br>Spend: $%{y:,}<br>Channel: %{legendgroup}<extra></extra>")
    st.plotly_chart(fig, use_container_width=True)
    c3, c4 = st.columns([1,1])
    with c3:
        st.download_button(
            "Download tactic spend (CSV)",
            data=tactic_grp.to_csv(index=False).encode("utf-8"),
            file_name="tactic_spend_by_channel.csv",
            mime="text/csv",
        )
    with c4:
        try:
            import plotly.io as pio
            img_bytes = fig.to_image(format="png")
            st.download_button(
                "Download chart (PNG)",
                data=img_bytes,
                file_name="tactic_spend_by_channel.png",
                mime="image/png",
            )
        except Exception:
            pass
