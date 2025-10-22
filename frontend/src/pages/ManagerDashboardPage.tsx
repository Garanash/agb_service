import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  CircularProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  CalendarToday,
  Assignment,
  People,
  TrendingUp,
  Schedule,
  Warning,
  CheckCircle,
  Cancel,
  PlayArrow,
  Stop,
  Edit,
  Visibility,
} from '@mui/icons-material';
import { DateCalendar } from '@mui/x-date-pickers/DateCalendar';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import dayjs, { Dayjs } from 'dayjs';
import 'dayjs/locale/ru';
import relativeTime from 'dayjs/plugin/relativeTime';

// Настраиваем dayjs
dayjs.extend(relativeTime);
dayjs.locale('ru');
import { useAuth } from 'hooks/useAuth';
import { apiService } from 'services/api';

interface DashboardStats {
  total_requests: number;
  recent_requests: number;
  today_requests: number;
  status_counts: { [key: string]: number };
  avg_processing_time_hours: number;
  active_contractors: number;
  active_customers: number;
  completion_rate: number;
}

interface CalendarEvent {
  id: string;
  title: string;
  start: string;
  end: string;
  type: string;
  status: string;
  contractor_name?: string;
  customer_name: string;
  equipment_type?: string;
  address?: string;
  color: string;
}

interface ContractorWorkload {
  contractor_id: number;
  name: string;
  specializations: string[];
  active_requests: number;
  completed_requests: number;
  avg_rating: number;
  availability_status: string;
  hourly_rate?: number;
  workload_percentage: number;
}

interface RecentActivity {
  id: number;
  type: string;
  title: string;
  status: string;
  status_text: string;
  timestamp: string;
  customer_name: string;
  contractor_name?: string;
  icon: string;
}

interface UpcomingDeadline {
  id: number;
  title: string;
  deadline: string;
  days_until: number;
  status: string;
  customer_name: string;
  priority: string;
  urgency: string;
}

const ManagerDashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [workload, setWorkload] = useState<ContractorWorkload[]>([]);
  const [activity, setActivity] = useState<RecentActivity[]>([]);
  const [deadlines, setDeadlines] = useState<UpcomingDeadline[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Календарь
  const [selectedDate, setSelectedDate] = useState<Dayjs>(dayjs());
  const [calendarView, setCalendarView] = useState<'month' | 'week' | 'day'>('month');
  const [scheduleDialogOpen, setScheduleDialogOpen] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);
  const [scheduleDate, setScheduleDate] = useState<Dayjs>(dayjs());

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Проверяем роль пользователя
      if (user?.role !== 'manager' && user?.role !== 'admin') {
        console.warn('User does not have manager role, skipping manager-specific data');
        setStats({
          total_requests: 0,
          recent_requests: 0,
          today_requests: 0,
          status_counts: {},
          avg_processing_time_hours: 0,
          active_contractors: 0,
          active_customers: 0,
          completion_rate: 0
        });
        setWorkload([]);
        setActivity([]);
        setDeadlines([]);
        return;
      }
      
      // Загружаем данные параллельно с обработкой ошибок
      const [statsData, workloadData, activityData, deadlinesData] = await Promise.all([
        apiService.getManagerStats().catch(err => {
          console.warn('Failed to load manager stats:', err);
          return {};
        }),
        apiService.getContractorWorkload().catch(err => {
          console.warn('Failed to load contractor workload:', err);
          return [];
        }),
        apiService.getRecentActivity().catch(err => {
          console.warn('Failed to load recent activity:', err);
          return [];
        }),
        apiService.getUpcomingDeadlines().catch(err => {
          console.warn('Failed to load upcoming deadlines:', err);
          return [];
        })
      ]);
      
      setStats(statsData);
      setWorkload(workloadData);
      setActivity(activityData);
      setDeadlines(deadlinesData);
      
      // Загружаем события календаря для текущего месяца
      await loadCalendarEvents();
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка загрузки данных дашборда');
    } finally {
      setLoading(false);
    }
  };

  const loadCalendarEvents = async () => {
    try {
      const startDate = selectedDate.startOf('month').toISOString();
      const endDate = selectedDate.endOf('month').toISOString();
      
      const eventsData = await apiService.getCalendarEvents(startDate, endDate);
      setEvents(eventsData);
    } catch (err: any) {
      console.error('Ошибка загрузки событий календаря:', err);
    }
  };

  const handleDateChange = (newDate: Dayjs | null) => {
    if (newDate) {
      setSelectedDate(newDate);
      loadCalendarEvents();
    }
  };

  const handleScheduleRequest = async () => {
    if (!selectedEvent) return;
    
    try {
      const requestId = parseInt(selectedEvent.id.replace('request_', ''));
      await apiService.scheduleRequest(requestId, scheduleDate.toISOString());
      
      setScheduleDialogOpen(false);
      setSelectedEvent(null);
      await loadCalendarEvents();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка планирования заявки');
    }
  };

  const getStatusColor = (status: string) => {
    const colors: { [key: string]: string } = {
      'new': '#2196f3',
      'manager_review': '#ff9800',
      'clarification': '#ff5722',
      'sent_to_contractors': '#9c27b0',
      'contractor_responses': '#673ab7',
      'assigned': '#4caf50',
      'in_progress': '#00bcd4',
      'completed': '#8bc34a',
      'cancelled': '#f44336'
    };
    return colors[status] || '#757575';
  };

  const getStatusText = (status: string) => {
    const texts: { [key: string]: string } = {
      'new': 'Новая',
      'manager_review': 'На рассмотрении',
      'clarification': 'Уточнение',
      'sent_to_contractors': 'Отправлена исполнителям',
      'contractor_responses': 'Отклики получены',
      'assigned': 'Назначена',
      'in_progress': 'В работе',
      'completed': 'Завершена',
      'cancelled': 'Отменена'
    };
    return texts[status] || status;
  };

  const getUrgencyColor = (urgency: string) => {
    const colors: { [key: string]: string } = {
      'high': 'error',
      'medium': 'warning',
      'low': 'success'
    };
    return colors[urgency] || 'default';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale="ru">
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Дашборд менеджера
        </Typography>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Статистика */}
        {stats && (
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center">
                    <Assignment color="primary" sx={{ mr: 2 }} />
                    <Box>
                      <Typography variant="h4">{stats.total_requests}</Typography>
                      <Typography color="text.secondary">Всего заявок</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center">
                    <TrendingUp color="success" sx={{ mr: 2 }} />
                    <Box>
                      <Typography variant="h4">{stats.completion_rate}%</Typography>
                      <Typography color="text.secondary">Процент выполнения</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center">
                    <People color="info" sx={{ mr: 2 }} />
                    <Box>
                      <Typography variant="h4">{stats.active_contractors}</Typography>
                      <Typography color="text.secondary">Активных исполнителей</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center">
                    <Schedule color="warning" sx={{ mr: 2 }} />
                    <Box>
                      <Typography variant="h4">{stats.avg_processing_time_hours}ч</Typography>
                      <Typography color="text.secondary">Среднее время обработки</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        <Grid container spacing={3}>
          {/* Календарь */}
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Календарь заявок
                </Typography>
                
                <Box sx={{ display: 'flex', gap: 2 }}>
                  <Box sx={{ flex: 1 }}>
                    <DateCalendar
                      value={selectedDate}
                      onChange={handleDateChange}
                      sx={{ width: '100%' }}
                    />
                  </Box>
                  
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="subtitle1" gutterBottom>
                      События на {selectedDate.format('DD MMMM YYYY')}
                    </Typography>
                    
                    <List dense>
                      {events
                        .filter(event => dayjs(event.start).isSame(selectedDate, 'day'))
                        .map((event) => (
                          <ListItem key={event.id} sx={{ px: 0 }}>
                            <ListItemIcon>
                              <Box
                                sx={{
                                  width: 12,
                                  height: 12,
                                  borderRadius: '50%',
                                  backgroundColor: event.color,
                                }}
                              />
                            </ListItemIcon>
                            <ListItemText
                              primary={event.title}
                              secondary={`${event.customer_name} • ${event.equipment_type || 'Оборудование'}`}
                            />
                            <IconButton
                              size="small"
                              onClick={() => {
                                setSelectedEvent(event);
                                setScheduleDialogOpen(true);
                              }}
                            >
                              <Edit />
                            </IconButton>
                          </ListItem>
                        ))}
                    </List>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Боковая панель */}
          <Grid item xs={12} md={4}>
            {/* Предстоящие дедлайны */}
            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Предстоящие дедлайны
                </Typography>
                
                <List dense>
                  {deadlines.slice(0, 5).map((deadline) => (
                    <ListItem key={deadline.id} sx={{ px: 0 }}>
                      <ListItemIcon>
                        <Warning color={getUrgencyColor(deadline.urgency) as any} />
                      </ListItemIcon>
                      <ListItemText
                        primary={deadline.title}
                        secondary={`${deadline.customer_name} • ${deadline.days_until} дн.`}
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>

            {/* Последняя активность */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Последняя активность
                </Typography>
                
                <List dense>
                  {activity.slice(0, 5).map((item) => (
                    <ListItem key={item.id} sx={{ px: 0 }}>
                      <ListItemIcon>
                        <Typography variant="body2">{item.icon}</Typography>
                      </ListItemIcon>
                      <ListItemText
                        primary={item.title}
                        secondary={`${item.customer_name} • ${dayjs(item.timestamp).fromNow()}`}
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Загрузка исполнителей */}
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Загрузка исполнителей
            </Typography>
            
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Исполнитель</TableCell>
                    <TableCell>Специализации</TableCell>
                    <TableCell>Активные заявки</TableCell>
                    <TableCell>Загрузка</TableCell>
                    <TableCell>Статус</TableCell>
                    <TableCell>Действия</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {workload.map((contractor) => (
                    <TableRow key={contractor.contractor_id}>
                      <TableCell>
                        <Box display="flex" alignItems="center">
                          <Avatar sx={{ mr: 2, width: 32, height: 32 }}>
                            {contractor.name.charAt(0)}
                          </Avatar>
                          {contractor.name}
                        </Box>
                      </TableCell>
                      <TableCell>
                        {contractor.specializations.slice(0, 2).map((spec) => (
                          <Chip key={spec} label={spec} size="small" sx={{ mr: 1, mb: 1 }} />
                        ))}
                        {contractor.specializations.length > 2 && (
                          <Chip label={`+${contractor.specializations.length - 2}`} size="small" />
                        )}
                      </TableCell>
                      <TableCell>{contractor.active_requests}</TableCell>
                      <TableCell>
                        <Box display="flex" alignItems="center">
                          <LinearProgress
                            variant="determinate"
                            value={contractor.workload_percentage}
                            sx={{ width: 100, mr: 1 }}
                          />
                          <Typography variant="body2">
                            {contractor.workload_percentage}%
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={contractor.availability_status === 'available' ? 'Доступен' : 'Занят'}
                          color={contractor.availability_status === 'available' ? 'success' : 'warning'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Tooltip title="Просмотреть профиль">
                          <IconButton size="small">
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>

        {/* Диалог планирования */}
        <Dialog open={scheduleDialogOpen} onClose={() => setScheduleDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Планирование заявки</DialogTitle>
          <DialogContent>
            {selectedEvent && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  {selectedEvent.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Заказчик: {selectedEvent.customer_name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Оборудование: {selectedEvent.equipment_type}
                </Typography>
              </Box>
            )}
            
            <TextField
              fullWidth
              type="datetime-local"
              label="Дата и время выполнения"
              value={scheduleDate.format('YYYY-MM-DDTHH:mm')}
              onChange={(e) => setScheduleDate(dayjs(e.target.value))}
              InputLabelProps={{ shrink: true }}
              sx={{ mt: 2 }}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setScheduleDialogOpen(false)}>Отмена</Button>
            <Button onClick={handleScheduleRequest} variant="contained">
              Запланировать
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </LocalizationProvider>
  );
};

export default ManagerDashboardPage;
