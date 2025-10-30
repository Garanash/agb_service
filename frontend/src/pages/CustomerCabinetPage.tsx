import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Grid,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Dashboard,
  Business,
  Add,
  Archive,
  Visibility,
  ExpandMore,
  CheckCircle,
  Pending,
  Build,
  Assignment,
  Cancel,
} from '@mui/icons-material';
import { useAuth } from 'hooks/useAuth';
import { apiService } from 'services/api';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { RequestStatus } from 'types/api';
import CustomerCompanyProfilePage from './CustomerCompanyProfilePage';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role='tabpanel'
      hidden={value !== index}
      id={`customer-tabpanel-${index}`}
      aria-labelledby={`customer-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

interface RequestWithStatus {
  id: number;
  title: string;
  description: string;
  status: RequestStatus;
  urgency?: string;
  created_at?: string;
  updated_at?: string;
  assigned_contractor_id?: number;
  final_price?: number;
}

const CustomerCabinetPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  
  // Читаем параметр tab из URL, по умолчанию 1 (Профиль компании)
  const initialTab = parseInt(searchParams.get('tab') || '1', 10);
  const [tabValue, setTabValue] = useState(initialTab);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [requests, setRequests] = useState<RequestWithStatus[]>([]);
  const [stats, setStats] = useState({
    total: 0,
    new: 0,
    in_progress: 0,
    completed: 0,
    cancelled: 0,
  });

  useEffect(() => {
    loadData();
  }, []);

  // Обновляем tabValue при изменении параметра tab в URL
  useEffect(() => {
    const tabParam = searchParams.get('tab');
    if (tabParam !== null) {
      const tabIndex = parseInt(tabParam, 10);
      if (!isNaN(tabIndex) && tabIndex >= 0 && tabIndex <= 3) {
        setTabValue(tabIndex);
      }
    }
  }, [searchParams]);

  const loadData = async () => {
    try {
      setLoading(true);
      const requestsData = await apiService.getCustomerRequests();
      setRequests(requestsData || []);

      // Подсчитываем статистику
      const statsData = {
        total: requestsData?.length || 0,
        new: requestsData?.filter((r: any) => r.status === 'new' || r.status === 'manager_review').length || 0,
        in_progress: requestsData?.filter((r: any) => r.status === 'in_progress' || r.status === 'assigned').length || 0,
        completed: requestsData?.filter((r: any) => r.status === 'completed').length || 0,
        cancelled: requestsData?.filter((r: any) => r.status === 'cancelled').length || 0,
      };
      setStats(statsData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка загрузки данных');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    if (newValue === 2) {
      // Переход на создание заявки - не меняем вкладку, перенаправляем
      navigate('/repair-requests/new');
      return;
    }
    setTabValue(newValue);
    // Обновляем URL параметр tab
    navigate(`/customer/cabinet?tab=${newValue}`, { replace: true });
  };

  const getStatusColor = (status: RequestStatus) => {
    const colors: { [key: string]: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' } = {
      new: 'info',
      manager_review: 'warning',
      clarification: 'warning',
      sent_to_contractors: 'info',
      contractor_responses: 'info',
      assigned: 'success',
      in_progress: 'primary',
      completed: 'success',
      cancelled: 'error',
    };
    return colors[status] || 'default';
  };

  const getStatusText = (status: RequestStatus) => {
    const texts: { [key: string]: string } = {
      new: 'Новая',
      manager_review: 'На рассмотрении',
      clarification: 'Уточнение',
      sent_to_contractors: 'Отправлена исполнителям',
      contractor_responses: 'Отклики исполнителей',
      assigned: 'Назначена',
      in_progress: 'В работе',
      completed: 'Завершена',
      cancelled: 'Отменена',
    };
    return texts[status] || status;
  };

  const viewRequestDetails = (requestId: number) => {
    navigate(`/customer/requests/${requestId}`);
  };

  // Вкладка 0: Главная
  const renderDashboard = () => {
    if (loading) {
      return (
        <Box display='flex' justifyContent='center' alignItems='center' minHeight='400px'>
          <CircularProgress />
        </Box>
      );
    }

    return (
      <Box>
        <Typography variant='h5' gutterBottom sx={{ mb: 3 }}>
          Обзор заявок
        </Typography>

        {/* Статистика */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display='flex' alignItems='center'>
                  <Build color='primary' sx={{ mr: 2 }} />
                  <Box>
                    <Typography variant='h4'>{stats.total}</Typography>
                    <Typography color='text.secondary'>Всего заявок</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display='flex' alignItems='center'>
                  <Pending color='warning' sx={{ mr: 2 }} />
                  <Box>
                    <Typography variant='h4'>{stats.new}</Typography>
                    <Typography color='text.secondary'>Новых</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display='flex' alignItems='center'>
                  <Assignment color='primary' sx={{ mr: 2 }} />
                  <Box>
                    <Typography variant='h4'>{stats.in_progress}</Typography>
                    <Typography color='text.secondary'>В работе</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display='flex' alignItems='center'>
                  <CheckCircle color='success' sx={{ mr: 2 }} />
                  <Box>
                    <Typography variant='h4'>{stats.completed}</Typography>
                    <Typography color='text.secondary'>Завершено</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Активные заявки */}
        <Card>
          <CardContent>
            <Typography variant='h6' gutterBottom>
              Активные заявки
            </Typography>
            {requests.length === 0 ? (
              <Alert severity='info'>У вас пока нет заявок</Alert>
            ) : (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>ID</TableCell>
                      <TableCell>Название</TableCell>
                      <TableCell>Статус</TableCell>
                      <TableCell>Дата создания</TableCell>
                      <TableCell>Действия</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {requests.slice(0, 5).map((request) => (
                      <TableRow key={request.id}>
                        <TableCell>#{request.id}</TableCell>
                        <TableCell>{request.title}</TableCell>
                        <TableCell>
                          <Chip
                            label={getStatusText(request.status)}
                            color={getStatusColor(request.status)}
                            size='small'
                          />
                        </TableCell>
                        <TableCell>
                          {request.created_at
                            ? new Date(request.created_at).toLocaleDateString('ru-RU')
                            : '-'}
                        </TableCell>
                        <TableCell>
                          <Button
                            size='small'
                            startIcon={<Visibility />}
                            onClick={() => viewRequestDetails(request.id)}
                          >
                            Подробнее
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </CardContent>
        </Card>
      </Box>
    );
  };

  // Вкладка 1: Профиль компании
  const renderCompanyProfile = () => {
    return <CustomerCompanyProfilePage hideTitle={true} />;
  };

  // Вкладка 3: Архив заявок
  const renderArchive = () => {
    if (loading) {
      return (
        <Box display='flex' justifyContent='center' alignItems='center' minHeight='400px'>
          <CircularProgress />
        </Box>
      );
    }

    return (
      <Box>
        <Typography variant='h5' gutterBottom sx={{ mb: 3 }}>
          Архив моих заявок
        </Typography>

        {requests.length === 0 ? (
          <Alert severity='info'>У вас пока нет заявок</Alert>
        ) : (
          <Box>
            {requests.map((request) => (
              <Accordion key={request.id} sx={{ mb: 2 }}>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', gap: 2 }}>
                    <Typography variant='h6' sx={{ flex: 1 }}>
                      #{request.id} - {request.title}
                    </Typography>
                    <Chip
                      label={getStatusText(request.status)}
                      color={getStatusColor(request.status)}
                      size='small'
                    />
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Box>
                    <Typography variant='body2' color='text.secondary' gutterBottom>
                      <strong>Описание:</strong> {request.description}
                    </Typography>
                    <Typography variant='body2' color='text.secondary' gutterBottom>
                      <strong>Дата создания:</strong>{' '}
                      {request.created_at
                        ? new Date(request.created_at).toLocaleString('ru-RU')
                        : '-'}
                    </Typography>
                    {request.updated_at && (
                      <Typography variant='body2' color='text.secondary' gutterBottom>
                        <strong>Последнее обновление:</strong>{' '}
                        {new Date(request.updated_at).toLocaleString('ru-RU')}
                      </Typography>
                    )}
                    {request.final_price && (
                      <Typography variant='body2' color='text.secondary' gutterBottom>
                        <strong>Итоговая стоимость:</strong> {request.final_price} руб.
                      </Typography>
                    )}
                    <Box sx={{ mt: 2 }}>
                      <Button
                        variant='outlined'
                        startIcon={<Visibility />}
                        onClick={() => viewRequestDetails(request.id)}
                      >
                        Подробнее
                      </Button>
                    </Box>
                  </Box>
                </AccordionDetails>
              </Accordion>
            ))}
          </Box>
        )}
      </Box>
    );
  };

  return (
    <Box sx={{ width: '100%', maxWidth: '1200px', mx: 'auto' }}>
      <Typography variant='h4' gutterBottom sx={{ mb: 3 }}>
        Личный кабинет заказчика
      </Typography>

      {error && (
        <Alert severity='error' sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label='customer cabinet tabs'>
          <Tab
            icon={<Dashboard />}
            label='Главная'
            iconPosition='start'
            id='customer-tab-0'
            aria-controls='customer-tabpanel-0'
          />
          <Tab
            icon={<Business />}
            label='Профиль компании'
            iconPosition='start'
            id='customer-tab-1'
            aria-controls='customer-tabpanel-1'
          />
          <Tab
            icon={<Add />}
            label='Создать заявку'
            iconPosition='start'
            id='customer-tab-2'
            aria-controls='customer-tabpanel-2'
          />
          <Tab
            icon={<Archive />}
            label='Архив моих заявок'
            iconPosition='start'
            id='customer-tab-3'
            aria-controls='customer-tabpanel-3'
          />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        {renderDashboard()}
      </TabPanel>
      <TabPanel value={tabValue} index={1}>
        {renderCompanyProfile()}
      </TabPanel>
      <TabPanel value={tabValue} index={3}>
        {renderArchive()}
      </TabPanel>
    </Box>
  );
};

export default CustomerCabinetPage;
