# Tableau Public version: build and publish guide

This reproduces the web dashboard in Tableau Public so you have the Tableau
keyword and a Tableau Public profile link. The data is already exported and
Tableau ready in this folder. Publishing happens in the Tableau Public desktop
app under your account (there is no API for free Tableau Public accounts), so
this is a guided ~30 minute build, not an automated one.

## What you need
- **Tableau Public (Desktop), free**: https://www.tableau.com/products/public/download
- A **free Tableau Public account**: https://public.tableau.com (sign up)

## Data (in this folder)
- `fct_opportunities.csv` (3,200 rows): the grain level opportunity fact. Use as
  the primary source. Tableau aggregates from this natively.
- `rep_attainment.csv` (188 rows): rep quota attainment per quarter, for the
  attainment KPIs and the top-reps sheet.

## Step 1: connect
1. Open Tableau Public, Connect to Text file, choose `fct_opportunities.csv`.
2. Add a second connection, Text file, `rep_attainment.csv` (keep it as a
   separate data source; you will only use it for two views).

## Step 2: calculated fields (on the fct_opportunities source)
Create these (Analysis menu, Create Calculated Field):
- **Won ARR** = `SUM([Won Amount])`
- **Open Pipeline** = `SUM([Open Pipeline Amount])`
- **Closed Won Count** = `SUM(IF [Is Won] THEN 1 ELSE 0 END)`
- **Closed Count** = `SUM(IF [Is Closed] THEN 1 ELSE 0 END)`
- **Win Rate** = `[Closed Won Count] / [Closed Count]`  (format as percentage)
- **Avg Won Deal** = `AVG(IF [Is Won] THEN [Amount] END)`
- **Avg Won Cycle** = `AVG(IF [Is Won] THEN [Sales Cycle Days] END)`

On the rep_attainment source:
- **Median Attainment** = `MEDIAN([Quota Attainment])`
- **Pct Hit Quota** = `AVG(IF [Hit Quota] THEN 1.0 ELSE 0 END)`  (format as percentage)

## Step 3: build the sheets (match the web dashboard)
1. **KPI tiles** (one sheet each, or text tiles): Won ARR, Win Rate, Open
   Pipeline (from fct); Median Attainment, Pct Hit Quota (from rep_attainment).
2. **Won ARR by quarter**: Columns `Fiscal Quarter`, Rows `Won ARR`, bar.
   Filter `Fiscal Quarter` to exclude any value after `2025-Q4`.
3. **Won ARR by segment**: Columns `Segment`, Rows `Won ARR`, color by `Segment`.
4. **Won ARR by lead source**: Columns `Lead Source`, Rows `Won ARR`, sort desc.
5. **Top reps by won ARR**: Rows `Rep Name`, Columns `Won ARR`, sort descending,
   filter to Top 8 by Won ARR.
6. **Segment performance table**: Rows `Segment`; add `Win Rate`, `Won ARR`,
   `Avg Won Deal`, `Avg Won Cycle` as text/columns.

## Step 4: assemble the dashboard
- New Dashboard, drag the KPI tiles across the top, then the four charts in a
  2x2 grid, then the segment table at the bottom.
- Title it "RevOps Analytics". Add a caption: "Synthetic, reproducible dataset.
  Modeled with dbt + DuckDB."

## Step 5: publish to Tableau Public
- Menu: File, Save to Tableau Public As. Sign in to your Tableau Public account.
- Name it "RevOps Analytics". After it saves, Tableau opens the public URL.
- That public URL is your portfolio link. Add it next to the live web dashboard.

## Cross check (your numbers should match these)
- Won ARR ~ $39.7M, Win Rate ~ 28.7%, Open Pipeline ~ $13.0M.
- Enterprise 19.8% win / $22.7M won / 159 day cycle; SMB 32.9% / $6.2M / 37 days.
- Median quota attainment ~ 79.6%, ~21% of rep quarters hit quota.
