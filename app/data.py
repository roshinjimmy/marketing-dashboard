from __future__ import annotations
from pathlib import Path
import os
from typing import Dict, Tuple, Iterable

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]

# Prefer the new 'data' folder; allow override via DATA_DIR env; fallback to old folder name
def _resolve_data_dir() -> Path:
    # 1) Explicit override via environment variable
    env_dir = os.environ.get("DATA_DIR")
    if env_dir:
        p = Path(env_dir).expanduser().resolve()
        if p.exists():
            return p
    # 2) New default 'data' in repo root
    p_new = ROOT / "data"
    if p_new.exists():
        return p_new
    # 3) Back-compat old folder name
    p_old = ROOT / "Marketing Intelligence Dashboard"
    if p_old.exists():
        return p_old
    # 4) Fallback to root (app will show empty dataframes if files are absent)
    return ROOT

DATA_DIR = _resolve_data_dir()


def _read_marketing_csv(path: Path, channel: str) -> pd.DataFrame:
    """Read a single channel CSV and standardize schema.

    Incoming columns: date, tactic, state, campaign, impression, clicks, spend, attributed revenue
    Standardized: date, channel, tactic, state, campaign, impressions, clicks, spend, attributed_revenue
    """
    df = pd.read_csv(path)
    # Rename to normalized schema
    rename_map = {
        "impression": "impressions",
        "attributed revenue": "attributed_revenue",
    }
    df = df.rename(columns=rename_map)

    # Add channel and ensure presence/order of columns
    df["channel"] = channel
    expected_cols = [
        "date",
        "channel",
        "tactic",
        "state",
        "campaign",
        "impressions",
        "clicks",
        "spend",
        "attributed_revenue",
    ]
    # Keep only expected columns if extras exist
    df = df[[c for c in expected_cols if c in df.columns] + [c for c in df.columns if c not in expected_cols]]

    # Types
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for col in ["impressions", "clicks", "spend", "attributed_revenue"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    # Clean strings (strip)
    for col in ["tactic", "state", "campaign", "channel"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    # Drop rows with invalid dates
    df = df.dropna(subset=["date"]).reset_index(drop=True)
    return df[expected_cols]


def load_marketing_data(data_dir: Path | None = None) -> pd.DataFrame:
    """Load and combine Facebook, Google, TikTok CSVs into a unified DataFrame."""
    ddir = (data_dir or DATA_DIR)
    paths = {
        "Facebook": ddir / "Facebook.csv",
        "Google": ddir / "Google.csv",
        "TikTok": ddir / "TikTok.csv",
    }
    # Compute mtimes and pass as cache keys
    paths_with_mtimes: list[tuple[str, str, float]] = []
    for ch, p in paths.items():
        mtime = p.stat().st_mtime if p.exists() else 0.0
        paths_with_mtimes.append((ch, str(p), mtime))

    df = _cached_read_marketing(tuple(paths_with_mtimes))
    return df


@st.cache_data(show_spinner=False)
def _cached_read_marketing(paths_with_mtimes: tuple[tuple[str, str, float], ...]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for channel, path_str, _mtime in paths_with_mtimes:
        p = Path(path_str)
        if p.exists():
            frames.append(_read_marketing_csv(p, channel))
    if not frames:
        return pd.DataFrame(
            columns=[
                "date",
                "channel",
                "tactic",
                "state",
                "campaign",
                "impressions",
                "clicks",
                "spend",
                "attributed_revenue",
            ]
        )
    df = pd.concat(frames, ignore_index=True)
    return df.sort_values(["date", "channel"]).reset_index(drop=True)


def load_business_data(data_dir: Path | None = None) -> pd.DataFrame:
    """Load business daily totals and standardize schema.

    Incoming columns: date,# of orders,# of new orders,new customers,total revenue,gross profit,COGS
    Standardized: date, orders, new_orders, new_customers, total_revenue, gross_profit, cogs
    """
    ddir = (data_dir or DATA_DIR)
    path = ddir / "business.csv"
    if not path.exists():
        return pd.DataFrame(
            columns=[
                "date",
                "orders",
                "new_orders",
                "new_customers",
                "total_revenue",
                "gross_profit",
                "cogs",
            ]
        )
    df = _cached_read_business(str(path), path.stat().st_mtime)
    return df


@st.cache_data(show_spinner=False)
def _cached_read_business(path_str: str, mtime: float) -> pd.DataFrame:
    path = Path(path_str)
    if not path.exists():
        return pd.DataFrame(
            columns=[
                "date",
                "orders",
                "new_orders",
                "new_customers",
                "total_revenue",
                "gross_profit",
                "cogs",
            ]
        )
    df = pd.read_csv(path)
    rename_map = {
        "# of orders": "orders",
        "# of new orders": "new_orders",
        "new customers": "new_customers",
        "total revenue": "total_revenue",
        "gross profit": "gross_profit",
        "COGS": "cogs",
    }
    df = df.rename(columns=rename_map)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for col in ["orders", "new_orders", "new_customers", "total_revenue", "gross_profit", "cogs"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    df = df.dropna(subset=["date"]).reset_index(drop=True)
    expected_cols = ["date", "orders", "new_orders", "new_customers", "total_revenue", "gross_profit", "cogs"]
    return df[expected_cols]


def get_available_filters(marketing_df: pd.DataFrame | None = None) -> Dict[str, list]:
    """Compute unique lists for filters from the marketing dataframe."""
    if marketing_df is None or marketing_df.empty:
        return {"channels": [], "tactics": [], "states": [], "campaigns": []}
    return {
        "channels": sorted(marketing_df["channel"].dropna().unique().tolist()),
        "tactics": sorted(marketing_df["tactic"].dropna().unique().tolist()),
        "states": sorted(marketing_df["state"].dropna().unique().tolist()),
        "campaigns": sorted(marketing_df["campaign"].dropna().unique().tolist()),
    }


def aggregate_marketing_daily(marketing_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate marketing metrics by date across all channels (for blending with business)."""
    if marketing_df is None or marketing_df.empty:
        return pd.DataFrame(columns=["date", "impressions", "clicks", "spend", "attributed_revenue"])
    grp = (
        marketing_df.groupby("date", as_index=False)[["impressions", "clicks", "spend", "attributed_revenue"]]
        .sum()
        .sort_values("date")
    )
    return grp


def load_all(data_dir: Path | None = None) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Convenience loader returning (marketing_df, business_df, marketing_daily).

    marketing_daily is marketing aggregated by date, useful for blended metrics with business.
    """
    m = load_marketing_data(data_dir)
    b = load_business_data(data_dir)
    md = aggregate_marketing_daily(m)
    return m, b, md
