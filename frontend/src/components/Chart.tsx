import React, { useState } from 'react'
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  PieChart, Pie, Cell, LineChart, Line, ScatterChart, Scatter, 
  AreaChart, Area, Legend
} from 'recharts'
import { ChevronDown, ChevronUp, Maximize2, Minimize2, Download, RefreshCw } from 'lucide-react'

interface ChartProps {
  chartType: string
  chartData: any
  isInline?: boolean
}

const COLORS = [
  '#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4', 
  '#84cc16', '#f97316', '#ec4899', '#6366f1', '#14b8a6', '#f43f5e'
]

const CHART_TYPES = {
  bar: 'Bar Chart',
  pie: 'Pie Chart', 
  line: 'Line Chart',
  scatter: 'Scatter Plot',
  area: 'Area Chart',
  composed: 'Composed Chart'
}

const Chart: React.FC<ChartProps> = ({ chartType, chartData }) => {
  const [isExpanded, setIsExpanded] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  if (!chartData || chartType === 'none') {
    return null
  }

  // Handle different chart data formats
  let processedData: any[] | null = null
  let chartConfig = null

  const processChartData = (data: any) => {
    if (data.type && data.data) {
      // Chart.js format conversion to Recharts format
      const { labels, datasets } = data.data
      return labels.map((label: string, index: number) => ({
        name: label,
        value: datasets[0].data[index],
        fill: datasets[0].backgroundColor?.[index] || COLORS[index % COLORS.length]
      }))
    } else if (Array.isArray(data)) {
      return data
    }
    return null
  }

  const handleDownload = () => {
    setIsLoading(true)
    // Simulate download process
    setTimeout(() => {
      setIsLoading(false)
      // In a real implementation, you would generate and download the chart as PNG/SVG
      console.log('Chart download initiated')
    }, 1000)
  }

  const renderChart = () => {
    processedData = processChartData(chartData)
    
    if (!processedData) {
      return (
        <div className="flex items-center justify-center h-48 text-gray-500">
          <div className="text-center">
            <RefreshCw className="w-8 h-8 mx-auto mb-2 animate-spin" />
            <p className="text-sm">Unable to process chart data</p>
          </div>
        </div>
      )
    }

    const chartHeight = isExpanded ? 400 : 250
    const commonProps = {
      width: "100%",
      height: chartHeight,
      data: processedData
    }

    switch (chartType.toLowerCase()) {
      case 'bar':
        return (
          <ResponsiveContainer {...commonProps}>
            <BarChart data={processedData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="name" 
                fontSize={12} 
                tick={{ fill: '#6b7280' }}
                axisLine={{ stroke: '#e5e7eb' }}
              />
              <YAxis 
                fontSize={12} 
                tick={{ fill: '#6b7280' }}
                axisLine={{ stroke: '#e5e7eb' }}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#ffffff', 
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '12px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }} 
                cursor={{ fill: 'rgba(59, 130, 246, 0.1)' }}
              />
              <Bar 
                dataKey="value" 
                fill="#3b82f6" 
                radius={[4, 4, 0, 0]}
                stroke="#2563eb"
                strokeWidth={1}
              />
            </BarChart>
          </ResponsiveContainer>
        )

      case 'pie':
        return (
          <ResponsiveContainer {...commonProps}>
            <PieChart>
              <Pie
                data={processedData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={isExpanded ? 120 : 80}
                fill="#8884d8"
                dataKey="value"
                stroke="#ffffff"
                strokeWidth={2}
              >
                {processedData.map((entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={entry.fill || COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#ffffff', 
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '12px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }} 
              />
              <Legend 
                verticalAlign="bottom" 
                height={36}
                iconType="circle"
                wrapperStyle={{ fontSize: '12px', color: '#6b7280' }}
              />
            </PieChart>
          </ResponsiveContainer>
        )

      case 'line':
        return (
          <ResponsiveContainer {...commonProps}>
            <LineChart data={processedData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="name" 
                fontSize={12} 
                tick={{ fill: '#6b7280' }}
                axisLine={{ stroke: '#e5e7eb' }}
              />
              <YAxis 
                fontSize={12} 
                tick={{ fill: '#6b7280' }}
                axisLine={{ stroke: '#e5e7eb' }}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#ffffff', 
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '12px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }} 
              />
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke="#3b82f6" 
                strokeWidth={3}
                dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, stroke: '#3b82f6', strokeWidth: 2 }}
              />
            </LineChart>
          </ResponsiveContainer>
        )

      case 'scatter':
        return (
          <ResponsiveContainer {...commonProps}>
            <ScatterChart data={processedData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="x" 
                fontSize={12} 
                tick={{ fill: '#6b7280' }}
                axisLine={{ stroke: '#e5e7eb' }}
              />
              <YAxis 
                dataKey="y" 
                fontSize={12} 
                tick={{ fill: '#6b7280' }}
                axisLine={{ stroke: '#e5e7eb' }}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#ffffff', 
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '12px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }} 
              />
              <Scatter 
                dataKey="y" 
                fill="#3b82f6" 
                stroke="#2563eb"
                strokeWidth={1}
              />
            </ScatterChart>
          </ResponsiveContainer>
        )

      case 'area':
        return (
          <ResponsiveContainer {...commonProps}>
            <AreaChart data={processedData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="name" 
                fontSize={12} 
                tick={{ fill: '#6b7280' }}
                axisLine={{ stroke: '#e5e7eb' }}
              />
              <YAxis 
                fontSize={12} 
                tick={{ fill: '#6b7280' }}
                axisLine={{ stroke: '#e5e7eb' }}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#ffffff', 
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '12px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }} 
              />
              <Area 
                type="monotone" 
                dataKey="value" 
                stroke="#3b82f6" 
                fill="url(#colorGradient)"
                strokeWidth={2}
              />
              <defs>
                <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
            </AreaChart>
          </ResponsiveContainer>
        )

      default:
        return (
          <div className="flex items-center justify-center h-48 text-gray-500">
            <div className="text-center">
              <RefreshCw className="w-8 h-8 mx-auto mb-2" />
              <p className="text-sm">Unsupported chart type: {chartType}</p>
            </div>
          </div>
        )
    }
  }

  chartConfig = renderChart()

  if (!chartConfig) {
    return (
      <div className="mt-3 p-4 bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg text-center text-gray-600 border border-gray-200">
        <div className="flex items-center justify-center mb-2">
          <RefreshCw className="w-6 h-6 text-gray-400" />
        </div>
        <p className="text-sm font-medium">Chart data available but format not supported</p>
        <p className="text-xs mt-1 text-gray-500">Chart type: {chartType}</p>
        <p className="text-xs text-gray-400 mt-1">Data points: {Array.isArray(chartData) ? chartData.length : 'Unknown'}</p>
      </div>
    )
  }

  const chartContainerClass = isFullscreen 
    ? "fixed inset-0 z-50 bg-white p-4 flex flex-col"
    : "mt-3 bg-white border border-gray-200 rounded-lg overflow-hidden max-w-full shadow-sm hover:shadow-md transition-shadow duration-200"

  return (
    <div className={chartContainerClass}>
      {/* Chart Header */}
      <div className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
            <h4 className="font-semibold text-gray-900 capitalize text-sm">
              {CHART_TYPES[chartType.toLowerCase() as keyof typeof CHART_TYPES] || `${chartType} Chart`}
            </h4>
          </div>
          <div className="flex items-center space-x-2">
            <div className="text-xs text-gray-600 bg-white px-2 py-1 rounded-full border">
              {processedData ? processedData.length : 0} data points
            </div>
            <div className="text-xs text-gray-500 bg-gray-200 px-2 py-1 rounded-full">
              Interactive
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-1">
          <button
            onClick={handleDownload}
            disabled={isLoading}
            className="p-2 hover:bg-gray-200 rounded-lg text-gray-600 hover:text-gray-800 transition-colors disabled:opacity-50"
            title="Download Chart"
          >
            {isLoading ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Download className="w-4 h-4" />
            )}
          </button>
          
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-2 hover:bg-gray-200 rounded-lg text-gray-600 hover:text-gray-800 transition-colors"
            title={isExpanded ? "Collapse" : "Expand"}
          >
            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
          
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-2 hover:bg-gray-200 rounded-lg text-gray-600 hover:text-gray-800 transition-colors"
            title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}
          >
            {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Chart Content */}
      <div className="p-4 overflow-hidden">
        <div className="w-full max-w-full">
          {chartConfig}
        </div>
      </div>

      {/* Chart Footer */}
      <div className="px-4 py-3 text-xs text-gray-500 bg-gradient-to-r from-gray-50 to-gray-100 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <span className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>Live data</span>
            </span>
            <span>Hover for details</span>
          </div>
          <span className="text-gray-400">Generated from your analysis</span>
        </div>
      </div>

      {/* Fullscreen Overlay */}
      {isFullscreen && (
        <div className="flex-1 flex items-center justify-center bg-gray-50">
          <div className="w-full h-full max-w-6xl max-h-[85vh] p-4">
            <div className="bg-white rounded-lg shadow-lg p-6 h-full">
              {chartConfig}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Chart
