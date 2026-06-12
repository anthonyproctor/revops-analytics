# RevOps Analytics: dbt + DuckDB pipeline

An end to end analytics engineering project that models a B2B SaaS revenue
operations dataset: raw CRM style exports cleaned and tested with dbt, then
shaped into revenue operations marts (rep quota attainment, pipeline funnel,
opportunity fact). Built to demonstrate the modern analyst stack (SQL, dbt data
modeling, testing, DuckDB) on a realistic sales dataset.

> Note on the data: the dataset is **synthetic and fully reproducible** (a
> seeded generator, no real or proprietary records). It is built to mirror the
> shape of a real CRM opportunity export so the modeling and metrics are
> realistic, not the records themselves.

## What this demonstrates

- **SQL data modeling**: staging models that clean and type raw exports, then
  marts that aggregate to business questions.
- **dbt**: `ref`-based DAG, seeds, schema tests, `dbt_utils`, view vs table
  materializations, sources and documentation.
- **Data quality testing**: 21 tests (unique, not_null, relationships,
  accepted_values, accepted_range) that all pass on build.
- **RevOps domain**: quota attainment, win rate, sales cycle, pipeline funnel,
  and segment / lead source performance.

## Stack

| Layer | Tool |
|---|---|
| Warehouse | DuckDB (local, zero ops) |
| Transformation | dbt (dbt-duckdb adapter) |
| Source data | Python generator (synthetic CRM export) |
| Tests / docs | dbt tests + dbt docs |

## Architecture

```
raw_*.csv (seeds)          staging (views)              marts (tables)
-----------------          --------------               --------------
raw_accounts        -->    stg_accounts        -->
raw_reps            -->    stg_reps            -->   fct_opportunities
raw_opportunities   -->    stg_opportunities   -->   mart_rep_attainment
raw_quotas          -->    stg_quotas          -->   mart_pipeline_funnel
```

- **staging/**: one model per source, cleans and casts types, normalizes
  booleans, derives sales cycle days. Materialized as views.
- **marts/fct_opportunities**: one analysis ready row per opportunity, enriched
  with account and rep attributes. Win / loss / open pipeline amounts split out.
- **marts/mart_rep_attainment**: won ARR vs quota per rep per fiscal quarter,
  with attainment %, win rate, and average won sales cycle.
- **marts/mart_pipeline_funnel**: conversion and pipeline health by segment and
  lead source (win rate, average deal size, cycle, open pipeline).

## Sample findings

From the generated dataset (3,200 opportunities across 24 reps, 8 quarters):

- **$39.7M** closed won ARR, **28.7%** overall win rate, **$13.0M** open pipeline.
- A clean inverse between deal size and conversion: **Enterprise** drives the most
  revenue (**$22.7M** won) but converts lowest (**19.8%**) and slowest (**159 day**
  sales cycle), while **SMB** converts highest (**32.9%**) and closes in **~37 days**.
- **Inbound** is the largest source by won ARR (**$12.4M**), but **Event** and
  **Outbound** convert at higher rates (~31% and ~30%).
- Quota attainment is realistic: median **80%**, with **21%** of rep quarters
  hitting quota.

## Run it

```bash
python3 -m venv .venv && ./.venv/bin/pip install dbt-duckdb
./.venv/bin/python generate_data.py          # build the synthetic seeds
cd dbt && export DBT_PROFILES_DIR="$PWD"
../.venv/bin/dbt deps
../.venv/bin/dbt seed --full-refresh
../.venv/bin/dbt build                        # run models + tests
../.venv/bin/dbt docs generate && ../.venv/bin/dbt docs serve   # lineage + docs
```

## Repository layout

```
generate_data.py            synthetic CRM export generator (seeded)
dbt/
  dbt_project.yml
  packages.yml              dbt_utils
  seeds/                    raw_*.csv (generated)
  models/
    staging/                stg_*.sql + tests
    marts/                  fct_opportunities, mart_rep_attainment, mart_pipeline_funnel
```
