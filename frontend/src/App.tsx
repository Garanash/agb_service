import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import 'dayjs/locale/ru';

import { AuthProvider, useAuth } from './hooks/useAuth';
import LoginPage from './pages/LoginPage';
import RegistrationPage from './pages/RegistrationPage';
import VerifyEmailPage from './pages/VerifyEmailPage';
import DashboardPage from './pages/DashboardPage';
import RepairRequestsPage from './pages/RepairRequestsPage';
import ContractorsPage from './pages/ContractorsPage';
import CustomersPage from './pages/CustomersPage';
import ProfilePage from './pages/ProfilePage';
import ProfileSettingsPage from './pages/ProfileSettingsPage';
import ManagerWorkflowPage from './pages/ManagerWorkflowPage';
import ManagerDashboardPage from './pages/ManagerDashboardPage';
import ManagerVerificationPage from './pages/ManagerVerificationPage';
import SecurityVerificationPage from './pages/SecurityVerificationPage';
import HRDocumentsPage from './pages/HRDocumentsPage';
import TelegramBotPage from './pages/TelegramBotPage';
import CustomerCabinetPage from './pages/CustomerCabinetPage';
import CreateRequestPage from './pages/CreateRequestPage';
import AdminPanelPage from './pages/AdminPanelPage';
import ContractorProfilePage from './pages/ContractorProfilePage';
import ContractorArchivePage from './pages/ContractorArchivePage';
import Layout from './components/layout/Layout';
import LoadingSpinner from './components/common/LoadingSpinner';

// Создаем тему Material-UI
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

// Компонент для защищенных маршрутов
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return isAuthenticated ? <>{children}</> : <Navigate to='/login' replace />;
};

// Компонент для публичных маршрутов (только для неавторизованных)
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return !isAuthenticated ? <>{children}</> : <Navigate to='/' replace />;
};

const AppRoutes: React.FC = () => {
  return (
    <Routes>
      <Route
        path='/login'
        element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        }
      />

      <Route
        path='/register'
        element={
          <PublicRoute>
            <RegistrationPage />
          </PublicRoute>
        }
      />

      <Route
        path='/verify-email'
        element={<VerifyEmailPage />}
      />

      <Route
        path='/'
        element={
          <ProtectedRoute>
            <Layout>
              <DashboardPage />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path='/repair-requests'
        element={
          <ProtectedRoute>
            <Layout>
              <RepairRequestsPage />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path='/contractors'
        element={
          <ProtectedRoute>
            <Layout>
              <ContractorsPage />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path='/customers'
        element={
          <ProtectedRoute>
            <Layout>
              <CustomersPage />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path='/profile'
        element={
          <ProtectedRoute>
            <Layout>
              <ProfilePage />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path='/profile/settings'
        element={
          <ProtectedRoute>
            <Layout>
              <ProfileSettingsPage />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path='/contractor/profile'
        element={
          <ProtectedRoute>
            <Layout>
              <ContractorProfilePage />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path='/manager/requests'
        element={
          <ProtectedRoute>
            <Layout>
              <ManagerWorkflowPage />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path='/manager/calendar'
        element={
          <ProtectedRoute>
            <Layout>
              <ManagerDashboardPage />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path='/manager/verification'
        element={
          <ProtectedRoute>
            <Layout>
              <ManagerVerificationPage />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path='/security/verification'
        element={
          <ProtectedRoute>
            <Layout>
              <SecurityVerificationPage />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path='/hr/documents'
        element={
          <ProtectedRoute>
            <Layout>
              <HRDocumentsPage />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path='/telegram/bot'
        element={
          <ProtectedRoute>
            <Layout>
              <TelegramBotPage />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path='/customer/cabinet'
        element={
          <ProtectedRoute>
            <Layout>
              <CustomerCabinetPage />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path='/repair-requests/new'
        element={
          <ProtectedRoute>
            <Layout>
              <CreateRequestPage />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path='/admin/panel'
        element={
          <ProtectedRoute>
            <Layout>
              <AdminPanelPage />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path='/contractor/archive'
        element={
          <ProtectedRoute>
            <Layout>
              <ContractorArchivePage />
            </Layout>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
};

const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale='ru'>
        <AuthProvider>
          <Router>
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                minHeight: '100vh',
              }}
            >
              <AppRoutes />
            </Box>
          </Router>
        </AuthProvider>
      </LocalizationProvider>
    </ThemeProvider>
  );
};

export default App;
