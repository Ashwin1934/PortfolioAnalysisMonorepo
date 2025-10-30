import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const ValuationChart = ({ valuations }) => {
  // Process the data for the chart
  const chartData = valuations.map(val => ({
    date: new Date(val.created_at).toLocaleDateString(),
    growthValuation: val.valuation_growth,
    salesValuation: val.valuation_sales_growth,
    avgPriceTarget: val.avg_price_target
  })).reverse(); // Reverse to show oldest to newest

  return (
    <div className="valuation-chart">
      <h3>Valuation Trends</h3>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="growthValuation" 
            stroke="#8884d8" 
            name="Growth Rate Valuation"
          />
          <Line 
            type="monotone" 
            dataKey="salesValuation" 
            stroke="#82ca9d" 
            name="Sales Growth Valuation"
          />
          <Line 
            type="monotone" 
            dataKey="avgPriceTarget" 
            stroke="#ffc658" 
            name="Average Price Target"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ValuationChart;