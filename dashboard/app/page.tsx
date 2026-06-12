"use client";

import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
} from "recharts";
import data from "../public/data.json";

const usd = (n: number) =>
  n >= 1_000_000
    ? `$${(n / 1_000_000).toFixed(1)}M`
    : n >= 1_000
      ? `$${(n / 1_000).toFixed(0)}K`
      : `$${n}`;
const pct = (n: number) => `${(n * 100).toFixed(1)}%`;

const ACCENT = "#5b9cff";
const GREEN = "#3ecf8e";
const SEGMENT_COLORS: Record<string, string> = {
  Enterprise: "#5b9cff",
  "Mid-Market": "#3ecf8e",
  SMB: "#c084fc",
};

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-5">
      <h2 className="mb-4 text-sm font-medium text-white/60">{title}</h2>
      {children}
    </div>
  );
}

function Kpi({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-5">
      <div className="text-sm text-white/50">{label}</div>
      <div className="mt-1 text-3xl font-semibold tracking-tight">{value}</div>
      {sub && <div className="mt-1 text-xs text-white/40">{sub}</div>}
    </div>
  );
}

const tooltipStyle = {
  background: "#11151f",
  border: "1px solid rgba(255,255,255,0.12)",
  borderRadius: 8,
  color: "#e6e9ef",
} as const;

export default function Dashboard() {
  const k = data.kpis;
  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <header className="mb-8">
        <h1 className="text-2xl font-semibold tracking-tight">RevOps Analytics</h1>
        <p className="mt-1 text-white/50">
          B2B SaaS revenue operations, modeled with dbt + DuckDB. 3,200 opportunities,
          24 reps, 8 quarters.
        </p>
        <p className="mt-1 text-xs text-white/30">
          Synthetic, reproducible dataset. Transformations and tests in the dbt project.
        </p>
      </header>

      <section className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-4">
        <Kpi label="Closed won ARR" value={usd(k.won_arr)} sub="across 8 quarters" />
        <Kpi label="Win rate" value={pct(k.win_rate)} sub="closed won / closed" />
        <Kpi label="Open pipeline" value={usd(k.open_pipeline)} sub="not yet closed" />
        <Kpi
          label="Median quota attainment"
          value={pct(k.median_attainment)}
          sub={`${pct(k.pct_hit_quota)} of rep-quarters hit quota`}
        />
      </section>

      <section className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card title="Closed won ARR by quarter">
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.arr_by_quarter}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="quarter" tick={{ fill: "#8b93a7", fontSize: 12 }} />
                <YAxis tickFormatter={usd} tick={{ fill: "#8b93a7", fontSize: 12 }} width={48} />
                <Tooltip contentStyle={tooltipStyle} formatter={(v) => usd(Number(v))} cursor={{ fill: "rgba(255,255,255,0.04)" }} />
                <Bar dataKey="won_arr" fill={ACCENT} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card title="Won ARR by segment">
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.segment_perf}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="segment" tick={{ fill: "#8b93a7", fontSize: 12 }} />
                <YAxis tickFormatter={usd} tick={{ fill: "#8b93a7", fontSize: 12 }} width={48} />
                <Tooltip contentStyle={tooltipStyle} formatter={(v) => usd(Number(v))} cursor={{ fill: "rgba(255,255,255,0.04)" }} />
                <Bar dataKey="won_arr" radius={[4, 4, 0, 0]}>
                  {data.segment_perf.map((s) => (
                    <Cell key={s.segment} fill={SEGMENT_COLORS[s.segment] ?? ACCENT} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card title="Won ARR by lead source">
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.funnel_by_source}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="lead_source" tick={{ fill: "#8b93a7", fontSize: 12 }} />
                <YAxis tickFormatter={usd} tick={{ fill: "#8b93a7", fontSize: 12 }} width={48} />
                <Tooltip contentStyle={tooltipStyle} formatter={(v) => usd(Number(v))} cursor={{ fill: "rgba(255,255,255,0.04)" }} />
                <Bar dataKey="won_amount" fill={GREEN} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card title="Top reps by won ARR">
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.top_reps.slice(0, 8)} layout="vertical" margin={{ left: 24 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis type="number" tickFormatter={usd} tick={{ fill: "#8b93a7", fontSize: 12 }} />
                <YAxis type="category" dataKey="rep_name" tick={{ fill: "#8b93a7", fontSize: 11 }} width={96} />
                <Tooltip contentStyle={tooltipStyle} formatter={(v) => usd(Number(v))} cursor={{ fill: "rgba(255,255,255,0.04)" }} />
                <Bar dataKey="won" fill="#c084fc" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </section>

      <section className="mt-4">
        <Card title="Segment performance">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="text-white/50">
                <tr className="border-b border-white/10">
                  <th className="py-2 pr-4 font-medium">Segment</th>
                  <th className="py-2 pr-4 font-medium">Win rate</th>
                  <th className="py-2 pr-4 font-medium">Won ARR</th>
                  <th className="py-2 pr-4 font-medium">Avg deal</th>
                  <th className="py-2 pr-4 font-medium">Avg cycle (days)</th>
                </tr>
              </thead>
              <tbody>
                {data.segment_perf.map((s) => (
                  <tr key={s.segment} className="border-b border-white/5">
                    <td className="py-2 pr-4">
                      <span
                        className="mr-2 inline-block h-2 w-2 rounded-full align-middle"
                        style={{ background: SEGMENT_COLORS[s.segment] ?? ACCENT }}
                      />
                      {s.segment}
                    </td>
                    <td className="py-2 pr-4">{pct(s.win_rate)}</td>
                    <td className="py-2 pr-4">{usd(s.won_arr)}</td>
                    <td className="py-2 pr-4">{usd(s.avg_deal)}</td>
                    <td className="py-2 pr-4">{s.avg_cycle}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </section>

      <footer className="mt-10 text-xs text-white/30">
        Built with dbt, DuckDB, Next.js, and Recharts. Data is synthetic and reproducible.
      </footer>
    </main>
  );
}
