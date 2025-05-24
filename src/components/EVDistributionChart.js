import React from 'react';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';

// Register ChartJS components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const EVDistributionChart = ({ evData }) => {
  // Check if we have the expected data structure
  if (!evData || !evData.labels || !evData.bev_data || !evData.phev_data) {
    // Fallback for different data structure
    if (Array.isArray(evData)) {
      // Transform array data to expected format
      const labels = evData.map(item => item.SUBURB_NAME || item.suburb_name);
      const bevData = evData.map(item => item.BEV_COUNT || item.bev_count);
      const phevData = evData.map(item => item.PHEV_COUNT || item.phev_count);
      
      evData = {
        labels,
        bev_data: bevData,
        phev_data: phevData
      };
    } else {
      return <div className="p-4 text-red-500">Invalid data format for EV Distribution Chart</div>;
    }
  }

  const data = {
    labels: evData.labels,
    datasets: [
      {
        label: 'Battery Electric Vehicles (BEV)',
        data: evData.bev_data,
        backgroundColor: 'rgba(34, 197, 94, 0.8)',
        borderColor: 'rgba(34, 197, 94, 1)',
        borderWidth: 1,
      },
      {
        label: 'Plug-in Hybrid Electric Vehicles (PHEV)',
        data: evData.phev_data,
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
        borderColor: 'rgba(59, 130, 246, 1)',
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
        text: 'Top 10 Suburbs by EV Count (Stacked)',
        font: {
          size: 16,
        },
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        callbacks: {
          footer: function(tooltipItems) {
            let total = 0;
            tooltipItems.forEach(function(tooltipItem) {
              total += tooltipItem.parsed.y;
            });
            return 'Total: ' + total + ' EVs';
          }
        }
      },
    },
    scales: {
      x: {
        stacked: true,
        title: {
          display: true,
          text: 'Suburb',
        },
      },
      y: {
        stacked: true,
        beginAtZero: true,
        title: {
          display: true,
          text: 'Number of Vehicles',
        },
      },
    },
    interaction: {
      mode: 'index',
      intersect: false,
    },
  };

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow mb-8">
      <h3 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">
        EV Distribution by Suburb (Top 10)
      </h3>
      <div className="h-80">
        <Bar data={data} options={options} />
      </div>
    </div>
  );
};

export default EVDistributionChart;
