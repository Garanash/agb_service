import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Typography,
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
import ModernCard from 'components/modern/ModernCard';
import ModernList from 'components/modern/ModernList';
import ModernActions from 'components/modern/ModernActions';

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
      {/* Современная статистика */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <ModernCard
            title="Всего заявок"
            value={analytics?.overview?.total_requests || 0}
            subtitle={`+${analytics?.overview?.recent_requests_7d || 0} за неделю`}
            icon={<Build sx={{ fontSize: 28 }} />}
            gradient="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
            trend={{
              value: `+${analytics?.overview?.recent_requests_7d || 0} за неделю`,
              isPositive: true
            }}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <ModernCard
            title="Активные заявки"
            value={analytics?.overview?.active_requests || 0}
            subtitle="В работе"
            icon={<TrendingUp sx={{ fontSize: 28 }} />}
            gradient="linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <ModernCard
            title="Исполнители"
            value={analytics?.overview?.total_contractors || 0}
            subtitle="Зарегистрированы"
            icon={<People sx={{ fontSize: 28 }} />}
            gradient="linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <ModernCard
            title="Заказчики"
            value={analytics?.overview?.total_customers || 0}
            subtitle="Компании"
            icon={<Business sx={{ fontSize: 28 }} />}
            gradient="linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)"
          />
        </Grid>
      </Grid>

      {/* Основной контент */}
      <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
        {/* Современные последние заявки */}
        <Box sx={{ flex: '2 1 400px', minWidth: '400px' }}>
          <ModernList
            title="Последние заявки"
            items={recentRequests?.map(request => ({
              id: request.id,
              title: request.title,
              subtitle: request.description,
              description: request.address,
              status: {
                label: getStatusText(request.status),
                color: getStatusColor(request.status) as any
              },
              avatar: {
                icon: <Build sx={{ fontSize: 20 }} />,
                color: getStatusColor(request.status) === 'success' ? '#4caf50' : 
                       getStatusColor(request.status) === 'warning' ? '#ff9800' :
                       getStatusColor(request.status) === 'error' ? '#f44336' : '#2196f3'
              },
              metadata: [
                {
                  icon: <Assignment sx={{ fontSize: 14 }} />,
                  text: new Date(request.created_at).toLocaleDateString('ru-RU')
                }
              ]
            })) || []}
            emptyMessage="Нет заявок"
            emptyIcon={<Build sx={{ fontSize: 32, color: 'grey.400' }} />}
          />
        </Box>

        {/* Современные быстрые действия */}
        <Box sx={{ flex: '1 1 300px', minWidth: '300px' }}>
          <ModernActions
            title="Быстрые действия"
            actions={[
              {
                label: "Все заявки",
                icon: <Build />,
                onClick: () => navigate('/repair-requests'),
                variant: 'primary'
              },
              ...(user?.role === UserRole.CUSTOMER ? [{
                label: "Новая заявка",
                icon: <Add />,
                onClick: () => navigate('/repair-requests/new'),
                variant: 'secondary'
              }] : []),
              {
                label: "Мой профиль",
                icon: <AccountCircle />,
                onClick: () => navigate('/profile'),
                variant: 'outline'
              }
            ]}
          />
        </Box>
      </Box>
      </Box>
    </Box>
  );
};

export default DashboardPage;
