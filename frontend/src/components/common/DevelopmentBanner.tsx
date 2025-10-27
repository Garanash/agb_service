import React from 'react';
import { Alert, AlertTitle } from '@mui/material';

const DevelopmentBanner: React.FC = () => {
  return (
    <Alert 
      severity="info" 
      sx={{ 
        mb: 2, 
        backgroundColor: '#e3f2fd',
        '& .MuiAlert-icon': {
          color: '#2196f3'
        }
      }}
    >
      <AlertTitle sx={{ fontWeight: 'bold', mb: 0 }}>
        Платформа находится в разработке
      </AlertTitle>
      Вы участвуете в альфа тестировании
    </Alert>
  );
};

export default DevelopmentBanner;

