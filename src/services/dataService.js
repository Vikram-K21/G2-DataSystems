/**
 * Data Service for G2-DataSystems
 * This file contains all the functions to fetch data from the backend API
 */

// Base API URL - use environment variable or default to localhost
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';

/**
 * Fetch data from a specific table
 * @param {string} tableName - Name of the table to fetch
 * @param {number} limit - Maximum number of records to return
 * @returns {Promise<Array>} - Array of table records
 */
export const fetchTableData = async (tableName, limit = 100) => {
  try {
    const response = await fetch(`${API_BASE_URL}/tables/${tableName}?limit=${limit}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Error fetching ${tableName} data:`, error);
    throw error;
  }
};

/**
 * Fetch energy data with optional filters
 * @param {Object} filters - Optional filters for the data
 * @returns {Promise<Array>} - Array of energy data records
 */
export const fetchEnergyData = async (filters = {}) => {
  try {
    const queryParams = new URLSearchParams();
    
    // Add any filters to the query parameters
    if (filters.year) queryParams.append('year', filters.year);
    if (filters.suburb) queryParams.append('suburb', filters.suburb);
    
    const url = `${API_BASE_URL}/energy-data${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching energy data:', error);
    throw error;
  }
};

/**
 * Fetch EV metrics summary
 * @returns {Promise<Object>} - Object containing EV metrics
 */
export const fetchEVMetrics = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/ev_metrics`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching EV metrics:', error);
    throw error;
  }
};

/**
 * Fetch EV distribution data by suburb
 * @returns {Promise<Object>} - Object containing labels and data for chart
 */
export const fetchEVDistribution = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/ev-distribution`);
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching EV distribution data:', error);
    throw error;
  }
};

/**
 * Fetch EV price scatter plot data
 * @returns {Promise<Object>} - Object containing data for scatter plot
 */
export const fetchEVPriceScatter = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/ev-price-scatter`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching EV price scatter data:', error);
    throw error;
  }
};

/**
 * Fetch EV range scatter plot data
 * @returns {Promise<Object>} - Object containing data for scatter plot
 */
export const fetchEVRangeScatter = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/ev-range-scatter`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching EV range scatter data:', error);
    throw error;
  }
};

/**
 * Fetch energy consumption vs NO2 pollution data
 * @returns {Promise<Object>} - Object containing data for comparison chart
 */
export const fetchEnergyVsNO2 = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/energy-vs-no2`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching energy vs NO2 data:', error);
    throw error;
  }
};

/**
 * Fetch NO2 pollution trends over time
 * @returns {Promise<Object>} - Object containing data for trend chart
 */
export const fetchNO2Trends = async (years = [2022, 2023]) => {
  try {
    const queryParams = new URLSearchParams();
    years.forEach(year => queryParams.append('years', year));
    
    const response = await fetch(`${API_BASE_URL}/no2-trends?${queryParams.toString()}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching NO2 trends data:', error);
    throw error;
  }
};

/**
 * Fetch EV efficiency vs NO2 reduction analysis
 */
export const fetchEVEfficiencyAnalysis = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/ev-efficiency-analysis`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching EV efficiency analysis:', error);
    throw error;
  }
};

/**
 * Fetch energy environmental impact data
 */
export const fetchEnergyEnvironmentalImpact = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/energy-environmental-impact`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching energy environmental impact:', error);
    throw error;
  }
};

/**
 * Execute a custom query
 * @param {string} query - SQL query to execute
 * @returns {Promise<Array>} - Array of query results
 */
export const executeCustomQuery = async (query) => {
  try {
    const response = await fetch(`${API_BASE_URL}/custom-query?query=${encodeURIComponent(query)}`);
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error executing custom query:', error);
    throw error;
  }
};

export default {
  fetchTableData,
  fetchEnergyData,
  fetchEVMetrics,
  fetchEVDistribution,
  fetchEVPriceScatter,
  fetchEVRangeScatter,
  fetchEnergyVsNO2,
  fetchNO2Trends,
  executeCustomQuery
};