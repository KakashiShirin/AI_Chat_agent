import axios from 'axios';
import type { ApiResponse, DatabaseTable } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API Service for backend communication
export class ApiService {
  // Ask a question to the AI agent
  static async askQuestion(question: string): Promise<ApiResponse> {
    try {
      const response = await api.post('/api/ask', { question });
      return response.data;
    } catch (error) {
      console.error('Error asking question:', error);
      throw new Error('Failed to process your question. Please try again.');
    }
  }

  // Get database schema information
  static async getSchema(): Promise<Record<string, DatabaseTable>> {
    try {
      const response = await api.get('/api/schema');
      return response.data.schema;
    } catch (error) {
      console.error('Error fetching schema:', error);
      throw new Error('Failed to load database schema.');
    }
  }

  // Get available tables
  static async getTables(): Promise<string[]> {
    try {
      const response = await api.get('/api/tables');
      return response.data.tables;
    } catch (error) {
      console.error('Error fetching tables:', error);
      throw new Error('Failed to load database tables.');
    }
  }

  // Get sample queries
  static async getSampleQueries(): Promise<string[]> {
    try {
      const response = await api.get('/api/sample-queries');
      return response.data.sample_queries;
    } catch (error) {
      console.error('Error fetching sample queries:', error);
      // Return default sample queries if API fails
      return [
        'What are the top 5 product categories by revenue?',
        'Which states have the highest average order value?',
        'How many orders were placed each month in 2017?',
        'What is the distribution of payment methods?',
        'Which sellers have the highest customer satisfaction?',
        'What are the most popular products in São Paulo?',
        'How does order volume vary by day of the week?',
        'What is the average delivery time by state?',
        'Which product categories have the highest profit margins?',
        'How many customers made repeat purchases?'
      ];
    }
  }

  // Check health status
  static async checkHealth(): Promise<{ status: string; services: Record<string, boolean> }> {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      console.error('Error checking health:', error);
      throw new Error('Backend service is unavailable.');
    }
  }
}

export default api;
