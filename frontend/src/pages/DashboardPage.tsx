import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Chip,
  IconButton,
} from '@mui/material';
import {
  Add,
  Build,
  People,
  Business,
  TrendingUp,
  Assignment,
  AccountCircle,
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
          apiService.getDashboardAnalytics()
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
            variant="contained"
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
            variant="contained"
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
              variant="contained"
              startIcon={<Add />}
              onClick={() => navigate('/repair-requests/new')}
            >
              Создать заявку
            </Button>
            <Button
              variant="outlined"
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
      <Typography variant="h4" gutterBottom>
        Добро пожаловать, {user?.first_name}!
      </Typography>
      
      <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 3 }}>
        Роль: {user?.role === UserRole.ADMIN ? 'Администратор' : 
               user?.role === UserRole.CUSTOMER ? 'Заказчик' :
               user?.role === UserRole.CONTRACTOR ? 'Исполнитель' :
               user?.role === UserRole.SERVICE_ENGINEER ? 'Сервисный инженер' : 'Пользователь'}
      </Typography>

      {getRoleSpecificActions()}

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {/* Статистика */}
        <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
          <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Build color="primary" sx={{ mr: 2 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Всего заявок
                    </Typography>
                    <Typography variant="h4">
                      {analytics?.overview?.total_requests || 0}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Box>

          <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <TrendingUp color="success" sx={{ mr: 2 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Активные
                    </Typography>
                    <Typography variant="h4">
                      {analytics?.overview?.active_requests || 0}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Box>

          <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <People color="info" sx={{ mr: 2 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Исполнители
                    </Typography>
                    <Typography variant="h4">
                      {analytics?.overview?.total_contractors || 0}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Box>

          <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Business color="warning" sx={{ mr: 2 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Заказчики
                    </Typography>
                    <Typography variant="h4">
                      {analytics?.overview?.total_customers || 0}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Box>
        </Box>

        {/* Основной контент */}
        <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
          {/* Последние заявки */}
          <Box sx={{ flex: '2 1 400px', minWidth: '400px' }}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Последние заявки
              </Typography>
              <List>
                {recentRequests?.map((request) => (
                  <ListItem key={request.id} divider>
                    <ListItemText
                      primary={request.title}
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            {request.description}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {new Date(request.created_at).toLocaleDateString('ru-RU')}
                          </Typography>
                        </Box>
                      }
                    />
                    <ListItemSecondaryAction>
                      <Chip
                        label={getStatusText(request.status)}
                        color={getStatusColor(request.status)}
                        size="small"
                      />
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
                {(!recentRequests || recentRequests.length === 0) && (
                  <ListItem>
                    <ListItemText
                      primary="Нет заявок"
                      secondary="Создайте первую заявку или дождитесь новых"
                    />
                  </ListItem>
                )}
              </List>
            </Paper>
          </Box>

          {/* Быстрые действия */}
          <Box sx={{ flex: '1 1 300px', minWidth: '300px' }}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Быстрые действия
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Button
                  variant="outlined"
                  startIcon={<Build />}
                  onClick={() => navigate('/repair-requests')}
                  fullWidth
                >
                  Все заявки
                </Button>
                {user?.role === UserRole.CUSTOMER && (
                  <Button
                    variant="outlined"
                    startIcon={<Add />}
                    onClick={() => navigate('/repair-requests/new')}
                    fullWidth
                  >
                    Новая заявка
                  </Button>
                )}
                <Button
                  variant="outlined"
                  startIcon={<AccountCircle />}
                  onClick={() => navigate('/profile')}
                  fullWidth
                >
                  Мой профиль
                </Button>
              </Box>
            </Paper>
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

export default DashboardPage;
