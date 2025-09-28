# Technical Documentation - AI Data Agent

## System Architecture

### Overview
The AI Data Agent is a conversational platform that enables users to upload data files and ask natural language questions to gain insights through AI-powered analysis and visualization.

### Technology Stack

#### Frontend
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS with custom components
- **Charts**: Recharts for data visualization
- **State Management**: React Hooks (useState, useEffect)
- **Build Tool**: Vite
- **Deployment**: Vercel

#### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: SQLite (development) / PostgreSQL (production)
- **AI Integration**: Google Gemini API
- **Data Processing**: Pandas, NumPy
- **Deployment**: Railway

### Core Components

#### 1. AI Agent Service (`backend/app/services/ai_agent.py`)

**Purpose**: Core intelligence engine that processes natural language queries and generates data analysis.

**Key Features**:
- Multi-model fallback system (Gemini 2.5 Pro → Flash → Flash-Lite)
- Multi-API key rotation for reliability
- Automatic model switching on rate limits
- Secure code execution environment
- Comprehensive logging and monitoring

**Model Hierarchy**:
```python
primary_model_name = 'gemini-2.5-pro'           # Most advanced
fallback_model_name = 'gemini-2.5-flash'        # Price-performance
tertiary_model_name = 'gemini-2.5-flash-lite'   # Cost-efficient
```

**Execution Flow**:
1. Schema extraction from uploaded data
2. Prompt construction with context
3. Model selection and API call
4. Safe code execution in sandbox
5. Result synthesis and chart generation

#### 2. Data Processor (`backend/app/services/data_processor.py`)

**Purpose**: Handles file uploads, data cleaning, and database operations.

**Features**:
- Excel/CSV file processing
- Data type inference and cleaning
- SQLite table creation and management
- Schema extraction for AI analysis
- Data cleanup functionality

#### 3. Chat Session Manager (`backend/app/services/chat_session_manager.py`)

**Purpose**: Manages chat sessions, context, and conversation history.

**Features**:
- Session creation and management
- Context preservation across messages
- Message history tracking
- Session cleanup and expiration
- Multi-session support

#### 4. Frontend Components

**Landing Page** (`frontend/src/components/LandingPage.tsx`):
- Professional welcome interface
- Feature highlights and animations
- Call-to-action for starting the agent

**Chat Interface** (`frontend/src/components/ChatInterface.tsx`):
- Sidebar layout with session management
- Message display with proper formatting
- Chart integration within messages
- Real-time status indicators

**File Upload** (`frontend/src/components/FileUpload.tsx`):
- Drag-and-drop interface
- File validation and processing
- Upload progress and status
- Error handling and feedback

**API Key Manager** (`frontend/src/components/ApiKeyManager.tsx`):
- Multi-key management interface
- Usage tracking and statistics
- Model status monitoring
- Security features (key masking)

**Data Visualization** (`frontend/src/components/DataVisualization.tsx`):
- Interactive chart components
- Multiple chart types (bar, pie, line)
- Responsive design
- Chart controls and options

### API Endpoints

#### Core Endpoints
- `POST /api/v1/upload` - File upload and processing
- `GET /api/v1/schema/{session_id}` - Get data schema
- `POST /api/v1/query` - Process natural language queries
- `GET /api/v1/health` - Health check

#### Chat Management
- `POST /api/v1/chat/create` - Create new chat session
- `POST /api/v1/chat/query` - Send message to chat
- `GET /api/v1/chat/{chat_id}/context` - Get chat context
- `GET /api/v1/chat/sessions` - List all sessions
- `DELETE /api/v1/chat/{chat_id}` - Delete chat session
- `POST /api/v1/chat/cleanup` - Cleanup expired sessions

#### API Key Management
- `POST /api/v1/api-keys/add` - Add new API key
- `POST /api/v1/api-keys/validate` - Validate API key
- `GET /api/v1/api-keys/status` - Get key status
- `GET /api/v1/credits` - Get credit usage
- `POST /api/v1/credits/reset` - Reset credit tracking

#### Model Management
- `GET /api/v1/model/status` - Get model status
- `POST /api/v1/model/reset` - Reset to primary model

#### Data Management
- `POST /api/v1/cleanup/all` - Clear all data

### Database Schema

#### Sessions Table
```sql
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_tables TEXT -- JSON string of table names
);
```

#### Data Tables
Dynamic tables created based on uploaded files:
- Column names are sanitized for SQL compatibility
- Data types are inferred automatically
- Sample data is stored for AI context

### Security Features

#### API Key Security
- Keys are masked in UI displays
- Sanitized from error messages
- Secure storage and rotation
- Validation before use

#### Data Security
- Sandboxed code execution
- Input validation and sanitization
- SQL injection prevention
- File type validation

### Error Handling

#### Model Fallback
- Automatic detection of rate limit errors
- Seamless switching to fallback models
- Comprehensive error logging
- User-friendly error messages

#### API Error Handling
- Multi-key rotation on failures
- Retry logic with exponential backoff
- Graceful degradation
- Detailed error reporting

### Performance Optimizations

#### Frontend
- Component lazy loading
- Optimized re-renders
- Efficient state management
- Responsive image handling

#### Backend
- Database connection pooling
- Caching for schema data
- Efficient data processing
- Memory management

### Monitoring and Logging

#### Logging System
- Enhanced logging with structured output
- API call tracking
- Performance metrics
- Error tracking and reporting

#### Usage Tracking
- API call counts per key
- Token usage monitoring
- Cost estimation
- Performance analytics

### Deployment Configuration

#### Environment Variables
```bash
# Backend
GEMINI_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./data.db
LOG_LEVEL=INFO

# Frontend
VITE_API_BASE_URL=http://localhost:8000
```

#### Production Setup
- Railway for backend deployment
- Vercel for frontend deployment
- PostgreSQL for production database
- Environment-specific configurations

### Development Guidelines

#### Code Standards
- TypeScript for frontend
- Python type hints for backend
- Comprehensive error handling
- Unit tests for critical functions

#### Git Workflow
- Feature branches for new development
- Comprehensive commit messages
- Code review process
- Automated testing

### Troubleshooting

#### Common Issues
1. **Model Switching**: Check API key validity and rate limits
2. **File Upload**: Verify file format and size limits
3. **Chart Rendering**: Ensure data format compatibility
4. **Session Management**: Check database connectivity

#### Debug Tools
- Enhanced logging system
- API endpoint testing
- Database query monitoring
- Frontend developer tools

---

*Last Updated: December 26, 2024*
