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
  Avatar,
  Divider,
  LinearProgress,
  Badge,
} from '@mui/material';
import {
  Add,
  Build,
  People,
  Business,
  TrendingUp,
  Assignment,
  AccountCircle,
  ArrowUpward,
  ArrowDownward,
  MoreVert,
  Star,
  Schedule,
  LocationOn,
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
      {/* Современная статистика */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            position: 'relative',
            overflow: 'hidden',
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              right: 0,
              width: '100px',
              height: '100px',
              background: 'rgba(255,255,255,0.1)',
              borderRadius: '50%',
              transform: 'translate(30px, -30px)',
            }
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
                    {analytics?.overview?.total_requests || 0}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Всего заявок
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                    <ArrowUpward sx={{ fontSize: 16, mr: 0.5 }} />
                    <Typography variant="caption">
                      +{analytics?.overview?.recent_requests_7d || 0} за неделю
                    </Typography>
                  </Box>
                </Box>
                <Avatar sx={{ 
                  bgcolor: 'rgba(255,255,255,0.2)', 
                  width: 56, 
                  height: 56,
                  backdropFilter: 'blur(10px)'
                }}>
                  <Build sx={{ fontSize: 28 }} />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            color: 'white',
            position: 'relative',
            overflow: 'hidden',
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              right: 0,
              width: '100px',
              height: '100px',
              background: 'rgba(255,255,255,0.1)',
              borderRadius: '50%',
              transform: 'translate(30px, -30px)',
            }
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
                    {analytics?.overview?.active_requests || 0}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Активные заявки
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                    <TrendingUp sx={{ fontSize: 16, mr: 0.5 }} />
                    <Typography variant="caption">
                      В работе
                    </Typography>
                  </Box>
                </Box>
                <Avatar sx={{ 
                  bgcolor: 'rgba(255,255,255,0.2)', 
                  width: 56, 
                  height: 56,
                  backdropFilter: 'blur(10px)'
                }}>
                  <TrendingUp sx={{ fontSize: 28 }} />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            color: 'white',
            position: 'relative',
            overflow: 'hidden',
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              right: 0,
              width: '100px',
              height: '100px',
              background: 'rgba(255,255,255,0.1)',
              borderRadius: '50%',
              transform: 'translate(30px, -30px)',
            }
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
                    {analytics?.overview?.total_contractors || 0}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Исполнители
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                    <People sx={{ fontSize: 16, mr: 0.5 }} />
                    <Typography variant="caption">
                      Зарегистрированы
                    </Typography>
                  </Box>
                </Box>
                <Avatar sx={{ 
                  bgcolor: 'rgba(255,255,255,0.2)', 
                  width: 56, 
                  height: 56,
                  backdropFilter: 'blur(10px)'
                }}>
                  <People sx={{ fontSize: 28 }} />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
            color: 'white',
            position: 'relative',
            overflow: 'hidden',
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              right: 0,
              width: '100px',
              height: '100px',
              background: 'rgba(255,255,255,0.1)',
              borderRadius: '50%',
              transform: 'translate(30px, -30px)',
            }
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
                    {analytics?.overview?.total_customers || 0}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Заказчики
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                    <Business sx={{ fontSize: 16, mr: 0.5 }} />
                    <Typography variant="caption">
                      Компании
                    </Typography>
                  </Box>
                </Box>
                <Avatar sx={{ 
                  bgcolor: 'rgba(255,255,255,0.2)', 
                  width: 56, 
                  height: 56,
                  backdropFilter: 'blur(10px)'
                }}>
                  <Business sx={{ fontSize: 28 }} />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

        {/* Основной контент */}
        <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
          {/* Современные последние заявки */}
          <Box sx={{ flex: '2 1 400px', minWidth: '400px' }}>
            <Card sx={{ 
              borderRadius: 3,
              boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255,255,255,0.2)'
            }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
                  <Typography variant="h6" sx={{ fontWeight: 'bold', color: 'text.primary' }}>
                    Последние заявки
                  </Typography>
                  <Badge badgeContent={recentRequests?.length || 0} color="primary">
                    <Assignment sx={{ color: 'primary.main' }} />
                  </Badge>
                </Box>
                
                <List sx={{ p: 0 }}>
                  {recentRequests?.map((request, index) => (
                    <React.Fragment key={request.id}>
                      <ListItem sx={{ 
                        p: 2,
                        borderRadius: 2,
                        mb: 1,
                        bgcolor: 'rgba(0,0,0,0.02)',
                        '&:hover': {
                          bgcolor: 'rgba(0,0,0,0.05)',
                          transform: 'translateY(-2px)',
                          transition: 'all 0.2s ease-in-out'
                        }
                      }}>
                        <Avatar sx={{ 
                          bgcolor: getStatusColor(request.status) === 'success' ? '#4caf50' : 
                                   getStatusColor(request.status) === 'warning' ? '#ff9800' :
                                   getStatusColor(request.status) === 'error' ? '#f44336' : '#2196f3',
                          mr: 2,
                          width: 40,
                          height: 40
                        }}>
                          <Build sx={{ fontSize: 20 }} />
                        </Avatar>
                        
                        <ListItemText
                          primary={
                            <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                              {request.title}
                            </Typography>
                          }
                          secondary={
                            <Box>
                              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                                {request.description}
                              </Typography>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                  <Schedule sx={{ fontSize: 14, mr: 0.5, color: 'text.secondary' }} />
                                  <Typography variant="caption" color="text.secondary">
                                    {new Date(request.created_at).toLocaleDateString('ru-RU')}
                                  </Typography>
                                </Box>
                                {request.address && (
                                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                    <LocationOn sx={{ fontSize: 14, mr: 0.5, color: 'text.secondary' }} />
                                    <Typography variant="caption" color="text.secondary">
                                      {request.address}
                                    </Typography>
                                  </Box>
                                )}
                              </Box>
                            </Box>
                          }
                        />
                        
                        <ListItemSecondaryAction>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Chip
                              label={getStatusText(request.status)}
                              color={getStatusColor(request.status)}
                              size="small"
                              sx={{ 
                                fontWeight: 'bold',
                                borderRadius: 2
                              }}
                            />
                            <IconButton size="small">
                              <MoreVert />
                            </IconButton>
                          </Box>
                        </ListItemSecondaryAction>
                      </ListItem>
                      {index < recentRequests.length - 1 && <Divider sx={{ mx: 2 }} />}
                    </React.Fragment>
                  ))}
                  
                  {(!recentRequests || recentRequests.length === 0) && (
                    <ListItem sx={{ p: 3, textAlign: 'center' }}>
                      <Box sx={{ width: '100%' }}>
                        <Avatar sx={{ 
                          bgcolor: 'grey.100', 
                          width: 64, 
                          height: 64, 
                          mx: 'auto', 
                          mb: 2 
                        }}>
                          <Build sx={{ fontSize: 32, color: 'grey.400' }} />
                        </Avatar>
                        <Typography variant="h6" color="text.secondary" sx={{ mb: 1 }}>
                          Нет заявок
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Создайте первую заявку или дождитесь новых
                        </Typography>
                      </Box>
                    </ListItem>
                  )}
                </List>
              </CardContent>
            </Card>
          </Box>

          {/* Современные быстрые действия */}
          <Box sx={{ flex: '1 1 300px', minWidth: '300px' }}>
            <Card sx={{ 
              borderRadius: 3,
              boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255,255,255,0.2)'
            }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <Star sx={{ color: 'primary.main', mr: 1 }} />
                  <Typography variant="h6" sx={{ fontWeight: 'bold', color: 'text.primary' }}>
                    Быстрые действия
                  </Typography>
                </Box>
                
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Button
                    variant="contained"
                    startIcon={<Build />}
                    onClick={() => navigate('/repair-requests')}
                    fullWidth
                    sx={{ 
                      borderRadius: 2,
                      py: 1.5,
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      '&:hover': {
                        background: 'linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%)',
                        transform: 'translateY(-2px)',
                        boxShadow: '0 8px 25px rgba(102, 126, 234, 0.3)'
                      },
                      transition: 'all 0.3s ease-in-out'
                    }}
                  >
                    Все заявки
                  </Button>
                  
                  {user?.role === UserRole.CUSTOMER && (
                    <Button
                      variant="contained"
                      startIcon={<Add />}
                      onClick={() => navigate('/repair-requests/new')}
                      fullWidth
                      sx={{ 
                        borderRadius: 2,
                        py: 1.5,
                        background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                        '&:hover': {
                          background: 'linear-gradient(135deg, #e881f0 0%, #f3455a 100%)',
                          transform: 'translateY(-2px)',
                          boxShadow: '0 8px 25px rgba(240, 147, 251, 0.3)'
                        },
                        transition: 'all 0.3s ease-in-out'
                      }}
                    >
                      Новая заявка
                    </Button>
                  )}
                  
                  <Button
                    variant="outlined"
                    startIcon={<AccountCircle />}
                    onClick={() => navigate('/profile')}
                    fullWidth
                    sx={{ 
                      borderRadius: 2,
                      py: 1.5,
                      borderColor: 'primary.main',
                      color: 'primary.main',
                      '&:hover': {
                        borderColor: 'primary.dark',
                        backgroundColor: 'primary.light',
                        transform: 'translateY(-2px)',
                        boxShadow: '0 8px 25px rgba(25, 118, 210, 0.2)'
                      },
                      transition: 'all 0.3s ease-in-out'
                    }}
                  >
                    Мой профиль
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

export default DashboardPage;
