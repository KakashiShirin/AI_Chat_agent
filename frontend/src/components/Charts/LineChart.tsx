import React from 'react';
import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { Typography, Paper } from '@mui/material';

interface LineChartProps {
  data: any[];
  dataKey: string;
  lineKey: string;
  title?: string;
  height?: number;
}

const LineChart: React.FC<LineChartProps> = ({
  data,
  dataKey,
  lineKey,
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
        <RechartsLineChart
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
            fontSize={12}
          />
          <YAxis fontSize={12} />
          <Tooltip 
            formatter={(value: any) => [value, lineKey]}
            labelFormatter={(label: any) => `${dataKey}: ${label}`}
          />
          <Legend />
          <Line 
            type="monotone" 
            dataKey={lineKey} 
            stroke="#1976d2" 
            strokeWidth={2}
            dot={{ fill: '#1976d2', strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6 }}
          />
        </RechartsLineChart>
      </ResponsiveContainer>
    </Paper>
  );
};

export default LineChart;
