import React, { useState, useEffect } from 'react'
import { BarChart3, Table, AlertCircle, Loader2 } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import toast from 'react-hot-toast'
import { apiService } from '../services/api'

interface DataVisualizationProps {
  sessionId: string | null
  isConnected: boolean
}

interface SchemaInfo {
  session_id: string
  schema: Record<string, {
    columns: Array<{
      name: string
      type: string
    }>
    sample_data: any[]
  }>
}

const COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4', '#84cc16', '#f97316']

const DataVisualization: React.FC<DataVisualizationProps> = ({ sessionId, isConnected }) => {
  const [schemaInfo, setSchemaInfo] = useState<SchemaInfo | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [selectedTable, setSelectedTable] = useState<string | null>(null)

  useEffect(() => {
    if (sessionId && isConnected) {
      loadSchema()
    }
  }, [sessionId, isConnected])

  const loadSchema = async () => {
    if (!sessionId) {
      console.log('DataVisualization: No sessionId provided')
      return
    }

    console.log('DataVisualization: Loading schema for sessionId:', sessionId)
    setIsLoading(true)
    try {
      const schema = await apiService.getSchema(sessionId)
      console.log('DataVisualization: Schema loaded:', schema)
      console.log('DataVisualization: Schema structure:', JSON.stringify(schema, null, 2))
      setSchemaInfo(schema)
      
      // Select first table by default
      const firstTable = Object.keys(schema.schema)[0]
      if (firstTable) {
        setSelectedTable(firstTable)
        console.log('DataVisualization: Selected first table:', firstTable)
      }
    } catch (error) {
      console.error('DataVisualization: Failed to load schema:', error)
      toast.error('Failed to load data schema')
      setSchemaInfo(null) // Ensure we clear any previous data
    } finally {
      setIsLoading(false)
    }
  }

  const generateChartData = (tableName: string) => {
    if (!schemaInfo || !schemaInfo.schema[tableName]) return null

    const tableData = schemaInfo.schema[tableName]
    const sampleData = tableData.sample_data

    // Check if sample_data exists and is an array
    if (!sampleData || !Array.isArray(sampleData) || sampleData.length === 0) {
      console.log(`DataVisualization: No sample data for table ${tableName}`)
      return null
    }

    // Check if columns exist and is an array
    if (!tableData.columns || !Array.isArray(tableData.columns)) {
      console.log(`DataVisualization: No columns data for table ${tableName}`)
      return null
    }

    // Try to find numeric columns for charts
    const numericColumns = tableData.columns.filter(col => 
      col && col.type && (col.type === 'numeric' || col.type === 'integer' || col.type === 'float')
    )

    if (numericColumns.length === 0) {
      console.log(`DataVisualization: No numeric columns found for table ${tableName}`)
      return null
    }

    // Create chart data from sample data
    const chartData = sampleData.map((row, index) => {
      const dataPoint: any = { index: index + 1 }
      numericColumns.forEach(col => {
        dataPoint[col.name] = row[col.name] || 0
      })
      return dataPoint
    })

    return {
      data: chartData,
      numericColumns: numericColumns.map(col => col.name)
    }
  }

  const generatePieData = (tableName: string, columnName: string) => {
    if (!schemaInfo || !schemaInfo.schema[tableName]) return null

    const tableData = schemaInfo.schema[tableName]
    const sampleData = tableData.sample_data

    // Check if sample_data exists and is an array
    if (!sampleData || !Array.isArray(sampleData) || sampleData.length === 0) {
      console.log(`DataVisualization: No sample data for pie chart in table ${tableName}`)
      return null
    }

    // Count occurrences of each value
    const counts: Record<string, number> = {}
    sampleData.forEach(row => {
      const value = row[columnName] || 'Unknown'
      counts[value] = (counts[value] || 0) + 1
    })

    return Object.entries(counts).map(([name, value], index) => ({
      name,
      value,
      color: COLORS[index % COLORS.length]
    }))
  }

  if (!sessionId) {
    console.log('DataVisualization: Rendering no session state')
    return (
      <div className="card text-center">
        <BarChart3 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">No Data Available</h3>
        <p className="text-gray-600 mb-4">
          Please upload a data file first to view visualizations.
        </p>
        <p className="text-sm text-gray-500">
          Go to the Upload tab to get started.
        </p>
      </div>
    )
  }

  if (isLoading) {
    console.log('DataVisualization: Rendering loading state')
    return (
      <div className="card text-center">
        <Loader2 className="w-16 h-16 text-primary-600 mx-auto mb-4 animate-spin" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Loading Data Schema</h3>
        <p className="text-gray-600">Please wait while we load your data structure...</p>
        <p className="text-sm text-gray-500 mt-2">Session ID: {sessionId}</p>
      </div>
    )
  }

  if (!schemaInfo) {
    console.log('DataVisualization: Rendering no schema state')
    return (
      <div className="card text-center">
        <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Failed to Load Data</h3>
        <p className="text-gray-600 mb-4">
          We couldn't load your data schema. Please try again.
        </p>
        <div className="space-y-2">
          <p className="text-sm text-gray-500">Session ID: {sessionId}</p>
          <p className="text-sm text-gray-500">Connection: {isConnected ? 'Connected' : 'Disconnected'}</p>
        </div>
        <button onClick={loadSchema} className="btn-primary mt-4">
          Retry
        </button>
      </div>
    )
  }

  console.log('DataVisualization: Rendering main content with schema:', schemaInfo)
  const tables = Object.keys(schemaInfo.schema)
  
  // Check if we have any tables
  if (tables.length === 0) {
    console.log('DataVisualization: No tables found in schema')
    return (
      <div className="card text-center">
        <AlertCircle className="w-16 h-16 text-yellow-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">No Tables Found</h3>
        <p className="text-gray-600 mb-4">
          The data schema was loaded but no tables were found.
        </p>
        <div className="space-y-2">
          <p className="text-sm text-gray-500">Session ID: {sessionId}</p>
          <p className="text-sm text-gray-500">Schema keys: {Object.keys(schemaInfo).join(', ')}</p>
        </div>
        <button onClick={loadSchema} className="btn-primary mt-4">
          Retry
        </button>
      </div>
    )
  }
  
  const chartData = selectedTable ? generateChartData(selectedTable) : null
  
  // Debug logging
  if (selectedTable) {
    console.log(`DataVisualization: Selected table: ${selectedTable}`)
    console.log(`DataVisualization: Table data:`, schemaInfo.schema[selectedTable])
    console.log(`DataVisualization: Chart data result:`, chartData)
  }

  return (
    <div className="space-y-6">
      {/* Table Selection */}
      <div className="card">
        <div className="flex items-center space-x-3 mb-4">
          <Table className="w-6 h-6 text-primary-600" />
          <h2 className="text-xl font-bold text-gray-900">Data Tables</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {tables.map((tableName) => {
            const tableInfo = schemaInfo.schema[tableName]
            const isSelected = selectedTable === tableName
            
            return (
              <button
                key={tableName}
                onClick={() => setSelectedTable(tableName)}
                className={`p-4 rounded-lg border-2 text-left transition-colors duration-200 ${
                  isSelected
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <h3 className="font-medium text-gray-900 mb-2">{tableName}</h3>
                <div className="text-sm text-gray-600">
                  <p>{tableInfo.columns?.length || 0} columns</p>
                  <p>{tableInfo.sample_data?.length || 0} sample rows</p>
                </div>
              </button>
            )
          })}
        </div>
      </div>

      {/* Table Schema */}
      {selectedTable && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Table Schema: {selectedTable}
          </h3>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Column Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Data Type
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {schemaInfo.schema[selectedTable]?.columns?.map((column, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {column?.name || 'Unknown'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {column?.type || 'Unknown'}
                      </span>
                    </td>
                  </tr>
                )) || []}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Sample Data */}
      {selectedTable && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Sample Data: {selectedTable}
          </h3>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  {schemaInfo.schema[selectedTable].columns.map((column, index) => (
                    <th
                      key={index}
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      {column.name}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {schemaInfo.schema[selectedTable].sample_data.map((row, rowIndex) => (
                  <tr key={rowIndex}>
                    {schemaInfo.schema[selectedTable].columns.map((column, colIndex) => (
                      <td
                        key={colIndex}
                        className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                      >
                        {row[column.name] || '-'}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Charts */}
      {selectedTable && chartData && (
        <div className="card">
          <div className="flex items-center space-x-3 mb-6">
            <BarChart3 className="w-6 h-6 text-primary-600" />
            <h3 className="text-lg font-semibold text-gray-900">Data Visualizations</h3>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Bar Chart */}
            {chartData.numericColumns.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-900 mb-4">Numeric Data Distribution</h4>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData.data}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="index" />
                      <YAxis />
                      <Tooltip />
                      {chartData.numericColumns.map((column, index) => (
                        <Bar
                          key={column}
                          dataKey={column}
                          fill={COLORS[index % COLORS.length]}
                        />
                      ))}
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}

            {/* Pie Chart for categorical data */}
            {selectedTable && (
              <div>
                <h4 className="font-medium text-gray-900 mb-4">Categorical Distribution</h4>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={generatePieData(selectedTable, schemaInfo.schema[selectedTable].columns[0]?.name || '')}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {generatePieData(selectedTable, schemaInfo.schema[selectedTable].columns[0]?.name || '')?.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* No Charts Available */}
      {selectedTable && !chartData && (
        <div className="card text-center">
          <BarChart3 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No Charts Available</h3>
          <p className="text-gray-600 mb-4">
            This table doesn't have the data needed for visualization.
          </p>
          <div className="text-sm text-gray-500 space-y-1">
            <p>• No numeric columns found for charts</p>
            <p>• No sample data available</p>
            <p>• Data structure may be incomplete</p>
          </div>
          <div className="mt-4 p-3 bg-gray-50 rounded-lg text-left">
            <p className="text-xs text-gray-600 font-mono">
              Table: {selectedTable}
            </p>
            <p className="text-xs text-gray-600 font-mono">
              Columns: {schemaInfo.schema[selectedTable]?.columns?.length || 0}
            </p>
            <p className="text-xs text-gray-600 font-mono">
              Sample data: {schemaInfo.schema[selectedTable]?.sample_data?.length || 0} rows
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

export default DataVisualization
