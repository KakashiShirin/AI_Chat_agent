import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { apiService } from '../services/api'

interface FileUploadProps {
  onUploadSuccess: (sessionId: string) => void
  isConnected: boolean
}

const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess, isConnected }) => {
  const [isUploading, setIsUploading] = useState(false)
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)

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
    <div className="max-w-2xl mx-auto">
      <div className="card">
        <div className="text-center mb-6">
          <Upload className="w-16 h-16 text-primary-600 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload Your Data</h2>
          <p className="text-gray-600">
            Upload CSV or Excel files to start analyzing your data with AI
          </p>
        </div>

        {/* Dropzone */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors duration-200 ${
            isDragActive
              ? 'border-primary-500 bg-primary-50'
              : uploadedFile
              ? 'border-green-500 bg-green-50'
              : 'border-gray-300 hover:border-gray-400'
          } ${!isConnected || isUploading ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <input {...getInputProps()} />
          
          {uploadedFile ? (
            <div className="space-y-4">
              <CheckCircle className="w-12 h-12 text-green-500 mx-auto" />
              <div>
                <p className="text-lg font-medium text-gray-900">{uploadedFile.name}</p>
                <p className="text-sm text-gray-500">{formatFileSize(uploadedFile.size)}</p>
              </div>
              <p className="text-sm text-gray-600">
                Click to upload a different file
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              <FileText className="w-12 h-12 text-gray-400 mx-auto" />
              <div>
                <p className="text-lg font-medium text-gray-900">
                  {isDragActive ? 'Drop the file here' : 'Drag & drop your file here'}
                </p>
                <p className="text-sm text-gray-500">or click to browse</p>
              </div>
              <div className="text-xs text-gray-400">
                Supports CSV, XLS, XLSX files up to 10MB
              </div>
            </div>
          )}
        </div>

        {/* File Info */}
        {uploadedFile && (
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <FileText className="w-5 h-5 text-gray-500" />
                <div>
                  <p className="font-medium text-gray-900">{uploadedFile.name}</p>
                  <p className="text-sm text-gray-500">
                    {formatFileSize(uploadedFile.size)} • {uploadedFile.type || 'Unknown type'}
                  </p>
                </div>
              </div>
              
              <button
                onClick={() => setUploadedFile(null)}
                className="text-gray-400 hover:text-gray-600"
                disabled={isUploading}
              >
                <AlertCircle className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}

        {/* Upload Button */}
        {uploadedFile && (
          <div className="mt-6 text-center">
            <button
              onClick={handleUpload}
              disabled={!isConnected || isUploading}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isUploading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4 mr-2" />
                  Upload & Analyze
                </>
              )}
            </button>
          </div>
        )}

        {/* Connection Status */}
        {!isConnected && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center space-x-2 text-red-800">
              <AlertCircle className="w-4 h-4" />
              <span className="text-sm font-medium">Backend connection lost</span>
            </div>
            <p className="text-sm text-red-600 mt-1">
              Please check your backend server and try again.
            </p>
          </div>
        )}

        {/* Instructions */}
        <div className="mt-8 p-4 bg-blue-50 rounded-lg">
          <h3 className="font-medium text-blue-900 mb-2">File Requirements:</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Supported formats: CSV, XLS, XLSX</li>
            <li>• Maximum file size: 10MB</li>
            <li>• First row should contain column headers</li>
            <li>• Data should be in tabular format</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default FileUpload
