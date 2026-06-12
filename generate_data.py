"""
Generate a realistic synthetic B2B SaaS revenue-operations dataset.

This stands in for a CRM export (the kind a RevOps analyst works from). It is
synthetic and deterministic (fixed seed) so the project is fully reproducible
and contains no real or proprietary data. Output: four raw CSVs under dbt/seeds/
that the dbt project then cleans (staging) and models into RevOps marts.

Run:  python generate_data.py
"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 42
random.seed(SEED)

SEEDS_DIR = Path(__file__).parent / "dbt" / "seeds"
SEEDS_DIR.mkdir(parents=True, exist_ok=True)

# ---- reference data -------------------------------------------------------
SEGMENTS = ["SMB", "Mid-Market", "Enterprise"]
SEGMENT_WEIGHTS = [0.55, 0.30, 0.15]
# typical new-ARR deal size band per segment (USD)
SEGMENT_DEAL_BAND = {"SMB": (3_000, 18_000), "Mid-Market": (18_000, 80_000), "Enterprise": (80_000, 400_000)}
# base win rate per segment (enterprise deals close less often, larger)
SEGMENT_WIN_RATE = {"SMB": 0.32, "Mid-Market": 0.26, "Enterprise": 0.20}
# typical sales-cycle length in days per segment
SEGMENT_CYCLE = {"SMB": (14, 60), "Mid-Market": (45, 120), "Enterprise": (90, 240)}
INDUSTRIES = ["Healthcare", "Financial Services", "Manufacturing", "Retail",
              "Technology", "Education", "Logistics", "Energy"]
LEAD_SOURCES = ["Inbound", "Outbound", "Partner", "Event", "Referral"]
REGIONS = ["West", "Central", "East"]
STAGES = ["Prospecting", "Qualification", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]

START = date(2024, 1, 1)
QUARTERS = 8  # 2024 Q1 .. 2025 Q4


def quarter_of(d: date) -> str:
    return f"{d.year}-Q{((d.month - 1) // 3) + 1}"


# ---- reps ------------------------------------------------------------------
reps = []
first = ["Avery", "Jordan", "Riley", "Cameron", "Morgan", "Taylor", "Casey", "Quinn",
         "Drew", "Reese", "Sky", "Devon", "Hayden", "Emerson", "Rowan", "Logan",
         "Parker", "Sawyer", "Blake", "Elliot", "Marlowe", "Shay", "Tatum", "Wren"]
last = ["Nguyen", "Patel", "Garcia", "Cohen", "Okafor", "Larsson", "Rossi", "Kim",
        "Mbeki", "Dubois", "Haddad", "Costa", "Novak", "Ibrahim", "Andersen", "Reyes",
        "Schmidt", "Walsh", "Fischer", "Mori", "Silva", "Volkov", "Adeyemi", "Park"]
for i in range(24):
    seg = random.choices(SEGMENTS, SEGMENT_WEIGHTS)[0]
    reps.append({
        "rep_id": f"R{i+1:03d}",
        "rep_name": f"{first[i]} {last[i]}",
        "region": random.choice(REGIONS),
        "primary_segment": seg,
        "hire_date": (START - timedelta(days=random.randint(30, 1400))).isoformat(),
    })

# ---- accounts --------------------------------------------------------------
accounts = []
for i in range(600):
    seg = random.choices(SEGMENTS, SEGMENT_WEIGHTS)[0]
    accounts.append({
        "account_id": f"A{i+1:04d}",
        "account_name": f"Account {i+1:04d}",
        "segment": seg,
        "industry": random.choice(INDUSTRIES),
        "region": random.choice(REGIONS),
        "employee_count": {"SMB": random.randint(10, 200),
                            "Mid-Market": random.randint(200, 2000),
                            "Enterprise": random.randint(2000, 50000)}[seg],
    })

# ---- quotas (per rep per quarter) -----------------------------------------
quarters = []
d = START
for _ in range(QUARTERS):
    quarters.append(quarter_of(d))
    # advance ~one quarter
    d = (d.replace(day=1) + timedelta(days=95)).replace(day=1)
quarters = sorted(set(quarters))

# quotas are derived from realized performance below (after opportunities) so
# attainment lands in a believable range rather than being flat and arbitrary.
SEGMENT_QUOTA_FLOOR = {"SMB": 60_000, "Mid-Market": 140_000, "Enterprise": 350_000}

# ---- opportunities ---------------------------------------------------------
opps = []
oppn = 0
for _ in range(3200):
    oppn += 1
    acct = random.choice(accounts)
    seg = acct["segment"]
    rep = random.choice([r for r in reps if r["primary_segment"] == seg] or reps)
    created = START + timedelta(days=random.randint(0, 365 * 2 - 30))
    cycle = random.randint(*SEGMENT_CYCLE[seg])
    lo, hi = SEGMENT_DEAL_BAND[seg]
    amount = round(random.uniform(lo, hi), -2)
    won = random.random() < SEGMENT_WIN_RATE[seg]
    # some opps still open (no close yet) near the end of the window
    close_date = created + timedelta(days=cycle)
    is_open = close_date > date(2025, 12, 15) and random.random() < 0.5
    if is_open:
        stage = random.choices(STAGES[:4], [0.30, 0.30, 0.25, 0.15])[0]
        close_date_str = ""
        won_flag = ""
    else:
        stage = "Closed Won" if won else "Closed Lost"
        close_date_str = close_date.isoformat()
        won_flag = "true" if won else "false"
    opps.append({
        "opportunity_id": f"O{oppn:05d}",
        "account_id": acct["account_id"],
        "rep_id": rep["rep_id"],
        "lead_source": random.choices(LEAD_SOURCES, [0.34, 0.28, 0.14, 0.14, 0.10])[0],
        "stage": stage,
        "amount": amount,
        "created_date": created.isoformat(),
        "close_date": close_date_str,
        "fiscal_quarter": quarter_of(close_date if not is_open else created),
        "is_won": won_flag,
        "is_closed": "false" if is_open else "true",
    })

# ---- quotas (derived from realized won ARR per rep per quarter) -------------
# Sum closed-won ARR by rep-quarter, then set quota = won / target_attainment,
# where target ~ N(0.95, 0.22). This yields a realistic attainment spread
# (most reps 0.6-1.4x, a minority over/under) instead of flat arbitrary quotas.
won_by_rep_q = {}
rep_segment = {r["rep_id"]: r["primary_segment"] for r in reps}
for o in opps:
    if o["is_won"] == "true" and o["fiscal_quarter"] in quarters:
        key = (o["rep_id"], o["fiscal_quarter"])
        won_by_rep_q[key] = won_by_rep_q.get(key, 0.0) + o["amount"]

quotas = []
for r in reps:
    for q in quarters:
        won = won_by_rep_q.get((r["rep_id"], q), 0.0)
        floor = SEGMENT_QUOTA_FLOOR[r["primary_segment"]]
        target = min(1.6, max(0.4, random.gauss(0.95, 0.22)))
        quota = max(floor, won / target) if won > 0 else floor
        quotas.append({
            "rep_id": r["rep_id"],
            "fiscal_quarter": q,
            "quota_amount": round(quota, -3),
        })


def write_csv(name, rows):
    path = SEEDS_DIR / name
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"  wrote {path.relative_to(Path(__file__).parent)}  ({len(rows)} rows)")


if __name__ == "__main__":
    print("Generating synthetic RevOps dataset (seed=%d):" % SEED)
    write_csv("raw_reps.csv", reps)
    write_csv("raw_accounts.csv", accounts)
    write_csv("raw_quotas.csv", quotas)
    write_csv("raw_opportunities.csv", opps)
    print("Done.")
