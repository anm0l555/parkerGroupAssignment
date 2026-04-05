# Assignment Objectives: Answers And Solution Mapping

## Objective 1: Create a basic portfolio monitoring dashboard that shows insights and trends in the portfolio over time
### Answer
I built a multi-tab Streamlit dashboard that tracks the portfolio across time from four angles:

- portfolio composition
- financial health
- risk and policy action
- individual customer drilldown

The dashboard includes time-series charts for liquidity, exposure, balance, margins, reward economics, delinquency, customer activation, and rating migration. For the portfolio views, the financial charts now use monthly averages so the visuals reflect the average visible customer instead of total book size. It also includes tables and donut charts to summarize the latest visible state of the portfolio.

### How the solution addresses the objective
- Uses a monthly tape across 11 periods
- Supports portfolio-wide and filtered analysis
- Shows both trends and latest-state composition
- Uses average-based portfolio trends and count-based composition charts for clearer storytelling
- Allows row-level inspection behind each major chart

## Objective 2: Come up with a risk rating system and a credit policy for Slampex
### Answer
I implemented two rule-based scorecards:

1. An applicant or inactive scorecard for approval decisions
2. An active portfolio scorecard for ongoing limit management

The applicant scorecard emphasizes liquidity, revenue, coverage, margins, and company age. The active scorecard emphasizes delinquency, utilization, transaction activity, repayment, and liquidity.

Scores are mapped into:
- `A`
- `B`
- `C`
- `D`
- `E`
- `Insufficient Data`

The policy engine then maps each rating into a decision such as:
- approve
- approve with moderate limit
- increase limit
- hold
- manual review
- reduce limit
- freeze spend
- request more data

### How the solution addresses the objective
- Aligns scoring logic to available fields rather than forcing one model across all rows
- Separates underwriting logic from portfolio management logic
- Produces consistent, explainable decisions instead of black-box outputs

## Objective 3: Apply your rating methodology to the portfolio to show the risk composition of customers in the provided data
### Answer
The dashboard applies the scorecards to the full tape and visualizes the result through:

- risk rating mix
- risk rating trend over time
- policy action mix
- customer summary table

This shows not only how many customers fall into each rating band, but also what action should be taken for each band.

### How the solution addresses the objective
- Scores every row using the relevant scorecard
- Maps scores to ratings and policy actions
- Makes composition visible through donut charts, trend charts, and tables

## Objective 4: Propose actions that you would take to improve the approval rate and the health of the portfolio, and to reduce losses
### Answer
I would take five actions:

1. Only giving credit limits for a shorter period and huge amount to those whose deliquent days are least as well as least deliquent balance.
2. Offering limit to those who are not utilising more than 50 % credit limit over months and also paying dues on time.
3.Create a fast-track underwriting lane for high-liquidity applicants using cash-flow signals.
4. Approve or expand limits for `A` and `B` customers with clean delinquency and healthy utilization.
5. Hold `C` customers under monthly monitoring and manual review.
6. Reduce limits for `D` customers and freeze `E` customers until risk is resolved.
7. Introduce early-warning triggers combining rising utilization, weakening liquidity, and emerging delinquency.

### How the solution addresses the objective
- The applicant scorecard improves approvals by using cash and revenue instead of waiting for full traditional history
- The active scorecard supports dynamic limit management
- The delinquency stress logic turns raw delinquency into expected-loss thinking
- The risk-adjusted contribution view shows where profitable growth is worth pursuing and where it is not

## Objective 5: Propose any other opportunities or risks for the business that may be surfaced by the data
### Answer
The data surfaces both strategic opportunity and operational risk.

### Opportunities
- A real inactive-to-active conversion path exists in the tape
- Dynamic limit expansion can increase spend and interchange on healthy accounts
- Risk-adjusted profitability can prevent over-penalizing valuable customers with small operational slippage

### Risks
- Data completeness is a major issue because a large share of customers cannot be fully scored
- Industry and geography gaps reduce segmentation quality
- Profitability fields such as rewards and delinquency are sparse, so economics should be treated directionally

### How the solution addresses the objective
- Makes missingness visible through `Insufficient Data` outcomes
- Highlights conversion as a measurable business process
- Separates raw contribution from risk-adjusted contribution so growth decisions are more grounded
