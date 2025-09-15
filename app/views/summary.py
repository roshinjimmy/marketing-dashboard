import streamlit as st
import pandas as pd
import plotly.express as px
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

    # Export UI removed per request

    # Apply filters to marketing data for channel-level cards
    m_filtered = _apply_filters(marketing_df, filters)
    # For blended KPIs, aggregate filtered marketing then join with business
    m_daily = m_filtered.groupby("date", as_index=False)[["impressions", "clicks", "spend", "attributed_revenue"]].sum()
    blended = compute_blended_kpis(m_daily, business_df)

    # Export handled at header button

    # Helper: compute previous period date range for deltas
    def _prev_period_rng() -> tuple[pd.Timestamp | None, pd.Timestamp | None]:
        dr = (filters or {}).get("date_range") or []
        if not (isinstance(dr, list) and len(dr) == 2):
            return None, None
        try:
            cur_start = pd.to_datetime(dr[0])
            cur_end = pd.to_datetime(dr[1])
        except Exception:
            return None, None
        if pd.isna(cur_start) or pd.isna(cur_end):
            return None, None
        # previous period length matches current; end is day before current start
        period_len = (cur_end - cur_start).days
        prev_end = cur_start - pd.Timedelta(days=1)
        prev_start = prev_end - pd.Timedelta(days=period_len)
        return prev_start.normalize(), prev_end.normalize()

    pp_start, pp_end = _prev_period_rng()

    total_spend = float(m_daily["spend"].sum()) if not m_daily.empty else 0.0
    total_revenue = float(blended["total_revenue"].sum()) if not blended.empty else 0.0
    total_attr_rev = float(m_filtered["attributed_revenue"].sum()) if not m_filtered.empty else 0.0
    total_new_customers = int(business_df["new_customers"].sum()) if not business_df.empty else 0
    mer = (total_revenue / total_spend) if total_spend else 0.0
    blended_cac = (total_spend / total_new_customers) if total_new_customers else 0.0
    attributed_roas = (total_attr_rev / total_spend) if total_spend else 0.0

    # Previous period aggregates (if date range is set)
    spend_pp = rev_pp = attr_rev_pp = mer_pp = cac_pp = roas_pp = None
    if pp_start is not None and pp_end is not None:
        # Marketing prev window
        m_pp = marketing_df[(marketing_df["date"] >= pp_start) & (marketing_df["date"] <= pp_end)].copy()
        # Respect current categorical filters (channels/tactics/states)
        m_pp = _apply_filters(m_pp, {**(filters or {}), "date_range": [pp_start, pp_end]})
        m_daily_pp = m_pp.groupby("date", as_index=False)[["impressions", "clicks", "spend", "attributed_revenue"]].sum()
        blended_pp = compute_blended_kpis(m_daily_pp, business_df[(business_df["date"] >= pp_start) & (business_df["date"] <= pp_end)])
        spend_pp = float(m_daily_pp["spend"].sum()) if not m_daily_pp.empty else 0.0
        rev_pp = float(blended_pp["total_revenue"].sum()) if not blended_pp.empty else 0.0
        attr_rev_pp = float(m_pp["attributed_revenue"].sum()) if not m_pp.empty else 0.0
        mer_pp = (rev_pp / spend_pp) if spend_pp else 0.0
        # Use prev window new customers for CAC baseline
        b_pp = business_df[(business_df["date"] >= pp_start) & (business_df["date"] <= pp_end)]
        new_cust_pp = float(b_pp["new_customers"].sum()) if not b_pp.empty else 0.0
        cac_pp = (spend_pp / new_cust_pp) if new_cust_pp else 0.0
        roas_pp = (attr_rev_pp / spend_pp) if spend_pp else 0.0

    def pct_delta(cur: float, prev: float | None) -> str | None:
        if prev is None:
            return None
        try:
            if prev == 0:
                return None
            pct = 100.0 * (cur - prev) / prev
            return f"{pct:+.1f}%"
        except Exception:
            return None

    targets = (filters or {}).get("targets", {})
    tg_mer = targets.get("mer")
    tg_cac = targets.get("cac")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Spend", _fmt_currency(total_spend), delta=pct_delta(total_spend, spend_pp))
    with c2:
        st.metric("Total revenue", _fmt_currency(total_revenue), delta=pct_delta(total_revenue, rev_pp))
    with c3:
        if tg_mer:
            delta = mer - tg_mer
            st.metric("MER", _fmt_float(mer), delta=f"{delta:+.2f}")
        else:
            st.metric("MER", _fmt_float(mer), delta=pct_delta(mer, mer_pp))
    with c4:
        if tg_cac:
            delta = tg_cac - blended_cac  # lower CAC is better, so invert
            st.metric("Blended CAC", _fmt_currency(blended_cac), delta=f"{delta:+.0f}", delta_color="inverse")
        else:
            st.metric("Blended CAC", _fmt_currency(blended_cac), delta=pct_delta(blended_cac, cac_pp), delta_color="inverse")

    # Second row: attributed ROAS vs target (if provided)
    tg_roas = targets.get("roas")
    if tg_roas:
        c = st.columns(1)[0]
        with c:
            st.metric("Attributed ROAS", _fmt_float(attributed_roas), delta=f"{(attributed_roas - tg_roas):+.2f}")
    else:
        c = st.columns(1)[0]
        with c:
            st.metric("Attributed ROAS", _fmt_float(attributed_roas), delta=pct_delta(attributed_roas, roas_pp))

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

    with st.expander("Metrics & Interpretation", expanded=False):
        st.markdown('<style>.metrics-header {font-size: 18px !important; font-weight: 500 !important;}</style>', unsafe_allow_html=True)
        st.write(
            """
            Metrics
            - MER (Blended ROAS) = Total Revenue / Total Ad Spend
            - Blended CAC = Total Ad Spend / New Customers
            - AOV = Total Revenue / Orders
            - Attributed ROAS = Attributed Revenue / Spend (per channel; from platform reporting)

            How to interpret
            - Use the filters to isolate channels, tactics, or states and a date window.
            - KPIs show current totals; deltas compare to the immediately previous, same-length period.
            - MER reflects overall return on ad spend from business revenue; Attributed ROAS comes from platform reporting.
            - Blended CAC is inverted for color semantics (lower is better); look for downward movement.
            - The Channel breakdown highlights where spend is concentrated and where efficiency (ROAS) is higher or lower.
            
            """
        )
