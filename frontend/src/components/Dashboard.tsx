"use client";

import { useState, useEffect } from "react";
import MaterialSelector from "./MaterialSelector";
import ForecastChart from "./ForecastChart";

// Define the structure of our data points for type safety
interface HistoricalDataPoint {
  date: string;
  value: number;
}

interface ForecastDataPoint {
  date: string;
  forecast: number;
}

// Get API URL from environment variables, with a fallback for safety
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

export default function Dashboard() {
  // State management for the dashboard
  const [materials, setMaterials] = useState<string[]>([]);
  const [selectedMaterial, setSelectedMaterial] = useState<string>("");
  const [historicalData, setHistoricalData] = useState<HistoricalDataPoint[]>(
    []
  );
  const [forecastData, setForecastData] = useState<ForecastDataPoint[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Effect to fetch the list of materials when the component mounts
  useEffect(() => {
    async function fetchMaterials() {
      try {
        const response = await fetch(`${API_URL}/materials`);
        if (!response.ok) throw new Error("Failed to fetch materials");
        const data = await response.json();
        setMaterials(data);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "An unknown error occurred"
        );
      }
    }
    fetchMaterials();
  }, []); // Empty dependency array means this runs once on mount

  // Effect to fetch forecast and historical data when a material is selected
  useEffect(() => {
    if (!selectedMaterial) {
      // Clear data if no material is selected
      setHistoricalData([]);
      setForecastData([]);
      setError(null);
      return;
    }

    async function fetchDataForMaterial() {
      setIsLoading(true);
      setError(null);

      try {
        // Fetch both historical and forecast data in parallel
        const [histRes, forecastRes] = await Promise.all([
          fetch(`${API_URL}/historical-data/${selectedMaterial}`),
          fetch(`${API_URL}/forecast?material_id=${selectedMaterial}`),
        ]);

        if (!histRes.ok)
          throw new Error(
            `Failed to fetch historical data for ${selectedMaterial}`
          );
        if (!forecastRes.ok) {
          const errorData = await forecastRes.json();
          throw new Error(
            errorData.detail ||
              `Failed to fetch forecast for ${selectedMaterial}`
          );
        }

        const histData = await histRes.json();
        const forecastPayload = await forecastRes.json();

        setHistoricalData(histData);
        setForecastData(forecastPayload.forecast);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "An unknown error occurred"
        );
        setHistoricalData([]);
        setForecastData([]);
      } finally {
        setIsLoading(false);
      }
    }

    fetchDataForMaterial();
  }, [selectedMaterial]); // This effect re-runs whenever selectedMaterial changes

  return (
    <div className="p-4 sm:p-6 lg:p-8 bg-gray-900 min-h-screen text-white">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight text-white">
            Forecasting Dashboard
          </h1>
          <p className="mt-1 text-gray-400">
            Select a material to visualize its historical data and price
            forecast.
          </p>
        </header>

        <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
          <div className="mb-6">
            <MaterialSelector
              materials={materials}
              selectedMaterial={selectedMaterial}
              onMaterialChange={setSelectedMaterial}
              isLoading={isLoading}
            />
          </div>

          {/* Conditional Rendering for Loading and Error states */}
          {isLoading && (
            <div className="flex items-center justify-center h-96">
              <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500"></div>
            </div>
          )}

          {error && !isLoading && (
            <div className="flex items-center justify-center h-96 bg-red-900/20 border border-red-500/50 rounded-lg">
              <div className="text-center">
                <p className="text-red-400 font-semibold">An Error Occurred</p>
                <p className="text-red-400/80 mt-1">{error}</p>
              </div>
            </div>
          )}

          {!isLoading && !error && (
            <ForecastChart
              historicalData={historicalData}
              forecastData={forecastData}
              materialId={selectedMaterial}
            />
          )}
        </div>
      </div>
    </div>
  );
}
