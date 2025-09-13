import streamlit as st
from views import summary, drilldown, trends, data_quality, profit, geo_tactic
from datetime import timedelta
import pandas as pd
import data as data_mod
import metrics as metrics_mod

st.set_page_config(page_title="Marketing Intelligence Dashboard", layout="wide")


def sidebar_nav(marketing_df):
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Executive Summary", "Drilldown", "Trends", "Profit", "Geo & Tactic", "Data Quality"]) 
    # Filters
    filters = {}
    filt_opts = data_mod.get_available_filters(marketing_df)
    st.sidebar.markdown("### Filters")
    channels = st.sidebar.multiselect(
        "Channel",
        options=filt_opts.get("channels", []),
        default=filt_opts.get("channels", []),
        key="filter_channels",
    )
    tactics = st.sidebar.multiselect(
        "Tactic",
        options=filt_opts.get("tactics", []),
        default=filt_opts.get("tactics", []),
        key="filter_tactics",
    )
    states = st.sidebar.multiselect(
        "State",
        options=filt_opts.get("states", []),
        default=filt_opts.get("states", []),
        key="filter_states",
    )
    # Default last 60 days if available
    min_date = marketing_df["date"].min() if not marketing_df.empty else None
    max_date = marketing_df["date"].max() if not marketing_df.empty else None
    default_range = []
    if pd.notna(pd.to_datetime(min_date)) and pd.notna(pd.to_datetime(max_date)):
        start_default = max_date - timedelta(days=60)
        if start_default < min_date:
            start_default = min_date
        default_range = [start_default.date(), max_date.date()]
    date_range = st.sidebar.date_input("Date range", value=default_range, key="filter_date_range")

    # Reset button
    if st.sidebar.button("Reset filters"):
        for k in ["filter_channels", "filter_tactics", "filter_states", "filter_date_range"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()
    filters.update({"channels": channels, "tactics": tactics, "states": states, "date_range": date_range})
    return page, filters


def main():
    st.title("Marketing Intelligence Dashboard")
    marketing_df, business_df, marketing_daily = data_mod.load_all()
    # Store for other views
    st.session_state["marketing_df"] = marketing_df
    st.session_state["business_df"] = business_df
    st.session_state["marketing_daily"] = marketing_daily
    page, filters = sidebar_nav(marketing_df)

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
