import { UploadCloud } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-slate-50 px-6 py-12">
      <div className="mx-auto flex max-w-5xl flex-col gap-8">
        <header className="flex flex-col gap-3">
          <p className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Local-first nutrition analytics
          </p>
          <h1 className="text-4xl font-semibold text-slate-900">
            Import your MyFitnessPal history and unlock five years of insight.
          </h1>
          <p className="max-w-2xl text-base text-slate-600">
            Bites keeps everything on your machine while turning daily logs into a beautiful dashboard of trends, phases, and
            data quality insights.
          </p>
        </header>

        <Card className="border-dashed bg-white/70">
          <div className="flex flex-col items-center gap-4 py-8 text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-slate-100">
              <UploadCloud className="h-8 w-8 text-slate-600" />
            </div>
            <div className="space-y-1">
              <h2 className="text-lg font-semibold">Drop your export here</h2>
              <p className="text-sm text-slate-500">
                Upload CSV files or a ZIP from the MyFitnessPal export tool. We validate totals + diary entries on import.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Button>Choose files</Button>
              <Button variant="ghost">View sample format</Button>
            </div>
          </div>
        </Card>

        <div className="grid gap-6 md:grid-cols-3">
          {[
            {
              title: "Fast local ingest",
              description: "Normalize meals, units, and macros into a clean DuckDB schema without sending data anywhere.",
            },
            {
              title: "Premium dashboards",
              description: "Track rolling averages, variance, and high-protein meal counts with polished visuals.",
            },
            {
              title: "Transparent phases",
              description: "Understand diet phases with change-point detection and clear explanations of the deltas.",
            },
          ].map((item) => (
            <Card key={item.title} className="bg-white">
              <h3 className="text-lg font-semibold text-slate-900">{item.title}</h3>
              <p className="mt-2 text-sm text-slate-600">{item.description}</p>
            </Card>
          ))}
        </div>

        <div className="flex flex-wrap gap-4">
          <Button>Go to Dashboard</Button>
          <Button variant="ghost">Explore sample data</Button>
        </div>
      </div>
    </main>
  );
}
