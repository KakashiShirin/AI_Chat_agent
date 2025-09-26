import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  TextField,
  IconButton,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  Chip,
  Divider,
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as AIIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import { ChatMessage, ApiResponse } from '../../types';
import { ApiService } from '../../services/api';
import BarChart from '../Charts/BarChart';
import LineChart from '../Charts/LineChart';
import DataTable from '../Charts/DataTable';

interface ChatInterfaceProps {
  onMessageAdd?: (message: ChatMessage) => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ onMessageAdd }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setError(null);

    try {
      const response: ApiResponse = await ApiService.askQuestion(inputValue.trim());
      
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: response.summary,
        timestamp: new Date(),
        data: response,
      };

      setMessages(prev => [...prev, assistantMessage]);
      onMessageAdd?.(assistantMessage);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const renderVisualization = (data: ApiResponse) => {
    if (!data.visualization) return null;

    const { type, data: chartData, dataKey, barKey, title } = data.visualization;

    switch (type) {
      case 'bar_chart':
        return (
          <BarChart
            data={chartData}
            dataKey={dataKey || 'name'}
            barKey={barKey || 'value'}
            title={title}
          />
        );
      case 'line_chart':
        return (
          <LineChart
            data={chartData}
            dataKey={dataKey || 'name'}
            lineKey={barKey || 'value'}
            title={title}
          />
        );
      default:
        return null;
    }
  };

  const renderTable = (data: ApiResponse) => {
    if (!data.tableData) return null;

    return (
      <DataTable
        columns={data.tableData.columns}
        rows={data.tableData.rows}
        title="Query Results"
      />
    );
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Messages Area */}
      <Box sx={{ flexGrow: 1, overflow: 'auto', p: 2 }}>
        {messages.length === 0 && (
          <Box sx={{ textAlign: 'center', mt: 4 }}>
            <AIIcon sx={{ fontSize: 64, color: 'grey.400', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              Welcome to Cordly AI
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Ask questions about the Brazilian e-commerce dataset in natural language
            </Typography>
          </Box>
        )}

        {messages.map((message) => (
          <Box key={message.id} sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
              {message.type === 'user' ? (
                <PersonIcon color="primary" />
              ) : (
                <AIIcon color="secondary" />
              )}
              
              <Paper
                elevation={1}
                sx={{
                  p: 2,
                  maxWidth: '80%',
                  backgroundColor: message.type === 'user' ? 'primary.light' : 'grey.100',
                  color: message.type === 'user' ? 'primary.contrastText' : 'text.primary',
                }}
              >
                <Typography variant="body1" sx={{ mb: 1 }}>
                  {message.content}
                </Typography>
                
                {message.data && (
                  <>
                    <Divider sx={{ my: 1 }} />
                    
                    {/* Execution Info */}
                    <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                      <Chip
                        label={`${(message.data.executionTime * 1000).toFixed(0)}ms`}
                        size="small"
                        color="info"
                        variant="outlined"
                      />
                      <Chip
                        label="SQL Query"
                        size="small"
                        color="default"
                        variant="outlined"
                        onClick={() => console.log(message.data?.sqlQuery)}
                      />
                    </Box>

                    {/* Visualization */}
                    {renderVisualization(message.data)}
                    
                    {/* Table */}
                    {renderTable(message.data)}
                  </>
                )}
              </Paper>
            </Box>
          </Box>
        ))}

        {isLoading && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <AIIcon color="secondary" />
            <Paper elevation={1} sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CircularProgress size={16} />
                <Typography variant="body2">Processing your question...</Typography>
              </Box>
            </Paper>
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <div ref={messagesEndRef} />
      </Box>

      {/* Input Area */}
      <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a question about the data... (e.g., 'What are the top 5 states by customer count?')"
            disabled={isLoading}
            variant="outlined"
            size="small"
          />
          <IconButton
            color="primary"
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isLoading}
            sx={{ alignSelf: 'flex-end' }}
          >
            <SendIcon />
          </IconButton>
        </Box>
      </Box>
    </Box>
  );
};

export default ChatInterface;
