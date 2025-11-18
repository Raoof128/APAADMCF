import React from 'react';
import { Typography, Box, Alert } from '@mui/material';

const PIAList: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 4, fontWeight: 600 }}>
        Privacy Impact Assessments
      </Typography>
      <Alert severity="info">
        PIA management interface coming soon. This will allow you to create, review, and approve Privacy Impact Assessments.
      </Alert>
    </Box>
  );
};

export default PIAList;
