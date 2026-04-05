# Slampex Portfolio Risk & Growth Memo

## Executive Summary
Slampex is running a portfolio with two very different operating needs inside one dataset: underwriting a large inactive or applicant pool, and managing a much smaller live credit portfolio. The sample covers `41,914` monthly rows, `4,811` unique companies, and `11` monthly snapshots from March 2025 through January 2026. Only `813` companies are ever active, while `3,998` never become active in the provided period. That gap is the core opportunity: improve approvals for healthy applicants while tightening live limit management and early-warning controls for weaker accounts.

I evaluated three solution paths:

1. Monitoring-first. Strong for descriptive reporting, but too passive for the assignment.
2. Balanced hybrid. Selected. Combines portfolio monitoring, rule-based underwriting, dynamic limit management, and a profitability lens.
3. Profitability-first. Attractive conceptually, but the overlap of fee, reward, and delinquency fields is too sparse to support a pure CLV-style framework on its own.

## Data Shape And Practical Constraints
- `149` companies first appear inactive and later activate, which means approval and conversion analysis is genuinely possible in this tape.
- Data coverage is uneven. Financial strength fields such as `cash_avg_l3m` and `revenue_l3m` are materially more available than delinquency and reward economics.
- `727` rows contain delinquency observations and `916` rows contain reward point observations, so profitability and loss views should be treated as directional, not as a full lifetime value model.
- In the latest visible customer snapshot, roughly two-thirds of companies fall into `Insufficient Data` under the scorecard rules. That is not a model failure; it is a direct signal that data completeness itself is one of Slampex's biggest operating risks.
- Industry is missing on a meaningful share of rows, so dashboard views standardize blanks to `Unknown`.
- Postal data is mixed quality, so regional analysis is presented as a heuristic operating view rather than a regulatory geography.

## Objective 1: Portfolio Monitoring Dashboard
The dashboard is built in Streamlit with four tabs:

1. `Portfolio Overview`
2. `Financial Health`
3. `Risk & Policy`
4. `Customer Drilldown`

Global filters support `All` or filtered views by:
- customer
- industry
- region
- active status
- risk rating
- reference date range

The dashboard includes:
- Active vs inactive portfolio trend
- First-time activation trend
- Donut charts for risk rating, lifecycle, and policy action
- Average current ratio and quick ratio trend
- Average credit limit and average balance trend
- Average cash and revenue trend
- Average gross, operating, and net margin trend
- Average reward points trend
- Average delinquent balance and average DQ day trend among delinquent rows
- Sortable customer and segment tables

For portfolio charting, I use winsorized averages for financial and exposure measures and counts for composition views. This is a presentation choice intended to reduce the impact of extreme outliers in the displayed trends while still leaving the raw monthly records available in drilldown. Customer drilldown views continue to show raw monthly values.

## Objective 2: Risk Rating System And Credit Policy
I implemented two scorecards so the methodology matches the dataset:

- Applicant / inactive scorecard for underwriting and approval decisions
- Active portfolio scorecard for live exposure management

### Applicant / Inactive Scorecard
Weights:
- `cash_avg_l3m`: 25%
- `revenue_l3m`: 20%
- `current_ratio`: 15%
- `quick_ratio`: 10%
- `gross_margin`: 10%
- `operating_margin`: 10%
- `net_margin`: 5%
- `company_age_years`: 5%

### Active Portfolio Scorecard
Weights:
- `delinquency_score`: 20%
- `utilization_score`: 15%
- `transaction_volume`: 15%
- `cash_avg_l3m`: 15%
- `revenue_l3m`: 10%
- `current_ratio`: 10%
- `quick_ratio`: 5%
- `monthly_cc_debt_repayment`: 10%

### Ratings
- `A`: 80 to 100
- `B`: 65 to 79
- `C`: 50 to 64
- `D`: 35 to 49
- `E`: below 35
- `Insufficient Data`: less than 50% of score weight available

### Policy Actions
- `A`: approve or increase up to 30%
- `B`: approve or increase up to 15%
- `C`: manual review, capped limit, monthly monitoring
- `D`: decline new approval or reduce existing limit by 25%
- `E`: decline or freeze, then focus on resolution

## Objective 3: Risk Composition Of The Portfolio
The dashboard surfaces portfolio composition in three ways:

- Risk rating mix
- Lifecycle mix: `Always Active`, `Activated Later`, `Never Active`, `Mixed/Deactivated`
- Policy mix based on the live recommendation engine

This makes the risk picture actionable. Instead of just showing “good” and “bad” customers, the dashboard shows how much of the population is ready for approval, ready for limit expansion, stuck in manual review, or ready for contraction or collections treatment.

## Objective 4: Improve Approval Rate, Health, And Losses
### Improve Approval Rate
- Create a cash-flow underwriting lane using `cash_avg_l3m`, `revenue_l3m`, `current_ratio`, and `quick_ratio`.
- Use the rule-based initial limit formula `min(25% of cash_avg_l3m, 8% of revenue_l3m)` and then scale it by risk rating.
- Fast-track `A` and `B` inactive applicants that have strong liquidity but limited historical credit footprint.

### Improve Portfolio Health
- Expand limits for active `A` and `B` customers only when delinquency is clean and utilization is healthy.
- Hold `C` customers flat and monitor monthly for trend deterioration.
- Reduce exposure for `D` customers and freeze `E` accounts until balance resolution.

### Reduce Losses
- Use delinquency buckets and stress haircuts to move from descriptive delinquency to expected-loss thinking.
- Trigger intervention as soon as a customer leaves `Current`, instead of waiting for severe delinquency.
- Monitor rising utilization and weakening liquidity together, because that combination often precedes loss emergence.

## Objective 5: Additional Opportunities And Risks
### Opportunities
- A real conversion opportunity exists because some customers clearly move from inactive to active over time.
- Dynamic limit management can increase interchange revenue on the healthiest active accounts.
- Risk-adjusted profitability helps prevent overreacting to small operational delays from otherwise valuable customers.

### Risks
- Sparse delinquency and reward data means reported profitability is a directional operating view, not a full accounting P&L.
- Missing industry and geography fields make segmentation less reliable and create avoidable operational blind spots.
- A single blunt approval policy would either reject too many healthy applicants or overexpose Slampex to weaker names.

## How The Fintech Approaches Are Used
### 1. Real-Time Cash Flow Underwriting
Implemented directly in the applicant scorecard and initial limit recommendation. This is the strongest fit for increasing approvals safely.

### 2. Dynamic Credit Limit Management
Implemented through the active portfolio scorecard and policy engine. Limits are expanded, held, reduced, or frozen based on recent condition.

### 3. Risk-Adjusted Unit Economics
Implemented as a decision lens rather than a full CLV model. The dashboard shows:
- observed net contribution
- stress expected loss
- risk-adjusted contribution

In the industry comparison chart, these are shown as average customer economics by industry rather than total segment economics so that large segments do not dominate the visual purely because of size.

## Key Assumptions
- Missing delinquency fields are treated as no observed delinquency only for aggregate profitability logic.
- Winsorization at the 1st and 99th percentiles is used to reduce distortion inside the score construction logic and the portfolio display charts.
- Portfolio charts use averages for financial and exposure measures, while composition charts use customer counts.
- Reward points are valued at `$0.01` each, per the assignment.
- Delinquent balance is treated as exposed balance rather than a confirmed write-off, so expected loss is estimated through delinquency haircuts.
