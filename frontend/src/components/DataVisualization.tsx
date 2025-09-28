import React, { useState, useEffect } from 'react'
import { BarChart3, Table, AlertCircle } from 'lucide-react'
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
      <div className="card-elevated text-center animate-scale-in">
        <div className="w-24 h-24 bg-gradient-primary rounded-3xl flex items-center justify-center mx-auto mb-6 animate-float">
          <BarChart3 className="w-12 h-12 text-white" />
        </div>
        <h3 className="text-2xl font-bold text-gray-900 mb-3">No Data Available</h3>
        <p className="text-gray-600 mb-6 text-lg">
          Please upload a data file first to view visualizations.
        </p>
        <div className="bg-primary-50 rounded-xl p-4 border border-primary-200">
          <p className="text-sm text-primary-700 font-medium">
            📊 Go to the Upload tab to get started
          </p>
        </div>
      </div>
    )
  }

  if (isLoading) {
    console.log('DataVisualization: Rendering loading state')
    return (
      <div className="card-elevated text-center animate-scale-in">
        <div className="w-24 h-24 bg-gradient-primary rounded-3xl flex items-center justify-center mx-auto mb-6 animate-pulse">
          <BarChart3 className="w-12 h-12 text-white" />
        </div>
        <h3 className="text-2xl font-bold text-gray-900 mb-3">Loading Data Schema</h3>
        <p className="text-gray-600 mb-4">Please wait while we load your data structure...</p>
        <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
          <p className="text-sm text-gray-500 font-mono">Session ID: {sessionId}</p>
        </div>
      </div>
    )
  }

  if (!schemaInfo) {
    console.log('DataVisualization: Rendering no schema state')
    return (
      <div className="card-elevated text-center animate-scale-in">
        <div className="w-24 h-24 bg-gradient-error rounded-3xl flex items-center justify-center mx-auto mb-6">
          <AlertCircle className="w-12 h-12 text-white" />
        </div>
        <h3 className="text-2xl font-bold text-gray-900 mb-3">Failed to Load Data</h3>
        <p className="text-gray-600 mb-6 text-lg">
          We couldn't load your data schema. Please try again.
        </p>
        <div className="space-y-3 mb-6">
          <div className="bg-gray-50 rounded-xl p-3 border border-gray-200">
            <p className="text-sm text-gray-500 font-mono">Session ID: {sessionId}</p>
          </div>
          <div className="bg-gray-50 rounded-xl p-3 border border-gray-200">
            <p className="text-sm text-gray-500 font-mono">
              Connection: {isConnected ? 'Connected' : 'Disconnected'}
            </p>
          </div>
        </div>
        <button onClick={loadSchema} className="btn-primary">
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
      <div className="card-elevated text-center animate-scale-in">
        <div className="w-24 h-24 bg-gradient-warning rounded-3xl flex items-center justify-center mx-auto mb-6">
          <AlertCircle className="w-12 h-12 text-white" />
        </div>
        <h3 className="text-2xl font-bold text-gray-900 mb-3">No Tables Found</h3>
        <p className="text-gray-600 mb-6 text-lg">
          The data schema was loaded but no tables were found.
        </p>
        <div className="space-y-3 mb-6">
          <div className="bg-gray-50 rounded-xl p-3 border border-gray-200">
            <p className="text-sm text-gray-500 font-mono">Session ID: {sessionId}</p>
          </div>
          <div className="bg-gray-50 rounded-xl p-3 border border-gray-200">
            <p className="text-sm text-gray-500 font-mono">
              Schema keys: {Object.keys(schemaInfo).join(', ')}
            </p>
          </div>
        </div>
        <button onClick={loadSchema} className="btn-primary">
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
    <div className="space-y-8 animate-fade-in">
      {/* Table Selection */}
      <div className="card-elevated">
        <div className="flex items-center space-x-4 mb-6">
          <div className="w-12 h-12 bg-gradient-primary rounded-xl flex items-center justify-center">
            <Table className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Data Tables</h2>
            <p className="text-gray-600">Select a table to view its structure and data</p>
          </div>
        </div>

        <div className="grid-responsive-3">
          {tables.map((tableName) => {
            const tableInfo = schemaInfo.schema[tableName]
            const isSelected = selectedTable === tableName
            
            return (
              <button
                key={tableName}
                onClick={() => setSelectedTable(tableName)}
                className={`p-6 rounded-2xl border-2 text-left transition-all duration-300 hover:scale-105 min-h-[120px] ${
                  isSelected
                    ? 'border-primary-500 bg-primary-50 shadow-lg'
                    : 'border-gray-200 hover:border-primary-300 hover:shadow-md'
                }`}
              >
                <div className="flex items-start space-x-3 mb-3">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                    isSelected ? 'bg-primary-500' : 'bg-gray-200'
                  }`}>
                    <Table className={`w-4 h-4 ${
                      isSelected ? 'text-white' : 'text-gray-600'
                    }`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-gray-900 break-all text-sm leading-tight" title={tableName}>
                      {tableName}
                    </h3>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                    <span>{tableInfo.columns?.length || 0} columns</span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                    <span>{tableInfo.sample_data?.length || 0} sample rows</span>
                  </div>
                </div>
              </button>
            )
          })}
        </div>
      </div>

      {/* Table Schema */}
      {selectedTable && (
        <div className="card-elevated">
          <div className="flex items-center space-x-3 mb-6">
            <div className="w-10 h-10 bg-gradient-accent rounded-xl flex items-center justify-center">
              <Table className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900">Table Schema</h3>
              <p className="text-gray-600 break-all text-sm" title={selectedTable}>
                {selectedTable && selectedTable.length > 30 ? `${selectedTable.substring(0, 30)}...` : selectedTable}
              </p>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gradient-to-r from-gray-50 to-gray-100">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider min-w-[200px]">
                    Column Name
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider min-w-[150px]">
                    Data Type
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {schemaInfo.schema[selectedTable]?.columns?.map((column, index) => (
                  <tr key={index} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900 break-words max-w-[200px]">
                      <span className="block truncate" title={column?.name || 'Unknown'}>
                        {column?.name || 'Unknown'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500 break-words max-w-[150px]">
                      <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-800 truncate" title={column?.type || 'Unknown'}>
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
        <div className="card-elevated">
          <div className="flex items-center space-x-3 mb-6">
            <div className="w-10 h-10 bg-gradient-success rounded-xl flex items-center justify-center">
              <Table className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900">Sample Data</h3>
              <p className="text-gray-600 break-all text-sm" title={selectedTable}>
                {selectedTable && selectedTable.length > 30 ? `${selectedTable.substring(0, 30)}...` : selectedTable}
              </p>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gradient-to-r from-gray-50 to-gray-100">
                <tr>
                  {schemaInfo.schema[selectedTable].columns.map((column, index) => (
                    <th
                      key={index}
                      className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider min-w-[120px]"
                    >
                      <span className="block truncate" title={column.name}>
                        {column.name}
                      </span>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {schemaInfo.schema[selectedTable].sample_data.map((row, rowIndex) => (
                  <tr key={rowIndex} className="hover:bg-gray-50 transition-colors">
                    {schemaInfo.schema[selectedTable].columns.map((column, colIndex) => (
                      <td
                        key={colIndex}
                        className="px-6 py-4 text-sm text-gray-900 max-w-[200px]"
                      >
                        <span className="block truncate" title={String(row[column.name] || '-')}>
                          {row[column.name] || '-'}
                        </span>
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
        <div className="card-elevated">
          <div className="flex items-center space-x-4 mb-8">
            <div className="w-12 h-12 bg-gradient-accent rounded-xl flex items-center justify-center">
              <BarChart3 className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-gray-900">Data Visualizations</h3>
              <p className="text-gray-600">Interactive charts and graphs for your data</p>
            </div>
          </div>

          <div className="grid-responsive-2">
            {/* Bar Chart */}
            {chartData.numericColumns.length > 0 && (
              <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl p-6 border border-blue-200">
                <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                  <BarChart3 className="w-5 h-5 mr-2 text-blue-600" />
                  Numeric Data Distribution
                </h4>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData.data}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                      <XAxis dataKey="index" stroke="#6b7280" />
                      <YAxis stroke="#6b7280" />
                      <Tooltip 
                        contentStyle={{
                          backgroundColor: 'white',
                          border: '1px solid #e5e7eb',
                          borderRadius: '8px',
                          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                        }}
                      />
                      {chartData.numericColumns.map((column, index) => (
                        <Bar
                          key={column}
                          dataKey={column}
                          fill={COLORS[index % COLORS.length]}
                          radius={[4, 4, 0, 0]}
                        />
                      ))}
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}

            {/* Pie Chart for categorical data */}
            {selectedTable && (
              <div className="bg-gradient-to-br from-green-50 to-blue-50 rounded-2xl p-6 border border-green-200">
                <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                  <BarChart3 className="w-5 h-5 mr-2 text-green-600" />
                  Categorical Distribution
                </h4>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={generatePieData(selectedTable, schemaInfo.schema[selectedTable].columns[0]?.name || '') || []}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={100}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {(generatePieData(selectedTable, schemaInfo.schema[selectedTable].columns[0]?.name || '') || []).map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip 
                        contentStyle={{
                          backgroundColor: 'white',
                          border: '1px solid #e5e7eb',
                          borderRadius: '8px',
                          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                        }}
                      />
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
        <div className="card-elevated text-center animate-scale-in">
          <div className="w-24 h-24 bg-gradient-warning rounded-3xl flex items-center justify-center mx-auto mb-6">
            <BarChart3 className="w-12 h-12 text-white" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-3">No Charts Available</h3>
          <p className="text-gray-600 mb-6 text-lg">
            This table doesn't have the data needed for visualization.
          </p>
          <div className="bg-gray-50 rounded-xl p-6 border border-gray-200 mb-6">
            <div className="text-sm text-gray-600 space-y-3">
              <div className="flex items-center justify-center space-x-2">
                <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                <span>No numeric columns found for charts</span>
              </div>
              <div className="flex items-center justify-center space-x-2">
                <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                <span>No sample data available</span>
              </div>
              <div className="flex items-center justify-center space-x-2">
                <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                <span>Data structure may be incomplete</span>
              </div>
            </div>
          </div>
          <div className="bg-gray-100 rounded-xl p-4 text-left">
            <h4 className="font-semibold text-gray-900 mb-3">Debug Information</h4>
            <div className="space-y-2 text-sm text-gray-600 font-mono">
              <p>Table: {selectedTable}</p>
              <p>Columns: {schemaInfo.schema[selectedTable]?.columns?.length || 0}</p>
              <p>Sample data: {schemaInfo.schema[selectedTable]?.sample_data?.length || 0} rows</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default DataVisualization
