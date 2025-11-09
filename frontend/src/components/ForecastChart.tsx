"use client";

import React, { useMemo } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from "recharts";
import type { TooltipProps } from "recharts";

interface DataPoint {
  date: string;
  value: number;
}
interface ForecastPoint {
  date: string;
  forecast: number;
}

interface ForecastChartProps {
  historicalData: DataPoint[];
  forecastData: ForecastPoint[];
  materialId: string;
}

type RechartsTooltipValue = number | string | Array<number | string>;
type RechartsTooltip = TooltipProps<RechartsTooltipValue, string>;

// Helper to format date strings to "Mon YYYY" or "Month YYYY"
const formatMonthYearShort = (isoDate: string) => {
  try {
    return new Intl.DateTimeFormat(undefined, {
      month: "short",
      year: "numeric",
    }).format(new Date(isoDate));
  } catch {
    return isoDate;
  }
};
const formatMonthYearLong = (isoDate: string) => {
  try {
    return new Intl.DateTimeFormat(undefined, {
      month: "long",
      year: "numeric",
    }).format(new Date(isoDate));
  } catch {
    return isoDate;
  }
};

// Helper to format numbers (simple)
const formatNumber = (v: number | string) => {
  if (typeof v === "number")
    return v.toLocaleString(undefined, { maximumFractionDigits: 2 });
  // if it's a string that parses to a number, format it
  const n = Number(v);
  if (!Number.isNaN(n))
    return n.toLocaleString(undefined, { maximumFractionDigits: 2 });
  return String(v);
};

// Helper to merge two series into one data array keyed by date
function mergeSeries(
  historical: DataPoint[],
  forecast: ForecastPoint[]
): Array<{ date: string; historical?: number; forecast?: number }> {
  const map = new Map<
    string,
    { date: string; historical?: number; forecast?: number }
  >();
  historical.forEach((d) => {
    map.set(d.date, { date: d.date, historical: d.value });
  });
  forecast.forEach((f) => {
    const existing = map.get(f.date);
    if (existing) existing.forecast = f.forecast;
    else map.set(f.date, { date: f.date, forecast: f.forecast });
  });
  // Sort by date (assumes ISO strings; adapt if different)
  return Array.from(map.values()).sort((a, b) => (a.date < b.date ? -1 : 1));
}

export default function ForecastChart({
  historicalData,
  forecastData,
  materialId,
}: ForecastChartProps) {
  const data = useMemo(
    () => mergeSeries(historicalData, forecastData),
    [historicalData, forecastData]
  );

  if (!data.length) {
    return (
      <div className="flex items-center justify-center h-96 bg-gray-800 rounded-lg">
        <p className="text-gray-400">
          Please select a material to view the forecast.
        </p>
      </div>
    );
  }

  // Optional: control tick interval to avoid overcrowding. Choose a target number of ticks.
  const targetTicks = 6;
  const interval = Math.max(
    0,
    Math.floor(Math.max(1, data.length / targetTicks)) - 1
  );

  // Properly typed tooltip formatters using Recharts types
  const tooltipLabelFormatter: NonNullable<
    RechartsTooltip["labelFormatter"]
  > = (label) => String(formatMonthYearLong(String(label ?? "")));

  const tooltipFormatter: NonNullable<RechartsTooltip["formatter"]> = (
    value
  ) => {
    // value can sometimes be an array (stacked series), so handle that
    let valToFormat: number | string = "";
    if (Array.isArray(value)) {
      valToFormat = value[0] ?? "";
    } else {
      valToFormat = (value ?? "") as number | string;
    }
    return formatNumber(valToFormat);
  };

  return (
    <div>
      {/* Use materialId so it is not unused; small title above the chart */}
      <h3 className="text-gray-200 mb-2">Price Forecast for {materialId}</h3>

      <div style={{ width: "100%", height: 480 }}>
        <ResponsiveContainer>
          <LineChart data={data}>
            <CartesianGrid stroke="#4b5563" />
            <XAxis
              dataKey="date"
              tick={{ fill: "#d1d5db" }}
              tickFormatter={formatMonthYearShort}
              interval={interval}
              minTickGap={20}
            />
            <YAxis tick={{ fill: "#d1d5db" }} />
            <Tooltip
              labelFormatter={tooltipLabelFormatter}
              formatter={tooltipFormatter}
              wrapperStyle={{
                backgroundColor: "#111827",
                borderRadius: 8,
                border: "1px solid #374151",
                color: "#d1d5db",
              }}
              labelStyle={{ color: "#9ca3af" }}
              contentStyle={{ backgroundColor: "#0b1220", borderRadius: 6 }}
            />
            <Legend verticalAlign="top" align="right" />
            <Line
              type="monotone"
              dataKey="historical"
              name="Historical Data"
              stroke="#1f77b4"
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="forecast"
              name="Forecast"
              stroke="#ff7f0e"
              strokeDasharray="4 4"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
