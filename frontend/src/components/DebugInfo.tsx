import React from 'react'
import { Bug, Database, Wifi, WifiOff } from 'lucide-react'

interface DebugInfoProps {
  sessionId: string | null
  isConnected: boolean
  activeTab: string
}

const DebugInfo: React.FC<DebugInfoProps> = ({ sessionId, isConnected, activeTab }) => {
  return (
    <div className="fixed bottom-4 right-4 bg-white border border-gray-200 rounded-lg p-3 shadow-lg z-50">
      <div className="flex items-center space-x-2 mb-2">
        <Bug className="w-4 h-4 text-gray-600" />
        <span className="text-sm font-medium text-gray-900">Debug Info</span>
      </div>
      
      <div className="space-y-1 text-xs text-gray-600">
        <div className="flex items-center space-x-2">
          <Database className="w-3 h-3" />
          <span>Session: {sessionId ? sessionId.slice(0, 8) + '...' : 'None'}</span>
        </div>
        
        <div className="flex items-center space-x-2">
          {isConnected ? <Wifi className="w-3 h-3 text-green-500" /> : <WifiOff className="w-3 h-3 text-red-500" />}
          <span>Backend: {isConnected ? 'Connected' : 'Disconnected'}</span>
        </div>
        
        <div className="flex items-center space-x-2">
          <span className="w-3 h-3 bg-blue-500 rounded-full"></span>
          <span>Tab: {activeTab}</span>
        </div>
      </div>
    </div>
  )
}

export default DebugInfo
