from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


DATA_PATH = Path(__file__).with_name("slampex_data_snapshot_tape.tsv")
NUMERIC_COLUMNS = [
    "credit_limit",
    "balance",
    "cash_avg_l3m",
    "revenue_l3m",
    "gross_margin",
    "operating_margin",
    "net_margin",
    "current_ratio",
    "quick_ratio",
    "monthly_non_cc_debt_repayment",
    "monthly_cc_debt_repayment",
    "transaction_volume",
    "fees_volume",
    "rewardpoints",
    "total_balance",
    "delinquent_balance",
    "dq_days",
]
WINSORIZED_COLUMNS = [
    "credit_limit",
    "balance",
    "cash_avg_l3m",
    "revenue_l3m",
    "gross_margin",
    "operating_margin",
    "net_margin",
    "current_ratio",
    "quick_ratio",
    "monthly_non_cc_debt_repayment",
    "monthly_cc_debt_repayment",
    "transaction_volume",
    "fees_volume",
    "rewardpoints",
    "delinquent_balance",
    "dq_days",
    "utilization_pct",
]
APPLICANT_WEIGHTS = {
    "cash_avg_score": 25,
    "revenue_score": 20,
    "current_ratio_score": 15,
    "quick_ratio_score": 10,
    "gross_margin_score": 10,
    "operating_margin_score": 10,
    "net_margin_score": 5,
    "company_age_score": 5,
}
ACTIVE_WEIGHTS = {
    "delinquency_score": 20,
    "utilization_score": 15,
    "transaction_volume_score": 15,
    "cash_avg_score": 15,
    "revenue_score": 10,
    "current_ratio_score": 10,
    "quick_ratio_score": 5,
    "monthly_cc_debt_score": 10,
}
DELINQUENCY_HAIRCUTS = {
    "Current": 0.00,
    "1-30": 0.10,
    "31-90": 0.35,
    "91-180": 0.60,
    "180+": 0.90,
}
RATING_FACTORS = {"A": 1.0, "B": 0.85, "C": 0.60, "D": 0.25, "E": 0.0}


def assign_region_bucket(value: object) -> str:
    if pd.isna(value):
        return "International/Unknown"
    postal_code = str(value).strip()
    if not postal_code:
        return "International/Unknown"
    first_character = postal_code[0]
    if not first_character.isdigit():
        return "International/Unknown"
    digit = int(first_character)
    if digit <= 2:
        return "Northeast"
    if digit == 3:
        return "South"
    if digit <= 6:
        return "Midwest"
    return "West"


def winsorize_series(series: pd.Series) -> pd.Series:
    valid = series.dropna()
    if valid.empty:
        return series
    lower, upper = valid.quantile([0.01, 0.99])
    return series.clip(lower=lower, upper=upper)


def percentile_score_by_month(frame: pd.DataFrame, column: str) -> pd.Series:
    return frame.groupby("ref_date")[column].rank(pct=True, method="average") * 100


def score_current_ratio(series: pd.Series) -> pd.Series:
    return pd.Series(
        np.select(
            [
                series >= 2.0,
                (series >= 1.2) & (series < 2.0),
                (series >= 1.0) & (series < 1.2),
                (series >= 0.8) & (series < 1.0),
                series < 0.8,
            ],
            [100, 75, 50, 25, 0],
            default=np.nan,
        ),
        index=series.index,
    )


def score_quick_ratio(series: pd.Series) -> pd.Series:
    return pd.Series(
        np.select(
            [
                series >= 1.2,
                (series >= 0.8) & (series < 1.2),
                (series >= 0.5) & (series < 0.8),
                series < 0.5,
            ],
            [100, 75, 40, 0],
            default=np.nan,
        ),
        index=series.index,
    )


def score_gross_margin(series: pd.Series) -> pd.Series:
    return pd.Series(
        np.select(
            [
                series >= 0.40,
                (series >= 0.20) & (series < 0.40),
                (series >= 0.0) & (series < 0.20),
                series < 0.0,
            ],
            [100, 75, 40, 0],
            default=np.nan,
        ),
        index=series.index,
    )


