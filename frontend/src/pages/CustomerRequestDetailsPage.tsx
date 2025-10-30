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
  Divider,
  Paper,
} from '@mui/material';
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineOppositeContent,
} from '@mui/lab';
import { ArrowBack, CheckCircle, Pending, Build, Assignment, Cancel } from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from 'hooks/useAuth';
import { apiService } from 'services/api';
import { RequestStatus } from 'types/api';

const CustomerRequestDetailsPage: React.FC = () => {
  const { requestId } = useParams<{ requestId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [request, setRequest] = useState<any>(null);

  useEffect(() => {
    if (requestId) {
      loadRequestDetails();
    }
  }, [requestId]);

  const loadRequestDetails = async () => {
    try {
      setLoading(true);
      const requestData = await apiService.getRepairRequest(parseInt(requestId!));
      setRequest(requestData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка загрузки данных заявки');
    } finally {
      setLoading(false);
    }
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

  const getStatusIcon = (status: RequestStatus) => {
    switch (status) {
      case 'completed':
        return <CheckCircle />;
      case 'cancelled':
        return <Cancel />;
      case 'in_progress':
      case 'assigned':
        return <Build />;
      case 'manager_review':
      case 'clarification':
        return <Pending />;
      default:
        return <Assignment />;
    }
  };

  const getStatusTimeline = () => {
    if (!request) return [];

    const timeline: Array<{ status: RequestStatus; date: string; title: string }> = [];

    if (request.created_at) {
      timeline.push({
        status: 'new' as RequestStatus,
        date: request.created_at,
        title: 'Заявка создана',
      });
    }

    if (request.status !== 'new' && request.updated_at) {
      timeline.push({
        status: request.status,
        date: request.updated_at,
        title: `Статус изменен: ${getStatusText(request.status)}`,
      });
    }

    if (request.assigned_at) {
      timeline.push({
        status: 'assigned' as RequestStatus,
        date: request.assigned_at,
        title: 'Исполнитель назначен',
      });
    }

    if (request.processed_at) {
      timeline.push({
        status: 'in_progress' as RequestStatus,
        date: request.processed_at,
        title: 'Работы начаты',
      });
    }

    return timeline;
  };

  if (loading) {
    return (
      <Box display='flex' justifyContent='center' alignItems='center' minHeight='400px'>
        <CircularProgress />
      </Box>
    );
  }

  if (error || !request) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity='error'>{error || 'Заявка не найдена'}</Alert>
        <Button sx={{ mt: 2 }} onClick={() => navigate('/customer/cabinet')}>
          Вернуться в кабинет
        </Button>
      </Box>
    );
  }

  const timeline = getStatusTimeline();

  return (
    <Box sx={{ p: 3, maxWidth: '1200px', mx: 'auto' }}>
      <Button
        startIcon={<ArrowBack />}
        onClick={() => navigate('/customer/cabinet')}
        sx={{ mb: 3 }}
      >
        Вернуться в кабинет
      </Button>

      <Typography variant='h4' gutterBottom>
        Заявка #{request.id}
      </Typography>

      <Grid container spacing={3} sx={{ mt: 1 }}>
        {/* Основная информация */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant='h6' gutterBottom>
                Основная информация
              </Typography>
              <Divider sx={{ mb: 2 }} />

              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant='subtitle2' color='text.secondary'>
                    Название
                  </Typography>
                  <Typography variant='body1'>{request.title}</Typography>
                </Grid>

                <Grid item xs={12}>
                  <Typography variant='subtitle2' color='text.secondary'>
                    Описание
                  </Typography>
                  <Typography variant='body1'>{request.description}</Typography>
                </Grid>

                {request.urgency && (
                  <Grid item xs={12} sm={6}>
                    <Typography variant='subtitle2' color='text.secondary'>
                      Срочность
                    </Typography>
                    <Chip
                      label={
                        request.urgency === 'critical'
                          ? 'Критическая'
                          : request.urgency === 'high'
                          ? 'Высокая'
                          : request.urgency === 'medium'
                          ? 'Средняя'
                          : 'Низкая'
                      }
                      color={request.urgency === 'critical' ? 'error' : 'default'}
                      size='small'
                    />
                  </Grid>
                )}

                <Grid item xs={12} sm={6}>
                  <Typography variant='subtitle2' color='text.secondary'>
                    Статус
                  </Typography>
                  <Chip
                    label={getStatusText(request.status)}
                    color={getStatusColor(request.status)}
                    icon={getStatusIcon(request.status)}
                  />
                </Grid>

                {request.address && (
                  <Grid item xs={12}>
                    <Typography variant='subtitle2' color='text.secondary'>
                      Адрес
                    </Typography>
                    <Typography variant='body1'>
                      {[request.region, request.city, request.address]
                        .filter(Boolean)
                        .join(', ')}
                    </Typography>
                  </Grid>
                )}

                {request.equipment_type && (
                  <Grid item xs={12} sm={6}>
                    <Typography variant='subtitle2' color='text.secondary'>
                      Тип оборудования
                    </Typography>
                    <Typography variant='body1'>{request.equipment_type}</Typography>
                  </Grid>
                )}

                {request.equipment_brand && (
                  <Grid item xs={12} sm={6}>
                    <Typography variant='subtitle2' color='text.secondary'>
                      Бренд оборудования
                    </Typography>
                    <Typography variant='body1'>{request.equipment_brand}</Typography>
                  </Grid>
                )}

                {request.final_price && (
                  <Grid item xs={12}>
                    <Typography variant='subtitle2' color='text.secondary'>
                      Итоговая стоимость
                    </Typography>
                    <Typography variant='h6' color='primary'>
                      {request.final_price} руб.
                    </Typography>
                  </Grid>
                )}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* История статусов */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant='h6' gutterBottom>
                История статусов
              </Typography>
              <Divider sx={{ mb: 2 }} />

              {timeline.length === 0 ? (
                <Alert severity='info'>История пока пуста</Alert>
              ) : (
                <Timeline>
                  {timeline.map((item, index) => (
                    <TimelineItem key={index}>
                      <TimelineOppositeContent sx={{ flex: 0.3 }}>
                        <Typography variant='caption' color='text.secondary'>
                          {new Date(item.date).toLocaleDateString('ru-RU')}
                          <br />
                          {new Date(item.date).toLocaleTimeString('ru-RU', {
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </Typography>
                      </TimelineOppositeContent>
                      <TimelineSeparator>
                        <TimelineDot color={getStatusColor(item.status)}>
                          {getStatusIcon(item.status)}
                        </TimelineDot>
                        {index < timeline.length - 1 && <TimelineConnector />}
                      </TimelineSeparator>
                      <TimelineContent>
                        <Typography variant='body2'>{item.title}</Typography>
                      </TimelineContent>
                    </TimelineItem>
                  ))}
                </Timeline>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default CustomerRequestDetailsPage;

