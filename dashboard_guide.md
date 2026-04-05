# Dashboard Guide: Slampex Portfolio Risk & Growth Dashboard

## Purpose
This dashboard is designed to help Parker review how Slampex's portfolio is performing over time, how customer risk is being rated, where approvals can be safely expanded, and where limits or collections action should be tightened.

The dashboard is intentionally split into four tabs so the story flows from high-level portfolio monitoring down to individual customer drilldown.

## Global Filters
The filters at the top apply to every tab:

- `Customer`: choose `All` for portfolio view or one company for customer drilldown
- `Industry`: focus on one or many industries
- `Region`: uses a heuristic region bucket from postal code
- `Active Status`: `All`, `Active`, or `Inactive`
- `Risk Rating`: filter to rating bands such as `A`, `B`, `C`, `D`, `E`, or `Insufficient Data`
- `Reference Window`: restrict the month range being analyzed

## Tab 1: Portfolio Overview
This tab answers, “What is happening to the book overall?”

### Portfolio Volume by Status
- Shows the count of customer-month rows split between active customers and inactive or applicant rows
- Useful for understanding the mix between approved book and pipeline

### First-Time Activations
- Shows how many customers first became active in each month
- Useful for identifying whether conversion is happening steadily or in bursts

### Risk Rating Mix
- Donut chart of the latest visible customer snapshot by rating band
- Useful for seeing quality mix in the current filtered population

### Lifecycle Mix
- Donut chart showing `Always Active`, `Activated Later`, `Never Active`, and `Mixed/Deactivated`
- Useful for separating pipeline behavior from live portfolio behavior

### Policy Mix
- Donut chart showing the current recommendation engine output
- Examples: approve, increase limit, hold, reduce, freeze, request more data

### Observed vs Risk-Adjusted Contribution by Industry
- Compares average observed economics with average economics after a delinquency stress haircut
- Useful for identifying industries that look attractive before risk but weaker after adjusting for potential loss

### Segment Summary
- Industry and region level summary table
- Includes customer count, active share, average risk score, observed contribution, risk-adjusted contribution, and delinquent balance

## Tab 2: Financial Health
This tab answers, “How strong are customers financially?”

### Current Ratio vs Quick Ratio
- Shows average liquidity strength over time
- Useful for underwriting quality and early stress detection

### Cash and Revenue Momentum
- Compares average trailing cash average and average trailing-three-month revenue
- Useful for cash-flow underwriting and identifying companies with scale but weak liquidity

### Credit Limit and Balance Over Time
- Shows average exposure extended and average balance used over time
- Useful for utilization and exposure monitoring

### Margin Profile Over Time
- Shows average gross, operating, and net margin together
- Useful for understanding whether revenues are translating into durable profitability

## Tab 3: Risk & Policy
This tab answers, “What action should Slampex take?”

### Reward Points Over Time
- Portfolio view averages reward points
- Can be split by industry or risk rating
- Useful for checking whether reward cost is concentrated in the healthiest segments or being spent inefficiently

### Delinquent Balance and DQ Days
- Shows average delinquent balance and average delinquency severity among delinquent rows
- Useful for understanding both size of exposure and seriousness of delinquency

### Risk Rating Composition Over Time
- Shows how rating mix changes month by month
- Useful for tracking whether the book is improving, worsening, or staying stable

### Customer Summary Table
- One row per customer in the latest visible snapshot
- Includes risk score, risk rating, policy action, recommended limit, utilization, delinquency bucket, and risk-adjusted contribution

## Tab 4: Customer Drilldown
This tab answers, “What is the full story for one customer?”

### Profile Cards
- Industry and region
- Lifecycle and active status
- Risk and policy action
- Current limit and recommended limit

### Customer Risk Score Over Time
- Shows the monthly movement in the selected customer’s risk score
- Useful for explaining whether a recommendation is stable or trend-driven

### Raw Monthly Records
- Displays the underlying monthly rows for the selected customer
- Useful for validation and interview discussion

## Aggregation Rules Used In The Dashboard
These were chosen intentionally by column type:

| Metric | Aggregation | Why |
| --- | --- | --- |
| `current_ratio`, `quick_ratio` | Average | Shows the average visible customer by month |
| `cash_avg_l3m`, `revenue_l3m` | Average | These fields are already customer-scale average style measures, so averaging them is intuitive |
| `gross_margin`, `operating_margin`, `net_margin` | Average | Keeps margin charts consistent with an average-customer storytelling approach |
| `credit_limit`, `balance` | Average | Shows the average exposure profile rather than total book size |
| `rewardpoints` | Average | Shows average reward activity instead of total program size |
| `delinquent_balance` | Average | Shows average delinquent exposure instead of total delinquent book size |
| `dq_days` | Average among delinquent rows | Shows average delinquency severity for rows currently delinquent |
| Mix charts | Latest snapshot count | Each customer should contribute once to composition charts |

The only charts that still use counts are the status trend, activation trend, mix charts, and risk rating composition chart.

Important note:
- The dashboard charts now use winsorized values for portfolio views, so display values will intentionally differ from a raw Excel pivot average on the same rows.
- Raw monthly records are still shown in the drilldown table for auditability.

## Row-Level Traceability
Every major chart now includes an expander labeled `View rows behind ...`.

This allows the reviewer to:
- select a month or category from that chart
- see every row contributing to that slice
- validate the numbers without leaving the dashboard

This is especially useful in an interview because it shows that the dashboard is not only visual, but auditable.

## Dark Mode Compatibility
The dashboard now uses Streamlit theme-aware styling:

- chart backgrounds are transparent instead of hardcoded white
- cards use theme variables instead of fixed light backgrounds
- text inherits the active Streamlit theme

That means the dashboard remains readable in both light mode and dark mode.