def score_operating_margin(series: pd.Series) -> pd.Series:
    return pd.Series(
        np.select(
            [
                series >= 0.15,
                (series >= 0.05) & (series < 0.15),
                (series >= 0.0) & (series < 0.05),
                series < 0.0,
            ],
            [100, 75, 40, 0],
            default=np.nan,
        ),
        index=series.index,
    )


def score_net_margin(series: pd.Series) -> pd.Series:
    return pd.Series(
        np.select(
            [
                series >= 0.10,
                (series >= 0.03) & (series < 0.10),
                (series >= 0.0) & (series < 0.03),
                series < 0.0,
            ],
            [100, 75, 50, 0],
            default=np.nan,
        ),
        index=series.index,
    )


def score_company_age(series: pd.Series) -> pd.Series:
    return pd.Series(
        np.select(
            [
                series >= 5,
                (series >= 3) & (series < 5),
                (series >= 1) & (series < 3),
                series < 1,
            ],
            [100, 75, 50, 25],
            default=np.nan,
        ),
        index=series.index,
    )


def score_utilization(series: pd.Series) -> pd.Series:
    return pd.Series(
        np.select(
            [
                (series >= 20) & (series <= 80),
                (series > 80) & (series <= 95),
                (series >= 10) & (series < 20),
                series < 10,
                (series > 95) & (series <= 100),
                series > 100,
            ],
            [100, 75, 60, 40, 25, 0],
            default=np.nan,
        ),
        index=series.index,
    )


def score_delinquency(series: pd.Series) -> pd.Series:
    filled = series.fillna(0)
    return pd.Series(
        np.select(
            [
                filled <= 0,
                (filled > 0) & (filled <= 30),
                (filled > 30) & (filled <= 90),
                filled > 90,
            ],
            [100, 60, 25, 0],
            default=np.nan,
        ),
        index=series.index,
    )


def compute_weighted_score(frame: pd.DataFrame, weights: dict[str, int]) -> tuple[pd.Series, pd.Series]:
    score_frame = frame[list(weights)]
    weight_series = pd.Series(weights)
    available_weight = score_frame.notna().mul(weight_series, axis=1).sum(axis=1)
    weighted_sum = score_frame.fillna(0).mul(weight_series, axis=1).sum(axis=1)
    score = (weighted_sum / available_weight).where(available_weight >= 50)
    return score, available_weight


def map_risk_rating(score: pd.Series) -> pd.Series:
    rating = np.select(
        [
            score >= 80,
            (score >= 65) & (score < 80),
            (score >= 50) & (score < 65),
            (score >= 35) & (score < 50),
            score < 35,
        ],
        ["A", "B", "C", "D", "E"],
        default="Insufficient Data",
    )
    return pd.Series(rating, index=score.index).where(score.notna(), "Insufficient Data")


def build_lifecycle_group(frame: pd.DataFrame) -> pd.Series:
    ordered = frame.sort_values(["customer_id", "ref_date"])

    def classify(group: pd.DataFrame) -> str:
        statuses = group["is_active"].tolist()
        if all(statuses):
            return "Always Active"
        if not any(statuses):
            return "Never Active"
        if (not statuses[0]) and statuses[-1]:
            return "Activated Later"
        return "Mixed/Deactivated"

    return ordered.groupby("customer_id").apply(classify)


