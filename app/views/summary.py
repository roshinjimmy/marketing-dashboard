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
    total_attr_rev = float(m_filtered["attributed_revenue"].sum()) if not m_filtered.empty else 0.0
    total_new_customers = int(business_df["new_customers"].sum()) if not business_df.empty else 0
    mer = (total_revenue / total_spend) if total_spend else 0.0
    blended_cac = (total_spend / total_new_customers) if total_new_customers else 0.0
    attributed_roas = (total_attr_rev / total_spend) if total_spend else 0.0

    targets = (filters or {}).get("targets", {})
    tg_mer = targets.get("mer")
    tg_cac = targets.get("cac")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Spend", _fmt_currency(total_spend))
    with c2:
        st.metric("Total revenue", _fmt_currency(total_revenue))
    with c3:
        if tg_mer:
            delta = mer - tg_mer
            st.metric("MER", _fmt_float(mer), delta=f"{delta:+.2f}")
        else:
            st.metric("MER", _fmt_float(mer))
    with c4:
        if tg_cac:
            delta = tg_cac - blended_cac  # lower CAC is better, so invert
            st.metric("Blended CAC", _fmt_currency(blended_cac), delta=f"{delta:+.0f}")
        else:
            st.metric("Blended CAC", _fmt_currency(blended_cac))

    # Second row: attributed ROAS vs target (if provided)
    tg_roas = targets.get("roas")
    if tg_roas:
        c = st.columns(1)[0]
        with c:
            st.metric("Attributed ROAS", _fmt_float(attributed_roas), delta=f"{(attributed_roas - tg_roas):+.2f}")

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
    # If ROAS target provided, add variance column for quick scan
    roas_target = targets.get("roas")
    if roas_target:
        channel_grp["ROAS Δ vs target"] = channel_grp["roas"].apply(lambda x: x - roas_target)
    display_cols = ["channel", "spend", "attributed_revenue", "roas", "impressions", "clicks"]
    if roas_target:
        display_cols.append("ROAS Δ vs target")
    # Build formatted display copy (keep raw for CSV export)
    display_df = channel_grp[display_cols].sort_values("spend", ascending=False).copy()
    # Formatting helpers
    def _fmt_money(v):
        try:
            return f"${v:,.0f}"
        except Exception:
            return "-$-"
    def _fmt_int(v):
        try:
            return f"{int(v):,}"
        except Exception:
            return "0"
    def _fmt_roas(v):
        try:
            return f"{v:,.2f}"
        except Exception:
            return "0.00"
    # Apply formatting
    if "spend" in display_df:
        display_df["spend"] = display_df["spend"].apply(_fmt_money)
    if "attributed_revenue" in display_df:
        display_df["attributed_revenue"] = display_df["attributed_revenue"].apply(_fmt_money)
    if "roas" in display_df:
        display_df["roas"] = display_df["roas"].apply(_fmt_roas)
    if "impressions" in display_df:
        display_df["impressions"] = display_df["impressions"].apply(_fmt_int)
    if "clicks" in display_df:
        display_df["clicks"] = display_df["clicks"].apply(_fmt_int)
    if "ROAS Δ vs target" in display_df:
        display_df["ROAS Δ vs target"] = display_df["ROAS Δ vs target"].apply(lambda v: f"{v:+.2f}" if pd.notna(v) else "")

    st.dataframe(
        display_df.rename(columns={
            "channel": "Channel",
            "spend": "Spend",
            "attributed_revenue": "Attributed revenue",
            "roas": "Attributed ROAS",
            "impressions": "Impressions",
            "clicks": "Clicks",
        }),
        use_container_width=True,
    )

    # Exports
    st.download_button(
        label="Download blended KPIs (CSV)",
        data=blended.to_csv(index=False).encode("utf-8") if blended is not None else b"",
        file_name="blended_summary.csv",
        mime="text/csv",
    )
    st.download_button(
        label="Download channel breakdown (CSV)",
        data=channel_grp.to_csv(index=False).encode("utf-8") if channel_grp is not None else b"",
        file_name="channel_breakdown.csv",
        mime="text/csv",
    )
    with st.expander("Metric definitions"):
        st.write("""
        - MER (Blended ROAS) = Total Revenue / Total Ad Spend
        - Blended CAC = Total Ad Spend / New Customers
        - AOV = Total Revenue / Orders
        - Attributed ROAS = Attributed Revenue / Spend (per channel; from platform reporting)
        """)
