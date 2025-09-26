import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Box,
  Divider,
  Chip,
} from '@mui/material';
import {
  Chat as ChatIcon,
  TableChart as TableChartIcon,
  QueryStats as QueryStatsIcon,
  History as HistoryIcon,
  Help as HelpIcon,
} from '@mui/icons-material';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const drawerWidth = 280;

const Sidebar: React.FC<SidebarProps> = ({ 
  open, 
  onClose, 
  activeTab, 
  onTabChange 
}) => {
  const menuItems = [
    { id: 'chat', label: 'AI Chat', icon: <ChatIcon /> },
    { id: 'tables', label: 'Database Tables', icon: <TableChartIcon /> },
    { id: 'queries', label: 'Sample Queries', icon: <QueryStatsIcon /> },
    { id: 'history', label: 'Query History', icon: <HistoryIcon /> },
    { id: 'help', label: 'Help & Tips', icon: <HelpIcon /> },
  ];

  return (
    <Drawer
      variant="temporary"
      anchor="left"
      open={open}
      onClose={onClose}
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
        },
      }}
    >
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Navigation
        </Typography>
        <Chip 
          label="Phase 3 - Frontend" 
          size="small" 
          color="primary" 
          variant="outlined"
        />
      </Box>
      
      <Divider />
      
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.id} disablePadding>
            <ListItemButton
              selected={activeTab === item.id}
              onClick={() => onTabChange(item.id)}
              sx={{
                '&.Mui-selected': {
                  backgroundColor: 'primary.main',
                  color: 'primary.contrastText',
                  '&:hover': {
                    backgroundColor: 'primary.dark',
                  },
                  '& .MuiListItemIcon-root': {
                    color: 'primary.contrastText',
                  },
                },
              }}
            >
              <ListItemIcon>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      
      <Box sx={{ flexGrow: 1 }} />
      
      <Divider />
      
      <Box sx={{ p: 2 }}>
        <Typography variant="caption" color="text.secondary">
          Brazilian E-Commerce Dataset
        </Typography>
        <Typography variant="caption" display="block" color="text.secondary">
          9 interconnected tables
        </Typography>
      </Box>
    </Drawer>
  );
};

export default Sidebar;
