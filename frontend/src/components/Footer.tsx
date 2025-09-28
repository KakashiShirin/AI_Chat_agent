import React, { useState } from 'react'
import { Github, Mail, ExternalLink, Brain, Code, Heart } from 'lucide-react'

interface FooterProps {
  onNavigate: (tab: string) => void
}

const Footer: React.FC<FooterProps> = ({ onNavigate }) => {
  const [showAbout, setShowAbout] = useState(false)

  const handleLinkClick = (tab: string) => {
    onNavigate(tab)
    setShowAbout(false)
  }

  if (showAbout) {
    return (
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-3xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto animate-scale-in">
          <div className="p-8">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-primary rounded-xl flex items-center justify-center">
                  <Brain className="w-5 h-5 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900">About AI Data Agent</h2>
              </div>
              <button
                onClick={() => setShowAbout(false)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ExternalLink className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            {/* Content */}
            <div className="space-y-6">
              <div className="prose prose-gray max-w-none">
                <p className="text-gray-600 leading-relaxed">
                  AI Data Agent is an intelligent data analysis platform that transforms your raw data into actionable insights 
                  through the power of artificial intelligence. Built with modern web technologies and cutting-edge AI models.
                </p>
              </div>

              {/* Features */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Features</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                      <Brain className="w-3 h-3 text-primary-600" />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">AI-Powered Analysis</h4>
                      <p className="text-sm text-gray-600">Natural language data queries</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-accent-100 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                      <Code className="w-3 h-3 text-accent-600" />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">Smart Visualizations</h4>
                      <p className="text-sm text-gray-600">Automatic chart generation</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-success-100 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                      <ExternalLink className="w-3 h-3 text-success-600" />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">Easy Integration</h4>
                      <p className="text-sm text-gray-600">Multiple data formats supported</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-warning-100 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                      <Heart className="w-3 h-3 text-warning-600" />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">User-Friendly</h4>
                      <p className="text-sm text-gray-600">Intuitive interface design</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Developer Info */}
              <div className="bg-gradient-to-r from-gray-50 to-blue-50 rounded-2xl p-6 border border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Made by</h3>
                <div className="flex items-center space-x-4">
                  <div className="w-16 h-16 bg-gradient-primary rounded-2xl flex items-center justify-center">
                    <span className="text-white font-bold text-xl">NK</span>
                  </div>
                  <div className="flex-1">
                    <h4 className="text-xl font-bold text-gray-900">Naga Sai Kanishka</h4>
                    <p className="text-gray-600 mb-3">Data Scientist and AI Enthusiast</p>
                    <div className="flex space-x-4">
                      <a
                        href="https://github.com/KakashiShirin"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center space-x-2 text-gray-600 hover:text-primary-600 transition-colors"
                      >
                        <Github className="w-4 h-4" />
                        <span className="text-sm">GitHub</span>
                      </a>
                      <a
                        href="mailto:Kakashi.wrk000@gmail.com"
                        className="flex items-center space-x-2 text-gray-600 hover:text-primary-600 transition-colors"
                      >
                        <Mail className="w-4 h-4" />
                        <span className="text-sm">Email</span>
                      </a>
                    </div>
                  </div>
                </div>
              </div>

              {/* Tech Stack */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Built With</h3>
                <div className="flex flex-wrap gap-2">
                  {['React', 'TypeScript', 'Tailwind CSS', 'Python', 'FastAPI', 'PostgreSQL', 'Gemini AI'].map((tech) => (
                    <span
                      key={tech}
                      className="px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm font-medium"
                    >
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Footer Actions */}
            <div className="mt-8 pt-6 border-t border-gray-200">
              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  onClick={() => handleLinkClick('upload')}
                  className="btn-primary flex-1"
                >
                  Get Started
                </button>
                <button
                  onClick={() => handleLinkClick('api-keys')}
                  className="btn-secondary flex-1"
                >
                  Manage API Keys
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <footer className="bg-white/80 backdrop-blur-md border-t border-white/20 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="md:col-span-2">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
                <Brain className="w-4 h-4 text-white" />
              </div>
              <span className="text-lg font-bold text-gray-900">AI Data Agent</span>
            </div>
            <p className="text-gray-600 mb-4 max-w-md">
              Transform your data into insights with the power of artificial intelligence. 
              Upload, analyze, and visualize your data through natural conversation.
            </p>
            <div className="flex space-x-4">
              <a
                href="https://github.com/KakashiShirin"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 bg-gray-100 hover:bg-primary-100 rounded-lg transition-colors group"
              >
                <Github className="w-4 h-4 text-gray-600 group-hover:text-primary-600" />
              </a>
              <a
                href="mailto:Kakashi.wrk000@gmail.com"
                className="p-2 bg-gray-100 hover:bg-primary-100 rounded-lg transition-colors group"
              >
                <Mail className="w-4 h-4 text-gray-600 group-hover:text-primary-600" />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-4">Quick Links</h3>
            <ul className="space-y-2">
              <li>
                <button
                  onClick={() => handleLinkClick('upload')}
                  className="text-sm text-gray-600 hover:text-primary-600 transition-colors"
                >
                  Upload Data
                </button>
              </li>
              <li>
                <button
                  onClick={() => handleLinkClick('chat')}
                  className="text-sm text-gray-600 hover:text-primary-600 transition-colors"
                >
                  AI Chat
                </button>
              </li>
              <li>
                <button
                  onClick={() => handleLinkClick('visualization')}
                  className="text-sm text-gray-600 hover:text-primary-600 transition-colors"
                >
                  Data Visualization
                </button>
              </li>
              <li>
                <button
                  onClick={() => handleLinkClick('api-keys')}
                  className="text-sm text-gray-600 hover:text-primary-600 transition-colors"
                >
                  API Keys
                </button>
              </li>
            </ul>
          </div>

          {/* About */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-4">About</h3>
            <ul className="space-y-2">
              <li>
                <button
                  onClick={() => setShowAbout(true)}
                  className="text-sm text-gray-600 hover:text-primary-600 transition-colors"
                >
                  About Project
                </button>
              </li>
              <li>
                <span className="text-sm text-gray-600">Made by Naga Sai Kanishka</span>
              </li>
              <li>
                <a
                  href="mailto:Kakashi.wrk000@gmail.com"
                  className="text-sm text-gray-600 hover:text-primary-600 transition-colors"
                >
                  Contact
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-8 pt-6 border-t border-gray-200 flex flex-col sm:flex-row justify-between items-center">
          <p className="text-sm text-gray-500">
            © 2024 AI Data Agent. Built with ❤️ by Naga Sai Kanishka
          </p>
          <div className="flex items-center space-x-4 mt-4 sm:mt-0">
            <span className="text-sm text-gray-500">Powered by</span>
            <div className="flex items-center space-x-2">
              <div className="w-6 h-6 bg-gradient-primary rounded flex items-center justify-center">
                <Brain className="w-3 h-3 text-white" />
              </div>
              <span className="text-sm font-medium text-gray-700">Gemini AI</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer
