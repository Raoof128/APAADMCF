import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box } from '@mui/material';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import ADMRegistry from './pages/ADMRegistry';
import PIAList from './pages/PIAList';
import RequestsList from './pages/RequestsList';
import ComplianceMonitoring from './pages/ComplianceMonitoring';
import Login from './pages/Login';

function App() {
  const [isAuthenticated, setIsAuthenticated] = React.useState<boolean>(
    !!localStorage.getItem('token')
  );

  const handleLogin = (token: string) => {
    localStorage.setItem('token', token);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
  };

  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <Layout onLogout={handleLogout}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/adm-registry" element={<ADMRegistry />} />
        <Route path="/pia" element={<PIAList />} />
        <Route path="/requests" element={<RequestsList />} />
        <Route path="/compliance" element={<ComplianceMonitoring />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}

export default App;
