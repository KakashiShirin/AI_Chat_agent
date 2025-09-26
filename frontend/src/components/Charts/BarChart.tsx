import React from 'react';
import {
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { Box, Typography, Paper } from '@mui/material';

interface BarChartProps {
  data: any[];
  dataKey: string;
  barKey: string;
  title?: string;
  height?: number;
}

const BarChart: React.FC<BarChartProps> = ({
  data,
  dataKey,
  barKey,
  title,
  height = 400,
}) => {
  return (
    <Paper elevation={2} sx={{ p: 2, height: height + 60 }}>
      {title && (
        <Typography variant="h6" gutterBottom align="center">
          {title}
        </Typography>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <RechartsBarChart
          data={data}
          margin={{
            top: 20,
            right: 30,
            left: 20,
            bottom: 5,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey={dataKey} 
            angle={-45}
            textAnchor="end"
            height={80}
            fontSize={12}
          />
          <YAxis fontSize={12} />
          <Tooltip 
            formatter={(value: any) => [value, barKey]}
            labelFormatter={(label: any) => `${dataKey}: ${label}`}
          />
          <Legend />
          <Bar 
            dataKey={barKey} 
            fill="#1976d2" 
            radius={[4, 4, 0, 0]}
          />
        </RechartsBarChart>
      </ResponsiveContainer>
    </Paper>
  );
};

export default BarChart;
