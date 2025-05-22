"use client";
import React, { useState, useEffect } from 'react';
import { 
  fetchTableData, 
  fetchEnergyData, 
  fetchEVMetrics,
  fetchEVDistribution,
  fetchEVPriceScatter,
  fetchEVRangeScatter,
  fetchEnergyVsNO2,
  fetchNO2Trends
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
  const [evMetrics, setEVMetrics] = useState(null);
  const [evDistribution, setEVDistribution] = useState(null);
  const [evPriceScatter, setEVPriceScatter] = useState(null);
  const [evRangeScatter, setEVRangeScatter] = useState(null);
  const [energyVsNO2, setEnergyVsNO2] = useState(null);
  const [no2Trends, setNO2Trends] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Function to load all data
    const loadData = async () => {
      setLoading(true);
      try {
        // Load data from backend
        const tableResult = await fetchTableData('energy_pollution_fact', 5);
        setTableData(tableResult);
        
        const energyResult = await fetchEnergyData();
        setEnergyData(energyResult);
        
        const metricsResult = await fetchEVMetrics();
        setEVMetrics(metricsResult);
        
        // Chart data
        const evDistributionData = await fetchEVDistribution();
        setEVDistribution(evDistributionData);
        
        const evPriceData = await fetchEVPriceScatter();
        setEVPriceScatter(evPriceData);
        
        const evRangeData = await fetchEVRangeScatter();
        setEVRangeScatter(evRangeData);
        
        const energyNO2Data = await fetchEnergyVsNO2();
        setEnergyVsNO2(energyNO2Data);
        
        const no2TrendsData = await fetchNO2Trends();
        setNO2Trends(no2TrendsData);
        
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

  // Filter for 2023 data if available
  const energy2023 = energyData.filter(item => item.year === 2023 || item.YEAR === 2023);

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
            {activeTab === "evAdoption" && evMetrics && (
              <div>
                <h2 className="text-2xl font-bold mb-6 text-green-600 dark:text-green-400">
                  EV Adoption Metrics
                </h2>
                {/* Metrics Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                  <MetricCard title="Total EVs" value={evMetrics.total_evs.toLocaleString()} />
                  <MetricCard title="Battery EVs (BEV)" value={evMetrics.bev.toLocaleString()} />
                  <MetricCard title="Plug-in Hybrid EVs (PHEV)" value={evMetrics.phev.toLocaleString()} />
                  <MetricCard title="BEV Percentage" value={`${evMetrics.bev_percentage.toFixed(1)}%`} />
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
                
                {/* Energy vs Pollution Scatter Plot */}
                {energyVsNO2 && (
                  <ScatterPlotChart
                    data={energyVsNO2}  // Pass the whole object, not just energyVsNO2.data
                    xKey="ENERGY_CONSUMPTION"
                    yKey="NO2_LEVEL"
                    title="Energy Consumption vs NO2 Pollution (2023)"
                    excludePoints={['sydney']}
                  />
                )}
                
                {/* NO2 Levels Over Time */}
                {no2Trends && (
                  <LineChartComponent
                    data={no2Trends}  // Pass the whole object, not just no2Trends.data
                    xKey="YEAR"
                    yKey="NO2_LEVEL"
                    title="NO2 Levels Over Years by Suburb"
                    colorBy="SUBURB_NAME"
                  />
                )}
              </div>
            )}
            
            {/* Suburb Analysis Tab */}
            {activeTab === "suburbAnalysis" && (
              <div>
                <h2 className="text-2xl font-bold mb-6 text-green-600 dark:text-green-400">
                  Suburb Comparison
                </h2>
                
                {/* EV Adoption by Suburb */}
                {evDistribution && (
                  <EVDistributionChart evData={evDistribution} />
                )}
                
                {/* EV Adoption vs NO2 Reduction */}
                <h2 className="text-2xl font-bold mb-6 text-green-600 dark:text-green-400">
                  EV Adoption vs NO2 Reduction
                </h2>
                
                {energyVsNO2 && (
                  <ScatterPlotChart
                    data={energyVsNO2.data || []}
                    xKey="TOTAL_EVS"
                    yKey="NO2_CHANGE_PCT"
                    title="Relationship between EV Adoption and NO2 Change"
                  />
                )}
                
                {/* Data Table */}
                {tableData.length > 0 && (
                  <div className="mt-12">
                    <h2 className="text-2xl font-bold mb-6 text-green-600 dark:text-green-400">
                      Raw Data Sample
                    </h2>
                    <div className="overflow-x-auto bg-white dark:bg-gray-800 shadow rounded-lg">
                      <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                        <thead className="bg-gray-50 dark:bg-gray-700">
                          <tr>
                            {Object.keys(tableData[0]).map(key => (
                              <th key={key} className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                {key}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                          {tableData.map((row, index) => (
                            <tr key={index} className={index % 2 === 0 ? 'bg-gray-50 dark:bg-gray-900' : ''}>
                              {Object.values(row).map((value, i) => (
                                <td key={i} className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                                  {value !== null ? value.toString() : 'null'}
                                </td>
                              ))}
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