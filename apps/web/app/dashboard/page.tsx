"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Card } from "@/components/ui/card";

const kpi = [
  { label: "Avg kcal", value: "2,120" },
  { label: "Avg protein", value: "148 g" },
  { label: "Avg fiber", value: "28 g" },
  { label: "Kcal variance", value: "220" },
  { label: "30g meals/day", value: "2.4" },
  { label: "Completeness", value: "92%" },
];

const chartData = Array.from({ length: 12 }).map((_, index) => ({
  day: `W${index + 1}`,
  kcal: 1800 + index * 30,
  protein: 120 + index * 2,
  fiber: 22 + index,
  upf: 0.2 + index * 0.02,
}));

export default function DashboardPage() {
  return (
    <main className="min-h-screen bg-slate-50 px-6 py-10">
      <div className="mx-auto flex max-w-6xl flex-col gap-8">
        <header className="flex flex-col gap-2">
          <h1 className="text-3xl font-semibold text-slate-900">Dashboard</h1>
          <p className="text-sm text-slate-500">
            Rolling trends, data quality, and diet phase insights.
          </p>
        </header>

        <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-6">
          {kpi.map((item) => (
            <Card key={item.label} className="space-y-1">
              <p className="text-xs uppercase tracking-wide text-slate-500">
                {item.label}
              </p>
              <p className="text-xl font-semibold text-slate-900">{item.value}</p>
            </Card>
          ))}
        </div>

        <Card>
          <h2 className="text-lg font-semibold text-slate-900">Kcal + Protein trend</h2>
          <p className="text-sm text-slate-500">Rolling 7-day mean overlay.</p>
          <div className="mt-6 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ left: 8, right: 8 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="day" tickLine={false} axisLine={false} />
                <YAxis tickLine={false} axisLine={false} />
                <Tooltip />
                <Line type="monotone" dataKey="kcal" stroke="#0f172a" strokeWidth={2} />
                <Line type="monotone" dataKey="protein" stroke="#38bdf8" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <div className="grid gap-4 lg:grid-cols-3">
          <Card>
            <h3 className="text-base font-semibold">Fiber per 1000 kcal</h3>
            <div className="mt-4 h-40">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="fiber" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.6} />
                      <stop offset="95%" stopColor="#38bdf8" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <Area
                    type="monotone"
                    dataKey="fiber"
                    stroke="#38bdf8"
                    fill="url(#fiber)"
                  />
                  <XAxis dataKey="day" hide />
                  <YAxis hide />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </Card>
          <Card>
            <h3 className="text-base font-semibold">Variance</h3>
            <div className="mt-4 h-40">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <Area type="monotone" dataKey="kcal" stroke="#0f172a" fill="#e2e8f0" />
                  <XAxis dataKey="day" hide />
                  <YAxis hide />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </Card>
          <Card>
            <h3 className="text-base font-semibold">UPF proxy</h3>
            <div className="mt-4 h-40">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <Line type="monotone" dataKey="upf" stroke="#f97316" strokeWidth={2} />
                  <XAxis dataKey="day" hide />
                  <YAxis hide />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </div>

        <Card>
          <h3 className="text-base font-semibold">Diet phases</h3>
          <p className="text-sm text-slate-500">
            Click a phase to see why we detected it.
          </p>
          <div className="mt-4 flex flex-wrap gap-3">
            {["Higher-protein phase", "Lower-carb phase", "Balanced phase"].map(
              (label) => (
                <button
                  key={label}
                  className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700"
                >
                  {label}
                </button>
              )
            )}
          </div>
        </Card>
      </div>
    </main>
  );
}