def determine_policy(row: pd.Series) -> pd.Series:
    rating = row["risk_rating"]
    underwriting_limit = row["underwriting_limit"]
    current_limit = row["credit_limit"] if pd.notna(row["credit_limit"]) else 0.0
    balance = row["balance"] if pd.notna(row["balance"]) else 0.0
    dq_days = row["dq_days"] if pd.notna(row["dq_days"]) else 0.0
    utilization = row["utilization_pct"]
    healthy_utilization = pd.notna(utilization) and 20 <= utilization <= 80
    clean_payment = dq_days <= 0

    if rating == "Insufficient Data":
        return pd.Series(["Request More Data", underwriting_limit])

    if bool(row["is_active"]):
        if rating == "A" and clean_payment and healthy_utilization and current_limit > 0:
            return pd.Series(["Increase Limit +30%", current_limit * 1.30])
        if rating == "B" and clean_payment and healthy_utilization and current_limit > 0:
            return pd.Series(["Increase Limit +15%", current_limit * 1.15])
        if rating == "C":
            held_limit = current_limit if current_limit > 0 else underwriting_limit
            return pd.Series(["Manual Review / Hold", held_limit])
        if rating == "D":
            return pd.Series(["Reduce Limit -25% and Watch", current_limit * 0.75])
        if rating == "E":
            return pd.Series(["Freeze Spend / Collections", max(balance, 0.0)])
        held_limit = current_limit if current_limit > 0 else underwriting_limit
        return pd.Series(["Hold and Monitor Monthly", held_limit])

    if rating == "A":
        return pd.Series(["Approve up to Recommended Limit", underwriting_limit])
    if rating == "B":
        return pd.Series(["Approve with Moderate Limit", underwriting_limit])
    if rating == "C":
        return pd.Series(["Manual Review and Capped Limit", underwriting_limit])
    if rating == "D":
        return pd.Series(["Decline Now / Revisit Later", underwriting_limit])
    return pd.Series(["Decline or Freeze", 0.0])


