import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from metrics import compute_blended_kpis
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

    # Add custom CSS for styled KPI cards
    st.markdown("""
    <style>
    .kpi-card {
        background-color: white;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        text-align: center;
        border-top: 4px solid;
        transition: transform 0.3s;
    }
    .kpi-card:hover {
        transform: translateY(-5px);
    }
    .kpi-card-spend {
        border-color: #4267B2;
    }
    .kpi-card-revenue {
        border-color: #42B72A;
    }
    .kpi-card-mer {
        border-color: #0066CC;
    }
    .kpi-card-cac {
        border-color: #DB4437;
    }
    .kpi-card-roas {
        border-color: #25F4EE;
    }
    .kpi-label {
        font-size: 16px;
        font-weight: 500;
        color: #555;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .kpi-delta {
        font-size: 14px;
        padding: 4px 8px;
        border-radius: 12px;
        display: inline-block;
    }
    .kpi-delta-positive {
        background-color: rgba(66, 183, 42, 0.1);
        color: #42B72A;
    }
    .kpi-delta-negative {
        background-color: rgba(219, 68, 55, 0.1);
        color: #DB4437;
    }
    .kpi-delta-neutral {
        background-color: rgba(0, 0, 0, 0.05);
        color: #555;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Creating styled KPI cards with Attributed ROAS included
    tg_roas = targets.get("roas")
    
    # Create 5 columns for all KPIs in a single row
    c1, c2, c3, c4, c5 = st.columns(5)
    
    with c1:
        delta_str = pct_delta(total_spend, spend_pp)
        delta_class = "kpi-delta-neutral"
        if delta_str:
            delta_class = "kpi-delta-negative" if "-" in delta_str else "kpi-delta-positive"
            if "%" not in delta_str:
                delta_str += "%"
        
        # Only show delta if date filter is applied (pp_start and pp_end are not None)
        delta_html = f'<div class="kpi-delta {delta_class}">{delta_str}</div>' if pp_start is not None else ''
        
        st.markdown(f"""
        <div class="kpi-card kpi-card-spend">
            <div class="kpi-label">Spend</div>
            <div class="kpi-value">{_fmt_currency(total_spend)}</div>
            {delta_html}
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        delta_str = pct_delta(total_revenue, rev_pp)
        delta_class = "kpi-delta-neutral"
        if delta_str:
            delta_class = "kpi-delta-positive" if "-" not in delta_str else "kpi-delta-negative"
            if "%" not in delta_str:
                delta_str += "%"
        
        # Only show delta if date filter is applied (pp_start and pp_end are not None)
        delta_html = f'<div class="kpi-delta {delta_class}">{delta_str}</div>' if pp_start is not None else ''
        
        st.markdown(f"""
        <div class="kpi-card kpi-card-revenue">
            <div class="kpi-label">Total Revenue</div>
            <div class="kpi-value">{_fmt_currency(total_revenue)}</div>
            {delta_html}
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        if tg_mer:
            delta = mer - tg_mer
            delta_str = f"{delta:+.2f}"
            delta_class = "kpi-delta-positive" if delta > 0 else "kpi-delta-negative"
        else:
            delta_str = pct_delta(mer, mer_pp)
            delta_class = "kpi-delta-neutral"
            if delta_str:
                delta_class = "kpi-delta-positive" if "-" not in delta_str else "kpi-delta-negative"
                if "%" not in delta_str:
                    delta_str += "%"
        
        # Only show delta if date filter is applied (pp_start and pp_end are not None) or if target is provided
        show_delta = pp_start is not None or tg_mer is not None
        delta_html = f'<div class="kpi-delta {delta_class}">{delta_str}</div>' if show_delta else ''
        
        st.markdown(f"""
        <div class="kpi-card kpi-card-mer">
            <div class="kpi-label">MER</div>
            <div class="kpi-value">{_fmt_float(mer)}</div>
            {delta_html}
        </div>
        """, unsafe_allow_html=True)
        
    with c4:
        if tg_cac:
            delta = tg_cac - blended_cac  # lower CAC is better, so invert
            delta_str = f"{delta:+.0f}"
            delta_class = "kpi-delta-positive" if delta > 0 else "kpi-delta-negative"
        else:
            delta_str = pct_delta(blended_cac, cac_pp)
            delta_class = "kpi-delta-neutral"
            if delta_str:
                # For CAC, negative is good (lower cost)
                delta_class = "kpi-delta-positive" if "-" in delta_str else "kpi-delta-negative"
                if "%" not in delta_str:
                    delta_str += "%"
        
        # Only show delta if date filter is applied (pp_start and pp_end are not None) or if target is provided
        show_delta = pp_start is not None or tg_cac is not None
        delta_html = f'<div class="kpi-delta {delta_class}">{delta_str}</div>' if show_delta else ''
        
        st.markdown(f"""
        <div class="kpi-card kpi-card-cac">
            <div class="kpi-label">Blended CAC</div>
            <div class="kpi-value">{_fmt_currency(blended_cac)}</div>
            {delta_html}
        </div>
        """, unsafe_allow_html=True)
    
    with c5:
        if tg_roas:
            delta = attributed_roas - tg_roas
            delta_str = f"{delta:+.2f}"
            delta_class = "kpi-delta-positive" if delta > 0 else "kpi-delta-negative"
        else:
            delta_str = pct_delta(attributed_roas, roas_pp)
            delta_class = "kpi-delta-neutral"
            if delta_str:
                delta_class = "kpi-delta-positive" if "-" not in delta_str else "kpi-delta-negative"
                if "%" not in delta_str:
                    delta_str += "%"
        
        # Only show delta if date filter is applied (pp_start and pp_end are not None) or if target is provided
        show_delta = pp_start is not None or tg_roas is not None
        delta_html = f'<div class="kpi-delta {delta_class}">{delta_str}</div>' if show_delta else ''
        
        st.markdown(f"""
        <div class="kpi-card kpi-card-roas">
            <div class="kpi-label">Attributed ROAS</div>
            <div class="kpi-value">{_fmt_float(attributed_roas)}</div>
            {delta_html}
        </div>
        """, unsafe_allow_html=True)

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
    
    # Create visual charts for channel metrics
    col1, col2 = st.columns(2)
    
    with col1:
        # Spend by channel donut chart
        spend_df = channel_grp.sort_values("spend", ascending=False).copy()
        fig = px.pie(
            spend_df, 
            values="spend", 
            names="channel", 
            title="Spend Distribution by Channel",
            color="channel",
            color_discrete_map=CHANNEL_COLORS,
            hole=0.4
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            legend_title_text="Channel",
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # ROAS by channel bar chart
        roas_df = channel_grp.sort_values("roas", ascending=False).copy()
        fig = px.bar(
            roas_df,
            x="channel",
            y="roas",
            title="Attributed ROAS by Channel",
            color="channel",
            color_discrete_map=CHANNEL_COLORS,
            text_auto='.2f'
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(
            xaxis_title="Channel",
            yaxis_title="ROAS",
            legend_title_text="Channel"
        )
        # Add target line if available
        if tg_roas:
            fig.add_shape(
                type="line",
                x0=-0.5,
                x1=len(roas_df)-0.5,
                y0=tg_roas,
                y1=tg_roas,
                line=dict(color="red", width=2, dash="dash")
            )
            fig.add_annotation(
                x=len(roas_df)-0.5,
                y=tg_roas,
                text=f"Target: {tg_roas:.2f}",
                showarrow=False,
                yshift=10,
                font=dict(color="red")
            )
        st.plotly_chart(fig, use_container_width=True)
    
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

    # Add detailed metrics table
    st.markdown("### Detailed Channel Metrics")
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
    
    # CTR & CPC comparison
    st.markdown("### Channel Efficiency Metrics")
    channel_metrics = m_filtered.groupby("channel", as_index=False).agg({
        "impressions": "sum",
        "clicks": "sum",
        "spend": "sum"
    })
    channel_metrics["ctr"] = channel_metrics.apply(
        lambda r: (r["clicks"] / r["impressions"]) * 100 if r["impressions"] else 0.0, axis=1
    )
    channel_metrics["cpc"] = channel_metrics.apply(
        lambda r: (r["spend"] / r["clicks"]) if r["clicks"] else 0.0, axis=1
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CTR comparison
        ctr_df = channel_metrics.sort_values("ctr", ascending=False).copy()
        fig = px.bar(
            ctr_df,
            x="channel",
            y="ctr",
            title="Click-Through Rate by Channel",
            color="channel",
            color_discrete_map=CHANNEL_COLORS,
            text_auto='.2f'
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(
            xaxis_title="Channel",
            yaxis_title="CTR (%)",
            yaxis=dict(ticksuffix="%"),
            legend_title_text="Channel"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # CPC comparison
        cpc_df = channel_metrics.sort_values("cpc", ascending=True).copy()  # Lower CPC is better
        fig = px.bar(
            cpc_df,
            x="channel",
            y="cpc",
            title="Cost Per Click by Channel",
            color="channel",
            color_discrete_map=CHANNEL_COLORS,
            text_auto='.2f'
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(
            xaxis_title="Channel",
            yaxis_title="CPC ($)",
            yaxis=dict(tickprefix="$"),
            legend_title_text="Channel"
        )
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("Metrics & Interpretation", expanded=False):
        st.markdown('<style>.metrics-header {font-size: 18px !important; font-weight: 500 !important;}</style>', unsafe_allow_html=True)
        st.markdown(
            """
            ### Key Metrics
            
            **KPI Cards**
            - **Spend**: Total advertising expenditure across all channels
            - **Total Revenue**: Gross revenue from all business activities
            - **MER**: Total Revenue / Total Ad Spend
            - **Blended CAC**: Total Ad Spend / New Customers
            - **Attributed ROAS**: Platform-reported Revenue / Spend
            
            **Channel Metrics**
            - **Spend Distribution**: Budget allocation across channels
            - **Attributed ROAS**: Channel-specific conversion efficiency
            - **CTR**: (Clicks / Impressions) × 100% - ad relevance indicator
            - **CPC**: Spend / Clicks - traffic acquisition cost
            
            ### Quick Interpretation
            - **KPI Cards**: Green = positive trend, Red = negative trend (for CAC, lower is better)
            - **Delta Values**: Compare to previous equal-length period or target (if set)
            - **Channel Charts**: Identify budget allocation and relative performance efficiency
            - **Efficiency Metrics**: Higher CTR = better ad relevance; Lower CPC = more cost-efficient clicks
            
            **Tips**: Use filters to isolate channels or date ranges; set targets in sidebar for threshold evaluation; examine all metrics together for a complete performance picture.
            """
        )
