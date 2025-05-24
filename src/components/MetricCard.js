import React from 'react';

const MetricCard = ({ title, value }) => {
  return (
    <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
          {title}
        </dt>
        <dd className="mt-1 text-3xl font-semibold text-gray-900 dark:text-white">
          {value}
        </dd>
      </div>
    </div>
  );
};

export default MetricCard;