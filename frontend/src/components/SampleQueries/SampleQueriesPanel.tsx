import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  Grid,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import { QueryStats as QueryStatsIcon } from '@mui/icons-material';
import { ApiService } from '../../services/api';

interface SampleQueriesPanelProps {
  onQuerySelect: (query: string) => void;
}

const SampleQueriesPanel: React.FC<SampleQueriesPanelProps> = ({ onQuerySelect }) => {
  const [queries, setQueries] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSampleQueries();
  }, []);

  const loadSampleQueries = async () => {
    try {
      setLoading(true);
      const sampleQueries = await ApiService.getSampleQueries();
      setQueries(sampleQueries);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load sample queries');
    } finally {
      setLoading(false);
    }
  };

  const getQueryCategory = (query: string): string => {
    const lowerQuery = query.toLowerCase();
    if (lowerQuery.includes('top') || lowerQuery.includes('highest')) return 'Top Analysis';
    if (lowerQuery.includes('average') || lowerQuery.includes('mean')) return 'Averages';
    if (lowerQuery.includes('count') || lowerQuery.includes('how many')) return 'Counts';
    if (lowerQuery.includes('month') || lowerQuery.includes('time')) return 'Time Series';
    if (lowerQuery.includes('distribution') || lowerQuery.includes('payment')) return 'Distribution';
    return 'General';
  };

  const getCategoryColor = (category: string): 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info' => {
    switch (category) {
      case 'Top Analysis': return 'primary';
      case 'Averages': return 'secondary';
      case 'Counts': return 'success';
      case 'Time Series': return 'warning';
      case 'Distribution': return 'error';
      default: return 'info';
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 200 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <QueryStatsIcon sx={{ mr: 1 }} />
        <Typography variant="h5" gutterBottom>
          Sample Queries
        </Typography>
      </Box>

      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Click on any query below to try it out. These examples demonstrate the types of questions you can ask about the Brazilian e-commerce dataset.
      </Typography>

      <Grid container spacing={2}>
        {queries.map((query, index) => {
          const category = getQueryCategory(query);
          const color = getCategoryColor(category);
          
          return (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card 
                sx={{ 
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  '&:hover': {
                    transform: 'translateY(-2px)',
                    boxShadow: 3,
                  }
                }}
              >
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Chip
                      label={category}
                      size="small"
                      color={color}
                      variant="outlined"
                    />
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    {query}
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button
                    size="small"
                    onClick={() => onQuerySelect(query)}
                    sx={{ ml: 'auto' }}
                  >
                    Try This Query
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          );
        })}
      </Grid>

      <Box sx={{ mt: 3, p: 2, backgroundColor: 'grey.50', borderRadius: 1 }}>
        <Typography variant="body2" color="text.secondary">
          <strong>Tip:</strong> You can ask questions in natural language. The AI will automatically generate the appropriate SQL query and provide visualizations when possible.
        </Typography>
      </Box>
    </Box>
  );
};

export default SampleQueriesPanel;
