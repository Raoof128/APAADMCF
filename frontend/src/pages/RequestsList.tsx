import React from 'react';
import { Typography, Box, Alert } from '@mui/material';

const RequestsList: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 4, fontWeight: 600 }}>
        Individual Requests
      </Typography>
      <Alert severity="info">
        Individual requests management interface coming soon. This will allow you to handle explanation, review, and correction requests.
      </Alert>
    </Box>
  );
};

export default RequestsList;
