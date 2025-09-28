import React, { useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { ChevronDown, ChevronUp, Maximize2, Minimize2 } from 'lucide-react'

interface ChartProps {
  chartType: string
  chartData: any
  isInline?: boolean
}

const COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4', '#84cc16', '#f97316']

const Chart: React.FC<ChartProps> = ({ chartType, chartData, isInline = true }) => {
  const [isExpanded, setIsExpanded] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)

  if (!chartData || chartType === 'none') {
    return null
  }

  // Handle different chart data formats
  let processedData = null
  let chartConfig = null

  if (chartData.type === 'bar' && chartData.data) {
    // Chart.js format conversion to Recharts format
    const { labels, datasets } = chartData.data
    processedData = labels.map((label: string, index: number) => ({
      name: label,
      value: datasets[0].data[index],
      fill: datasets[0].backgroundColor?.[index] || COLORS[index % COLORS.length]
    }))
    
    chartConfig = (
      <ResponsiveContainer width="100%" height={isExpanded ? 400 : 200}>
        <BarChart data={processedData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" fontSize={12} />
          <YAxis fontSize={12} />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#f8fafc', 
              border: '1px solid #e2e8f0',
              borderRadius: '6px',
              fontSize: '12px'
            }} 
          />
          <Bar dataKey="value" fill="#3b82f6" radius={[2, 2, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    )
  } else if (chartData.type === 'pie' && chartData.data) {
    // Chart.js format conversion to Recharts format
    const { labels, datasets } = chartData.data
    processedData = labels.map((label: string, index: number) => ({
      name: label,
      value: datasets[0].data[index],
      fill: datasets[0].backgroundColor?.[index] || COLORS[index % COLORS.length]
    }))
    
    chartConfig = (
      <ResponsiveContainer width="100%" height={isExpanded ? 400 : 200}>
        <PieChart>
          <Pie
            data={processedData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            outerRadius={isExpanded ? 100 : 60}
            fill="#8884d8"
            dataKey="value"
          >
            {processedData.map((entry: any, index: number) => (
              <Cell key={`cell-${index}`} fill={entry.fill} />
            ))}
          </Pie>
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#f8fafc', 
              border: '1px solid #e2e8f0',
              borderRadius: '6px',
              fontSize: '12px'
            }} 
          />
        </PieChart>
      </ResponsiveContainer>
    )
  } else if (Array.isArray(chartData)) {
    // Direct array format
    processedData = chartData
    chartConfig = (
      <ResponsiveContainer width="100%" height={isExpanded ? 400 : 200}>
        <BarChart data={processedData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" fontSize={12} />
          <YAxis fontSize={12} />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#f8fafc', 
              border: '1px solid #e2e8f0',
              borderRadius: '6px',
              fontSize: '12px'
            }} 
          />
          <Bar dataKey="value" fill="#3b82f6" radius={[2, 2, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    )
  }

  if (!chartConfig) {
    return (
      <div className="mt-3 p-3 bg-gray-50 rounded-lg text-center text-gray-600 border border-gray-200">
        <p className="text-sm">📊 Chart data available but format not supported</p>
        <p className="text-xs mt-1">Chart type: {chartType}</p>
      </div>
    )
  }

  const chartContainerClass = isFullscreen 
    ? "fixed inset-0 z-50 bg-white p-4 flex flex-col"
    : "mt-3 bg-white border border-gray-200 rounded-lg overflow-hidden"

  return (
    <div className={chartContainerClass}>
      {/* Chart Header */}
      <div className="flex items-center justify-between p-3 bg-gray-50 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
          <h4 className="font-medium text-gray-900 capitalize text-sm">
            {chartType} Chart
          </h4>
          <div className="text-xs text-gray-500 bg-gray-200 px-2 py-1 rounded">
            {processedData?.length || 0} data points
          </div>
        </div>
        
        <div className="flex items-center space-x-1">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1 hover:bg-gray-200 rounded text-gray-600 hover:text-gray-800 transition-colors"
            title={isExpanded ? "Collapse" : "Expand"}
          >
            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
          
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-1 hover:bg-gray-200 rounded text-gray-600 hover:text-gray-800 transition-colors"
            title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}
          >
            {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Chart Content */}
      <div className="p-3">
        {chartConfig}
      </div>

      {/* Chart Footer */}
      <div className="px-3 pb-3 text-xs text-gray-500 bg-gray-50 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <span>Interactive chart - hover for details</span>
          <span>Generated from your data analysis</span>
        </div>
      </div>

      {/* Fullscreen Overlay */}
      {isFullscreen && (
        <div className="flex-1 flex items-center justify-center">
          <div className="w-full h-full max-w-4xl max-h-[80vh]">
            {chartConfig}
          </div>
        </div>
      )}
    </div>
  )
}

export default Chart
