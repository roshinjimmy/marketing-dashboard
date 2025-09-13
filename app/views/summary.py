import streamlit as st
import pandas as pd
from metrics import compute_blended_kpis


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


def _fmt_currency(x: float) -> str:
    try:
        return f"${x:,.0f}"
    except Exception:
        return "$0"


def _fmt_float(x: float) -> str:
    try:
        return f"{x:,.2f}"
    except Exception:
        return "0.00"


def render(filters: dict, marketing_df: pd.DataFrame, business_df: pd.DataFrame, marketing_daily: pd.DataFrame):
    st.subheader("Executive Summary")

    # Apply filters to marketing data for channel-level cards
    m_filtered = _apply_filters(marketing_df, filters)
    # For blended KPIs, aggregate filtered marketing then join with business
    m_daily = m_filtered.groupby("date", as_index=False)[["impressions", "clicks", "spend", "attributed_revenue"]].sum()
    blended = compute_blended_kpis(m_daily, business_df)

    total_spend = float(m_daily["spend"].sum()) if not m_daily.empty else 0.0
    total_revenue = float(blended["total_revenue"].sum()) if not blended.empty else 0.0
    total_new_customers = int(business_df["new_customers"].sum()) if not business_df.empty else 0
    mer = (total_revenue / total_spend) if total_spend else 0.0
    blended_cac = (total_spend / total_new_customers) if total_new_customers else 0.0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Spend", _fmt_currency(total_spend))
    with c2:
        st.metric("Total revenue", _fmt_currency(total_revenue))
    with c3:
        st.metric("MER", _fmt_float(mer))
    with c4:
        st.metric("Blended CAC", _fmt_currency(blended_cac))

    st.markdown("### Channel breakdown")
    if m_filtered.empty:
        st.warning("No data for selected filters.")
        return
    channel_grp = m_filtered.groupby("channel", as_index=False).agg({
        "spend": "sum",
        "attributed_revenue": "sum",
        "impressions": "sum",
        "clicks": "sum",
    })
    channel_grp["roas"] = channel_grp.apply(
        lambda r: (r["attributed_revenue"] / r["spend"]) if r["spend"] else 0.0, axis=1
    )
    st.dataframe(
        channel_grp[["channel", "spend", "attributed_revenue", "roas", "impressions", "clicks"]]
        .sort_values("spend", ascending=False)
        .rename(columns={
            "channel": "Channel",
            "spend": "Spend",
            "attributed_revenue": "Attributed revenue",
            "roas": "Attributed ROAS",
            "impressions": "Impressions",
            "clicks": "Clicks",
        }),
        use_container_width=True,
    )
    with st.expander("Metric definitions"):
        st.write("""
        - MER (Blended ROAS) = Total Revenue / Total Ad Spend
        - Blended CAC = Total Ad Spend / New Customers
        - AOV = Total Revenue / Orders
        - Attributed ROAS = Attributed Revenue / Spend (per channel; from platform reporting)
        """)
