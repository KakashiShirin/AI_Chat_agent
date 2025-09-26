import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Box,
} from '@mui/material';

interface DataTableProps {
  columns: string[];
  rows: string[][];
  title?: string;
  maxRows?: number;
}

const DataTable: React.FC<DataTableProps> = ({
  columns,
  rows,
  title,
  maxRows = 10,
}) => {
  const displayRows = rows.slice(0, maxRows);
  const hasMoreRows = rows.length > maxRows;

  return (
    <Paper elevation={2} sx={{ p: 2 }}>
      {title && (
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
      )}
      
      <TableContainer>
        <Table size="small" stickyHeader>
          <TableHead>
            <TableRow>
              {columns.map((column, index) => (
                <TableCell 
                  key={index}
                  sx={{ 
                    fontWeight: 'bold',
                    backgroundColor: 'grey.100',
                    borderBottom: '2px solid',
                    borderBottomColor: 'primary.main'
                  }}
                >
                  {column}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {displayRows.map((row, rowIndex) => (
              <TableRow 
                key={rowIndex}
                hover
                sx={{ 
                  '&:nth-of-type(odd)': { 
                    backgroundColor: 'grey.50' 
                  } 
                }}
              >
                {row.map((cell, cellIndex) => (
                  <TableCell key={cellIndex}>
                    {cell}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      
      {hasMoreRows && (
        <Box sx={{ mt: 1, textAlign: 'center' }}>
          <Typography variant="caption" color="text.secondary">
            Showing {maxRows} of {rows.length} rows
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default DataTable;
