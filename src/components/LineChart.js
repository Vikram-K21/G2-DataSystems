import React from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';

// Register ChartJS components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const LineChartComponent = ({ data, xKey, yKey, title, colorBy }) => {
  // Handle different data formats
  let chartData = [];
  
  if (!data) {
    return <div className="p-4 text-red-500">No data available for line chart</div>;
  }
  
  // Check if data is in the format returned by backend
  if (data.data && Array.isArray(data.data)) {
    chartData = data.data;
    // Use the keys provided by the backend if available
    if (data.x_key) xKey = data.x_key;
    if (data.y_key) yKey = data.y_key;
    if (data.color_by) colorBy = data.color_by;
  } else if (Array.isArray(data)) {
    chartData = data;
  } else {
    return <div className="p-4 text-red-500">Invalid data format for line chart</div>;
  }
  
  if (chartData.length === 0) {
    return <div className="p-4 text-red-500">No data available for line chart</div>;
  }

  // Get unique values for the colorBy field to create separate lines
  const uniqueCategories = colorBy 
    ? [...new Set(chartData.map(item => item[colorBy]))]
    : ['Default'];

  // Generate colors for each category
  const colors = [
    'rgba(54, 162, 235, 1)',
    'rgba(255, 99, 132, 1)',
    'rgba(75, 192, 192, 1)',
    'rgba(255, 159, 64, 1)',
    'rgba(153, 102, 255, 1)',
    'rgba(255, 206, 86, 1)',
    'rgba(231, 233, 237, 1)',
  ];

  // Prepare datasets
  const datasets = uniqueCategories.map((category, index) => {
    const categoryData = colorBy 
      ? chartData.filter(item => item[colorBy] === category)
      : chartData;
    
    // Sort data by xKey if it's a number or date
    categoryData.sort((a, b) => {
      if (typeof a[xKey] === 'number') {
        return a[xKey] - b[xKey];
      }
      return String(a[xKey]).localeCompare(String(b[xKey]));
    });
    
    return {
      label: category,
      data: categoryData.map(item => item[yKey]),
      borderColor: colors[index % colors.length],
      backgroundColor: colors[index % colors.length].replace('1)', '0.2)'),
      tension: 0.1,
      pointRadius: 4,
      pointHoverRadius: 6,
    };
  });

  // Get labels (x-axis values)
  let labels;
  if (colorBy) {
    // Get unique x values across all categories
    const allXValues = [...new Set(chartData.map(item => item[xKey]))];
    allXValues.sort((a, b) => {
      if (typeof a === 'number') {
        return a - b;
      }
      return String(a).localeCompare(String(b));
    });
    labels = allXValues;
  } else {
    labels = chartData.map(item => item[xKey]);
  }

  const chartDataConfig = {
    labels,
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
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: yKey.replace(/_/g, ' ').toUpperCase(),
        },
      },
      x: {
        title: {
          display: true,
          text: xKey.replace(/_/g, ' ').toUpperCase(),
        },
      },
    },
  };

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow mb-8">
      <h3 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">{title}</h3>
      <div className="h-80">
        <Line data={chartDataConfig} options={options} />
      </div>
    </div>
  );
};

export default LineChartComponent;