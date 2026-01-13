import { Card } from "@/components/ui/card";

const years = [
  {
    year: 2024,
    averageKcal: 2100,
    averageProtein: 140,
    variance: 210,
    topFoods: ["Chicken salad", "Greek yogurt", "Oatmeal"],
    highlight: "Shifted into a higher-protein phase mid-year.",
  },
  {
    year: 2023,
    averageKcal: 1980,
    averageProtein: 132,
    variance: 260,
    topFoods: ["Turkey wrap", "Protein shake", "Fruit bowl"],
    highlight: "More consistent calories in Q3 with higher fiber intake.",
  },
];

export default function ReportsPage() {
  return (
    <main className="min-h-screen bg-slate-50 px-6 py-10">
      <div className="mx-auto flex max-w-5xl flex-col gap-6">
        <header>
          <h1 className="text-3xl font-semibold text-slate-900">Year in Review</h1>
          <p className="text-sm text-slate-500">
            Summaries by year for easy sharing or PDF export.
          </p>
        </header>

        {years.map((year) => (
          <Card key={year.year}>
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-semibold">{year.year}</h2>
              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-500">
                {year.highlight}
              </span>
            </div>
            <div className="mt-4 grid gap-4 md:grid-cols-3">
              <div>
                <p className="text-xs uppercase tracking-wide text-slate-500">Avg kcal</p>
                <p className="text-lg font-semibold">{year.averageKcal}</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-wide text-slate-500">Avg protein</p>
                <p className="text-lg font-semibold">{year.averageProtein} g</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-wide text-slate-500">Variance</p>
                <p className="text-lg font-semibold">{year.variance}</p>
              </div>
            </div>
            <div className="mt-4">
              <p className="text-xs uppercase tracking-wide text-slate-500">Top foods</p>
              <div className="mt-2 flex flex-wrap gap-2">
                {year.topFoods.map((food) => (
                  <span
                    key={food}
                    className="rounded-full border border-slate-200 px-3 py-1 text-xs font-medium text-slate-600"
                  >
                    {food}
                  </span>
                ))}
              </div>
            </div>
          </Card>
        ))}
      </div>
    </main>
  );
}
