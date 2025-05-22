"use client";

import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

export default function LineChartComponent({ data, xKey, yKey, title, colorBy }) {
  // Get unique values for the x-axis
  const xValues = [...new Set(data.map(item => item[xKey]))].sort();
  
  // Get unique values for the color grouping
  const colorGroups = [...new Set(data.map(item => item[colorBy]))];
  
  // Generate colors for each group
  const colors = [
    'rgba(52, 211, 153, 1)',
    'rgba(96, 165, 250, 1)',
    'rgba(251, 146, 60, 1)',
    'rgba(167, 139, 250, 1)',
    'rgba(248, 113, 113, 1)',
    'rgba(45, 212, 191, 1)',
    'rgba(251, 191, 36, 1)',
    'rgba(232, 121, 249, 1)',
  ];
  
  // Create datasets for each color group
  const datasets = colorGroups.map((group, index) => {
    const groupData = data.filter(item => item[colorBy] === group);
    
    // Create a map of x values to y values for this group
    const dataMap = {};
    groupData.forEach(item => {
      dataMap[item[xKey]] = item[yKey];
    });
    
    // Create the dataset with values for each x value
    return {
      label: group,
      data: xValues.map(x => dataMap[x] || null),
      borderColor: colors[index % colors.length],
      backgroundColor: colors[index % colors.length].replace('1)', '0.1)'),
      borderWidth: 2,
      tension: 0.3,
    };
  });
  
  const chartData = {
    labels: xValues,
    datasets,
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
        text: title,
        font: {
          size: 16,
        },
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: xKey.replace(/_/g, ' '),
        },
      },
      y: {
        title: {
          display: true,
          text: yKey.replace(/_/g, ' '),
        },
      },
    },
  };

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow mb-8">
      <div style={{ height: '400px' }}>
        <Line data={chartData} options={options} />
      </div>
    </div>
  );
}