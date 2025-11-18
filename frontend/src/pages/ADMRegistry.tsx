import React from 'react';
import { Typography, Box, Alert } from '@mui/material';

const ADMRegistry: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 4, fontWeight: 600 }}>
        ADM System Registry
      </Typography>
      <Alert severity="info">
        ADM System Registry interface coming soon. This will allow you to catalogue and manage all automated decision-making systems.
      </Alert>
    </Box>
  );
};

export default ADMRegistry;
