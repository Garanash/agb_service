import React from 'react';
import { Box, Button, Typography } from '@mui/material';
import { Star } from '@mui/icons-material';

interface ModernActionButtonProps {
  label: string;
  icon: React.ReactNode;
  onClick: () => void;
  variant?: 'primary' | 'secondary' | 'outline';
  fullWidth?: boolean;
}

interface ModernActionsProps {
  title: string;
  actions: ModernActionButtonProps[];
}

const ModernActions: React.FC<ModernActionsProps> = ({ title, actions }) => {
  const getButtonStyles = (variant: string = 'primary') => {
    switch (variant) {
      case 'primary':
        return {
          borderRadius: 2,
          py: 1.5,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          '&:hover': {
            background: 'linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%)',
            transform: 'translateY(-2px)',
            boxShadow: '0 8px 25px rgba(102, 126, 234, 0.3)'
          },
          transition: 'all 0.3s ease-in-out'
        };
      case 'secondary':
        return {
          borderRadius: 2,
          py: 1.5,
          background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
          '&:hover': {
            background: 'linear-gradient(135deg, #e881f0 0%, #f3455a 100%)',
            transform: 'translateY(-2px)',
            boxShadow: '0 8px 25px rgba(240, 147, 251, 0.3)'
          },
          transition: 'all 0.3s ease-in-out'
        };
      case 'outline':
        return {
          borderRadius: 2,
          py: 1.5,
          borderColor: 'primary.main',
          color: 'primary.main',
          '&:hover': {
            borderColor: 'primary.dark',
            backgroundColor: 'primary.light',
            transform: 'translateY(-2px)',
            boxShadow: '0 8px 25px rgba(25, 118, 210, 0.2)'
          },
          transition: 'all 0.3s ease-in-out'
        };
      default:
        return {};
    }
  };

  return (
    <Box
      sx={{
        borderRadius: 3,
        boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255,255,255,0.2)',
        background: 'rgba(255,255,255,0.9)',
        p: 3
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <Star sx={{ color: 'primary.main', mr: 1 }} />
        <Typography variant="h6" sx={{ fontWeight: 'bold', color: 'text.primary' }}>
          {title}
        </Typography>
      </Box>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {actions.map((action, index) => (
          <Button
            key={index}
            variant={action.variant === 'outline' ? 'outlined' : 'contained'}
            startIcon={action.icon}
            onClick={action.onClick}
            fullWidth={action.fullWidth}
            sx={getButtonStyles(action.variant)}
          >
            {action.label}
          </Button>
        ))}
      </Box>
    </Box>
  );
};

export default ModernActions;
