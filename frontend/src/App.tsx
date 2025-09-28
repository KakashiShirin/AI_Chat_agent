import React, { useState, useEffect } from 'react'
import { Brain, Upload, Settings, BarChart3, Database } from 'lucide-react'
import ChatInterface from './components/ChatInterface'
import FileUpload from './components/FileUpload'
import ApiKeyManager from './components/ApiKeyManager'
import DataVisualization from './components/DataVisualization'
import DebugInfo from './components/DebugInfo'
import { apiService } from './services/api'

type Tab = 'chat' | 'upload' | 'api-keys' | 'visualization'

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('chat')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    // Check backend connection
    const checkConnection = async () => {
      try {
        await apiService.healthCheck()
        setIsConnected(true)
      } catch (error) {
        setIsConnected(false)
        console.error('Backend connection failed:', error)
      }
    }

    checkConnection()
    const interval = setInterval(checkConnection, 30000) // Check every 30 seconds

    return () => clearInterval(interval)
  }, [])

  const tabs = [
    { id: 'chat' as Tab, label: 'Chat', icon: Brain },
    { id: 'upload' as Tab, label: 'Upload', icon: Upload },
    { id: 'api-keys' as Tab, label: 'API Keys', icon: Settings },
    { id: 'visualization' as Tab, label: 'Data', icon: BarChart3 },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="flex items-center justify-center w-10 h-10 bg-primary-600 rounded-lg">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">AI Data Agent</h1>
                <p className="text-sm text-gray-500">Intelligent Data Analysis</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-sm text-gray-600">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              
              {sessionId && (
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <Database className="w-4 h-4" />
                  <span>Session: {sessionId.slice(0, 8)}...</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              )
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'chat' && (
          <ChatInterface 
            sessionId={sessionId} 
            onSessionChange={setSessionId}
            isConnected={isConnected}
          />
        )}
        
        {activeTab === 'upload' && (
          <FileUpload 
            onUploadSuccess={(newSessionId) => {
              setSessionId(newSessionId)
              setActiveTab('chat')
            }}
            isConnected={isConnected}
          />
        )}
        
        {activeTab === 'api-keys' && (
          <ApiKeyManager isConnected={isConnected} />
        )}
        
        {activeTab === 'visualization' && (
          <DataVisualization 
            sessionId={sessionId}
            isConnected={isConnected}
          />
        )}
      </main>
      
      {/* Debug Info - Remove in production */}
      <DebugInfo 
        sessionId={sessionId}
        isConnected={isConnected}
        activeTab={activeTab}
      />
    </div>
  )
}

export default App
