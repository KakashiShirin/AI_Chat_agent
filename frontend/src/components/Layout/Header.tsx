import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  IconButton,
  Chip,
} from '@mui/material';
import {
  Analytics as AnalyticsIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';

interface HeaderProps {
  onSettingsClick?: () => void;
}

const Header: React.FC<HeaderProps> = ({ onSettingsClick }) => {
  return (
    <AppBar position="static" elevation={1}>
      <Toolbar>
        <AnalyticsIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Cordly AI
        </Typography>
        <Typography variant="subtitle2" sx={{ mr: 2, opacity: 0.8 }}>
          Conversational Business Intelligence
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Chip 
            label="Hybrid AI" 
            size="small" 
            color="secondary" 
            variant="outlined"
            sx={{ 
              borderColor: 'rgba(255,255,255,0.5)',
              color: 'white',
              '& .MuiChip-label': { fontSize: '0.75rem' }
            }}
          />
          
          <IconButton
            color="inherit"
            onClick={onSettingsClick}
            size="small"
          >
            <SettingsIcon />
          </IconButton>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
