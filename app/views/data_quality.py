import streamlit as st
import pandas as pd


def render():
    st.subheader("Data Quality")
    if "marketing_df" not in st.session_state or "business_df" not in st.session_state:
        st.info("Data not loaded yet. Visit Executive Summary first or reload.")
        return

    m = st.session_state["marketing_df"].copy()
    b = st.session_state["business_df"].copy()

    # Coverage
    st.markdown("### Coverage")
    m_dates = (m["date"].min(), m["date"].max()) if not m.empty else (None, None)
    b_dates = (b["date"].min(), b["date"].max()) if not b.empty else (None, None)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Marketing rows", f"{len(m):,}")
    with c2:
        st.metric("Business rows", f"{len(b):,}")
    with c3:
        st.write(f"Marketing date range: {m_dates[0]} → {m_dates[1]}")
        st.write(f"Business date range: {b_dates[0]} → {b_dates[1]}")

    # Nulls & zeros
    st.markdown("### Nulls & Zeros")
    num_cols_m = ["impressions", "clicks", "spend", "attributed_revenue"]
    nulls_m = m[num_cols_m].isna().sum().rename("nulls")
    zeros_m = (m[num_cols_m] == 0).sum().rename("zeros")
    dq_m = pd.concat([nulls_m, zeros_m], axis=1)
    num_cols_b = ["orders", "new_orders", "new_customers", "total_revenue", "gross_profit", "cogs"]
    nulls_b = b[num_cols_b].isna().sum().rename("nulls")
    zeros_b = (b[num_cols_b] == 0).sum().rename("zeros")
    dq_b = pd.concat([nulls_b, zeros_b], axis=1)
    col1, col2 = st.columns(2)
    with col1:
        st.write("Marketing numeric columns:")
        st.dataframe(dq_m)
    with col2:
        st.write("Business numeric columns:")
        st.dataframe(dq_b)

    # Reconciliation: platform attributed revenue vs business revenue
    st.markdown("### Revenue Reconciliation")
    platform_attr_rev = float(m["attributed_revenue"].sum()) if not m.empty else 0.0
    business_rev = float(b["total_revenue"].sum()) if not b.empty else 0.0
    delta = business_rev - platform_attr_rev
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Platform attributed revenue", f"${platform_attr_rev:,.0f}")
    with c2:
        st.metric("Business revenue", f"${business_rev:,.0f}")
    with c3:
        st.metric("Delta (Business − Platform)", f"${delta:,.0f}")

    st.caption("Note: Platform-attributed revenue and business revenue measure different things. We show both for transparency.")

    # Outliers: CPC z-score > 3 by campaign-date (using marketing data)
    st.markdown("### Outliers (CPC z-score > 3)")
    if m.empty:
        st.info("No marketing data to evaluate outliers.")
    else:
        mm = m.copy()
        mm["cpc"] = mm.apply(lambda r: (r["spend"] / r["clicks"]) if r["clicks"] else 0.0, axis=1)
        # compute z-scores on rows with clicks>0
        valid = mm[mm["clicks"] > 0].copy()
        if valid.empty:
            st.info("No rows with clicks > 0 to compute CPC outliers.")
        else:
            mean_cpc = valid["cpc"].mean()
            std_cpc = valid["cpc"].std(ddof=0)
            if std_cpc == 0 or pd.isna(std_cpc):
                st.info("CPC standard deviation is zero; no outliers.")
            else:
                valid["cpc_z"] = (valid["cpc"] - mean_cpc) / std_cpc
                outliers = valid[valid["cpc_z"].abs() > 3][["date", "channel", "tactic", "state", "campaign", "clicks", "spend", "cpc", "cpc_z"]]
                if outliers.empty:
                    st.success("No CPC outliers detected (|z| <= 3).")
                else:
                    st.dataframe(outliers.sort_values("cpc_z", key=lambda s: s.abs(), ascending=False), use_container_width=True)

    with st.expander("Metrics & Interpretation", expanded=False):
        st.markdown('<style>.metrics-header {font-size: 18px !important; font-weight: 500 !important;}</style>', unsafe_allow_html=True)
        st.write(
            """
            - Coverage: confirm both data sources align in date ranges and record counts.
            - Nulls & Zeros: zeros may be legitimate but spikes can indicate tracking or ingestion issues.
            - Revenue reconciliation: large sustained deltas could signal attribution or accounting differences; investigate methodology.
            - CPC outliers: extreme CPC spikes often trace to delivery anomalies, limited audience, or reporting glitches.
            - To export data or charts, use the Export Data button in the header.
            """
        )
    # Export note removed; exports not available.
