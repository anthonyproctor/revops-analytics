"""
Export the dbt marts from DuckDB into a single JSON the dashboard reads at
build time. Run after `dbt build`. Output: dashboard/public/data.json
"""
import json
from pathlib import Path
import duckdb

ROOT = Path(__file__).parent
con = duckdb.connect(str(ROOT / "dbt" / "revops.duckdb"), read_only=True)


def rows(sql):
    cur = con.sql(sql)
    cols = cur.columns
    return [dict(zip(cols, r)) for r in cur.fetchall()]


kpis = rows("""
    select
        round(sum(won_amount), 0)                                   as won_arr,
        round(sum(open_pipeline_amount), 0)                         as open_pipeline,
        count(*)                                                    as total_opps,
        round(sum(case when is_won then 1 else 0 end) * 1.0
              / nullif(sum(case when is_closed then 1 else 0 end), 0), 3) as win_rate
    from fct_opportunities
""")[0]
att = rows("select round(median(quota_attainment),3) median_attainment, round(avg(case when hit_quota then 1.0 else 0 end),3) pct_hit_quota from mart_rep_attainment")[0]
kpis.update(att)

arr_by_quarter = rows("""
    select fiscal_quarter as quarter, round(sum(won_amount), 0) as won_arr
    from fct_opportunities
    where is_won and fiscal_quarter <= '2025-Q4'
    group by 1 order by 1
""")

segment_perf = rows("""
    select
        segment,
        round(sum(case when is_won then 1 else 0 end) * 1.0
              / nullif(sum(case when is_closed then 1 else 0 end), 0), 3) as win_rate,
        round(sum(won_amount), 0)                       as won_arr,
        round(avg(case when is_won then amount end), 0) as avg_deal,
        round(avg(case when is_won then sales_cycle_days end), 0) as avg_cycle
    from fct_opportunities
    group by 1
    order by won_arr desc
""")

funnel_by_source = rows("""
    select
        lead_source,
        round(sum(won_amount), 0)                  as won_amount,
        round(sum(open_pipeline_amount), 0)        as open_pipeline,
        round(sum(case when is_won then 1 else 0 end) * 1.0
              / nullif(sum(case when is_closed then 1 else 0 end), 0), 3) as win_rate
    from fct_opportunities
    group by 1
    order by won_amount desc
""")

top_reps = rows("""
    select
        rep_name,
        round(sum(won_amount), 0)        as won,
        round(avg(quota_attainment), 3)  as attainment
    from mart_rep_attainment
    group by 1
    order by won desc
    limit 12
""")

data = {
    "kpis": kpis,
    "arr_by_quarter": arr_by_quarter,
    "segment_perf": segment_perf,
    "funnel_by_source": funnel_by_source,
    "top_reps": top_reps,
}

out = ROOT / "dashboard" / "public" / "data.json"
out.write_text(json.dumps(data, indent=2))
print(f"wrote {out}  ({out.stat().st_size} bytes)")
print(json.dumps(kpis, indent=2))
