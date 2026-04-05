# Prompt Portfolio for the Parker Assignment


## Prompt 1: End-to-End Assignment Strategy and Dashboard Build



```text
You are a senior financial associate with 15 years of experience in financial analysis, portfolio optimization, and risk strategy. You are highly technical, business-minded, and skilled at solving real-world financial problems using data and AI.

I am working on an assignment for Parker for a Data Analyst 1 role. I want to demonstrate not only strong analysis, but also creativity, technical thinking, and the ability to build a useful business-facing dashboard.

I have been given the following assignment and a TSV data file. Please do the following in a structured way:

1. Analyze the assignment in depth.
2. Review all columns in the dataset and explain what each field likely means and how it can be used.
3. Suggest multiple ways to solve the problem, with pros and cons for each approach.
4. Recommend the best approach for the assignment and explain why.
5. Keep all assignment objectives in mind and answer them one by one.
6. Plan the workflow clearly before writing code.
7. Then build the solution and dashboard.

Assignment:
The objective of this task is to provide insights into the portfolio of Slampex Credit Cards and develop a strategy to improve approvals and reduce losses. Slampex provides credit cards to its business customers, which are a combination of traditional statement terms and rolling terms. The credit duration spans from 1 day to up to 90 days.

You have been provided with a monthly snapshot of a sample of Slampex customers and applicants, across one year. For each month and each company, you have a set of financial, demographic, transaction, and delinquency information.

Objectives:
1. Create a basic portfolio monitoring dashboard that shows insights and trends in the portfolio over time.
2. Come up with a risk rating system and a credit policy for Slampex.
3. Apply your rating methodology to the portfolio to show the risk composition of customers in the provided data.
4. Propose actions that you would take to improve the approval rate, improve portfolio health, and reduce losses.
5. Propose any other opportunities or risks for the business that may be surfaced by the data.

Important notes:
1. `is_active` is true if the customer had an active credit limit, and false if the customer was not onboarded or was deactivated.
2. The term portfolio corresponds only to customers who are not applicants, but may have some kind of established relationship with Slampex.
3. Slampex Card offers reward points on transactions with a credit period of 15 days or less. For longer terms, they charge a fee. One reward point is equal to one cent. Slampex earns a flat interchange fee of 2.25% per transaction.
4. You may make reasonable assumptions, but clearly highlight them.

Dashboard requirements:
- I want to view one customer at a time as well as the full portfolio.
- I want filters for:
  - industry
  - unique customer
  - address region (create region buckets automatically)
  - active/inactive status
  - an `All` option for every filter
- I want graphs, pie charts, donut charts, and circular composition charts for different types of borrowers.
- I want sorting and filtering on important data columns and categories.

I specifically want the dashboard to include the following charts:
1. Current ratio and quick ratio
2. Credit limit and balance over time in one chart
3. Cash average for the last 3 months and revenue for the last 3 months
4. Gross margin, operating margin, and net margin
5. Reward points
6. Delinquent balance and delinquency days

Use the best possible visualization style and presentation logic, but always keep the assignment objectives in mind.

I also want you to evaluate whether the following approaches can be incorporated:

1. Real-Time Cash Flow Underwriting Model (Brex / Ramp style)
Use fields such as:
- `cash_avg_l3m`
- `revenue_l3m`
- `current_ratio`
- `quick_ratio`

2. Dynamic Credit Limit Management (Stripe style)
Use fields such as:
- `monthly_non_cc_debt_repayment`
- `credit_limit`
- `balance`
- `dq_days`

3. Risk-Adjusted Unit Economics (Capital One / Amex style)
Use fields such as:
- `transaction_volume`
- `fees_volume`
- `rewardpoints`
- `delinquent_balance`

Please start by thinking through the problem, analyzing the data structure, and proposing the best solution path before implementation.
```

## Prompt 2: Aggregation Methodology Review


```text
Please review the aggregation logic used in the dashboard and determine which metrics should use sum, average, or median.

Do not treat every chart the same way. Analyze the nature of each column and recommend the correct aggregation based on financial meaning.

For example:
- exposure measures may need one treatment
- ratio and margin measures may need another
- customer-scale financial fields may need another
- delinquency fields may need special treatment

I want a clear explanation for each chart so I can defend the methodology in an interview.

After analyzing the logic, update the dashboard, documentation, and submission files so the methodology is consistent everywhere.
```

## Prompt 3: Data Reconciliation and Validation


```text
I am seeing a mismatch between the dashboard values and the source data. Please investigate the exact reason for the discrepancy.

For a selected month, compare:
1. the raw source data values
2. the dashboard chart values
3. any transformed or winsorized values used in the pipeline

Then explain clearly:
- whether rows are being excluded
- whether nulls are being handled differently
- whether winsorization or clipping is changing the chart values
- which number is mathematically correct for the chosen methodology

Please fix the code if needed and make sure the dashboard logic, documentation, and displayed methodology are all aligned.
```


