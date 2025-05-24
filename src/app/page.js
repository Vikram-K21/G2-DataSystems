"use client";
import React, { useState, useEffect } from 'react';
import { 
  fetchTableData, 
  fetchEnergyData, 
  //fetchEVMetrics,
  fetchEVDistribution,
  fetchEVPriceScatter,
  fetchEVRangeScatter,
  fetchEVEfficiencyAnalysis,
  fetchEnergyEnvironmentalImpact
} from '../services/dataService';
import MetricCard from "../components/MetricCard";
import EVDistributionChart from "../components/EVDistributionChart";
import ScatterPlotChart from "../components/ScatterPlotChart";
import LineChartComponent from "../components/LineChart";

export default function Home() {
  // State for active tab
  const [activeTab, setActiveTab] = useState("evAdoption");
  
  // State to store the data
  const [tableData, setTableData] = useState([]);
  const [energyData, setEnergyData] = useState([]);
  //const [evMetrics, setEVMetrics] = useState(null);
  const [evDistribution, setEVDistribution] = useState(null);
  const [evPriceScatter, setEVPriceScatter] = useState(null);
  const [evRangeScatter, setEVRangeScatter] = useState(null);
  const [evEfficiencyAnalysis, setEVEfficiencyAnalysis] = useState(null);
  const [energyEnvironmentalImpact, setEnergyEnvironmentalImpact] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Function to load all data
    const loadData = async () => {
      setLoading(true);
      try {
        // Load data from backend
        const tableResult = await fetchTableData('energy_fact', 5);
        setTableData(tableResult);
        
        const energyResult = await fetchEnergyData();
        setEnergyData(energyResult);
        
        //const metricsResult = await fetchEVMetrics();
        //setEVMetrics(metricsResult);
        
        // Chart data
        const evDistributionData = await fetchEVDistribution();
        setEVDistribution(evDistributionData);
        
        const evPriceData = await fetchEVPriceScatter();
        setEVPriceScatter(evPriceData);
        
        const evRangeData = await fetchEVRangeScatter();
        setEVRangeScatter(evRangeData);
        
        // New environmental analysis data
        const evEfficiencyData = await fetchEVEfficiencyAnalysis();
        setEVEfficiencyAnalysis(evEfficiencyData);
        
        const energyEnvironmentalData = await fetchEnergyEnvironmentalImpact();
        setEnergyEnvironmentalImpact(energyEnvironmentalData);
        
        setError(null);
      } catch (err) {
        console.error('Error loading data:', err);
        setError('Failed to load data from the backend. Check console for details.');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

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
        <div className="text-center py-100 mb-12">
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
        
        {/* Loading state */}
        {loading && (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-green-500"></div>
            <span className="ml-3 text-xl">Loading data...</span>
          </div>
        )}
        
        {/* Error state */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900 p-4 rounded-lg mb-8">
            <p className="text-red-700 dark:text-red-300 font-bold">{error}</p>
          </div>
        )}
        
        {!loading && !error && (
          <>
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
                  {/* <MetricCard title="Total EVs" value={evMetrics.total_evs.toLocaleString()} />
                  <MetricCard title="Battery EVs (BEV)" value={evMetrics.bev.toLocaleString()} />
                  <MetricCard title="Plug-in Hybrid EVs (PHEV)" value={evMetrics.phev.toLocaleString()} />
                  <MetricCard title="BEV Percentage" value={`${evMetrics.bev_percentage.toFixed(1)}%`} /> */}
                </div>
                
                {/* EV Distribution Chart */}
                {evDistribution && (
                  <EVDistributionChart evData={evDistribution} />
                )}
                
                {/* EV Price and Range Analysis */}
                <h2 className="text-2xl font-bold mb-6 text-green-600 dark:text-green-400">
                  EV Price and Range Analysis
                </h2>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                  {evPriceScatter && (
                    <ScatterPlotChart
                      data={evPriceScatter.data}
                      xKey={evPriceScatter.x_key || "price"}
                      yKey={evPriceScatter.y_key || "count"}
                      title="EV Adoption vs Average Price"
                    />
                  )}
                  
                  {evRangeScatter && (
                    <ScatterPlotChart
                      data={evRangeScatter.data}
                      xKey={evRangeScatter.x_key || "range"}
                      yKey={evRangeScatter.y_key || "count"}
                      title="EV Adoption vs Average Range"
                    />
                  )}
                </div>
              </div>
            )}
            
            {/* Environmental Impact Tab */}
            {activeTab === "environmentalImpact" && (
              <div>
                <h2 className="text-2xl font-bold mb-6 text-green-600 dark:text-green-400">
                  Environmental Impact Analysis
                </h2>
                
                {/* EV Efficiency vs NO2 Reduction Analysis */}
                {evEfficiencyAnalysis && (
                  <div className="mb-8">
                    <h3 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">
                      EV Efficiency vs NO2 Reduction by Suburb and Year
                    </h3>
                    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                        <thead className="bg-gray-50 dark:bg-gray-700">
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                              Suburb
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                              Year
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                              EV Efficiency
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                              NO2 Reduction %
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                              Energy Change %
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                              NO2 per EV
                            </th>
                          </tr>
                        </thead>
                        <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                          {evEfficiencyAnalysis.slice(0, 10).map((row, index) => (
                            <tr key={index} className={index % 2 === 0 ? 'bg-gray-50 dark:bg-gray-900' : ''}>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                                {row.SUBURB_NAME}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                                {row.YEAR}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                                {row.EV_EFFICIENCY}
                              </td>
                              <td className={`px-6 py-4 whitespace-nowrap text-sm ${
                                row.NO2_REDUCTION_PCT < 0 ? 'text-green-600' : 'text-red-600'
                              }`}>
                                {row.NO2_REDUCTION_PCT}%
                              </td>
                              <td className={`px-6 py-4 whitespace-nowrap text-sm ${
                                row.ENERGY_CHANGE_PCT < 0 ? 'text-green-600' : 'text-red-600'
                              }`}>
                                {row.ENERGY_CHANGE_PCT}%
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                                {row.NO2_PER_EV}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
                
                {/* Energy Environmental Impact Dashboard */}
                {energyEnvironmentalImpact && (
                  <div className="mb-8">
                    <h3 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">
                      Energy vs Environmental Performance by Suburb
                    </h3>
                    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                        <thead className="bg-gray-50 dark:bg-gray-700">
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                              Suburb
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                              Avg Energy Consumption
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                              Energy Change %
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                              Avg NO2 Level
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                              NO2 Change %
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                              EV Efficiency
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                              Performance
                            </th>
                          </tr>
                        </thead>
                        <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                          {energyEnvironmentalImpact.slice(0, 10).map((row, index) => (
                            <tr key={index} className={index % 2 === 0 ? 'bg-gray-50 dark:bg-gray-900' : ''}>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                                {row.SUBURB_NAME}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                                {row.AVG_ENERGY_CONSUMPTION?.toLocaleString()}
                              </td>
                              <td className={`px-6 py-4 whitespace-nowrap text-sm ${
                                row.ENERGY_CHANGE_PCT < 0 ? 'text-green-600' : 'text-red-600'
                              }`}>
                                {row.ENERGY_CHANGE_PCT}%
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                                {row.AVG_NO2_LEVEL}
                              </td>
                              <td className={`px-6 py-4 whitespace-nowrap text-sm ${
                                row.NO2_CHANGE_PCT < 0 ? 'text-green-600' : 'text-red-600'
                              }`}>
                                {row.NO2_CHANGE_PCT}%
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                                {row.EV_EFFICIENCY}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm">
                                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                  row.ENVIRONMENTAL_PERFORMANCE === 'Excellent' ? 'bg-green-100 text-green-800' :
                                  row.ENVIRONMENTAL_PERFORMANCE === 'Good' ? 'bg-blue-100 text-blue-800' :
                                  row.ENVIRONMENTAL_PERFORMANCE === 'Moderate' ? 'bg-yellow-100 text-yellow-800' :
                                  'bg-red-100 text-red-800'
                                }`}>
                                  {row.ENVIRONMENTAL_PERFORMANCE}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </main>
      
      {/* Footer */}
      <footer className="bg-white dark:bg-gray-800 shadow-inner mt-12">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <p className="text-center text-gray-500 dark:text-gray-400">
            EcoWatt Dashboard - G2 DataSystems 2024
          </p>
        </div>
      </footer>
    </div>
  );
}