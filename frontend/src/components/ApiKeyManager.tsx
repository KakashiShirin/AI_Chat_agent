import React, { useState, useEffect } from 'react'
import { Key, Plus, Eye, EyeOff, AlertCircle, Loader2, Cpu, RefreshCw } from 'lucide-react'
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
  const [modelStatus, setModelStatus] = useState<any>(null)
  const [isResettingModel, setIsResettingModel] = useState(false)

  useEffect(() => {
    if (isConnected) {
      loadApiKeyStatus()
      loadCreditUsage()
      loadModelStatus()
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

  const clearAllData = async () => {
    if (!confirm('Are you sure you want to clear all data? This will remove all chat sessions, uploaded data, and analysis history. This action cannot be undone.')) {
      return
    }

    try {
      await apiService.clearAllData()
      toast.success('All data cleared successfully!')
      await loadApiKeyStatus()
      await loadCreditUsage()
      await loadModelStatus()
    } catch (error) {
      toast.error('Failed to clear all data')
    }
  }

  const loadModelStatus = async () => {
    try {
      const status = await apiService.getModelStatus()
      setModelStatus(status)
    } catch (error) {
      console.error('Failed to load model status:', error)
    }
  }

  const resetToPrimaryModel = async () => {
    setIsResettingModel(true)
    try {
      await apiService.resetToPrimaryModel()
      toast.success('Model reset to primary model!')
      await loadModelStatus()
    } catch (error) {
      toast.error('Failed to reset model')
    } finally {
      setIsResettingModel(false)
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
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Add API Key */}
      <div className="card-elevated animate-scale-in">
        <div className="flex items-center space-x-4 mb-8">
          <div className="w-12 h-12 bg-gradient-primary rounded-xl flex items-center justify-center">
            <Key className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Manage API Keys</h2>
            <p className="text-gray-600">Add and manage your Gemini API keys for AI analysis</p>
          </div>
        </div>

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              Add New Gemini API Key
            </label>
            <div className="flex space-x-3">
              <div className="flex-1 relative">
                <input
                  type={showApiKey ? 'text' : 'password'}
                  value={newApiKey}
                  onChange={(e) => setNewApiKey(e.target.value)}
                  placeholder="Enter your Gemini API key..."
                  className="input-field pr-12"
                  disabled={!isConnected}
                />
                <button
                  type="button"
                  onClick={() => setShowApiKey(!showApiKey)}
                  className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                >
                  {showApiKey ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
              
              <button
                onClick={validateApiKey}
                disabled={!newApiKey.trim() || !isConnected || isValidating}
                className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed px-6"
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
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed px-6"
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

          <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-200">
            <h3 className="font-semibold text-blue-900 mb-3 flex items-center">
              <Key className="w-5 h-5 mr-2" />
              API Key Information
            </h3>
            <ul className="text-sm text-blue-800 space-y-2">
              <li className="flex items-center">
                <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                Get your API key from <a href="https://makersuite.google.com/app/apikey" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline font-medium">Google AI Studio</a>
              </li>
              <li className="flex items-center">
                <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                API keys are used for AI analysis and are rotated automatically
              </li>
              <li className="flex items-center">
                <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                Multiple keys provide better reliability and load distribution
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* API Key Status */}
      {apiKeyStatus && (
        <div className="card-elevated">
          <div className="flex items-center space-x-3 mb-6">
            <div className="w-10 h-10 bg-gradient-accent rounded-xl flex items-center justify-center">
              <Key className="w-5 h-5 text-white" />
            </div>
            <h3 className="text-xl font-bold text-gray-900">API Key Status</h3>
          </div>
          
          <div className="grid-responsive-3 mb-8">
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-2xl border border-blue-200">
              <div className="text-3xl font-bold text-blue-600 mb-2">{apiKeyStatus.total_api_keys}</div>
              <div className="text-sm text-blue-800 font-medium">Total API Keys</div>
            </div>
            <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-2xl border border-green-200">
              <div className="text-3xl font-bold text-green-600 mb-2">{apiKeyStatus.total_calls}</div>
              <div className="text-sm text-green-800 font-medium">Total Calls</div>
            </div>
            <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-2xl border border-purple-200">
              <div className="text-3xl font-bold text-purple-600 mb-2">{apiKeyStatus.total_tokens.toLocaleString()}</div>
              <div className="text-sm text-purple-800 font-medium">Total Tokens</div>
            </div>
          </div>

          {Object.keys(apiKeyStatus.api_key_usage).length > 0 && (
            <div className="space-y-4">
              <h4 className="font-semibold text-gray-900 text-lg">Individual Key Usage</h4>
              <div className="grid-responsive-2">
                {Object.entries(apiKeyStatus.api_key_usage).map(([key, usage], index) => (
                  <div key={key} className="bg-gradient-to-br from-gray-50 to-gray-100 p-6 rounded-2xl border border-gray-200 hover:shadow-md transition-all duration-300">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
                          <Key className="w-4 h-4 text-white" />
                        </div>
                        <div>
                          <span className="font-semibold text-gray-900">
                            Key #{index + 1}
                          </span>
                          <p className="text-sm text-gray-600 font-mono">{maskApiKey(key)}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        {index === 0 && (
                          <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                            Active
                          </span>
                        )}
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          usage.calls_made > 0 ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-600'
                        }`}>
                          {usage.calls_made > 0 ? 'Used' : 'Unused'}
                        </span>
                      </div>
                    </div>
                    
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Calls Made:</span>
                        <span className="font-semibold text-gray-900">{usage.calls_made}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Tokens Used:</span>
                        <span className="font-semibold text-gray-900">{usage.tokens_used.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Last Used:</span>
                        <span className="font-semibold text-gray-900 text-xs">{formatTimestamp(usage.last_used)}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Model Status */}
      {modelStatus && (
        <div className="card-elevated">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-warning rounded-xl flex items-center justify-center">
                <Cpu className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900">AI Model Status</h3>
            </div>
            <button
              onClick={resetToPrimaryModel}
              disabled={isResettingModel || !modelStatus.is_using_fallback}
              className="btn-warning text-sm px-4 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isResettingModel ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <RefreshCw className="w-4 h-4 mr-2" />
              )}
              Reset to Primary
            </button>
          </div>

          <div className="grid-responsive-3 mb-6">
            <div className={`p-6 rounded-2xl border transition-all duration-300 ${
              modelStatus.is_using_fallback 
                ? 'bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200' 
                : 'bg-gradient-to-br from-green-50 to-green-100 border-green-200'
            }`}>
              <div className="flex items-center space-x-3 mb-3">
                <div className={`w-3 h-3 rounded-full ${
                  modelStatus.is_using_fallback ? 'bg-orange-500' : 'bg-green-500'
                }`}></div>
                <span className="font-semibold text-gray-900">Current Model</span>
              </div>
              <div className="text-lg font-bold text-gray-900 mb-1">
                {modelStatus.current_model === 'gemini-2.5-pro' ? 'Gemini 2.5 Pro' : 
                 modelStatus.current_model === 'gemini-2.5-flash' ? 'Gemini 2.5 Flash' : 
                 'Gemini 2.5 Flash-Lite'}
              </div>
              <div className="text-sm text-gray-600">
                {modelStatus.is_using_fallback ? 'Using fallback model' : 'Using primary model'}
              </div>
            </div>

            <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-2xl border border-blue-200">
              <div className="flex items-center space-x-3 mb-3">
                <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                <span className="font-semibold text-gray-900">Primary Model</span>
              </div>
              <div className="text-lg font-bold text-gray-900 mb-1">Gemini 2.5 Pro</div>
              <div className="text-sm text-gray-600">Most advanced thinking model</div>
            </div>

            <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-2xl border border-purple-200">
              <div className="flex items-center space-x-3 mb-3">
                <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                <span className="font-semibold text-gray-900">Fallback Models</span>
              </div>
              <div className="text-lg font-bold text-gray-900 mb-1">2.5 Flash → Flash-Lite</div>
              <div className="text-sm text-gray-600">Price-performance → Cost-efficient</div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-gray-50 to-gray-100 p-6 rounded-2xl border border-gray-200">
            <h4 className="font-semibold text-gray-900 mb-4">Model Configuration</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Current Model:</span>
                  <span className="font-semibold text-gray-900">{modelStatus.current_model}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Primary Model:</span>
                  <span className="font-semibold text-gray-900">{modelStatus.primary_model}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Fallback Model:</span>
                  <span className="font-semibold text-gray-900">{modelStatus.fallback_model}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Tertiary Model:</span>
                  <span className="font-semibold text-gray-900">{modelStatus.tertiary_model}</span>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">API Keys:</span>
                  <span className="font-semibold text-gray-900">{modelStatus.api_keys_count}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Total Calls:</span>
                  <span className="font-semibold text-gray-900">{modelStatus.total_calls}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Total Tokens:</span>
                  <span className="font-semibold text-gray-900">{modelStatus.total_tokens.toLocaleString()}</span>
                </div>
              </div>
            </div>
          </div>

          {modelStatus.is_using_fallback && (
            <div className="mt-4 p-4 bg-orange-50 border border-orange-200 rounded-xl">
              <div className="flex items-center space-x-2 text-orange-800">
                <AlertCircle className="w-4 h-4" />
                <span className="text-sm font-medium">Using Fallback Model</span>
              </div>
              <p className="text-sm text-orange-700 mt-1">
                The system has automatically switched to a fallback model due to rate limits or quota issues with Gemini 2.5 Pro.
                Current fallback chain: Pro → Flash → Flash-Lite. You can reset to the primary model using the button above.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Credit Usage */}
      {creditUsage && (
        <div className="card-elevated">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-success rounded-xl flex items-center justify-center">
                <Key className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900">Credit Usage</h3>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={resetCredits}
                className="btn-warning text-sm px-4 py-2"
              >
                Reset Tracking
              </button>
              <button
                onClick={clearAllData}
                className="btn-error text-sm px-4 py-2"
              >
                Clear All Data
              </button>
            </div>
          </div>

          <div className="grid-responsive-2">
            <div className="bg-gradient-to-br from-gray-50 to-gray-100 p-6 rounded-2xl border border-gray-200">
              <div className="text-2xl font-bold text-gray-900 mb-2">{creditUsage.total_api_calls}</div>
              <div className="text-sm text-gray-600 font-medium">Total API Calls</div>
            </div>
            <div className="bg-gradient-to-br from-gray-50 to-gray-100 p-6 rounded-2xl border border-gray-200">
              <div className="text-2xl font-bold text-gray-900 mb-2">{creditUsage.total_tokens_used.toLocaleString()}</div>
              <div className="text-sm text-gray-600 font-medium">Total Tokens</div>
            </div>
            <div className="bg-gradient-to-br from-gray-50 to-gray-100 p-6 rounded-2xl border border-gray-200">
              <div className="text-2xl font-bold text-gray-900 mb-2">${creditUsage.estimated_cost_usd.toFixed(6)}</div>
              <div className="text-sm text-gray-600 font-medium">Estimated Cost</div>
            </div>
            <div className="bg-gradient-to-br from-gray-50 to-gray-100 p-6 rounded-2xl border border-gray-200">
              <div className="text-2xl font-bold text-gray-900 mb-2">{creditUsage.api_keys_count}</div>
              <div className="text-sm text-gray-600 font-medium">Active Keys</div>
            </div>
          </div>
        </div>
      )}

      {/* Connection Status */}
      {!isConnected && (
        <div className="card-elevated bg-error-50 border-error-200">
          <div className="flex items-center space-x-3 text-error-800">
            <AlertCircle className="w-6 h-6" />
            <div>
              <span className="font-semibold text-lg">Backend Connection Lost</span>
              <p className="text-error-700 mt-1">
                Please check your backend server and try again.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ApiKeyManager
