"use client";

import {
  ColumnDef,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { useMemo, useState } from "react";

import { Card } from "@/components/ui/card";

interface DayRow {
  date: string;
  calories: number;
  protein: number;
  completeness: number;
  flags: string;
}

const sampleRows: DayRow[] = [
  {
    date: "2024-01-01",
    calories: 2020,
    protein: 140,
    completeness: 0.92,
    flags: ""
  },
  {
    date: "2024-01-02",
    calories: 1780,
    protein: 118,
    completeness: 0.78,
    flags: "Low completeness"
  },
];

export default function ExplorerPage() {
  const [sorting, setSorting] = useState([] as Array<{ id: string; desc: boolean }>);
  const columns = useMemo<ColumnDef<DayRow>[]>(
    () => [
      { accessorKey: "date", header: "Date" },
      { accessorKey: "calories", header: "Calories" },
      { accessorKey: "protein", header: "Protein" },
      {
        accessorKey: "completeness",
        header: "Completeness",
        cell: ({ row }) => `${Math.round(row.original.completeness * 100)}%`,
      },
      { accessorKey: "flags", header: "Flags" },
    ],
    []
  );

  const table = useReactTable({
    data: sampleRows,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  });

  return (
    <main className="min-h-screen bg-slate-50 px-6 py-10">
      <div className="mx-auto flex max-w-6xl flex-col gap-6">
        <header>
          <h1 className="text-3xl font-semibold text-slate-900">Explorer</h1>
          <p className="text-sm text-slate-500">
            Sort, filter, and inspect daily nutrition quality.
          </p>
        </header>

        <Card>
          <div className="overflow-hidden rounded-xl border border-slate-200">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-100 text-xs uppercase text-slate-500">
                {table.getHeaderGroups().map((headerGroup) => (
                  <tr key={headerGroup.id}>
                    {headerGroup.headers.map((header) => (
                      <th
                        key={header.id}
                        className="px-4 py-3 font-semibold"
                        onClick={header.column.getToggleSortingHandler()}
                      >
                        {header.column.columnDef.header as string}
                      </th>
                    ))}
                  </tr>
                ))}
              </thead>
              <tbody>
                {table.getRowModel().rows.map((row) => (
                  <tr key={row.id} className="border-t border-slate-200">
                    {row.getVisibleCells().map((cell) => (
                      <td key={cell.id} className="px-4 py-3">
                        {cell.renderValue() as string}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        <Card>
          <h2 className="text-lg font-semibold">Day details</h2>
          <p className="text-sm text-slate-500">
            Select a day to see meals and top contributors.
          </p>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <h3 className="font-semibold">Meals</h3>
              <ul className="mt-3 space-y-2 text-sm text-slate-600">
                <li>Breakfast — 420 kcal, 25 g protein</li>
                <li>Lunch — 560 kcal, 40 g protein</li>
                <li>Dinner — 720 kcal, 55 g protein</li>
              </ul>
            </div>
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <h3 className="font-semibold">Top foods</h3>
              <ul className="mt-3 space-y-2 text-sm text-slate-600">
                <li>Chicken salad — 420 kcal</li>
                <li>Protein bar — 200 kcal</li>
                <li>Oatmeal — 150 kcal</li>
              </ul>
            </div>
          </div>
        </Card>
      </div>
    </main>
  );
}
