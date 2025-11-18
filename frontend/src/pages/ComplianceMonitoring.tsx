import React from 'react';
import { Typography, Box, Alert } from '@mui/material';

const ComplianceMonitoring: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 4, fontWeight: 600 }}>
        Compliance Monitoring
      </Typography>
      <Alert severity="info">
        Compliance monitoring interface coming soon. This will display drift detection, fairness monitoring, and compliance alerts.
      </Alert>
    </Box>
  );
};

export default ComplianceMonitoring;
