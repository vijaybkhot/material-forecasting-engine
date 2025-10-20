"use client";
import dynamic from "next/dynamic";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

// Define types for our data points for better type safety
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

export default function ForecastChart({
  historicalData,
  forecastData,
  materialId,
}: ForecastChartProps) {
  if (!historicalData.length && !forecastData.length) {
    return (
      <div className="flex items-center justify-center h-96 bg-gray-800 rounded-lg">
        <p className="text-gray-400">
          Please select a material to view the forecast.
        </p>
      </div>
    );
  }

  const historicalTrace = {
    x: historicalData.map((d) => d.date),
    y: historicalData.map((d) => d.value),
    mode: "lines",
    name: "Historical Data",
    line: { color: "#1f77b4" }, // Blue
  };

  const forecastTrace = {
    x: forecastData.map((d) => d.date),
    y: forecastData.map((d) => d.forecast),
    mode: "lines",
    name: "Forecast",
    line: { color: "#ff7f0e", dash: "dash" }, // Orange, dashed
  };

  return (
    <Plot
      data={[historicalTrace, forecastTrace]}
      layout={{
        title: `Price Forecast for ${materialId}`,
        paper_bgcolor: "#1f2937", // gray-800
        plot_bgcolor: "#1f2937", // gray-800
        font: {
          color: "#d1d5db", // gray-300
        },
        xaxis: {
          title: "Date",
          gridcolor: "#4b5563", // gray-600
        },
        yaxis: {
          title: "Price Index",
          gridcolor: "#4b5563", // gray-600
        },
        legend: {
          orientation: "h",
          yanchor: "bottom",
          y: 1.02,
          xanchor: "right",
          x: 1,
        },
      }}
      useResizeHandler={true}
      className="w-full h-full"
      style={{ minHeight: "400px" }}
    />
  );
}
