"use client";

import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export default function EVDistributionChart({ evData }) {
  // Sort data by total EVs in descending order
  const sortedData = [...evData].sort((a, b) => b.TOTAL_EVS - a.TOTAL_EVS).slice(0, 10);
  
  const chartData = {
    labels: sortedData.map(item => item.SUBURB_NAME),
    datasets: [
      {
        label: 'Battery EVs (BEV)',
        data: sortedData.map(item => item.BEV_COUNT),
        backgroundColor: 'rgba(52, 211, 153, 0.8)',
        borderColor: 'rgba(52, 211, 153, 1)',
        borderWidth: 1,
      },
      {
        label: 'Plug-in Hybrid EVs (PHEV)',
        data: sortedData.map(item => item.PHEV_COUNT),
        backgroundColor: 'rgba(96, 165, 250, 0.8)',
        borderColor: 'rgba(96, 165, 250, 1)',
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'EV Distribution by Suburb (Top 10)',
        font: {
          size: 16,
        },
      },
    },
    scales: {
      x: {
        stacked: true,
      },
      y: {
        stacked: true,
        title: {
          display: true,
          text: 'Number of Vehicles',
        },
      },
    },
  };

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow mb-8">
      <div style={{ height: '400px' }}>
        <Bar data={chartData} options={options} />
      </div>
    </div>
  );
}