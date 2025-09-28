import React from 'react'
import Chart from './Chart'

const ChartDemo: React.FC = () => {
  // Sample chart data
  const sampleBarData = {
    type: 'bar',
    data: {
      labels: ['Engineering', 'Sales', 'Marketing', 'HR'],
      datasets: [{
        label: 'Employee Count',
        data: [5, 4, 3, 3],
        backgroundColor: ['#3b82f6', '#ef4444', '#10b981', '#f59e0b']
      }]
    }
  }

  const samplePieData = {
    type: 'pie',
    data: {
      labels: ['Engineering', 'Sales', 'Marketing', 'HR'],
      datasets: [{
        data: [5, 4, 3, 3],
        backgroundColor: ['#3b82f6', '#ef4444', '#10b981', '#f59e0b']
      }]
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <h2 className="text-lg font-semibold mb-4">Inline Chart Demo</h2>
        
        <div className="space-y-4">
          <div>
            <p className="text-sm text-gray-700 mb-3">
              Here's a bar chart showing employee distribution by department:
            </p>
            <Chart chartType="bar" chartData={sampleBarData} />
          </div>
          
          <div>
            <p className="text-sm text-gray-700 mb-3">
              And here's a pie chart showing the same data:
            </p>
            <Chart chartType="pie" chartData={samplePieData} />
          </div>
        </div>
      </div>
      
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-semibold text-blue-900 mb-2">✨ New Features:</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• <strong>Inline Integration:</strong> Charts appear directly in chat messages</li>
          <li>• <strong>Interactive Controls:</strong> Expand/collapse and fullscreen options</li>
          <li>• <strong>Context Preservation:</strong> Charts stay with their related chat message</li>
          <li>• <strong>Responsive Design:</strong> Adapts to different screen sizes</li>
          <li>• <strong>Hover Details:</strong> Interactive tooltips with data points</li>
          <li>• <strong>Professional Styling:</strong> Clean, modern appearance</li>
        </ul>
      </div>
    </div>
  )
}

export default ChartDemo