def latest_customer_snapshot(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame
    return (
        frame.sort_values(["customer_id", "ref_date"])
        .groupby("customer_id", as_index=False)
        .tail(1)
        .sort_values(["customer_id", "ref_date"])
    )


def prepare_dataframe(frame: pd.DataFrame) -> pd.DataFrame:
    data = frame.copy()
    data["ref_date"] = pd.to_datetime(data["ref_date"], errors="coerce")
    data["incorporation_year"] = pd.to_datetime(data["incorporation_year"], errors="coerce")
    for column in NUMERIC_COLUMNS:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data["industry_clean"] = data["industrycategory"].fillna("").replace("", "Unknown")
    data["region_bucket"] = data["addresspostalcode"].apply(assign_region_bucket)
    data["company_age_years"] = (data["ref_date"] - data["incorporation_year"]).dt.days / 365.25
    data.loc[data["company_age_years"] < 0, "company_age_years"] = np.nan
    data["ref_month"] = data["ref_date"].dt.to_period("M").astype(str)

    first_seen_date = data.groupby("customer_id")["ref_date"].transform("min")
    first_active_lookup = data.loc[data["is_active"]].groupby("customer_id")["ref_date"].min()
    data["first_seen_date"] = first_seen_date
    data["first_active_date"] = data["customer_id"].map(first_active_lookup)
    data["activation_lead_days"] = (data["first_active_date"] - data["first_seen_date"]).dt.days

    lifecycle_lookup = build_lifecycle_group(data)
    data["lifecycle_group"] = data["customer_id"].map(lifecycle_lookup)

    debt_available = data[["monthly_cc_debt_repayment", "monthly_non_cc_debt_repayment"]].notna().any(axis=1)
    data["total_monthly_debt"] = data[
        ["monthly_cc_debt_repayment", "monthly_non_cc_debt_repayment"]
    ].fillna(0).sum(axis=1)
    data.loc[~debt_available, "total_monthly_debt"] = np.nan

    data["utilization_pct"] = np.where(
        data["credit_limit"] > 0,
        (data["balance"] / data["credit_limit"]) * 100,
        np.nan,
    )
    data["cash_coverage_ratio"] = np.where(
        data["total_monthly_debt"] > 0,
        data["cash_avg_l3m"] / data["total_monthly_debt"],
        np.nan,
    )

    transaction_volume = data["transaction_volume"].fillna(0)
    fees_volume = data["fees_volume"].fillna(0)
    reward_points = data["rewardpoints"].fillna(0)
    delinquent_balance = data["delinquent_balance"].fillna(0)

    data["interchange_revenue"] = transaction_volume * 0.0225
    data["rewards_cost"] = reward_points * 0.01
    data["observed_net_contribution"] = (
        data["interchange_revenue"] + fees_volume - data["rewards_cost"]
    )

    dq_days = data["dq_days"].fillna(0)
    data["delinquency_bucket"] = np.select(
        [
            dq_days <= 0,
            (dq_days > 0) & (dq_days <= 30),
            (dq_days > 30) & (dq_days <= 90),
            (dq_days > 90) & (dq_days <= 180),
            dq_days > 180,
        ],
        ["Current", "1-30", "31-90", "91-180", "180+"],
        default="Current",
    )
    data["stress_expected_loss"] = delinquent_balance * data["delinquency_bucket"].map(DELINQUENCY_HAIRCUTS)
    data["risk_adjusted_contribution"] = data["observed_net_contribution"] - data["stress_expected_loss"]

    for column in WINSORIZED_COLUMNS:
        data[f"{column}_win"] = winsorize_series(data[column])

    data["cash_avg_score"] = percentile_score_by_month(data, "cash_avg_l3m_win")
    data["revenue_score"] = percentile_score_by_month(data, "revenue_l3m_win")
    data["transaction_volume_score"] = percentile_score_by_month(data, "transaction_volume_win")
    data["monthly_cc_debt_score"] = percentile_score_by_month(data, "monthly_cc_debt_repayment_win")

    data["current_ratio_score"] = score_current_ratio(data["current_ratio_win"])
    data["quick_ratio_score"] = score_quick_ratio(data["quick_ratio_win"])
    data["gross_margin_score"] = score_gross_margin(data["gross_margin_win"])
    data["operating_margin_score"] = score_operating_margin(data["operating_margin_win"])
    data["net_margin_score"] = score_net_margin(data["net_margin_win"])
    data["company_age_score"] = score_company_age(data["company_age_years"])
    data["utilization_score"] = score_utilization(data["utilization_pct_win"])
    data["delinquency_score"] = score_delinquency(data["dq_days"])

    applicant_score, applicant_weight = compute_weighted_score(data, APPLICANT_WEIGHTS)
    active_score, active_weight = compute_weighted_score(data, ACTIVE_WEIGHTS)
    data["applicant_score"] = applicant_score
    data["applicant_available_weight"] = applicant_weight
    data["active_score"] = active_score
    data["active_available_weight"] = active_weight
    data["scorecard_type"] = np.where(data["is_active"], "Active Portfolio", "Applicant / Inactive")
    data["risk_score"] = np.where(data["is_active"], data["active_score"], data["applicant_score"])
    data["available_score_weight"] = np.where(
        data["is_active"], data["active_available_weight"], data["applicant_available_weight"]
    )
    data["risk_rating"] = map_risk_rating(data["risk_score"])
    data["rating_factor"] = data["risk_rating"].map(RATING_FACTORS).fillna(0.0)

    limit_candidates = pd.concat(
        [data["cash_avg_l3m"] * 0.25, data["revenue_l3m"] * 0.08],
        axis=1,
    )
    data["base_limit_formula"] = limit_candidates.min(axis=1, skipna=True).clip(lower=0)
    data["underwriting_limit"] = (data["base_limit_formula"] * data["rating_factor"]).clip(lower=0)

    policy_frame = data.apply(determine_policy, axis=1)
    policy_frame.columns = ["policy_action", "recommended_limit"]
    data[["policy_action", "recommended_limit"]] = policy_frame
    data["recommended_limit"] = data["recommended_limit"].clip(lower=0)
    data["recommended_limit_gap"] = data["recommended_limit"] - data["credit_limit"].fillna(0)

    return data.sort_values(["customer_id", "ref_date"]).reset_index(drop=True)


def load_prepared_data(data_path: str | Path = DATA_PATH) -> pd.DataFrame:
    raw_frame = pd.read_csv(data_path, sep="\t", dtype={"addresspostalcode": "string"})
    return prepare_dataframe(raw_frame)
