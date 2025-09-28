import React, { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Loader2, AlertCircle, Plus, Trash2 } from 'lucide-react'
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
  onSessionChange, 
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
      const response = await apiService.getChatSessions()
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
      const response = await apiService.createChatSession(sessionId)
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
      await apiService.deleteChatSession(chatId)
      
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
      <div className="card text-center">
        <Bot className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">No Data Session</h3>
        <p className="text-gray-600 mb-4">
          Please upload a data file first to start chatting with the AI agent.
        </p>
        <p className="text-sm text-gray-500">
          Go to the Upload tab to get started.
        </p>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-[600px]">
      {/* Chat Session Management */}
      <div className="flex items-center justify-between mb-4 p-3 bg-gray-50 rounded-lg">
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium text-gray-700">Active Chat:</span>
          <span className="text-sm text-gray-600">
            {activeChatId ? `Chat ${activeChatId.slice(0, 8)}...` : 'No active chat'}
          </span>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={createNewChat}
            className="btn-secondary text-xs px-2 py-1"
            title="Create new chat"
          >
            <Plus className="w-3 h-3 mr-1" />
            New Chat
          </button>
        </div>
      </div>

      {/* Chat Sessions List */}
      {chatSessions.length > 0 && (
        <div className="mb-4">
          <div className="flex items-center space-x-2 overflow-x-auto pb-2">
            {chatSessions.map((session) => (
              <button
                key={session.chat_id}
                onClick={() => switchChat(session.chat_id)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm whitespace-nowrap transition-colors ${
                  activeChatId === session.chat_id
                    ? 'bg-primary-100 text-primary-700 border border-primary-200'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                <span>Chat {session.chat_id.slice(0, 8)}...</span>
                <span className="text-xs opacity-75">({session.message_count})</span>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    deleteChat(session.chat_id)
                  }}
                  className="text-red-500 hover:text-red-700"
                  title="Delete chat"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-4xl rounded-lg p-4 ${
                message.type === 'user'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white border border-gray-200'
              } ${message.chartType && message.chartType !== 'none' && message.chartData ? 'pb-2' : ''}`}
            >
              <div className="flex items-start space-x-3">
                {message.type === 'assistant' && (
                  <div className="flex-shrink-0">
                    <Bot className="w-5 h-5 text-gray-500 mt-0.5" />
                  </div>
                )}
                
                <div className="flex-1">
                  <div className="whitespace-pre-wrap text-sm">
                    {message.content}
                  </div>
                  
                  {message.error && (
                    <div className="mt-2 flex items-center space-x-2 text-red-600">
                      <AlertCircle className="w-4 h-4" />
                      <span className="text-xs">{message.error}</span>
                    </div>
                  )}
                  
                  <div className="mt-2 text-xs opacity-70">
                    {message.timestamp.toLocaleTimeString()}
                  </div>
                </div>
                
                {message.type === 'user' && (
                  <div className="flex-shrink-0">
                    <User className="w-5 h-5 text-white mt-0.5" />
                  </div>
                )}
              </div>
              
              {/* Chart integrated directly in the message */}
              {message.chartType && message.chartType !== 'none' && message.chartData && (
                <div className="mt-3 -mx-4 -mb-4">
                  <Chart chartType={message.chartType} chartData={message.chartData} />
                </div>
              )}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center space-x-3">
                <Bot className="w-5 h-5 text-gray-500" />
                <div className="flex items-center space-x-2">
                  <Loader2 className="w-4 h-4 animate-spin text-gray-500" />
                  <span className="text-sm text-gray-600">Analyzing your data...</span>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="flex space-x-2">
        <div className="flex-1">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={activeChatId ? "Ask me anything about your data..." : "Create a chat session to start..."}
            className="input-field resize-none h-12"
            rows={1}
            disabled={!isConnected || isLoading || !activeChatId}
          />
        </div>
        <button
          onClick={handleSendMessage}
          disabled={!inputValue.trim() || !isConnected || isLoading || !activeChatId}
          className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed px-4"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
      
      {!isConnected && (
        <div className="mt-2 text-center text-sm text-red-600">
          ⚠️ Backend connection lost. Please check your connection.
        </div>
      )}
    </div>
  )
}

export default ChatInterface
