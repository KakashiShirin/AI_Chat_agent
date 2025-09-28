# AI Data Agent Frontend

A modern React frontend for the AI Data Agent, built with TypeScript, Vite, and Tailwind CSS.

## 🚀 Features

- **Chat Interface**: Conversational AI data analysis
- **File Upload**: Drag & drop CSV/Excel file upload
- **API Key Management**: Multi-Gemini API key management
- **Data Visualization**: Interactive charts and data tables
- **Real-time Updates**: Live connection status and notifications
- **Responsive Design**: Mobile-friendly interface

## 🛠️ Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **Lucide React** for icons
- **Recharts** for data visualization
- **React Dropzone** for file uploads
- **React Hot Toast** for notifications
- **Axios** for API communication

## 📦 Installation

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

3. Build for production:
```bash
npm run build
```

## 🔧 Configuration

The frontend is configured to proxy API requests to `http://localhost:8000` (backend server).

To change the backend URL, update `vite.config.ts`:
```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://your-backend-url:port',
      changeOrigin: true,
    },
  },
}
```

## 📱 Usage

1. **Upload Data**: Go to the Upload tab and drag & drop your CSV/Excel file
2. **Chat with AI**: Use the Chat tab to ask questions about your data
3. **Manage API Keys**: Add your Gemini API keys in the API Keys tab
4. **View Data**: Explore your data structure in the Data tab

## 🎨 Components

- `App.tsx` - Main application component
- `ChatInterface.tsx` - AI chat interface
- `FileUpload.tsx` - File upload component
- `ApiKeyManager.tsx` - API key management
- `DataVisualization.tsx` - Data visualization

## 🔌 API Integration

The frontend communicates with the backend through the `apiService`:

- Health checks
- File uploads
- AI queries
- API key management
- Credit tracking

## 📱 Responsive Design

The interface is fully responsive and works on:
- Desktop (1024px+)
- Tablet (768px - 1023px)
- Mobile (320px - 767px)

## 🚀 Deployment

Build the project:
```bash
npm run build
```

The built files will be in the `dist` directory, ready for deployment to any static hosting service.
