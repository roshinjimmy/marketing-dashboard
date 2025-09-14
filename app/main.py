import streamlit as st
from views import summary, drilldown, trends, data_quality, profit, geo_tactic
from datetime import timedelta, date, datetime
import pandas as pd
import data as data_mod
from theme import apply_theme

st.set_page_config(page_title="Marketing Intelligence Dashboard", layout="wide")


def _parse_csv_list(val):
    if not val:
        return []
    if isinstance(val, list):
        vals = val
    else:
        vals = [val]
    out = []
    for v in vals:
        for p in str(v).split(","):
            p = p.strip()
            if p:
                out.append(p)
    return out


def _date_preset_range(max_dt: pd.Timestamp, kind: str) -> list[date]:
    if pd.isna(max_dt):
        return []
    end = max_dt.date()
    if kind == "L7":
        start = (max_dt - pd.Timedelta(days=6)).date()
    elif kind == "L30":
        start = (max_dt - pd.Timedelta(days=29)).date()
    elif kind == "L90":
        start = (max_dt - pd.Timedelta(days=89)).date()
    elif kind == "MTD":
        start = date(max_dt.year, max_dt.month, 1)
    elif kind == "QTD":
        q_start_month = ((max_dt.month - 1) // 3) * 3 + 1
        start = date(max_dt.year, q_start_month, 1)
    elif kind == "YTD":
        start = date(max_dt.year, 1, 1)
    else:
        return []
    return [start, end]


def _update_query_params(cur: dict):
    try:
        qp = st.query_params
        changed = False
        for k, v in cur.items():
            existing = qp.get(k)
            if existing != v:
                qp[k] = v
                changed = True
        if changed:
            st.query_params.update(qp)
    except Exception:
        # Fallback for older Streamlit: use experimental APIs if needed
        try:
            st.experimental_set_query_params(**cur)
        except Exception:
            pass


def sidebar_nav(marketing_df):
    # Compact navigation header at the very top
    st.sidebar.markdown(
        """
        <div class="oct-nav-header">
          <span class="oct-nav-title">Navigation</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    # Theme CSS is now injected globally in main()
    page = st.sidebar.radio("Go to", ["Executive Summary", "Drilldown", "Trends", "Profit", "Geo & Tactic", "Data Quality"], label_visibility="collapsed") 
    # Filters
    filters = {}
    filt_opts = data_mod.get_available_filters(marketing_df)
    st.sidebar.markdown("### Filters")
    # Query params (if any)
    try:
        qp = st.query_params
        qp_channels = _parse_csv_list(qp.get("channels"))
        qp_tactics = _parse_csv_list(qp.get("tactics"))
        qp_states = _parse_csv_list(qp.get("states"))
        qp_start = qp.get("start")
        qp_end = qp.get("end")
    except Exception:
        qp_channels = qp_tactics = qp_states = []
        qp_start = qp_end = None

    # Helper to render a simple checkbox group (no 'All' toggle)
    def checkbox_group(label: str, options: list[str], qp_default: list[str], group_key: str) -> list[str]:
        options = options or []
        st.sidebar.markdown(f"#### {label}")
        # Determine base selection: session -> query params -> all
        prev_sel = st.session_state.get(group_key)
        base_sel = [o for o in (prev_sel if isinstance(prev_sel, list) else (qp_default or options)) if o in options]
        selected: list[str] = []
        for opt in options:
            opt_key = f"chk_{group_key}_{opt}"
            checked = st.sidebar.checkbox(opt, value=(opt in base_sel), key=opt_key)
            if checked:
                selected.append(opt)
        # Persist group selection for reset/share and URL sync
        st.session_state[group_key] = selected
        return selected

    channels = checkbox_group(
        "Channel",
        options=filt_opts.get("channels", []),
        qp_default=qp_channels,
        group_key="filter_channels",
    )
    st.sidebar.markdown('<div class="oct-divider"></div>', unsafe_allow_html=True)
    tactics = checkbox_group(
        "Tactic",
        options=filt_opts.get("tactics", []),
        qp_default=qp_tactics,
        group_key="filter_tactics",
    )
    st.sidebar.markdown('<div class="oct-divider"></div>', unsafe_allow_html=True)
    states = checkbox_group(
        "State",
        options=filt_opts.get("states", []),
        qp_default=qp_states,
        group_key="filter_states",
    )
    # Default last 60 days if available
    min_date = marketing_df["date"].min() if not marketing_df.empty else None
    max_date = marketing_df["date"].max() if not marketing_df.empty else None
    # Apply any pending preset before creating the date_input widget
    if "_pending_date_range" in st.session_state:
        # Set the widget value prior to instantiation to avoid Streamlit API exceptions
        try:
            st.session_state["filter_date_range"] = st.session_state.pop("_pending_date_range")
        except Exception:
            st.session_state.pop("_pending_date_range", None)

    default_range = []
    if pd.notna(pd.to_datetime(min_date)) and pd.notna(pd.to_datetime(max_date)):
        # Query param overrides default
        if qp_start and qp_end:
            try:
                default_range = [pd.to_datetime(qp_start).date(), pd.to_datetime(qp_end).date()]
            except Exception:
                default_range = []
        if not default_range:
            start_default = max_date - timedelta(days=60)
            if start_default < min_date:
                start_default = min_date
            default_range = [start_default.date(), max_date.date()]
    # If a value already exists in session_state (e.g., from a previous run or preset), prefer it
    date_value = st.session_state.get("filter_date_range", default_range)
    date_range = st.sidebar.date_input("Date range", value=date_value, key="filter_date_range")

    # Preset chips
    if pd.notna(pd.to_datetime(max_date)):
        # Divider before quick ranges
        st.sidebar.markdown('<div class="oct-divider"></div>', unsafe_allow_html=True)
        st.sidebar.markdown("#### Quick ranges")
        # Wrap quick range buttons in a container to target CSS without affecting other buttons
        st.sidebar.markdown('<div id="quick-ranges">', unsafe_allow_html=True)
        r1, r2, r3 = st.sidebar.columns(3)
        if r1.button("Last 7"):
            st.session_state["_pending_date_range"] = _date_preset_range(max_date, "L7")
            st.rerun()
        if r2.button("Last 30"):
            st.session_state["_pending_date_range"] = _date_preset_range(max_date, "L30")
            st.rerun()
        if r3.button("Last 90"):
            st.session_state["_pending_date_range"] = _date_preset_range(max_date, "L90")
            st.rerun()
        r4, r5, r6 = st.sidebar.columns(3)
        if r4.button("MTD"):
            st.session_state["_pending_date_range"] = _date_preset_range(max_date, "MTD")
            st.rerun()
        if r5.button("QTD"):
            st.session_state["_pending_date_range"] = _date_preset_range(max_date, "QTD")
            st.rerun()
        if r6.button("YTD"):
            st.session_state["_pending_date_range"] = _date_preset_range(max_date, "YTD")
            st.rerun()
        st.sidebar.markdown('</div>', unsafe_allow_html=True)

    # (Removed) Table density toggle per request
    # Sync query params for shareable URLs
    qp_cur = {
        "channels": ",".join(channels) if channels else "",
        "tactics": ",".join(tactics) if tactics else "",
        "states": ",".join(states) if states else "",
    }
    if isinstance(date_range, list) and len(date_range) == 2:
        try:
            qp_cur["start"] = pd.to_datetime(date_range[0]).date().isoformat()
            qp_cur["end"] = pd.to_datetime(date_range[1]).date().isoformat()
        except Exception:
            pass
    _update_query_params(qp_cur)

    # KPI Targets (optional)
    st.sidebar.markdown('<div class="oct-divider"></div>', unsafe_allow_html=True)
    with st.sidebar.expander("KPI Targets (optional)"):
        t_mer = st.number_input("Target MER (Blended ROAS)", min_value=0.0, value=0.0, step=0.1, format="%.2f")
        t_roas = st.number_input("Target Attributed ROAS", min_value=0.0, value=0.0, step=0.1, format="%.2f")
        t_cac = st.number_input("Target Blended CAC ($)", min_value=0.0, value=0.0, step=1.0, format="%.0f")
        t_profit_roas = st.number_input("Target Profit ROAS", min_value=0.0, value=0.0, step=0.1, format="%.2f")
    targets = {
        "mer": t_mer if t_mer > 0 else None,
        "roas": t_roas if t_roas > 0 else None,
        "cac": t_cac if t_cac > 0 else None,
        "profit_roas": t_profit_roas if t_profit_roas > 0 else None,
    }

    # Share link
    st.sidebar.markdown('<div class="oct-divider"></div>', unsafe_allow_html=True)
    with st.sidebar.expander("Share link with filters"):
        parts = []
        for k in ["channels", "tactics", "states", "start", "end"]:
            v = qp_cur.get(k)
            if v:
                parts.append(f"{k}={v}")
        qs = ("?" + "&".join(parts)) if parts else ""
        st.code(qs, language="text")

    # Reset button at the very end (filled primary)
    st.sidebar.markdown('<div class="oct-divider"></div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div id="reset-filters">', unsafe_allow_html=True)
    if st.sidebar.button("Reset filters"):
        # Clear group selections and date
        for k in ["filter_channels", "filter_tactics", "filter_states", "filter_date_range"]:
            if k in st.session_state:
                del st.session_state[k]
        # Remove individual option checkboxes
        for opt in (filt_opts.get("channels", []) or []):
            st.session_state.pop(f"chk_filter_channels_{opt}", None)
        for opt in (filt_opts.get("tactics", []) or []):
            st.session_state.pop(f"chk_filter_tactics_{opt}", None)
        for opt in (filt_opts.get("states", []) or []):
            st.session_state.pop(f"chk_filter_states_{opt}", None)
        st.rerun()
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    filters.update({"channels": channels, "tactics": tactics, "states": states, "date_range": date_range, "targets": targets})
    return page, filters


def _apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    out = df.copy()
    channels = (filters or {}).get("channels") or []
    tactics = (filters or {}).get("tactics") or []
    states = (filters or {}).get("states") or []
    date_range = (filters or {}).get("date_range") or []
    if channels:
        out = out[out["channel"].isin(channels)]
    if tactics:
        out = out[out["tactic"].isin(tactics)]
    if states:
        out = out[out["state"].isin(states)]
    if isinstance(date_range, list) and len(date_range) == 2:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        out = out[(out["date"] >= start) & (out["date"] <= end)]
    return out


# Export center removed per request


def main():
    # Inject theme CSS globally
    css = apply_theme("Light")
    st.markdown(css, unsafe_allow_html=True)
    # Load data first
    marketing_df, business_df, marketing_daily = data_mod.load_all()
    # Store for other views
    st.session_state["marketing_df"] = marketing_df
    st.session_state["business_df"] = business_df
    st.session_state["marketing_daily"] = marketing_daily
    page, filters = sidebar_nav(marketing_df)
    
    # Page title
    st.title("Marketing Intelligence Dashboard")

    if page == "Executive Summary":
        summary.render(filters, marketing_df, business_df, marketing_daily)
    elif page == "Drilldown":
        drilldown.render(filters)
    elif page == "Trends":
        trends.render(filters)
    elif page == "Profit":
        profit.render(filters)
    elif page == "Geo & Tactic":
        geo_tactic.render(filters)
    elif page == "Data Quality":
        data_quality.render()


if __name__ == "__main__":
    main()
