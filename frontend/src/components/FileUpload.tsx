import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, CheckCircle, AlertCircle, Loader2, X, Key, Sparkles } from 'lucide-react'
import toast from 'react-hot-toast'
import { apiService } from '../services/api'

interface FileUploadProps {
  onUploadSuccess: (sessionId: string) => void
  onNavigateToApiKeys: () => void
  isConnected: boolean
}

const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess, onNavigateToApiKeys, isConnected }) => {
  const [isUploading, setIsUploading] = useState(false)
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [showApiKeyInfo, setShowApiKeyInfo] = useState(false)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (file) {
      setUploadedFile(file)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    },
    multiple: false,
    disabled: !isConnected || isUploading,
  })

  const handleUpload = async () => {
    if (!uploadedFile || !isConnected) return

    setIsUploading(true)
    try {
      const response = await apiService.uploadFile(uploadedFile)
      
      toast.success(`File uploaded successfully! ${response.tables_created} table(s) created.`)
      
      // Show API key information popup after successful upload
      setShowApiKeyInfo(true)
      
      onUploadSuccess(response.session_id)
      
    } catch (error: any) {
      console.error('Upload failed:', error)
      const errorMessage = error.response?.data?.detail || 'Upload failed. Please try again.'
      toast.error(errorMessage)
    } finally {
      setIsUploading(false)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Consolidated Upload Interface */}
      <div className="card-elevated">
        {/* Clickable Animated Header */}
        <div
          {...getRootProps()}
          className={`text-center cursor-pointer transition-all duration-300 ${
            isDragActive
              ? 'scale-105'
              : 'hover:scale-102'
          } ${!isConnected || isUploading ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <input {...getInputProps()} />
          
          <div className={`w-24 h-24 mx-auto mb-6 rounded-3xl flex items-center justify-center animate-float ${
            uploadedFile 
              ? 'bg-gradient-success' 
              : isDragActive 
                ? 'bg-gradient-primary scale-110' 
                : 'bg-gradient-primary'
          }`}>
            {uploadedFile ? (
              <CheckCircle className="w-12 h-12 text-white" />
            ) : (
              <Upload className="w-12 h-12 text-white" />
            )}
          </div>
          
          <h2 className="text-3xl font-bold text-gray-900 mb-3">Upload Your Data</h2>
          <p className="text-gray-600 text-lg mb-2">
            Upload CSV or Excel files to start analyzing your data with AI
          </p>
          
          {uploadedFile ? (
            <div className="space-y-4 animate-scale-in">
              <div>
                <p className="text-xl font-semibold text-gray-900">{uploadedFile.name}</p>
                <p className="text-sm text-gray-500 mt-1">{formatFileSize(uploadedFile.size)}</p>
              </div>
              <p className="text-sm text-gray-600 bg-gray-100 px-4 py-2 rounded-lg inline-block">
                Click to upload a different file
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-lg text-gray-700">
                {isDragActive ? 'Drop the file here' : 'Click here or drag & drop your file'}
              </p>
              <div className="bg-blue-50 rounded-xl p-4 border border-blue-200 max-w-md mx-auto">
                <p className="text-sm text-blue-700 font-medium">
                  Supports CSV, XLS, XLSX files up to 10MB
                </p>
              </div>
            </div>
          )}
        </div>

        {/* File Requirements */}
        <div className="mt-8 p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-200">
          <h3 className="font-semibold text-blue-900 mb-3 flex items-center">
            <FileText className="w-5 h-5 mr-2" />
            File Requirements
          </h3>
          <ul className="text-sm text-blue-800 space-y-2">
            <li className="flex items-center">
              <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
              Supported formats: CSV, XLS, XLSX
            </li>
            <li className="flex items-center">
              <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
              Maximum file size: 10MB
            </li>
            <li className="flex items-center">
              <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
              First row should contain column headers
            </li>
            <li className="flex items-center">
              <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
              Data should be in tabular format
            </li>
          </ul>
        </div>

        {/* Upload Button */}
        {uploadedFile && (
          <div className="text-center mt-8">
            <button
              onClick={handleUpload}
              disabled={!isConnected || isUploading}
              className="btn-success disabled:opacity-50 disabled:cursor-not-allowed px-8 py-4 text-lg"
            >
              {isUploading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin mr-3" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="w-5 h-5 mr-3" />
                  Upload & Analyze
                </>
              )}
            </button>
          </div>
        )}

        {/* Connection Status */}
        {!isConnected && (
          <div className="mt-6 p-4 bg-error-50 border border-error-200 rounded-xl">
            <div className="flex items-center space-x-2 text-error-800">
              <AlertCircle className="w-5 h-5" />
              <span className="text-sm font-medium">Backend connection lost</span>
            </div>
            <p className="text-sm text-error-700 mt-1">
              Please check your backend server and try again.
            </p>
          </div>
        )}

        {/* API Key Information Popup */}
        {showApiKeyInfo && (
          <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black bg-opacity-50">
            <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4 p-6 animate-scale-in">
              {/* Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gradient-primary rounded-lg flex items-center justify-center">
                    <Sparkles className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">API Key Information</h3>
                    <p className="text-sm text-gray-500">Get started with data analysis</p>
                  </div>
                </div>
                <button
                  onClick={() => setShowApiKeyInfo(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Content */}
              <div className="space-y-4">
                <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200">
                  <div className="flex items-start space-x-3">
                    <Key className="w-5 h-5 text-blue-600 mt-0.5" />
                    <div>
                      <h4 className="font-medium text-blue-900 mb-1">Use Your Own API Key</h4>
                      <p className="text-sm text-blue-700">
                        For unlimited usage, add your Gemini API key in the API Keys section.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl border border-green-200">
                  <div className="flex items-start space-x-3">
                    <Sparkles className="w-5 h-5 text-green-600 mt-0.5" />
                    <div>
                      <h4 className="font-medium text-green-900 mb-1">Free Trial Available</h4>
                      <p className="text-sm text-green-700">
                        You can explore the platform with our demo API key for testing purposes.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="text-xs text-gray-500 bg-gray-50 p-3 rounded-lg">
                  <p className="font-medium mb-1">💡 Pro Tip:</p>
                  <p>Add your API key for unlimited queries and better performance. The demo key has usage limits.</p>
                </div>
              </div>

              {/* Footer */}
              <div className="flex items-center justify-between mt-6 pt-4 border-t border-gray-200">
                <button
                  onClick={() => setShowApiKeyInfo(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-800 transition-colors"
                >
                  Got it
                </button>
                <button
                  onClick={() => {
                    setShowApiKeyInfo(false)
                    onNavigateToApiKeys()
                  }}
                  className="px-4 py-2 bg-gradient-primary text-white text-sm font-medium rounded-lg hover:shadow-lg transition-all duration-200"
                >
                  Add API Key
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default FileUpload
