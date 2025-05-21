"use client";

import { useState } from "react";
import Image from "next/image";
import dynamic from "next/dynamic";

export default function Dashboard() {
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
      </main>
    </div>
  );
}
