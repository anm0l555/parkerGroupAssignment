from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from analysis_engine import latest_customer_snapshot, load_prepared_data


PAGE_TITLE = "Slampex Portfolio Risk & Growth Dashboard"
DATA_PATH = Path(__file__).with_name("slampex_data_snapshot_tape.tsv")
CACHE_VERSION = "2026-04-05-winsorized-contribution-v2"
ACCENT_COLORS = {
    "primary": "#0f766e",
    "secondary": "#1d4ed8",
    "warning": "#d97706",
    "danger": "#b91c1c",
    "success": "#15803d",
    "neutral": "#475569",
}
BASE_TABLE_COLUMNS = [
    "customer_id",
    "ref_date",
    "industry_clean",
    "region_bucket",
    "is_active",
    "credit_limit",
    "balance",
    "cash_avg_l3m",
    "revenue_l3m",
    "gross_margin",
    "operating_margin",
    "net_margin",
    "current_ratio",
    "quick_ratio",
    "transaction_volume",
    "fees_volume",
    "rewardpoints",
    "delinquent_balance",
    "dq_days",
    "risk_score",
    "risk_rating",
    "policy_action",
    "recommended_limit",
]
CHART_NOTES = {
    "status_trend": "This view counts customer-month rows, because status is a portfolio volume measure rather than a financial amount.",
    "activations": "This view counts unique customers by first observed active month, which is the right measure for conversion timing.",
    "ratio": {
        "portfolio": "Portfolio ratio views use the winsorized monthly average so extreme outliers do not dominate the displayed trend.",
        "customer": "Customer view shows the raw monthly current and quick ratios for the selected company.",
    },
    "limit_balance": {
        "portfolio": "Credit limit and balance use winsorized monthly averages so the displayed line reflects stabilized exposure per visible row.",
        "customer": "Customer view shows the raw monthly credit limit and balance for the selected company.",
    },
    "cash_revenue": {
        "portfolio": "Cash and revenue use winsorized monthly averages so very large or unusual companies do not overwhelm the portfolio view.",
        "customer": "Customer view shows the raw monthly cash average and trailing-three-month revenue.",
    },
    "margin": {
        "portfolio": "Margin charts use winsorized monthly averages so one extreme positive or negative margin does not distort the displayed portfolio trend.",
        "customer": "Customer view shows the raw monthly gross, operating, and net margins.",
    },
    "reward": {
        "portfolio": "Reward points use winsorized monthly averages so displayed reward activity is less sensitive to unusual spikes or data anomalies.",
        "customer": "Customer view shows the raw monthly reward points earned by the selected company.",
    },
    "delinquency": {
        "portfolio": "Delinquent balance and DQ days use winsorized monthly averages among delinquent rows so the displayed severity is stabilized for outlier cases.",
        "customer": "Customer view shows the raw monthly delinquent balance and DQ days for the selected company.",
    },
    "mix": "Mix charts use the latest visible customer snapshot, so each customer contributes once to the segment count.",
    "profitability": "Observed and risk-adjusted contribution are winsorized before averaging by industry so the displayed economics are not dominated by a few extreme cases.",
    "rating_trend": "Risk rating trend counts unique customers by month and rating band, which is the correct unit for portfolio composition over time.",
}


