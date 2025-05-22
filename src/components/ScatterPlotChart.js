"use client";

import { Scatter } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend
);

export default function ScatterPlotChart({ data, xKey, yKey, title }) {
  const chartData = {
    datasets: [
      {
        label: title,
        data: data.map(item => ({
          x: item[xKey],
          y: item[yKey],
        })),
        backgroundColor: 'rgba(52, 211, 153, 0.6)',
        borderColor: 'rgba(52, 211, 153, 1)',
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
      title: {
        display: true,
        text: title,
        font: {
          size: 16,
        },
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const point = data[context.dataIndex];
            return point ? `${point.SUBURB_NAME}: (${context.parsed.x}, ${context.parsed.y})` : '';
          },
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
        <Scatter data={chartData} options={options} />
      </div>
    </div>
  );
}