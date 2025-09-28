import React, { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, AlertCircle, Plus, Trash2, Trash } from 'lucide-react'
import toast from 'react-hot-toast'
import { apiService, ChatResponse, ChatSession } from '../services/api'
import Chart from './Chart'

interface Message {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: Date
  chartType?: string
  chartData?: any
  error?: string
}

interface ChatInterfaceProps {
  sessionId: string | null
  onSessionChange: (sessionId: string | null) => void
  isConnected: boolean
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ 
  sessionId, 
  isConnected 
}) => {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([])
  const [activeChatId, setActiveChatId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Initialize chat session when database session is available
  useEffect(() => {
    if (sessionId && isConnected && !activeChatId) {
      initializeChatSession()
    }
  }, [sessionId, isConnected])

  // Load existing chat sessions
  useEffect(() => {
    if (isConnected) {
      loadChatSessions()
    }
  }, [isConnected])

  const initializeChatSession = async () => {
    if (!sessionId) return
    
    try {
      const response = await apiService.createChatSession(sessionId)
      setActiveChatId(response.chat_id)
      toast.success('New chat session created')
    } catch (error) {
      console.error('Failed to create chat session:', error)
      toast.error('Failed to create chat session')
    }
  }

  const loadChatSessions = async () => {
    try {
      console.log('Loading chat sessions...')
      const response = await apiService.getChatSessions()
      console.log('Chat sessions response:', response)
      setChatSessions(response.sessions)
      
      // If no active chat and we have sessions, use the first one
      if (!activeChatId && response.sessions.length > 0) {
        setActiveChatId(response.sessions[0].chat_id)
      }
    } catch (error) {
      console.error('Failed to load chat sessions:', error)
    }
  }

  const createNewChat = async () => {
    if (!sessionId) {
      toast.error('Please upload data first')
      return
    }
    
    try {
      console.log('Creating new chat session for sessionId:', sessionId)
      const response = await apiService.createChatSession(sessionId)
      console.log('Create chat session response:', response)
      setActiveChatId(response.chat_id)
      setMessages([]) // Clear messages for new chat
      toast.success('New chat session created')
      loadChatSessions() // Refresh session list
    } catch (error) {
      console.error('Failed to create new chat:', error)
      toast.error('Failed to create new chat')
    }
  }

  const deleteChat = async (chatId: string) => {
    try {
      console.log('Attempting to delete chat:', chatId)
      const result = await apiService.deleteChatSession(chatId)
      console.log('Delete result:', result)
      
      // If deleting active chat, switch to another or clear
      if (activeChatId === chatId) {
        const remainingSessions = chatSessions.filter(s => s.chat_id !== chatId)
        if (remainingSessions.length > 0) {
          setActiveChatId(remainingSessions[0].chat_id)
        } else {
          setActiveChatId(null)
          setMessages([])
        }
      }
      
      loadChatSessions() // Refresh session list
      toast.success('Chat session deleted')
    } catch (error) {
      console.error('Failed to delete chat:', error)
      toast.error('Failed to delete chat')
    }
  }

  const clearAllData = async () => {
    if (!confirm('Are you sure you want to clear all data? This will remove all chat sessions, uploaded data, and analysis history. This action cannot be undone.')) {
      return
    }

    try {
      console.log('Attempting to clear all data')
      const result = await apiService.clearAllData()
      console.log('Clear all result:', result)
      setActiveChatId(null)
      setMessages([])
      setChatSessions([])
      toast.success('All data cleared successfully!')
    } catch (error) {
      console.error('Failed to clear all data:', error)
      toast.error('Failed to clear all data')
    }
  }

  const switchChat = (chatId: string) => {
    setActiveChatId(chatId)
    setMessages([]) // Clear current messages, will be loaded from context
    loadChatContext(chatId)
  }

  const loadChatContext = async (chatId: string) => {
    try {
      const response = await apiService.getChatContext(chatId)
      const context = response.context
      
      // Convert conversation history to messages
      if (context.conversation_history) {
        const historyMessages: Message[] = context.conversation_history.map((item: any) => ({
          id: `msg-${item.timestamp}`,
          type: item.message.type,
          content: item.message.content,
          timestamp: new Date(item.timestamp * 1000),
          chartType: item.message.chart_type,
          chartData: item.message.chart_data
        }))
        setMessages(historyMessages)
      }
    } catch (error) {
      console.error('Failed to load chat context:', error)
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (sessionId) {
      // Add welcome message when session is available
      const welcomeMessage: Message = {
        id: 'welcome',
        type: 'assistant',
        content: `Welcome! I'm your AI Data Agent. I can help you analyze your data. You can ask me questions like:
        
• "What is the average salary?"
• "How many people are in each department?"
• "Show me the top 5 highest paid employees"
• "What is the data distribution?"

What would you like to know about your data?`,
        timestamp: new Date(),
      }
      setMessages([welcomeMessage])
    } else {
      setMessages([])
    }
  }, [sessionId])

  const handleSendMessage = async () => {
    if (!inputValue.trim() || !activeChatId || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      const response: ChatResponse = await apiService.sendChatMessage(inputValue.trim(), activeChatId)
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: response.answer,
        timestamp: new Date(),
        chartType: response.chart_type,
        chartData: response.chart_data,
        error: response.error,
      }

      setMessages(prev => [...prev, assistantMessage])

      if (response.error) {
        toast.error('Analysis failed. Please try again.')
      } else {
        toast.success('Analysis completed!')
      }
      
      // Refresh chat sessions to update message counts
      loadChatSessions()
    } catch (error) {
      console.error('Query failed:', error)
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'I apologize, but I encountered an error while processing your request. Please try again.',
        timestamp: new Date(),
        error: 'Failed to process query',
      }

      setMessages(prev => [...prev, errorMessage])
      toast.error('Failed to process your query. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  if (!sessionId) {
    return (
      <div className="card-elevated text-center animate-scale-in">
        <div className="w-24 h-24 bg-gradient-primary rounded-3xl flex items-center justify-center mx-auto mb-6 animate-float">
          <Bot className="w-12 h-12 text-white" />
        </div>
        <h3 className="text-2xl font-bold text-gray-900 mb-3">No Data Session</h3>
        <p className="text-gray-600 mb-6 text-lg">
          Please upload a data file first to start chatting with the AI agent.
        </p>
        <div className="bg-primary-50 rounded-xl p-4 border border-primary-200">
          <p className="text-sm text-primary-700 font-medium">
            💡 Go to the Upload tab to get started
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-[800px] bg-white rounded-2xl shadow-large border border-gray-100 overflow-hidden max-w-7xl mx-auto">
      {/* Left Sidebar - Chat Sessions */}
      <div className="w-80 bg-gray-50 border-r border-gray-200 flex flex-col mobile-hidden">
        {/* Header */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <h3 className="font-semibold text-gray-900">Chat Sessions</h3>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={createNewChat}
                className="btn-accent text-xs px-3 py-2"
                title="Create new chat"
              >
                <Plus className="w-3 h-3 mr-1" />
                New
              </button>
              <button
                onClick={clearAllData}
                className="btn-error text-xs px-3 py-2"
                title="Clear all data"
              >
                <Trash className="w-3 h-3 mr-1" />
                Clear All
              </button>
            </div>
          </div>
        </div>

        {/* Sessions List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          {chatSessions.length > 0 ? (
            chatSessions.map((session) => (
              <button
                key={session.chat_id}
                onClick={() => switchChat(session.chat_id)}
                className={`w-full flex items-center justify-between p-3 rounded-xl text-sm transition-all duration-300 hover:shadow-md ${
                  activeChatId === session.chat_id
                    ? 'bg-gradient-primary text-white shadow-lg'
                    : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
                }`}
              >
                <div className="flex items-center space-x-3 flex-1 min-w-0">
                  <div className={`w-2 h-2 rounded-full flex-shrink-0 ${
                    activeChatId === session.chat_id ? 'bg-white' : 'bg-primary-500'
                  }`} />
                  <span className="font-medium truncate">
                    Chat {session.chat_id.slice(0, 8)}...
                  </span>
                </div>
                <div className="flex items-center space-x-2 flex-shrink-0">
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    activeChatId === session.chat_id 
                      ? 'bg-white/20 text-white' 
                      : 'bg-gray-200 text-gray-600'
                  }`}>
                    {session.message_count}
                  </span>
                  <div
                    onClick={(e) => {
                      e.stopPropagation()
                      deleteChat(session.chat_id)
                    }}
                    className={`p-1 rounded-lg transition-colors cursor-pointer ${
                      activeChatId === session.chat_id
                        ? 'hover:bg-white/20 text-white'
                        : 'hover:bg-red-100 text-red-500 hover:text-red-700'
                    }`}
                    title="Delete chat"
                  >
                    <Trash2 className="w-3 h-3" />
                  </div>
                </div>
              </button>
            ))
          ) : (
            <div className="text-center py-8">
              <Bot className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-sm text-gray-500">No chat sessions yet</p>
              <p className="text-xs text-gray-400 mt-1">Create your first chat to get started</p>
            </div>
          )}
        </div>

        {/* Active Chat Info */}
        {activeChatId && (
          <div className="p-4 border-t border-gray-200 bg-white">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse" />
              <span className="text-xs text-gray-600">
                Active: {activeChatId.slice(0, 8)}...
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Right Side - Chat Messages */}
      <div className="flex-1 flex flex-col">
        {/* Mobile Header */}
        <div className="mobile-only p-4 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <h3 className="font-semibold text-gray-900">Chat Sessions</h3>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={createNewChat}
                className="btn-accent text-xs px-3 py-2"
                title="Create new chat"
              >
                <Plus className="w-3 h-3 mr-1" />
                New
              </button>
              <button
                onClick={clearAllData}
                className="btn-error text-xs px-3 py-2"
                title="Clear all data"
              >
                <Trash className="w-3 h-3 mr-1" />
                Clear
              </button>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-5">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'} animate-slide-up`}
            >
              <div
                className={`max-w-4xl w-full rounded-2xl p-5 transition-all duration-300 hover:shadow-lg ${
                  message.type === 'user'
                    ? 'bg-gradient-primary text-white shadow-lg'
                    : 'bg-gray-50 border border-gray-200 shadow-soft'
                } ${message.chartType && message.chartType !== 'none' && message.chartData ? 'pb-0' : ''}`}
              >
                <div className="flex items-start space-x-3">
                  {message.type === 'assistant' && (
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
                        <Bot className="w-4 h-4 text-white" />
                      </div>
                    </div>
                  )}
                  
                  <div className="flex-1 min-w-0 overflow-hidden">
                    <div className="whitespace-pre-wrap text-base leading-6 text-wrap-better">
                      {message.content}
                    </div>
                    
                    {message.error && (
                      <div className="mt-2 flex items-center space-x-2 text-error-600 bg-error-50 px-2 py-1 rounded-lg">
                        <AlertCircle className="w-3 h-3" />
                        <span className="text-xs font-medium">{message.error}</span>
                      </div>
                    )}
                    
                    <div className={`mt-2 text-xs ${
                      message.type === 'user' ? 'text-white/70' : 'text-gray-500'
                    }`}>
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                  
                  {message.type === 'user' && (
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                        <User className="w-4 h-4 text-white" />
                      </div>
                    </div>
                  )}
                </div>
                
                {/* Chart integrated directly in the message */}
                {message.chartType && message.chartType !== 'none' && message.chartData && (
                  <div className="mt-4 -mx-4 -mb-4 overflow-hidden">
                    <div className="bg-gradient-to-br from-white to-gray-50 rounded-b-2xl border-t border-gray-200 max-w-full shadow-sm">
                      <Chart chartType={message.chartType} chartData={message.chartData} />
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start animate-slide-up">
              <div className="bg-gray-50 border border-gray-200 rounded-2xl p-4 shadow-soft">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="loading-dots">
                      <div></div>
                      <div></div>
                      <div></div>
                    </div>
                    <span className="text-sm text-gray-600 font-medium">Analyzing your data...</span>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t border-gray-200 bg-white">
          <div className="flex space-x-3">
            <div className="flex-1">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={activeChatId ? "Ask me anything about your data..." : "Create a chat session to start..."}
                className="input-field resize-none h-12 text-base"
                rows={1}
                disabled={!isConnected || isLoading || !activeChatId}
              />
            </div>
            <button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || !isConnected || isLoading || !activeChatId}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed px-4 h-12"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
          
          {!isConnected && (
            <div className="mt-3 p-3 bg-error-50 border border-error-200 rounded-lg">
              <div className="flex items-center space-x-2 text-error-800">
                <AlertCircle className="w-4 h-4" />
                <span className="text-sm font-medium">Backend connection lost</span>
              </div>
              <p className="text-sm text-error-700 mt-1">
                Please check your backend server and try again.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ChatInterface
