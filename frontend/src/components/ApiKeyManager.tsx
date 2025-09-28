import React, { useState, useEffect } from 'react'
import { Key, Plus, Trash2, Eye, EyeOff, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { apiService, ApiKeyStatus } from '../services/api'

interface ApiKeyManagerProps {
  isConnected: boolean
}

const ApiKeyManager: React.FC<ApiKeyManagerProps> = ({ isConnected }) => {
  const [newApiKey, setNewApiKey] = useState('')
  const [isAdding, setIsAdding] = useState(false)
  const [isValidating, setIsValidating] = useState(false)
  const [apiKeyStatus, setApiKeyStatus] = useState<ApiKeyStatus | null>(null)
  const [showApiKey, setShowApiKey] = useState(false)
  const [creditUsage, setCreditUsage] = useState<any>(null)

  useEffect(() => {
    if (isConnected) {
      loadApiKeyStatus()
      loadCreditUsage()
    }
  }, [isConnected])

  const loadApiKeyStatus = async () => {
    try {
      const status = await apiService.getApiKeyStatus()
      setApiKeyStatus(status)
    } catch (error) {
      console.error('Failed to load API key status:', error)
    }
  }

  const loadCreditUsage = async () => {
    try {
      const usage = await apiService.getCreditUsage()
      setCreditUsage(usage)
    } catch (error) {
      console.error('Failed to load credit usage:', error)
    }
  }

  const validateApiKey = async () => {
    if (!newApiKey.trim()) return

    setIsValidating(true)
    try {
      const result = await apiService.validateApiKey(newApiKey.trim())
      
      if (result.valid) {
        toast.success('API key is valid!')
      } else {
        toast.error(result.message)
      }
    } catch (error) {
      toast.error('Failed to validate API key')
    } finally {
      setIsValidating(false)
    }
  }

  const addApiKey = async () => {
    if (!newApiKey.trim()) return

    setIsAdding(true)
    try {
      const result = await apiService.addApiKey(newApiKey.trim())
      toast.success(`API key added successfully! Total keys: ${result.total_keys}`)
      setNewApiKey('')
      await loadApiKeyStatus()
      await loadCreditUsage()
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to add API key'
      toast.error(errorMessage)
    } finally {
      setIsAdding(false)
    }
  }

  const resetCredits = async () => {
    try {
      await apiService.resetCreditTracking()
      toast.success('Credit tracking reset successfully!')
      await loadCreditUsage()
    } catch (error) {
      toast.error('Failed to reset credit tracking')
    }
  }

  const formatTimestamp = (timestamp?: number) => {
    if (!timestamp) return 'Never'
    return new Date(timestamp * 1000).toLocaleString()
  }

  const maskApiKey = (key: string) => {
    if (key.length <= 8) return key
    return key.slice(0, 4) + '•'.repeat(key.length - 8) + key.slice(-4)
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Add API Key */}
      <div className="card">
        <div className="flex items-center space-x-3 mb-6">
          <Key className="w-6 h-6 text-primary-600" />
          <h2 className="text-xl font-bold text-gray-900">Manage API Keys</h2>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Add New Gemini API Key
            </label>
            <div className="flex space-x-2">
              <div className="flex-1 relative">
                <input
                  type={showApiKey ? 'text' : 'password'}
                  value={newApiKey}
                  onChange={(e) => setNewApiKey(e.target.value)}
                  placeholder="Enter your Gemini API key..."
                  className="input-field pr-10"
                  disabled={!isConnected}
                />
                <button
                  type="button"
                  onClick={() => setShowApiKey(!showApiKey)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showApiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              
              <button
                onClick={validateApiKey}
                disabled={!newApiKey.trim() || !isConnected || isValidating}
                className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isValidating ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  'Validate'
                )}
              </button>
              
              <button
                onClick={addApiKey}
                disabled={!newApiKey.trim() || !isConnected || isAdding}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isAdding ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <>
                    <Plus className="w-4 h-4 mr-2" />
                    Add Key
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="text-sm text-gray-600">
            <p>• Get your API key from <a href="https://makersuite.google.com/app/apikey" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">Google AI Studio</a></p>
            <p>• API keys are used for AI analysis and are rotated automatically</p>
            <p>• Multiple keys provide better reliability and load distribution</p>
          </div>
        </div>
      </div>

      {/* API Key Status */}
      {apiKeyStatus && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">API Key Status</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{apiKeyStatus.total_api_keys}</div>
              <div className="text-sm text-blue-800">Total API Keys</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{apiKeyStatus.total_calls}</div>
              <div className="text-sm text-green-800">Total Calls</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{apiKeyStatus.total_tokens.toLocaleString()}</div>
              <div className="text-sm text-purple-800">Total Tokens</div>
            </div>
          </div>

          {Object.keys(apiKeyStatus.api_key_usage).length > 0 && (
            <div className="space-y-3">
              <h4 className="font-medium text-gray-900">Individual Key Usage:</h4>
              {Object.entries(apiKeyStatus.api_key_usage).map(([key, usage], index) => (
                <div key={key} className="bg-gray-50 p-4 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <Key className="w-4 h-4 text-gray-500" />
                      <span className="font-medium text-gray-900">
                        Key #{index + 1}: {maskApiKey(key)}
                      </span>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Calls:</span>
                      <span className="ml-2 font-medium">{usage.calls_made}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Tokens:</span>
                      <span className="ml-2 font-medium">{usage.tokens_used.toLocaleString()}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Last Used:</span>
                      <span className="ml-2 font-medium">{formatTimestamp(usage.last_used)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Credit Usage */}
      {creditUsage && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Credit Usage</h3>
            <button
              onClick={resetCredits}
              className="btn-secondary text-sm"
            >
              Reset Tracking
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-xl font-bold text-gray-900">{creditUsage.total_api_calls}</div>
              <div className="text-sm text-gray-600">Total API Calls</div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-xl font-bold text-gray-900">{creditUsage.total_tokens_used.toLocaleString()}</div>
              <div className="text-sm text-gray-600">Total Tokens</div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-xl font-bold text-gray-900">${creditUsage.estimated_cost_usd.toFixed(6)}</div>
              <div className="text-sm text-gray-600">Estimated Cost</div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-xl font-bold text-gray-900">{creditUsage.api_keys_count}</div>
              <div className="text-sm text-gray-600">Active Keys</div>
            </div>
          </div>
        </div>
      )}

      {/* Connection Status */}
      {!isConnected && (
        <div className="card bg-red-50 border-red-200">
          <div className="flex items-center space-x-2 text-red-800">
            <AlertCircle className="w-5 h-5" />
            <span className="font-medium">Backend Connection Lost</span>
          </div>
          <p className="text-red-700 mt-2">
            Please check your backend server and try again.
          </p>
        </div>
      )}
    </div>
  )
}

export default ApiKeyManager
