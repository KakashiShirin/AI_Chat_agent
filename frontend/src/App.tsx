import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box, useMediaQuery, Typography } from '@mui/material';
import Header from './components/Layout/Header';
import Sidebar from './components/Layout/Sidebar';
import ChatInterface from './components/Chat/ChatInterface';
import SampleQueriesPanel from './components/SampleQueries/SampleQueriesPanel';
import DatabaseTablesPanel from './components/Database/DatabaseTablesPanel';
import { ChatMessage } from './types';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('chat');
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const handleSidebarToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const handleTabChange = (tab: string) => {
    setActiveTab(tab);
    if (isMobile) {
      setSidebarOpen(false);
    }
  };

  const handleMessageAdd = (message: ChatMessage) => {
    setChatMessages(prev => [...prev, message]);
  };

  const handleQuerySelect = (query: string) => {
    setActiveTab('chat');
    // You could implement auto-filling the chat input here
    console.log('Selected query:', query);
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'chat':
        return <ChatInterface onMessageAdd={handleMessageAdd} />;
      case 'queries':
        return <SampleQueriesPanel onQuerySelect={handleQuerySelect} />;
      case 'tables':
        return <DatabaseTablesPanel />;
      case 'history':
        return (
          <Box sx={{ p: 2 }}>
            <Typography variant="h5" gutterBottom>
              Query History
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Query history feature coming soon...
            </Typography>
          </Box>
        );
      case 'help':
        return (
          <Box sx={{ p: 2 }}>
            <Typography variant="h5" gutterBottom>
              Help & Tips
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Welcome to Cordly AI! Here are some tips to get the most out of your experience:
            </Typography>
            <Box component="ul" sx={{ pl: 2 }}>
              <li>Ask questions in natural language - no need to know SQL</li>
              <li>Try sample queries to see what's possible</li>
              <li>Explore the database schema to understand the data structure</li>
              <li>Use specific terms like "top 5", "average", "count" for better results</li>
              <li>Include time periods like "in 2017" or "last month" for temporal analysis</li>
            </Box>
          </Box>
        );
      default:
        return <ChatInterface onMessageAdd={handleMessageAdd} />;
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', height: '100vh' }}>
        {/* Header */}
        <Header onSettingsClick={handleSidebarToggle} />
        
        {/* Sidebar */}
        <Sidebar
          open={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          activeTab={activeTab}
          onTabChange={handleTabChange}
        />
        
        {/* Main Content */}
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            display: 'flex',
            flexDirection: 'column',
            height: '100vh',
            overflow: 'hidden',
            ml: { xs: 0, md: sidebarOpen ? '280px' : 0 },
            transition: 'margin-left 0.3s ease',
          }}
        >
          {/* Content Area */}
          <Box
            sx={{
              flexGrow: 1,
              overflow: 'hidden',
              display: 'flex',
              flexDirection: 'column',
            }}
          >
            {renderContent()}
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;