"use client";

import { useState } from "react";
import Image from "next/image";
import MetricCard from "../components/MetricCard";
import EVDistributionChart from "../components/EVDistributionChart";
import ScatterPlotChart from "../components/ScatterPlotChart";
import LineChartComponent from "../components/LineChart";

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("evAdoption");

  // EVERYTHING HERE IS PLACEHOLDER, REMOVE BEFORE DEPLOYING WITH AZURE CONNECTION
  // VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV

  // Sample placeholder data for components
  const placeholderEvData = [
    { SUBURB_NAME: "North Sydney", TOTAL_EVS: 250, BEV_COUNT: 180, PHEV_COUNT: 70, AVG_PRICE: 65000, AVG_RANGE_KM: 400 },
    { SUBURB_NAME: "Parramatta", TOTAL_EVS: 180, BEV_COUNT: 120, PHEV_COUNT: 60, AVG_PRICE: 58000, AVG_RANGE_KM: 380 },
    { SUBURB_NAME: "Bondi", TOTAL_EVS: 320, BEV_COUNT: 260, PHEV_COUNT: 60, AVG_PRICE: 72000, AVG_RANGE_KM: 450 },
    { SUBURB_NAME: "Liverpool", TOTAL_EVS: 140, BEV_COUNT: 90, PHEV_COUNT: 50, AVG_PRICE: 52000, AVG_RANGE_KM: 350 },
    { SUBURB_NAME: "Chatswood", TOTAL_EVS: 280, BEV_COUNT: 210, PHEV_COUNT: 70, AVG_PRICE: 68000, AVG_RANGE_KM: 420 }
  ];

  const placeholderEnergyData = [
    { YEAR: 2020, SUBURB_NAME: "North Sydney", ENERGY_CONSUMPTION: 4500, NO2_LEVEL: 28, NO2_CHANGE_PCT: -5 },
    { YEAR: 2021, SUBURB_NAME: "North Sydney", ENERGY_CONSUMPTION: 4600, NO2_LEVEL: 26, NO2_CHANGE_PCT: -7 },
    { YEAR: 2022, SUBURB_NAME: "North Sydney", ENERGY_CONSUMPTION: 4700, NO2_LEVEL: 24, NO2_CHANGE_PCT: -8 },
    { YEAR: 2023, SUBURB_NAME: "North Sydney", ENERGY_CONSUMPTION: 4800, NO2_LEVEL: 22, NO2_CHANGE_PCT: -9 },
    { YEAR: 2020, SUBURB_NAME: "Parramatta", ENERGY_CONSUMPTION: 3800, NO2_LEVEL: 32, NO2_CHANGE_PCT: -3 },
    { YEAR: 2021, SUBURB_NAME: "Parramatta", ENERGY_CONSUMPTION: 3900, NO2_LEVEL: 31, NO2_CHANGE_PCT: -3 },
    { YEAR: 2022, SUBURB_NAME: "Parramatta", ENERGY_CONSUMPTION: 4000, NO2_LEVEL: 29, NO2_CHANGE_PCT: -6 },
    { YEAR: 2023, SUBURB_NAME: "Parramatta", ENERGY_CONSUMPTION: 4100, NO2_LEVEL: 27, NO2_CHANGE_PCT: -7 }
  ];

  // Filter for 2023 data
  const energy2023 = placeholderEnergyData.filter(item => item.YEAR === 2023);

  // Calculate metrics from placeholder data
  const totalEVs = placeholderEvData.reduce((sum, item) => sum + item.TOTAL_EVS, 0);
  const totalBEVs = placeholderEvData.reduce((sum, item) => sum + item.BEV_COUNT, 0);
  const totalPHEVs = placeholderEvData.reduce((sum, item) => sum + item.PHEV_COUNT, 0);
  const bevPercentage = (totalBEVs / totalEVs) * 100;

  // ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  // EVERYTHING ABOVE IS PLACEHOLDER, REMOVE BEFORE DEPLOYING WITH AZURE CONNECTION

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-green-600 dark:text-green-400">EcoWatt</h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {/* Hero Section */}
        <div className="text-center py-24 mb-12">
          <h1 className="text-4xl font-bold mb-4">
            In Sydney, ever since the introduction of electric vehicles (EVs), have they made any impact on reducing the amount of pollution yearly?
          </h1>
          <h2 className="text-2xl mb-4">
            The answer is yes, but not as much as we would like to see.
          </h2>
          <p className="text-lg">
            Below, shows some stats based off recent data from Sydney Power and Car registration data.
          </p>
        </div>

        <p className="mb-8">
          This dashboard analyzes the relationship between electric vehicle adoption,
          electricity consumption, and pollution levels across different suburbs.
        </p>

        {/* EVERYTHING BELOW IS PLACEHOLDER, REMOVE BEFORE DEPLOYING WITH AZURE CONNECTION */}

        <div className="bg-yellow-50 dark:bg-yellow-900 p-4 rounded-lg mb-8">
          <p className="text-yellow-700 dark:text-yellow-300 font-bold">
            Note: This is a preview with placeholder data. Actual data will be loaded from Azure SQL Database.
          </p>
        </div>

        {/* EVERYTHING ABOVE IS PLACEHOLDER, REMOVE BEFORE DEPLOYING WITH AZURE CONNECTION */}

        {/* Dashboard Tabs */}
        <div className="border-b border-gray-200 mb-8">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab("evAdoption")}
              className={`${
                activeTab === "evAdoption"
                  ? "border-green-500 text-green-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              EV Adoption Overview
            </button>
            <button
              onClick={() => setActiveTab("environmentalImpact")}
              className={`${
                activeTab === "environmentalImpact"
                  ? "border-green-500 text-green-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              Environmental Impact
            </button>
            <button
              onClick={() => setActiveTab("suburbAnalysis")}
              className={`${
                activeTab === "suburbAnalysis"
                  ? "border-green-500 text-green-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              Suburb Analysis
            </button>
          </nav>
        </div>

        {/* EV Adoption Tab */}
        {activeTab === "evAdoption" && (
          <div>
            <h2 className="text-2xl font-bold mb-6 text-green-600 dark:text-green-400">
              EV Adoption Metrics
            </h2>

            {/* Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <MetricCard title="Total EVs" value={totalEVs.toLocaleString()} />
              <MetricCard title="Battery EVs (BEV)" value={totalBEVs.toLocaleString()} />
              <MetricCard title="Plug-in Hybrid EVs (PHEV)" value={totalPHEVs.toLocaleString()} />
              <MetricCard title="BEV Percentage" value={`${bevPercentage.toFixed(1)}%`} />
            </div>

            {/* EV Distribution Chart */}
            <EVDistributionChart evData={placeholderEvData} />

            {/* EV Price and Range Analysis */}
            <h2 className="text-2xl font-bold mb-6 text-green-600 dark:text-green-400">
              EV Price and Range Analysis
            </h2>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              <ScatterPlotChart
                data={placeholderEvData}
                xKey="AVG_PRICE"
                yKey="TOTAL_EVS"
                title="EV Adoption vs Average Price"
              />
              <ScatterPlotChart
                data={placeholderEvData}
                xKey="AVG_RANGE_KM"
                yKey="TOTAL_EVS"
                title="EV Adoption vs Average Range"
              />
            </div>
          </div>
        )}

        {/* Environmental Impact Tab */}
        {activeTab === "environmentalImpact" && (
          <div>
            <h2 className="text-2xl font-bold mb-6 text-green-600 dark:text-green-400">
              Environmental Impact Analysis
            </h2>

            {/* Energy vs Pollution Scatter Plot */}
            <ScatterPlotChart
              data={energy2023}
              xKey="ENERGY_CONSUMPTION"
              yKey="NO2_LEVEL"
              title="Energy Consumption vs NO2 Pollution (2023)"
            />

            {/* NO2 Levels Over Time */}
            <h2 className="text-2xl font-bold mb-6 text-green-600 dark:text-green-400">
              NO2 Levels Over Time
            </h2>

            <LineChartComponent
              data={placeholderEnergyData}
              xKey="YEAR"
              yKey="NO2_LEVEL"
              title="NO2 Levels Over Years by Suburb"
              colorBy="SUBURB_NAME"
            />
          </div>
        )}

        {/* Suburb Analysis Tab */}
        {activeTab === "suburbAnalysis" && (
          <div>
            <h2 className="text-2xl font-bold mb-6 text-green-600 dark:text-green-400">
              Suburb Comparison
            </h2>

            {/* EV Adoption by Suburb */}
            <EVDistributionChart evData={placeholderEvData} />

            {/* EV Adoption vs NO2 Reduction */}
            <h2 className="text-2xl font-bold mb-6 text-green-600 dark:text-green-400">
              EV Adoption vs NO2 Reduction
            </h2>

            <ScatterPlotChart
              data={placeholderEnergyData}
              xKey="TOTAL_EVS"
              yKey="NO2_CHANGE_PCT"
              title="Relationship between EV Adoption and NO2 Change"
            />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white dark:bg-gray-800 shadow-inner mt-12">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <p className="text-center text-gray-500 dark:text-gray-400">
            EcoWatt Dashboard - Group 4 2025
          </p>
        </div>
      </footer>
    </div>
  );
}