import React from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { Bar, Line, Scatter } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const ChartComponent = ({ type, data, options }) => {
  const renderChart = () => {
    switch (type) {
      case 'bar':
        return <Bar data={data} options={options} />;
      case 'line':
        return <Line data={data} options={options} />;
      case 'scatter':
        return <Scatter data={data} options={options} />;
      default:
        return <p>Unsupported chart type</p>;
    }
  };

  return (
    <div className="chart-container">
      {renderChart()}
    </div>
  );
};

export default ChartComponent;