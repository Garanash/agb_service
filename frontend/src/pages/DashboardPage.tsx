import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Typography,
  Button,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
} from '@mui/material';
import {
  Build,
  People,
  Business,
  TrendingUp,
  Assignment,
  AccountCircle,
  Add,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from 'hooks/useAuth';
import { apiService } from 'services/api';
import { RepairRequest, RequestStatus, UserRole } from 'types/api';

const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [recentRequests, setRecentRequests] = useState<RepairRequest[]>([]);
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [requestsResponse, analyticsData] = await Promise.all([
          apiService.getRepairRequests(1, 5),
          apiService.getDashboardAnalytics(),
        ]);

        setRecentRequests(requestsResponse.items || []);
        setAnalytics(analyticsData);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
        setRecentRequests([]);
        setAnalytics(null);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const getStatusColor = (status: RequestStatus) => {
    switch (status) {
      case RequestStatus.NEW:
        return 'default';
      case RequestStatus.MANAGER_REVIEW:
        return 'warning';
      case RequestStatus.CLARIFICATION:
        return 'warning';
      case RequestStatus.SENT_TO_CONTRACTORS:
        return 'info';
      case RequestStatus.CONTRACTOR_RESPONSES:
        return 'info';
      case RequestStatus.ASSIGNED:
        return 'info';
      case RequestStatus.IN_PROGRESS:
        return 'primary';
      case RequestStatus.COMPLETED:
        return 'success';
      case RequestStatus.CANCELLED:
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusText = (status: RequestStatus) => {
    switch (status) {
      case RequestStatus.NEW:
        return 'Новая';
      case RequestStatus.MANAGER_REVIEW:
        return 'На рассмотрении';
      case RequestStatus.CLARIFICATION:
        return 'Уточнение';
      case RequestStatus.SENT_TO_CONTRACTORS:
        return 'Отправлена исполнителям';
      case RequestStatus.CONTRACTOR_RESPONSES:
        return 'Ожидание ответов';
      case RequestStatus.ASSIGNED:
        return 'Назначена';
      case RequestStatus.IN_PROGRESS:
        return 'В работе';
      case RequestStatus.COMPLETED:
        return 'Завершена';
      case RequestStatus.CANCELLED:
        return 'Отменена';
      default:
        return status;
    }
  };

  const getRoleSpecificActions = () => {
    switch (user?.role) {
      case UserRole.CUSTOMER:
        return (
          <Button
            variant='contained'
            startIcon={<Add />}
            onClick={() => navigate('/repair-requests/new')}
            sx={{ mb: 2 }}
          >
            Создать заявку
          </Button>
        );
      case UserRole.CONTRACTOR:
        return (
          <Button
            variant='contained'
            startIcon={<Assignment />}
            onClick={() => navigate('/repair-requests')}
            sx={{ mb: 2 }}
          >
            Просмотреть заявки
          </Button>
        );
      case UserRole.ADMIN:
        return (
          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            <Button
              variant='contained'
              startIcon={<Add />}
              onClick={() => navigate('/repair-requests/new')}
            >
              Создать заявку
            </Button>
            <Button
              variant='outlined'
              startIcon={<People />}
              onClick={() => navigate('/contractors')}
            >
              Управление исполнителями
            </Button>
          </Box>
        );
      default:
        return null;
    }
  };

  return (
    <Box>
      <Typography variant='h4' gutterBottom>
        Добро пожаловать, {user?.first_name}!
      </Typography>

      <Typography variant='subtitle1' color='text.secondary' sx={{ mb: 3 }}>
        Роль:{' '}
        {user?.role === UserRole.ADMIN
          ? 'Администратор'
          : user?.role === UserRole.CUSTOMER
            ? 'Заказчик'
            : user?.role === UserRole.CONTRACTOR
              ? 'Исполнитель'
              : user?.role === UserRole.SERVICE_ENGINEER
                ? 'Сервисный инженер'
                : 'Пользователь'}
      </Typography>

      {getRoleSpecificActions()}

      {/* Статистика - не показываем для исполнителя */}
      {user?.role !== UserRole.CONTRACTOR && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}
              >
                <Box>
                  <Typography variant='h4' component='div'>
                    {analytics?.overview?.total_requests || 0}
                  </Typography>
                  <Typography variant='body2' color='text.secondary'>
                    Всего заявок
                  </Typography>
                  <Typography variant='caption' color='success.main'>
                    +{analytics?.overview?.recent_requests_7d || 0} за неделю
                  </Typography>
                </Box>
                <Build sx={{ fontSize: 40, color: 'primary.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}
              >
                <Box>
                  <Typography variant='h4' component='div'>
                    {analytics?.overview?.active_requests || 0}
                  </Typography>
                  <Typography variant='body2' color='text.secondary'>
                    Активные заявки
                  </Typography>
                  <Typography variant='caption' color='text.secondary'>
                    В работе
                  </Typography>
                </Box>
                <TrendingUp sx={{ fontSize: 40, color: 'success.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}
              >
                <Box>
                  <Typography variant='h4' component='div'>
                    {analytics?.overview?.total_contractors || 0}
                  </Typography>
                  <Typography variant='body2' color='text.secondary'>
                    Исполнители
                  </Typography>
                  <Typography variant='caption' color='text.secondary'>
                    Зарегистрированы
                  </Typography>
                </Box>
                <People sx={{ fontSize: 40, color: 'info.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}
              >
                <Box>
                  <Typography variant='h4' component='div'>
                    {analytics?.overview?.total_customers || 0}
                  </Typography>
                  <Typography variant='body2' color='text.secondary'>
                    Заказчики
                  </Typography>
                  <Typography variant='caption' color='text.secondary'>
                    Компании
                  </Typography>
                </Box>
                <Business sx={{ fontSize: 40, color: 'warning.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      )}

      {/* Основной контент */}
      <Grid container spacing={3}>
        {/* Последние заявки */}
        <Grid item xs={12} md={user?.role === UserRole.CONTRACTOR ? 12 : 8}>
          <Card>
            <CardContent>
              <Typography variant='h6' gutterBottom>
                Последние заявки
              </Typography>
              {recentRequests.length > 0 ? (
                <List>
                  {recentRequests.map(request => (
                    <ListItem key={request.id} divider>
                      <ListItemIcon>
                        <Build />
                      </ListItemIcon>
                      <ListItemText
                        primary={request.title}
                        secondary={
                          <Box>
                            <Typography variant='body2' color='text.secondary'>
                              {request.description}
                            </Typography>
                            <Box
                              sx={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: 1,
                                mt: 1,
                              }}
                            >
                              <Chip
                                label={getStatusText(request.status)}
                                color={getStatusColor(request.status) as any}
                                size='small'
                              />
                              <Typography
                                variant='caption'
                                color='text.secondary'
                              >
                                {new Date(
                                  request.created_at,
                                ).toLocaleDateString('ru-RU')}
                              </Typography>
                            </Box>
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Build sx={{ fontSize: 48, color: 'grey.400', mb: 2 }} />
                  <Typography variant='h6' color='text.secondary'>
                    Нет заявок
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Быстрые действия - не показываем для исполнителя */}
        {user?.role !== UserRole.CONTRACTOR && (
          <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant='h6' gutterBottom>
                Быстрые действия
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Button
                  variant='contained'
                  startIcon={<Build />}
                  onClick={() => navigate('/repair-requests')}
                  fullWidth
                >
                  Все заявки
                </Button>
                {user?.role === UserRole.CUSTOMER && (
                  <Button
                    variant='outlined'
                    startIcon={<Add />}
                    onClick={() => navigate('/repair-requests/new')}
                    fullWidth
                  >
                    Новая заявка
                  </Button>
                )}
                <Button
                  variant='outlined'
                  startIcon={<AccountCircle />}
                  onClick={() => navigate('/profile')}
                  fullWidth
                >
                  Мой профиль
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default DashboardPage;
