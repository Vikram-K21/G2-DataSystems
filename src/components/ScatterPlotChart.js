import React from 'react';
import { Scatter } from 'react-chartjs-2';
import { Chart as ChartJS, LinearScale, PointElement, LineElement, Tooltip, Legend } from 'chart.js';

// Register ChartJS components
ChartJS.register(LinearScale, PointElement, LineElement, Tooltip, Legend);

const ScatterPlotChart = ({ data, xKey, yKey, title, excludePoints = [] }) => {
  // Add debugging
  console.log('ScatterPlot received data:', data);
  console.log('xKey:', xKey, 'yKey:', yKey);
  
  // Handle different data formats
  let chartData = [];
  
  if (!data) {
    return <div className="p-4 text-red-500">No data available for scatter plot (data is null/undefined)</div>;
  }
  
  // Check various possible data structures
  if (data.data && Array.isArray(data.data)) {
    console.log('Using data.data array format');
    chartData = data.data;
    // Use the keys provided by the backend if available
    if (data.x_key) xKey = data.x_key;
    if (data.y_key) yKey = data.y_key;
  } else if (Array.isArray(data)) {
    console.log('Using direct array format');
    chartData = data;
  } else if (typeof data === 'object' && data !== null) {
    // Try to extract data from other potential formats
    console.log('Trying to extract data from object');
    
    // Check if data has properties that might be arrays
    const possibleArrayProps = Object.keys(data).filter(key => 
      Array.isArray(data[key]) && data[key].length > 0
    );
    
    if (possibleArrayProps.length > 0) {
      console.log('Found array properties:', possibleArrayProps);
      // Use the first array property as data
      chartData = data[possibleArrayProps[0]];
    } else {
      // If no arrays found, try to convert the object itself to an array
      console.log('No array properties found, trying to use object keys');
      const keys = Object.keys(data);
      if (keys.length >= 2) {
        // Assume first key is x and second is y
        const xValues = data[keys[0]];
        const yValues = data[keys[1]];
        
        if (Array.isArray(xValues) && Array.isArray(yValues) && 
            xValues.length === yValues.length) {
          console.log('Creating points from parallel arrays');
          chartData = xValues.map((x, i) => ({ x, y: yValues[i] }));
        }
      }
    }
  }
  
  console.log('Processed chartData:', chartData);
  
  if (!chartData || chartData.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow mb-8">
        <h3 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">{title}</h3>
        <div className="p-4 text-red-500">
          No data available for scatter plot. 
          <pre className="mt-2 text-xs bg-gray-100 p-2 rounded">
            {JSON.stringify(data, null, 2)}
          </pre>
        </div>
      </div>
    );
  }

  // Filter out excluded points (like Sydney)
  chartData = chartData.filter(item => {
    // Check for suburb name in different possible formats
    const suburbName = item.SUBURB_NAME || item.suburb_name || item.suburbName || '';
    return !excludePoints.includes(suburbName.toLowerCase());
  });

  // Convert data to the format expected by Chart.js
  let formattedData;
  if (chartData[0] && typeof chartData[0].x !== 'undefined' && typeof chartData[0].y !== 'undefined') {
    // Data is already in {x, y} format
    console.log('Data already in x,y format');
    formattedData = chartData;
  } else {
    // Convert from array of objects to {x, y} format
    console.log(`Converting data using keys: ${xKey}, ${yKey}`);
    formattedData = chartData.map(item => {
      // Check if the keys exist in the item
      if (typeof item[xKey] === 'undefined' || typeof item[yKey] === 'undefined') {
        console.warn('Missing keys in data item:', item);
        return null;
      }
      return {
        x: item[xKey],
        y: item[yKey],
        label: item.SUBURB_NAME || item.suburb_name || ''
      };
    }).filter(item => item !== null);
  }

  console.log('Final formatted data:', formattedData);
  
  if (formattedData.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow mb-8">
        <h3 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">{title}</h3>
        <div className="p-4 text-red-500">
          Could not format data for scatter plot. Keys may be incorrect.
          <div className="mt-2">
            Looking for keys: {xKey}, {yKey}
          </div>
          <div className="mt-2">
            Available keys: {chartData.length > 0 ? Object.keys(chartData[0]).join(', ') : 'none'}
          </div>
        </div>
      </div>
    );
  }

  const scatterData = {
    datasets: [
      {
        label: title,
        data: formattedData,
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1,
        pointRadius: 6,
        pointHoverRadius: 8,
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
      tooltip: {
        callbacks: {
          label: function(context) {
            const point = context.raw;
            let label = point.label || '';
            if (label) {
              label += ': ';
            }
            label += `(${point.x}, ${point.y})`;
            return label;
          }
        }
      }
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
        <Scatter data={scatterData} options={options} />
      </div>
    </div>
  );
};

export default ScatterPlotChart;