def apply_theme() -> None:
    st.markdown(
        """
        <style>
            .block-container {
                padding-top: 1.5rem;
                padding-bottom: 2rem;
            }
            .metric-card {
                border: 1px solid var(--primary-color);
                border-radius: 14px;
                padding: 0.75rem 1rem;
                background: var(--secondary-background-color);
                color: var(--text-color);
            }
            .metric-card * {
                color: var(--text-color) !important;
            }
            .methodology-note {
                border-left: 4px solid var(--primary-color);
                padding: 0.75rem 1rem;
                background: var(--secondary-background-color);
                color: var(--text-color);
                border-radius: 8px;
                margin: 0.5rem 0 1rem 0;
            }
            .methodology-note * {
                color: var(--text-color) !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def configure_page() -> None:
    st.set_page_config(page_title=PAGE_TITLE, layout="wide")
    apply_theme()
    st.title(PAGE_TITLE)
    st.caption(
        "Balanced monitoring, underwriting, dynamic limit management, and risk-adjusted portfolio analysis."
    )


@st.cache_data(show_spinner=False)
def get_dashboard_data(data_path: str | Path, cache_version: str) -> pd.DataFrame:
    return load_prepared_data(data_path)


def ensure_display_columns(frame: pd.DataFrame) -> pd.DataFrame:
    data = frame.copy()
    fallback_pairs = {
        "observed_net_contribution_win": "observed_net_contribution",
        "risk_adjusted_contribution_win": "risk_adjusted_contribution",
        "stress_expected_loss_win": "stress_expected_loss",
        "interchange_revenue_win": "interchange_revenue",
        "rewards_cost_win": "rewards_cost",
        "delinquent_balance_win": "delinquent_balance",
        "rewardpoints_win": "rewardpoints",
        "utilization_pct_win": "utilization_pct",
    }
    for target, source in fallback_pairs.items():
        if target not in data.columns and source in data.columns:
            data[target] = data[source]
    return data


def multiselect_with_all(label: str, options: list[str], key: str) -> list[str]:
    all_options = ["All"] + options
    selected = st.multiselect(label, all_options, default=["All"], key=key)
    if not selected or "All" in selected:
        return options
    return selected


def format_figure(fig: go.Figure, title: str | None = None) -> go.Figure:
    fig.update_layout(
        title=title,
        legend_title_text="",
        margin=dict(l=20, r=20, t=50 if title else 20, b=20),
        hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="rgba(148, 163, 184, 0.25)", zeroline=False)
    return fig


def render_plot(fig: go.Figure) -> None:
    st.plotly_chart(fig, use_container_width=True, theme="streamlit")


def get_table_column_config() -> dict[str, object]:
    return {
        "ref_date": st.column_config.DatetimeColumn("ref_date", format="YYYY-MM-DD"),
        "first_active_date": st.column_config.DatetimeColumn("first_active_date", format="YYYY-MM-DD"),
        "is_active": st.column_config.CheckboxColumn("is_active"),
        "active": st.column_config.CheckboxColumn("active"),
        "active_share": st.column_config.NumberColumn("active_share", format="%.1f%%"),
        "credit_limit": st.column_config.NumberColumn("credit_limit", format="$%.0f"),
        "balance": st.column_config.NumberColumn("balance", format="$%.0f"),
        "cash_avg_l3m": st.column_config.NumberColumn("cash_avg_l3m", format="$%.0f"),
        "revenue_l3m": st.column_config.NumberColumn("revenue_l3m", format="$%.0f"),
        "transaction_volume": st.column_config.NumberColumn("transaction_volume", format="$%.0f"),
        "fees_volume": st.column_config.NumberColumn("fees_volume", format="$%.0f"),
        "rewardpoints": st.column_config.NumberColumn("rewardpoints", format="%.0f"),
        "delinquent_balance": st.column_config.NumberColumn("delinquent_balance", format="$%.0f"),
        "observed_net_contribution": st.column_config.NumberColumn("observed_net_contribution", format="$%.0f"),
        "risk_adjusted_contribution": st.column_config.NumberColumn("risk_adjusted_contribution", format="$%.0f"),
        "recommended_limit": st.column_config.NumberColumn("recommended_limit", format="$%.0f"),
        "avg_risk_score": st.column_config.NumberColumn("avg_risk_score", format="%.1f"),
        "risk_score": st.column_config.NumberColumn("risk_score", format="%.1f"),
        "utilization_pct": st.column_config.NumberColumn("utilization_pct", format="%.1f%%"),
        "gross_margin": st.column_config.NumberColumn("gross_margin", format="%.2f"),
        "operating_margin": st.column_config.NumberColumn("operating_margin", format="%.2f"),
        "net_margin": st.column_config.NumberColumn("net_margin", format="%.2f"),
        "current_ratio": st.column_config.NumberColumn("current_ratio", format="%.2f"),
        "quick_ratio": st.column_config.NumberColumn("quick_ratio", format="%.2f"),
        "dq_days": st.column_config.NumberColumn("dq_days", format="%.0f"),
    }


def safe_money(value: object) -> str:
    if pd.isna(value):
        return "$0"
    return f"${float(value):,.0f}"


def format_option(value: object) -> str:
    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d")
    return str(value)


def build_monthly_series(
    frame: pd.DataFrame,
    column: str,
    single_customer_view: bool,
    aggregate: str,
    prefer_winsorized: bool = True,
) -> pd.Series:
    value_column = column
    winsorized_column = f"{column}_win"
    if not single_customer_view and prefer_winsorized and winsorized_column in frame.columns:
        value_column = winsorized_column

    grouped = frame.groupby("ref_date")[value_column]
    if aggregate == "sum":
        return grouped.sum(min_count=1)
    if aggregate == "mean":
        return grouped.mean()
    return grouped.median()


def build_ratio_chart(frame: pd.DataFrame, single_customer_view: bool) -> go.Figure:
    chart_df = pd.DataFrame(
        {
            "ref_date": sorted(frame["ref_date"].dropna().unique()),
            "current_ratio": build_monthly_series(frame, "current_ratio", single_customer_view, "mean").values,
            "quick_ratio": build_monthly_series(frame, "quick_ratio", single_customer_view, "mean").values,
        }
    )
    title = (
        "Current Ratio vs Quick Ratio (Customer Monthly Values)"
        if single_customer_view
        else "Current Ratio vs Quick Ratio (Portfolio Average)"
    )
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=chart_df["ref_date"],
            y=chart_df["current_ratio"],
            mode="lines+markers",
            name="Current Ratio",
            line=dict(color=ACCENT_COLORS["primary"], width=3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=chart_df["ref_date"],
            y=chart_df["quick_ratio"],
            mode="lines+markers",
            name="Quick Ratio",
            line=dict(color=ACCENT_COLORS["secondary"], width=3),
        )
    )
    return format_figure(fig, title)


def build_limit_balance_chart(frame: pd.DataFrame, single_customer_view: bool) -> go.Figure:
    aggregate = "mean"
    chart_df = pd.DataFrame(
        {
            "ref_date": sorted(frame["ref_date"].dropna().unique()),
            "credit_limit": build_monthly_series(frame, "credit_limit", single_customer_view, aggregate).values,
            "balance": build_monthly_series(frame, "balance", single_customer_view, aggregate).values,
        }
    )
    title = (
        "Credit Limit and Balance Over Time (Customer Monthly Values)"
        if single_customer_view
        else "Credit Limit and Balance Over Time (Portfolio Average)"
    )
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            x=chart_df["ref_date"],
            y=chart_df["credit_limit"],
            name="Credit Limit",
            marker_color="rgba(15, 118, 110, 0.7)",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=chart_df["ref_date"],
            y=chart_df["balance"],
            mode="lines+markers",
            name="Balance",
            line=dict(color=ACCENT_COLORS["warning"], width=3),
        ),
        secondary_y=True,
    )
    fig.update_yaxes(title_text="Credit Limit", secondary_y=False)
    fig.update_yaxes(title_text="Balance", secondary_y=True)
    return format_figure(fig, title)


def build_cash_revenue_chart(frame: pd.DataFrame, single_customer_view: bool) -> go.Figure:
    chart_df = pd.DataFrame(
        {
            "ref_date": sorted(frame["ref_date"].dropna().unique()),
            "cash_avg_l3m": build_monthly_series(frame, "cash_avg_l3m", single_customer_view, "mean").values,
            "revenue_l3m": build_monthly_series(frame, "revenue_l3m", single_customer_view, "mean").values,
        }
    )
    title = (
        "Cash and Revenue Momentum (Customer Monthly Values)"
        if single_customer_view
        else "Cash and Revenue Momentum (Portfolio Average)"
    )
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            x=chart_df["ref_date"],
            y=chart_df["revenue_l3m"],
            name="Revenue L3M",
            marker_color="rgba(29, 78, 216, 0.7)",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=chart_df["ref_date"],
            y=chart_df["cash_avg_l3m"],
            mode="lines+markers",
            name="Cash Avg L3M",
            line=dict(color=ACCENT_COLORS["success"], width=3),
        ),
        secondary_y=True,
    )
    fig.update_yaxes(title_text="Revenue L3M", secondary_y=False)
    fig.update_yaxes(title_text="Cash Avg L3M", secondary_y=True)
    return format_figure(fig, title)


def build_margin_chart(frame: pd.DataFrame, single_customer_view: bool) -> go.Figure:
    chart_df = pd.DataFrame(
        {
            "ref_date": sorted(frame["ref_date"].dropna().unique()),
            "gross_margin": build_monthly_series(frame, "gross_margin", single_customer_view, "mean").values,
            "operating_margin": build_monthly_series(
                frame, "operating_margin", single_customer_view, "mean"
            ).values,
            "net_margin": build_monthly_series(frame, "net_margin", single_customer_view, "mean").values,
        }
    )
    title = (
        "Margin Profile Over Time (Customer Monthly Values)"
        if single_customer_view
        else "Margin Profile Over Time (Portfolio Average)"
    )
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=chart_df["ref_date"],
            y=chart_df["gross_margin"],
            mode="lines+markers",
            name="Gross Margin",
            line=dict(color=ACCENT_COLORS["primary"], width=3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=chart_df["ref_date"],
            y=chart_df["operating_margin"],
            mode="lines+markers",
            name="Operating Margin",
            line=dict(color=ACCENT_COLORS["warning"], width=3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=chart_df["ref_date"],
            y=chart_df["net_margin"],
            mode="lines+markers",
            name="Net Margin",
            line=dict(color=ACCENT_COLORS["secondary"], width=3),
        )
    )
    return format_figure(fig, title)


def build_reward_chart(frame: pd.DataFrame, single_customer_view: bool, split_dimension: str) -> go.Figure:
    chart_column = "rewardpoints" if single_customer_view else "rewardpoints_win"
    title = (
        "Reward Points Over Time (Customer Monthly Values)"
        if single_customer_view
        else "Reward Points Over Time (Portfolio Average)"
    )
    if single_customer_view:
        chart_df = (
            frame.groupby("ref_date")[chart_column]
            .mean()
            .rename("rewardpoints")
            .reset_index()
        )
        fig = px.bar(
            chart_df,
            x="ref_date",
            y="rewardpoints",
            labels={"ref_date": "Month", "rewardpoints": "Reward Points"},
            color_discrete_sequence=[ACCENT_COLORS["secondary"]],
        )
        return format_figure(fig, title)

    chart_df = (
        frame.groupby(["ref_date", split_dimension])[chart_column]
        .mean()
        .reset_index()
        .rename(columns={chart_column: "rewardpoints"})
    )
    fig = px.bar(
        chart_df,
        x="ref_date",
        y="rewardpoints",
        color=split_dimension,
        barmode="stack",
        labels={"ref_date": "Month", "rewardpoints": "Reward Points"},
    )
    return format_figure(fig, title)


def build_delinquency_chart(frame: pd.DataFrame, single_customer_view: bool) -> go.Figure:
    balance_aggregate = "mean"
    dq_source = frame if single_customer_view else frame.loc[frame["delinquent_balance"].fillna(0) > 0]
    ordered_dates = sorted(frame["ref_date"].dropna().unique())
    dq_series = build_monthly_series(
        dq_source,
        "dq_days",
        single_customer_view,
        "mean",
        prefer_winsorized=False,
    ).reindex(ordered_dates)
    chart_df = pd.DataFrame(
        {
            "ref_date": ordered_dates,
            "delinquent_balance": build_monthly_series(
                frame,
                "delinquent_balance",
                single_customer_view,
                balance_aggregate,
            ).reindex(ordered_dates).values,
            "dq_days": dq_series.values,
        }
    )
    title = (
        "Delinquent Balance and DQ Days (Customer Monthly Values)"
        if single_customer_view
        else "Delinquent Balance and DQ Days (Portfolio Average)"
    )
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            x=chart_df["ref_date"],
            y=chart_df["delinquent_balance"],
            name="Delinquent Balance",
            marker_color="rgba(185, 28, 28, 0.7)",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=chart_df["ref_date"],
            y=chart_df["dq_days"],
            mode="lines+markers",
            name="DQ Days",
            line=dict(color=ACCENT_COLORS["neutral"], width=3),
        ),
        secondary_y=True,
    )
    fig.update_yaxes(title_text="Delinquent Balance", secondary_y=False)
    fig.update_yaxes(title_text="Days Delinquent", secondary_y=True)
    return format_figure(fig, title)


def build_mix_chart(frame: pd.DataFrame, column: str, title: str) -> go.Figure:
    chart_df = frame[column].fillna("Unknown").value_counts().reset_index()
    chart_df.columns = [column, "count"]
    fig = px.pie(chart_df, names=column, values="count", hole=0.55)
    return format_figure(fig, title)


def build_status_trend(frame: pd.DataFrame) -> go.Figure:
    trend_df = (
        frame.groupby(["ref_date", "is_active"])["customer_id"]
        .count()
        .reset_index(name="customer_rows")
        .assign(status=lambda d: d["is_active"].map({True: "Active", False: "Inactive / Applicant"}))
    )
    fig = px.area(
        trend_df,
        x="ref_date",
        y="customer_rows",
        color="status",
        labels={"ref_date": "Month", "customer_rows": "Customer-Month Rows"},
        color_discrete_map={
            "Active": ACCENT_COLORS["primary"],
            "Inactive / Applicant": ACCENT_COLORS["neutral"],
        },
    )
    return format_figure(fig, "Portfolio Volume by Status (Customer-Month Count)")


def build_new_activations_chart(frame: pd.DataFrame) -> go.Figure:
    activation_df = (
        latest_customer_snapshot(frame)
        .dropna(subset=["first_active_date"])
        .groupby("first_active_date")["customer_id"]
        .nunique()
        .reset_index(name="newly_active_customers")
    )
    activation_df = activation_df.loc[
        activation_df["first_active_date"].between(frame["ref_date"].min(), frame["ref_date"].max())
    ]
    fig = px.bar(
        activation_df,
        x="first_active_date",
        y="newly_active_customers",
        labels={"first_active_date": "First Active Month", "newly_active_customers": "Customers"},
        color_discrete_sequence=[ACCENT_COLORS["warning"]],
    )
    return format_figure(fig, "First-Time Activations (Unique Customer Count)")


def build_profitability_chart(frame: pd.DataFrame) -> go.Figure:
    latest_frame = latest_customer_snapshot(frame)
    segment_df = (
        latest_frame.groupby("industry_clean")[
            ["observed_net_contribution_win", "risk_adjusted_contribution_win"]
        ]
        .mean()
        .reset_index()
        .sort_values("risk_adjusted_contribution_win", ascending=False)
        .head(10)
    )
    melted = segment_df.melt(
        id_vars="industry_clean",
        value_vars=["observed_net_contribution_win", "risk_adjusted_contribution_win"],
        var_name="metric",
        value_name="amount",
    )
    fig = px.bar(
        melted,
        x="industry_clean",
        y="amount",
        color="metric",
        barmode="group",
        labels={"industry_clean": "Industry", "amount": "Contribution"},
        color_discrete_map={
            "observed_net_contribution_win": ACCENT_COLORS["secondary"],
            "risk_adjusted_contribution_win": ACCENT_COLORS["success"],
        },
    )
    return format_figure(fig, "Observed vs Risk-Adjusted Contribution by Industry (Average per Customer)")


def build_rating_trend_chart(frame: pd.DataFrame) -> go.Figure:
    trend_df = (
        frame.groupby(["ref_date", "risk_rating"])["customer_id"]
        .nunique()
        .reset_index(name="customers")
    )
    fig = px.bar(
        trend_df,
        x="ref_date",
        y="customers",
        color="risk_rating",
        barmode="stack",
        labels={"ref_date": "Month", "customers": "Customers"},
    )
    return format_figure(fig, "Risk Rating Composition Over Time (Unique Customer Count)")


def build_customer_summary(frame: pd.DataFrame) -> pd.DataFrame:
    latest_frame = latest_customer_snapshot(frame)
    summary = latest_frame[
        [
            "customer_id",
            "industry_clean",
            "region_bucket",
            "is_active",
            "risk_score",
            "risk_rating",
            "policy_action",
            "recommended_limit",
            "utilization_pct_win",
            "delinquency_bucket",
            "risk_adjusted_contribution_win",
        ]
    ].rename(
        columns={
            "industry_clean": "industry",
            "region_bucket": "region",
            "is_active": "active",
            "utilization_pct_win": "utilization_pct",
            "risk_adjusted_contribution_win": "risk_adjusted_contribution",
        }
    )
    return summary.sort_values(["risk_score", "recommended_limit"], ascending=[False, False])


def build_segment_summary(frame: pd.DataFrame) -> pd.DataFrame:
    latest_frame = latest_customer_snapshot(frame)
    summary = (
        latest_frame.groupby(["industry_clean", "region_bucket"])
        .agg(
            customers=("customer_id", "nunique"),
            active_share=("is_active", "mean"),
            avg_risk_score=("risk_score", "mean"),
            observed_net_contribution=("observed_net_contribution_win", "sum"),
            risk_adjusted_contribution=("risk_adjusted_contribution_win", "sum"),
            delinquent_balance=("delinquent_balance_win", "sum"),
        )
        .reset_index()
        .sort_values("risk_adjusted_contribution", ascending=False)
    )
    summary["active_share"] = summary["active_share"] * 100
    return summary


def render_chart_rows(
    title: str,
    source_frame: pd.DataFrame,
    key_prefix: str,
    *,
    time_column: str | None = "ref_date",
    category_column: str | None = None,
    category_label: str | None = None,
    display_columns: list[str] | None = None,
) -> None:
    with st.expander(f"View rows behind {title}", expanded=False):
        detail = source_frame.copy()
        if detail.empty:
            st.info("No rows are available for this chart under the current filters.")
            return

        if time_column and time_column in detail.columns:
            time_options = sorted(detail[time_column].dropna().unique())
            if time_options:
                selected_time = st.selectbox(
                    "Select time slice",
                    options=time_options,
                    index=len(time_options) - 1,
                    key=f"{key_prefix}_time",
                    format_func=format_option,
                )
                detail = detail.loc[detail[time_column] == selected_time]

        if category_column and category_column in detail.columns:
            category_series = detail[category_column].fillna("Unknown").astype(str)
            category_options = sorted(category_series.unique().tolist())
            if category_options:
                selected_category = st.selectbox(
                    category_label or category_column,
                    options=category_options,
                    index=0,
                    key=f"{key_prefix}_category",
                )
                detail = detail.loc[category_series == selected_category]

        if detail.empty:
            st.info("No rows match the selected chart slice.")
            return

        columns = display_columns or BASE_TABLE_COLUMNS
        visible_columns = [column for column in columns if column in detail.columns]
        sort_columns = [column for column in [time_column, "customer_id"] if column and column in detail.columns]
        if sort_columns:
            detail = detail.sort_values(sort_columns)
        st.caption(f"{len(detail):,} row(s) contribute to this chart slice.")
        st.dataframe(
            detail[visible_columns],
            use_container_width=True,
            height=280,
            column_config=get_table_column_config(),
        )


def render_filters(frame: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns(5)
    customer_options = sorted(frame["customer_id"].dropna().unique().tolist())
    industry_options = sorted(frame["industry_clean"].dropna().unique().tolist())
    region_options = sorted(frame["region_bucket"].dropna().unique().tolist())
    risk_options = sorted(frame["risk_rating"].dropna().unique().tolist())

    with filter_col1:
        selected_customer = st.selectbox("Customer", ["All"] + customer_options, index=0)
    with filter_col2:
        selected_industries = multiselect_with_all("Industry", industry_options, key="industry_filter")
    with filter_col3:
        selected_regions = multiselect_with_all("Region", region_options, key="region_filter")
    with filter_col4:
        active_status = st.selectbox("Active Status", ["All", "Active", "Inactive"], index=0)
    with filter_col5:
        selected_ratings = multiselect_with_all("Risk Rating", risk_options, key="rating_filter")

    min_date = frame["ref_date"].min().date()
    max_date = frame["ref_date"].max().date()
    selected_dates = st.slider(
        "Reference Window",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="YYYY-MM",
    )

    filtered = frame.copy()
    filtered = filtered.loc[filtered["industry_clean"].isin(selected_industries)]
    filtered = filtered.loc[filtered["region_bucket"].isin(selected_regions)]
    filtered = filtered.loc[filtered["risk_rating"].isin(selected_ratings)]
    filtered = filtered.loc[
        filtered["ref_date"].between(pd.Timestamp(selected_dates[0]), pd.Timestamp(selected_dates[1]))
    ]

    if active_status == "Active":
        filtered = filtered.loc[filtered["is_active"]]
    elif active_status == "Inactive":
        filtered = filtered.loc[~filtered["is_active"]]

    if selected_customer != "All":
        filtered = filtered.loc[filtered["customer_id"] == selected_customer]

    return filtered, selected_customer


def render_kpis(frame: pd.DataFrame) -> None:
    latest_frame = latest_customer_snapshot(frame)
    unique_customers = latest_frame["customer_id"].nunique()
    active_share = latest_frame["is_active"].mean() if not latest_frame.empty else 0.0
    avg_risk_score = latest_frame["risk_score"].mean()
    observed_contribution = frame["observed_net_contribution_win"].sum()
    risk_adjusted_contribution = frame["risk_adjusted_contribution_win"].sum()

    kpi_cols = st.columns(5)
    metrics = [
        ("Visible Customers", f"{unique_customers:,}"),
        ("Active Share", f"{active_share:.1%}"),
        ("Avg Risk Score", f"{avg_risk_score:,.1f}" if pd.notna(avg_risk_score) else "N/A"),
        ("Observed Contribution", f"${observed_contribution:,.0f}"),
        ("Risk-Adjusted Contribution", f"${risk_adjusted_contribution:,.0f}"),
    ]
    for column, (label, value) in zip(kpi_cols, metrics):
        with column:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(label, value)
            st.markdown("</div>", unsafe_allow_html=True)


def render_overview_tab(frame: pd.DataFrame) -> None:
    latest_frame = latest_customer_snapshot(frame)

    left_col, right_col = st.columns(2)
    with left_col:
        render_plot(build_status_trend(frame))
        st.caption(CHART_NOTES["status_trend"])
        status_source = frame.assign(
            status=frame["is_active"].map({True: "Active", False: "Inactive / Applicant"})
        )
        render_chart_rows(
            "Portfolio Volume by Status",
            status_source,
            "status_trend",
            category_column="status",
            category_label="Status",
        )
    with right_col:
        render_plot(build_new_activations_chart(frame))
        st.caption(CHART_NOTES["activations"])
        activation_source = latest_frame.dropna(subset=["first_active_date"])
        render_chart_rows(
            "First-Time Activations",
            activation_source,
            "activations",
            time_column="first_active_date",
            display_columns=["customer_id", "first_active_date", "industry_clean", "region_bucket", "risk_rating", "policy_action"],
        )

    donut_col1, donut_col2, donut_col3 = st.columns(3)
    with donut_col1:
        render_plot(build_mix_chart(latest_frame, "risk_rating", "Risk Rating Mix (Latest Visible Customer Count)"))
        st.caption(CHART_NOTES["mix"])
        render_chart_rows(
            "Risk Rating Mix",
            latest_frame,
            "risk_mix",
            time_column=None,
            category_column="risk_rating",
            category_label="Risk Rating",
        )
    with donut_col2:
        render_plot(build_mix_chart(latest_frame, "lifecycle_group", "Lifecycle Mix (Latest Visible Customer Count)"))
        st.caption(CHART_NOTES["mix"])
        render_chart_rows(
            "Lifecycle Mix",
            latest_frame,
            "lifecycle_mix",
            time_column=None,
            category_column="lifecycle_group",
            category_label="Lifecycle Group",
            display_columns=["customer_id", "first_seen_date", "first_active_date", "lifecycle_group", "industry_clean", "region_bucket", "risk_rating", "policy_action"],
        )
    with donut_col3:
        render_plot(build_mix_chart(latest_frame, "policy_action", "Policy Mix (Latest Visible Customer Count)"))
        st.caption(CHART_NOTES["mix"])
        render_chart_rows(
            "Policy Mix",
            latest_frame,
            "policy_mix",
            time_column=None,
            category_column="policy_action",
            category_label="Policy Action",
        )

    chart_col, table_col = st.columns([1.4, 1])
    with chart_col:
        render_plot(build_profitability_chart(frame))
        st.caption(CHART_NOTES["profitability"])
        render_chart_rows(
            "Observed vs Risk-Adjusted Contribution by Industry",
            latest_frame,
            "profitability",
            time_column=None,
            category_column="industry_clean",
            category_label="Industry",
            display_columns=[
                "customer_id",
                "industry_clean",
                "region_bucket",
                "observed_net_contribution",
                "stress_expected_loss",
                "risk_adjusted_contribution",
                "risk_rating",
                "policy_action",
            ],
        )
    with table_col:
        st.subheader("Segment Summary")
        st.dataframe(
            build_segment_summary(frame),
            use_container_width=True,
            height=380,
            column_config=get_table_column_config(),
        )


def render_financial_health_tab(frame: pd.DataFrame, single_customer_view: bool) -> None:
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        render_plot(build_ratio_chart(frame, single_customer_view))
        st.caption(CHART_NOTES["ratio"]["customer" if single_customer_view else "portfolio"])
        render_chart_rows("Current Ratio vs Quick Ratio", frame, "ratio_chart")
    with chart_col2:
        render_plot(build_cash_revenue_chart(frame, single_customer_view))
        st.caption(CHART_NOTES["cash_revenue"]["customer" if single_customer_view else "portfolio"])
        render_chart_rows("Cash and Revenue Momentum", frame, "cash_revenue")

    render_plot(build_limit_balance_chart(frame, single_customer_view))
    st.caption(CHART_NOTES["limit_balance"]["customer" if single_customer_view else "portfolio"])
    render_chart_rows("Credit Limit and Balance Over Time", frame, "limit_balance")

    render_plot(build_margin_chart(frame, single_customer_view))
    st.caption(CHART_NOTES["margin"]["customer" if single_customer_view else "portfolio"])
    render_chart_rows("Margin Profile Over Time", frame, "margin_profile")


def render_risk_policy_tab(frame: pd.DataFrame, single_customer_view: bool) -> None:
    split_dimension = "industry_clean"
    if not single_customer_view:
        split_dimension = st.radio(
            "Split reward points by",
            options=["industry_clean", "risk_rating"],
            index=0,
            horizontal=True,
            format_func=lambda value: "Industry" if value == "industry_clean" else "Risk Rating",
        )

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        render_plot(build_reward_chart(frame, single_customer_view, split_dimension))
        st.caption(CHART_NOTES["reward"]["customer" if single_customer_view else "portfolio"])
        render_chart_rows(
            "Reward Points Over Time",
            frame,
            "reward_points",
            category_column=None if single_customer_view else split_dimension,
            category_label="Industry" if split_dimension == "industry_clean" else "Risk Rating",
        )
    with chart_col2:
        render_plot(build_delinquency_chart(frame, single_customer_view))
        st.caption(CHART_NOTES["delinquency"]["customer" if single_customer_view else "portfolio"])
        delinquency_source = frame if single_customer_view else frame.loc[frame["delinquent_balance"].fillna(0) > 0]
        render_chart_rows(
            "Delinquent Balance and DQ Days",
            delinquency_source,
            "delinquency",
            display_columns=[
                "customer_id",
                "ref_date",
                "industry_clean",
                "region_bucket",
                "delinquent_balance",
                "dq_days",
                "risk_rating",
                "policy_action",
            ],
        )

    render_plot(build_rating_trend_chart(frame))
    st.caption(CHART_NOTES["rating_trend"])
    render_chart_rows(
        "Risk Rating Composition Over Time",
        frame,
        "rating_trend",
        category_column="risk_rating",
        category_label="Risk Rating",
    )

    st.subheader("Customer Summary")
    st.dataframe(
        build_customer_summary(frame),
        use_container_width=True,
        height=420,
        column_config=get_table_column_config(),
    )


def render_customer_drilldown_tab(frame: pd.DataFrame, selected_customer: str) -> None:
    if selected_customer == "All":
        st.info("Select a single customer in the top filter bar to unlock the detailed monthly drilldown.")
        st.dataframe(
            build_customer_summary(frame),
            use_container_width=True,
            height=420,
            column_config=get_table_column_config(),
        )
        return

    latest_row = latest_customer_snapshot(frame).sort_values("ref_date").iloc[-1]
    profile_cols = st.columns(4)
    profile_values = [
        ("Industry / Region", f"{latest_row['industry_clean']} / {latest_row['region_bucket']}"),
        ("Lifecycle / Status", f"{latest_row['lifecycle_group']} / {'Active' if latest_row['is_active'] else 'Inactive'}"),
        ("Risk / Policy", f"{latest_row['risk_rating']} / {latest_row['policy_action']}"),
        ("Limit / Recommended", f"{safe_money(latest_row['credit_limit'])} / {safe_money(latest_row['recommended_limit'])}"),
    ]
    for column, (label, value) in zip(profile_cols, profile_values):
        with column:
            st.metric(label, value)

    score_chart = px.line(
        frame.sort_values("ref_date"),
        x="ref_date",
        y="risk_score",
        markers=True,
        labels={"ref_date": "Month", "risk_score": "Risk Score"},
    )
    render_plot(format_figure(score_chart, "Customer Risk Score Over Time"))
    st.caption("Customer drilldown always uses raw monthly values for the selected company.")

    st.subheader("Raw Monthly Records")
    st.dataframe(
        frame.sort_values("ref_date")[BASE_TABLE_COLUMNS],
        use_container_width=True,
        height=420,
        column_config=get_table_column_config(),
    )


def main() -> None:
    configure_page()
    frame = ensure_display_columns(get_dashboard_data(DATA_PATH, CACHE_VERSION))
    st.markdown(
        """
        <div class="methodology-note">
        The dashboard uses explicit aggregation rules by metric type,
        uses winsorized values for portfolio charts and summary economics except count-based composition views, keeps
        the raw monthly record table for auditability, and includes row-level explorers below charts so every visible
        segment can be traced back to the contributing records.
        </div>
        """,
        unsafe_allow_html=True,
    )

    filtered_frame, selected_customer = render_filters(frame)
    if filtered_frame.empty:
        st.warning("The current filter combination returned no rows. Broaden one or more filters to continue.")
        return

    single_customer_view = selected_customer != "All" and filtered_frame["customer_id"].nunique() == 1
    st.caption(
        f"Showing {len(filtered_frame):,} monthly rows across {filtered_frame['customer_id'].nunique():,} customer(s)."
    )
    render_kpis(filtered_frame)

    overview_tab, financial_tab, risk_tab, customer_tab = st.tabs(
        ["Portfolio Overview", "Financial Health", "Risk & Policy", "Customer Drilldown"]
    )
    with overview_tab:
        render_overview_tab(filtered_frame)
    with financial_tab:
        render_financial_health_tab(filtered_frame, single_customer_view)
    with risk_tab:
        render_risk_policy_tab(filtered_frame, single_customer_view)
    with customer_tab:
        render_customer_drilldown_tab(filtered_frame, selected_customer)


if __name__ == "__main__":
    main()
