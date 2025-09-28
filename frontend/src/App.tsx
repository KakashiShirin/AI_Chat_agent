import { useState, useEffect } from 'react'
import { Brain, Upload, Settings, BarChart3, Database, Home } from 'lucide-react'
import LandingPage from './components/LandingPage'
import ChatInterface from './components/ChatInterface'
import FileUpload from './components/FileUpload'
import ApiKeyManager from './components/ApiKeyManager'
import DataVisualization from './components/DataVisualization'
import Footer from './components/Footer'
import DebugInfo from './components/DebugInfo'
import { apiService } from './services/api'

type Tab = 'chat' | 'upload' | 'api-keys' | 'visualization'

function App() {
  const [showLanding, setShowLanding] = useState(true)
  const [activeTab, setActiveTab] = useState<Tab>('upload')
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

  const handleStartAgent = () => {
    setShowLanding(false)
    setActiveTab('upload')
  }

  const handleNavigate = (tab: string) => {
    setActiveTab(tab as Tab)
  }

  if (showLanding) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-purple-50/20 flex flex-col">
        <LandingPage onStartAgent={handleStartAgent} />
        <Footer onNavigate={handleNavigate} />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-purple-50/20 flex flex-col">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md shadow-soft border-b border-white/20 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16 sm:h-20">
            <div className="flex items-center space-x-3 sm:space-x-4">
              <button
                onClick={() => setShowLanding(true)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                title="Back to Home"
              >
                <Home className="w-4 h-4 text-gray-600" />
              </button>
              <div className="flex items-center justify-center w-10 h-10 sm:w-12 sm:h-12 bg-gradient-primary rounded-xl sm:rounded-2xl shadow-lg hover:shadow-glow transition-all duration-300 animate-float">
                <Brain className="w-5 h-5 sm:w-7 sm:h-7 text-white" />
              </div>
              <div className="mobile-hidden">
                <h1 className="text-xl sm:text-2xl font-bold text-gradient">AI Data Agent</h1>
                <p className="text-xs sm:text-sm text-gray-600 font-medium">Intelligent Data Analysis</p>
              </div>
              <div className="mobile-only">
                <h1 className="text-lg font-bold text-gradient">AI Agent</h1>
              </div>
            </div>
            
            <div className="flex items-center space-x-3 sm:space-x-6">
              <div className="flex items-center space-x-2 sm:space-x-3">
                <div className={`w-2 h-2 sm:w-3 sm:h-3 rounded-full animate-pulse ${
                  isConnected ? 'bg-success-500 shadow-glow' : 'bg-error-500'
                }`} />
                <span className={`text-xs sm:text-sm font-semibold mobile-hidden ${
                  isConnected ? 'text-success-700' : 'text-error-700'
                }`}>
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              
              {sessionId && (
                <div className="flex items-center space-x-1 sm:space-x-2 px-2 sm:px-4 py-1 sm:py-2 bg-primary-50 rounded-lg sm:rounded-xl border border-primary-200">
                  <Database className="w-3 h-3 sm:w-4 sm:h-4 text-primary-600" />
                  <span className="text-xs sm:text-sm font-medium text-primary-700 mobile-hidden">
                    Session: {sessionId.slice(0, 8)}...
                  </span>
                  <span className="text-xs font-medium text-primary-700 mobile-only">
                    {sessionId.slice(0, 4)}...
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white/60 backdrop-blur-sm border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-2 overflow-x-auto py-2">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`tab-button ${
                    activeTab === tab.id ? 'active' : 'inactive'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="hidden sm:inline">{tab.label}</span>
                </button>
              )
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8">
        <div className="animate-fade-in">
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
              onNavigateToApiKeys={() => setActiveTab('api-keys')}
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
        </div>
      </main>
      
      {/* Footer */}
      <Footer onNavigate={handleNavigate} />
      
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
