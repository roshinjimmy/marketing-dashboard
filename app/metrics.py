import numpy as np
import pandas as pd


def safe_divide(numer: pd.Series, denom: pd.Series) -> pd.Series:
    denom = denom.astype(float)
    numer = numer.astype(float)
    return pd.Series(np.where(denom == 0, 0.0, numer / denom))


essential_cols = {
    "ctr": ("clicks", "impressions"),
    "cpc": ("spend", "clicks"),
    "cpm": ("spend", "impressions"),
    "roas": ("attributed_revenue", "spend"),
}


def compute_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    out = df.copy()
    if {"clicks", "impressions"}.issubset(out.columns):
        out["ctr"] = safe_divide(out["clicks"], out["impressions"]).astype(float)
    if {"spend", "clicks"}.issubset(out.columns):
        out["cpc"] = safe_divide(out["spend"], out["clicks"]).astype(float)
    if {"spend", "impressions"}.issubset(out.columns):
        out["cpm"] = (1000.0 * safe_divide(out["spend"], out["impressions"]).astype(float))
    if {"attributed_revenue", "spend"}.issubset(out.columns):
        out["roas"] = safe_divide(out["attributed_revenue"], out["spend"]).astype(float)
    return out


def compute_blended_kpis(marketing_daily: pd.DataFrame, business_daily: pd.DataFrame) -> pd.DataFrame:
    """Join marketing daily totals with business daily to compute blended KPIs.

    Returns a daily dataframe with columns: date, spend, total_revenue, mer, blended_cac,
    aov, gross_margin_pct, contribution_after_ads, profit_roas.
    """
    if marketing_daily is None or marketing_daily.empty or business_daily is None or business_daily.empty:
        cols = [
            "date",
            "spend",
            "total_revenue",
            "mer",
            "blended_cac",
            "aov",
            "gross_margin_pct",
            "contribution_after_ads",
            "profit_roas",
        ]
        return pd.DataFrame(columns=cols)

    md = marketing_daily.rename(columns={"spend": "spend"}).copy()
    bd = business_daily.copy()
    df = pd.merge(md, bd, on="date", how="inner")

    spend = df["spend"].astype(float)
    total_rev = df["total_revenue"].astype(float)
    new_cust = df["new_customers"].astype(float)
    orders = df["orders"].astype(float)
    gross_profit = df["gross_profit"].astype(float)

    mer = safe_divide(total_rev, spend)
    blended_cac = safe_divide(spend, new_cust)
    aov = safe_divide(total_rev, orders)
    gross_margin_pct = safe_divide(gross_profit, total_rev)
    contribution_after_ads = gross_profit - spend
    profit_roas = safe_divide(gross_profit, spend)

    out = pd.DataFrame(
        {
            "date": df["date"],
            "spend": spend,
            "total_revenue": total_rev,
            "mer": mer,
            "blended_cac": blended_cac,
            "aov": aov,
            "gross_margin_pct": gross_margin_pct,
            "contribution_after_ads": contribution_after_ads,
            "profit_roas": profit_roas,
        }
    )
    return out.sort_values("date").reset_index(drop=True)
