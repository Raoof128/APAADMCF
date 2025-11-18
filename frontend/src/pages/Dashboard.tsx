import React, { useEffect, useState } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { apiClient } from '../services/api';

interface DashboardMetrics {
  critical_alerts: number;
  warning_alerts: number;
  recent_significant_drift: number;
  high_risk_systems: number;
}

const Dashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadMetrics();
  }, []);

  const loadMetrics = async () => {
    try {
      setLoading(true);
      const data = await apiClient.get('/api/v1/compliance/dashboard');
      setMetrics(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard metrics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 4, fontWeight: 600 }}>
        Compliance Dashboard
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <ErrorIcon color="error" sx={{ mr: 1 }} />
                <Typography variant="h6" color="error">
                  Critical Alerts
                </Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 600 }}>
                {metrics?.critical_alerts || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Require immediate attention
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <WarningIcon color="warning" sx={{ mr: 1 }} />
                <Typography variant="h6" color="warning.main">
                  Warning Alerts
                </Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 600 }}>
                {metrics?.warning_alerts || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Need review
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <WarningIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">
                  High-Risk Systems
                </Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 600 }}>
                {metrics?.high_risk_systems || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Under monitoring
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <CheckCircleIcon color="success" sx={{ mr: 1 }} />
                <Typography variant="h6">
                  Recent Drift Detections
                </Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 600 }}>
                {metrics?.recent_significant_drift || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Last 7 days
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Alert severity="info" sx={{ mt: 2 }}>
                Welcome to the Australian Privacy Act ADM Compliance Framework. Use the navigation menu to access different features.
              </Alert>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
