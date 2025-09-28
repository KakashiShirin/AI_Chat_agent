import React, { useState, useEffect } from 'react'
import { Brain, ArrowRight, Sparkles, BarChart3, Upload, MessageSquare, Key } from 'lucide-react'

interface LandingPageProps {
  onStartAgent: () => void
}

const LandingPage: React.FC<LandingPageProps> = ({ onStartAgent }) => {
  const [isVisible, setIsVisible] = useState(false)
  const [currentFeature, setCurrentFeature] = useState(0)

  const features = [
    {
      icon: Upload,
      title: 'Smart Data Upload',
      description: 'Upload CSV or Excel files with intelligent processing'
    },
    {
      icon: MessageSquare,
      title: 'AI-Powered Chat',
      description: 'Ask questions about your data in natural language'
    },
    {
      icon: BarChart3,
      title: 'Visual Analytics',
      description: 'Generate beautiful charts and insights automatically'
    },
    {
      icon: Key,
      title: 'API Management',
      description: 'Manage your AI keys with usage tracking'
    }
  ]

  useEffect(() => {
    setIsVisible(true)
    const interval = setInterval(() => {
      setCurrentFeature((prev) => (prev + 1) % features.length)
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-purple-50/20 flex flex-col">
      {/* Hero Section */}
      <div className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto text-center">
          {/* Main Logo and Title */}
          <div className={`transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            <div className="relative mb-8">
              <div className="w-32 h-32 sm:w-40 sm:h-40 bg-gradient-primary rounded-3xl flex items-center justify-center mx-auto mb-6 animate-float shadow-large">
                <Brain className="w-16 h-16 sm:w-20 sm:h-20 text-white" />
              </div>
              <div className="absolute -top-2 -right-2 w-8 h-8 bg-gradient-accent rounded-full flex items-center justify-center animate-bounce-gentle">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
            </div>
            
            <h1 className="text-4xl sm:text-6xl lg:text-7xl font-bold text-gradient mb-6 leading-tight">
              AI Data Agent
            </h1>
            <p className="text-xl sm:text-2xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
              Transform your data into insights with the power of artificial intelligence. 
              Upload, analyze, and visualize your data through natural conversation.
            </p>
          </div>

          {/* Feature Showcase */}
          <div className={`transition-all duration-1000 delay-300 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            <div className="mb-12">
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-large border border-white/20 max-w-4xl mx-auto">
                <div className="flex items-center justify-center space-x-4 mb-6">
                  {features.map((feature, index) => {
                    const Icon = feature.icon
                    return (
                      <div
                        key={index}
                        className={`w-12 h-12 rounded-xl flex items-center justify-center transition-all duration-500 ${
                          currentFeature === index
                            ? 'bg-gradient-primary text-white scale-110 shadow-lg'
                            : 'bg-gray-100 text-gray-500'
                        }`}
                      >
                        <Icon className="w-6 h-6" />
                      </div>
                    )
                  })}
                </div>
                <div className="min-h-[80px] flex items-center justify-center">
                  <div className="text-center">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      {features[currentFeature].title}
                    </h3>
                    <p className="text-gray-600">
                      {features[currentFeature].description}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* CTA Button */}
          <div className={`transition-all duration-1000 delay-500 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            <button
              onClick={onStartAgent}
              className="group bg-gradient-primary hover:bg-gradient-to-r hover:from-blue-600 hover:to-blue-700 text-white font-bold py-4 px-8 rounded-2xl text-lg transition-all duration-300 transform hover:scale-105 hover:shadow-xl focus:outline-none focus:ring-4 focus:ring-blue-500/20"
            >
              <span className="flex items-center space-x-3">
                <span>Start Your AI Agent</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-300" />
              </span>
            </button>
          </div>

          {/* Stats */}
          <div className={`transition-all duration-1000 delay-700 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            <div className="mt-16 grid grid-cols-1 sm:grid-cols-3 gap-8 max-w-2xl mx-auto">
              <div className="text-center">
                <div className="text-3xl font-bold text-primary-600 mb-2">100%</div>
                <div className="text-gray-600">AI Powered</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-primary-600 mb-2">∞</div>
                <div className="text-gray-600">Data Insights</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-primary-600 mb-2">24/7</div>
                <div className="text-gray-600">Available</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Floating Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-4 h-4 bg-primary-300 rounded-full animate-float opacity-60"></div>
        <div className="absolute top-40 right-20 w-6 h-6 bg-accent-300 rounded-full animate-float opacity-40" style={{ animationDelay: '1s' }}></div>
        <div className="absolute bottom-40 left-20 w-3 h-3 bg-success-300 rounded-full animate-float opacity-50" style={{ animationDelay: '2s' }}></div>
        <div className="absolute bottom-20 right-10 w-5 h-5 bg-warning-300 rounded-full animate-float opacity-30" style={{ animationDelay: '0.5s' }}></div>
      </div>
    </div>
  )
}

export default LandingPage
