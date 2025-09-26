import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  CircularProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import {
  TableChart as TableChartIcon,
  ExpandMore as ExpandMoreIcon,
  Key as KeyIcon,
  Link as LinkIcon,
} from '@mui/icons-material';
import { ApiService } from '../../services/api';
import { DatabaseTable } from '../../types';

interface DatabaseTablesPanelProps {}

const DatabaseTablesPanel: React.FC<DatabaseTablesPanelProps> = () => {
  const [tables, setTables] = useState<Record<string, DatabaseTable>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDatabaseSchema();
  }, []);

  const loadDatabaseSchema = async () => {
    try {
      setLoading(true);
      const schema = await ApiService.getSchema();
      setTables(schema);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load database schema');
    } finally {
      setLoading(false);
    }
  };

  const getDataTypeColor = (dataType: string): 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info' => {
    if (dataType.includes('varchar') || dataType.includes('text')) return 'primary';
    if (dataType.includes('int') || dataType.includes('bigint')) return 'secondary';
    if (dataType.includes('decimal') || dataType.includes('numeric')) return 'success';
    if (dataType.includes('timestamp') || dataType.includes('date')) return 'warning';
    if (dataType.includes('boolean')) return 'error';
    return 'info';
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
        <TableChartIcon sx={{ mr: 1 }} />
        <Typography variant="h5" gutterBottom>
          Database Schema
        </Typography>
      </Box>

      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Explore the Brazilian e-commerce dataset structure. This dataset contains 9 interconnected tables with information about customers, orders, products, and more.
      </Typography>

      <Grid container spacing={2}>
        {Object.entries(tables).map(([tableName, tableInfo]) => (
          <Grid item xs={12} key={tableName}>
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                  <Typography variant="h6" sx={{ flexGrow: 1 }}>
                    {tableName}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Chip
                      label={`${Object.keys(tableInfo.columns).length} columns`}
                      size="small"
                      color="info"
                      variant="outlined"
                    />
                    {tableInfo.primary_keys.length > 0 && (
                      <Chip
                        icon={<KeyIcon />}
                        label={`${tableInfo.primary_keys.length} PK`}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    )}
                    {tableInfo.foreign_keys.length > 0 && (
                      <Chip
                        icon={<LinkIcon />}
                        label={`${tableInfo.foreign_keys.length} FK`}
                        size="small"
                        color="secondary"
                        variant="outlined"
                      />
                    )}
                  </Box>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Columns:
                  </Typography>
                  <TableContainer component={Paper} variant="outlined">
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell><strong>Column Name</strong></TableCell>
                          <TableCell><strong>Data Type</strong></TableCell>
                          <TableCell><strong>Nullable</strong></TableCell>
                          <TableCell><strong>Default</strong></TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {Object.entries(tableInfo.columns).map(([columnName, columnInfo]) => (
                          <TableRow key={columnName}>
                            <TableCell>
                              {columnName}
                              {tableInfo.primary_keys.includes(columnName) && (
                                <KeyIcon sx={{ ml: 1, fontSize: 16, color: 'primary.main' }} />
                              )}
                            </TableCell>
                            <TableCell>
                              <Chip
                                label={columnInfo.data_type}
                                size="small"
                                color={getDataTypeColor(columnInfo.data_type)}
                                variant="outlined"
                              />
                            </TableCell>
                            <TableCell>
                              <Chip
                                label={columnInfo.is_nullable ? 'Yes' : 'No'}
                                size="small"
                                color={columnInfo.is_nullable ? 'warning' : 'success'}
                                variant="outlined"
                              />
                            </TableCell>
                            <TableCell>
                              {columnInfo.column_default || '-'}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Box>

                {tableInfo.foreign_keys.length > 0 && (
                  <Box>
                    <Typography variant="subtitle2" gutterBottom>
                      Foreign Key Relationships:
                    </Typography>
                    <TableContainer component={Paper} variant="outlined">
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell><strong>Column</strong></TableCell>
                            <TableCell><strong>References Table</strong></TableCell>
                            <TableCell><strong>References Column</strong></TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {tableInfo.foreign_keys.map((fk, index) => (
                            <TableRow key={index}>
                              <TableCell>{fk.column}</TableCell>
                              <TableCell>
                                <Chip
                                  label={fk.references_table}
                                  size="small"
                                  color="secondary"
                                  variant="outlined"
                                />
                              </TableCell>
                              <TableCell>{fk.references_column}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Box>
                )}
              </AccordionDetails>
            </Accordion>
          </Grid>
        ))}
      </Grid>

      <Box sx={{ mt: 3, p: 2, backgroundColor: 'grey.50', borderRadius: 1 }}>
        <Typography variant="body2" color="text.secondary">
          <strong>Dataset Info:</strong> This is the Brazilian E-Commerce Public Dataset by Olist, containing real-world e-commerce data with 9 interconnected tables covering customers, orders, products, sellers, payments, reviews, and geolocation information.
        </Typography>
      </Box>
    </Box>
  );
};

export default DatabaseTablesPanel;
