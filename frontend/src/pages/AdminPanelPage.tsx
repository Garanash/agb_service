import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Tooltip,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Menu,
  MenuItem as MenuItemComponent,
  Avatar,
  Badge,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Dashboard,
  People,
  Assignment,
  Security,
  Description,
  Telegram,
  TrendingUp,
  TrendingDown,
  MoreVert,
  Edit,
  Delete,
  Block,
  CheckCircle,
  Cancel,
  Visibility,
  FilterList,
  Search,
  Refresh,
  Download,
  ExpandMore,
  Person,
  Business,
  Build,
  Schedule,
  LocationOn,
  PriorityHigh,
} from '@mui/icons-material';
import { useAuth } from 'hooks/useAuth';
import { apiService } from 'services/api';
import { UserRole, RequestStatus } from 'types/api';

interface AdminDashboard {
  user_stats: {
    total_users: number;
    active_users: number;
    verified_users: number;
    recent_users: number;
    users_by_role: { [key: string]: number };
  };
  request_stats: {
    total_requests: number;
    recent_requests: number;
    requests_by_status: { [key: string]: number };
  };
  verification_stats: {
    total_verifications: number;
    pending_verifications: number;
    approved_verifications: number;
  };
  document_stats: {
    total_documents: number;
    pending_documents: number;
    completed_documents: number;
  };
  top_contractors: Array<{
    id: number;
    name: string;
    request_count: number;
  }>;
  top_customers: Array<{
    id: number;
    company_name: string;
    request_count: number;
  }>;
}

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  is_active: boolean;
  email_verified: boolean;
  created_at: string;
}

interface RepairRequest {
  id: number;
  title: string;
  description: string;
  status: RequestStatus;
  priority: string;
  urgency: string;
  created_at: string;
  customer_id: number;
  manager_id?: number;
  assigned_contractor_id?: number;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`admin-tabpanel-${index}`}
      aria-labelledby={`admin-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const AdminPanelPage: React.FC = () => {
  const { user } = useAuth();
  const [dashboard, setDashboard] = useState<AdminDashboard | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [requests, setRequests] = useState<RepairRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState(0);
  
  // Фильтры
  const [userFilters, setUserFilters] = useState({
    role: '',
    status: '',
    search: ''
  });
  const [requestFilters, setRequestFilters] = useState({
    status: '',
    priority: '',
    urgency: '',
    search: ''
  });
  
  // Диалоги
  const [userDialogOpen, setUserDialogOpen] = useState(false);
  const [requestDialogOpen, setRequestDialogOpen] = useState(false);
  const [createUserDialogOpen, setCreateUserDialogOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [selectedRequest, setSelectedRequest] = useState<RepairRequest | null>(null);
  const [userMenuAnchor, setUserMenuAnchor] = useState<null | HTMLElement>(null);
  
  // Состояние для создания пользователя
  const [newUser, setNewUser] = useState({
    username: '',
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    middle_name: '',
    phone: '',
    role: 'customer' as UserRole,
    is_active: true,
    email_verified: false
  });
  const [requestMenuAnchor, setRequestMenuAnchor] = useState<null | HTMLElement>(null);

  useEffect(() => {
    loadDashboardData();
    loadUsers();
    loadRequests();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const dashboardData = await apiService.getAdminDashboard();
      setDashboard(dashboardData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка загрузки данных дашборда');
    } finally {
      setLoading(false);
    }
  };

  const loadUsers = async () => {
    try {
      console.log('Loading users with filters:', userFilters);
      const usersData = await apiService.getAdminUsers(userFilters);
      console.log('Users loaded:', usersData);
      setUsers(usersData);
    } catch (err: any) {
      console.error('Error loading users:', err);
      setError(err.response?.data?.detail || 'Ошибка загрузки пользователей');
    }
  };

  const loadRequests = async () => {
    try {
      console.log('Loading requests with filters:', requestFilters);
      const requestsData = await apiService.getAdminRequests(requestFilters);
      console.log('Requests loaded:', requestsData);
      setRequests(requestsData);
    } catch (err: any) {
      console.error('Error loading requests:', err);
      setError(err.response?.data?.detail || 'Ошибка загрузки заявок');
    }
  };

  const handleUserStatusUpdate = async (userId: number, updates: any) => {
    try {
      await apiService.updateUserStatus(userId, updates);
      await loadUsers();
      await loadDashboardData();
      setSuccess('Статус пользователя обновлен');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка обновления статуса пользователя');
    }
  };

  const handleUserDelete = async (userId: number) => {
    try {
      await apiService.deleteUser(userId);
      await loadUsers();
      await loadDashboardData();
      setSuccess('Пользователь удален');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка удаления пользователя');
    }
  };

  const handleRequestStatusUpdate = async (requestId: number, updates: any) => {
    try {
      await apiService.updateRequestStatus(requestId, updates);
      await loadRequests();
      await loadDashboardData();
      setSuccess('Статус заявки обновлен');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка обновления статуса заявки');
    }
  };

  const handleCreateUser = async () => {
    try {
      // Валидация
      if (!newUser.username || !newUser.email || !newUser.password || !newUser.first_name || !newUser.last_name) {
        setError('Заполните все обязательные поля');
        return;
      }

      // Создаем пользователя через API
      await apiService.createUser(newUser);
      
      // Очищаем форму
      setNewUser({
        username: '',
        email: '',
        password: '',
        first_name: '',
        last_name: '',
        middle_name: '',
        phone: '',
        role: 'customer' as UserRole,
        is_active: true,
        email_verified: false
      });
      
      // Закрываем диалог и обновляем данные
      setCreateUserDialogOpen(false);
      await loadUsers();
      await loadDashboardData();
      setSuccess('Пользователь успешно создан');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка создания пользователя');
    }
  };

  const getStatusColor = (status: string) => {
    const colors: { [key: string]: string } = {
      'new': 'info',
      'manager_review': 'warning',
      'clarification': 'warning',
      'sent_to_contractors': 'info',
      'contractor_responses': 'info',
      'assigned': 'success',
      'in_progress': 'primary',
      'completed': 'success',
      'cancelled': 'error'
    };
    return colors[status] || 'default';
  };

  const getStatusText = (status: string) => {
    const texts: { [key: string]: string } = {
      'new': 'Новая',
      'manager_review': 'На рассмотрении',
      'clarification': 'Уточнение',
      'sent_to_contractors': 'Отправлена исполнителям',
      'contractor_responses': 'Отклики исполнителей',
      'assigned': 'Назначена',
      'in_progress': 'В работе',
      'completed': 'Завершена',
      'cancelled': 'Отменена'
    };
    return texts[status] || status;
  };

  const getRoleText = (role: UserRole) => {
    const texts: { [key: string]: string } = {
      'admin': 'Администратор',
      'customer': 'Заказчик',
      'contractor': 'Исполнитель',
      'manager': 'Менеджер',
      'security': 'Служба безопасности',
      'hr': 'HR'
    };
    return texts[role] || role;
  };

  const getRoleColor = (role: UserRole) => {
    const colors: { [key: string]: string } = {
      'admin': 'error',
      'customer': 'primary',
      'contractor': 'secondary',
      'manager': 'warning',
      'security': 'info',
      'hr': 'success'
    };
    return colors[role] || 'default';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Админ панель
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {/* Дашборд */}
      {dashboard && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          {/* Статистика пользователей */}
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <People color="primary" sx={{ mr: 2 }} />
                  <Box>
                    <Typography variant="h4">{dashboard.user_stats.total_users}</Typography>
                    <Typography color="text.secondary">Всего пользователей</Typography>
                    <Typography variant="body2" color="success.main">
                      +{dashboard.user_stats.recent_users} за 30 дней
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Статистика заявок */}
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <Assignment color="secondary" sx={{ mr: 2 }} />
                  <Box>
                    <Typography variant="h4">{dashboard.request_stats.total_requests}</Typography>
                    <Typography color="text.secondary">Всего заявок</Typography>
                    <Typography variant="body2" color="info.main">
                      +{dashboard.request_stats.recent_requests} за 30 дней
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Статистика проверок */}
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <Security color="warning" sx={{ mr: 2 }} />
                  <Box>
                    <Typography variant="h4">{dashboard.verification_stats.pending_verifications}</Typography>
                    <Typography color="text.secondary">Ожидают проверки</Typography>
                    <Typography variant="body2" color="warning.main">
                      {dashboard.verification_stats.approved_verifications} одобрено
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Статистика документов */}
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <Description color="success" sx={{ mr: 2 }} />
                  <Box>
                    <Typography variant="h4">{dashboard.document_stats.pending_documents}</Typography>
                    <Typography color="text.secondary">Ожидают документы</Typography>
                    <Typography variant="body2" color="success.main">
                      {dashboard.document_stats.completed_documents} завершено
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Топ исполнители */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Топ исполнители
                </Typography>
                <List>
                  {dashboard.top_contractors.map((contractor, index) => (
                    <ListItem key={contractor.id}>
                      <ListItemText
                        primary={`${index + 1}. ${contractor.name}`}
                        secondary={`${contractor.request_count} заявок`}
                      />
                      <Chip
                        label={contractor.request_count}
                        color="primary"
                        size="small"
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>

          {/* Топ заказчики */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Топ заказчики
                </Typography>
                <List>
                  {dashboard.top_customers.map((customer, index) => (
                    <ListItem key={customer.id}>
                      <ListItemText
                        primary={`${index + 1}. ${customer.company_name}`}
                        secondary={`${customer.request_count} заявок`}
                      />
                      <Chip
                        label={customer.request_count}
                        color="secondary"
                        size="small"
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Табы */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
          <Tab label="Пользователи" />
          <Tab label="Заявки" />
          <Tab label="Статистика" />
        </Tabs>
      </Box>

      {/* Пользователи */}
      <TabPanel value={tabValue} index={0}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Управление пользователями</Typography>
          <Box display="flex" gap={1}>
            <Button
              variant="contained"
              startIcon={<People />}
              onClick={() => setCreateUserDialogOpen(true)}
              sx={{ mr: 2 }}
            >
              Создать пользователя
            </Button>
            <TextField
              size="small"
              placeholder="Поиск пользователей..."
              value={userFilters.search}
              onChange={(e) => setUserFilters({ ...userFilters, search: e.target.value })}
            />
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Роль</InputLabel>
              <Select
                value={userFilters.role}
                onChange={(e) => setUserFilters({ ...userFilters, role: e.target.value })}
                label="Роль"
              >
                <MenuItem value="">Все роли</MenuItem>
                <MenuItem value="admin">Администратор</MenuItem>
                <MenuItem value="customer">Заказчик</MenuItem>
                <MenuItem value="contractor">Исполнитель</MenuItem>
                <MenuItem value="manager">Менеджер</MenuItem>
                <MenuItem value="security">Служба безопасности</MenuItem>
                <MenuItem value="hr">HR</MenuItem>
              </Select>
            </FormControl>
            <Button variant="outlined" onClick={loadUsers}>
              <Search />
            </Button>
          </Box>
        </Box>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Пользователь</TableCell>
                <TableCell>Роль</TableCell>
                <TableCell>Статус</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Дата регистрации</TableCell>
                <TableCell>Действия</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>
                    <Box display="flex" alignItems="center">
                      <Avatar sx={{ mr: 2, width: 32, height: 32 }}>
                        {user.first_name?.[0] || user.username[0]}
                      </Avatar>
                      <Box>
                        <Typography variant="subtitle2">
                          {user.first_name} {user.last_name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          @{user.username}
                        </Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={getRoleText(user.role)}
                      color={getRoleColor(user.role) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Box>
                      <Chip
                        label={user.is_active ? 'Активен' : 'Заблокирован'}
                        color={user.is_active ? 'success' : 'error'}
                        size="small"
                        sx={{ mb: 0.5 }}
                      />
                      <Chip
                        label={user.email_verified ? 'Подтвержден' : 'Не подтвержден'}
                        color={user.email_verified ? 'success' : 'warning'}
                        size="small"
                      />
                    </Box>
                  </TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>
                    {new Date(user.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <IconButton
                      onClick={(e) => {
                        setUserMenuAnchor(e.currentTarget);
                        setSelectedUser(user);
                      }}
                    >
                      <MoreVert />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>

      {/* Заявки */}
      <TabPanel value={tabValue} index={1}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Управление заявками</Typography>
          <Box display="flex" gap={1}>
            <TextField
              size="small"
              placeholder="Поиск заявок..."
              value={requestFilters.search}
              onChange={(e) => setRequestFilters({ ...requestFilters, search: e.target.value })}
            />
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Статус</InputLabel>
              <Select
                value={requestFilters.status}
                onChange={(e) => setRequestFilters({ ...requestFilters, status: e.target.value })}
                label="Статус"
              >
                <MenuItem value="">Все статусы</MenuItem>
                <MenuItem value="new">Новая</MenuItem>
                <MenuItem value="manager_review">На рассмотрении</MenuItem>
                <MenuItem value="assigned">Назначена</MenuItem>
                <MenuItem value="in_progress">В работе</MenuItem>
                <MenuItem value="completed">Завершена</MenuItem>
                <MenuItem value="cancelled">Отменена</MenuItem>
              </Select>
            </FormControl>
            <Button variant="outlined" onClick={loadRequests}>
              <Search />
            </Button>
          </Box>
        </Box>

        <TableContainer component={Paper} sx={{ mt: 2 }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Название</TableCell>
                <TableCell>Описание</TableCell>
                <TableCell>Статус</TableCell>
                <TableCell>Приоритет</TableCell>
                <TableCell>Срочность</TableCell>
                <TableCell>Дата создания</TableCell>
                <TableCell>Заказчик</TableCell>
                <TableCell>Исполнитель</TableCell>
                <TableCell>Действия</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {requests.map((request) => (
                <TableRow
                  key={request.id}
                  sx={{
                    '&:hover': {
                      backgroundColor: '#f5f5f5',
                    }
                  }}
                >
                  <TableCell>
                    <Typography variant="body2" fontWeight="bold">
                      #{request.id}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                      {request.title}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" noWrap sx={{ maxWidth: 300 }}>
                      {request.description}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={getStatusText(request.status)}
                      color={getStatusColor(request.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={request.priority}
                      color="info"
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={request.urgency}
                      color="warning"
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {new Date(request.created_at).toLocaleDateString('ru-RU', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {request.customer_id || '-'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {request.assigned_contractor_id || '-'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <IconButton
                      onClick={(e) => {
                        setRequestMenuAnchor(e.currentTarget);
                        setSelectedRequest(request);
                      }}
                      size="small"
                    >
                      <MoreVert />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
              
              {requests.length === 0 && (
                <TableRow>
                  <TableCell colSpan={10} align="center">
                    <Typography variant="body1" color="text.secondary">
                      Нет заявок для отображения
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>

      {/* Статистика */}
      <TabPanel value={tabValue} index={2}>
        <Typography variant="h6" gutterBottom>
          Детальная статистика
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Распределение пользователей по ролям
                </Typography>
                {dashboard && Object.entries(dashboard.user_stats.users_by_role).map(([role, count]) => (
                  <Box key={role} display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                    <Typography variant="body2">{getRoleText(role as UserRole)}</Typography>
                    <Box display="flex" alignItems="center" width="60%">
                      <LinearProgress
                        variant="determinate"
                        value={(count / dashboard.user_stats.total_users) * 100}
                        sx={{ width: '100%', mr: 1 }}
                      />
                      <Typography variant="body2">{count}</Typography>
                    </Box>
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Распределение заявок по статусам
                </Typography>
                {dashboard && Object.entries(dashboard.request_stats.requests_by_status).map(([status, count]) => (
                  <Box key={status} display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                    <Typography variant="body2">{getStatusText(status)}</Typography>
                    <Box display="flex" alignItems="center" width="60%">
                      <LinearProgress
                        variant="determinate"
                        value={(count / dashboard.request_stats.total_requests) * 100}
                        sx={{ width: '100%', mr: 1 }}
                      />
                      <Typography variant="body2">{count}</Typography>
                    </Box>
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Меню действий для пользователей */}
      <Menu
        anchorEl={userMenuAnchor}
        open={Boolean(userMenuAnchor)}
        onClose={() => setUserMenuAnchor(null)}
      >
        <MenuItemComponent onClick={() => {
          setUserMenuAnchor(null);
          setUserDialogOpen(true);
        }}>
          <Edit sx={{ mr: 1 }} />
          Редактировать
        </MenuItemComponent>
        <MenuItemComponent onClick={() => {
          if (selectedUser) {
            handleUserStatusUpdate(selectedUser.id, { is_active: !selectedUser.is_active });
          }
          setUserMenuAnchor(null);
        }}>
          {selectedUser?.is_active ? <Block sx={{ mr: 1 }} /> : <CheckCircle sx={{ mr: 1 }} />}
          {selectedUser?.is_active ? 'Заблокировать' : 'Активировать'}
        </MenuItemComponent>
        <MenuItemComponent onClick={() => {
          if (selectedUser) {
            handleUserDelete(selectedUser.id);
          }
          setUserMenuAnchor(null);
        }}>
          <Delete sx={{ mr: 1 }} />
          Удалить
        </MenuItemComponent>
      </Menu>

      {/* Меню действий для заявок */}
      <Menu
        anchorEl={requestMenuAnchor}
        open={Boolean(requestMenuAnchor)}
        onClose={() => setRequestMenuAnchor(null)}
      >
        <MenuItemComponent onClick={() => {
          setRequestMenuAnchor(null);
          setRequestDialogOpen(true);
        }}>
          <Edit sx={{ mr: 1 }} />
          Редактировать статус
        </MenuItemComponent>
        <MenuItemComponent onClick={() => {
          setRequestMenuAnchor(null);
        }}>
          <Visibility sx={{ mr: 1 }} />
          Просмотреть
        </MenuItemComponent>
      </Menu>

      {/* Диалог редактирования пользователя */}
      <Dialog open={userDialogOpen} onClose={() => setUserDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Редактирование пользователя</DialogTitle>
        <DialogContent>
          {selectedUser && (
            <Box sx={{ pt: 2 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={selectedUser.is_active}
                    onChange={(e) => setSelectedUser({ ...selectedUser, is_active: e.target.checked })}
                  />
                }
                label="Активен"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={selectedUser.email_verified}
                    onChange={(e) => setSelectedUser({ ...selectedUser, email_verified: e.target.checked })}
                  />
                }
                label="Email подтвержден"
              />
              <FormControl fullWidth sx={{ mt: 2 }}>
                <InputLabel>Роль</InputLabel>
                <Select
                  value={selectedUser.role}
                  onChange={(e) => setSelectedUser({ ...selectedUser, role: e.target.value as UserRole })}
                  label="Роль"
                >
                  <MenuItem value="admin">Администратор</MenuItem>
                  <MenuItem value="customer">Заказчик</MenuItem>
                  <MenuItem value="contractor">Исполнитель</MenuItem>
                  <MenuItem value="manager">Менеджер</MenuItem>
                  <MenuItem value="security">Служба безопасности</MenuItem>
                  <MenuItem value="hr">HR</MenuItem>
                </Select>
              </FormControl>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUserDialogOpen(false)}>Отмена</Button>
          <Button
            onClick={() => {
              if (selectedUser) {
                handleUserStatusUpdate(selectedUser.id, {
                  is_active: selectedUser.is_active,
                  email_verified: selectedUser.email_verified,
                  role: selectedUser.role
                });
              }
              setUserDialogOpen(false);
            }}
            variant="contained"
          >
            Сохранить
          </Button>
        </DialogActions>
      </Dialog>

      {/* Диалог редактирования заявки */}
      <Dialog open={requestDialogOpen} onClose={() => setRequestDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Редактирование заявки</DialogTitle>
        <DialogContent>
          {selectedRequest && (
            <Box sx={{ pt: 2 }}>
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Статус</InputLabel>
                <Select
                  value={selectedRequest.status}
                  onChange={(e) => setSelectedRequest({ ...selectedRequest, status: e.target.value as RequestStatus })}
                  label="Статус"
                >
                  <MenuItem value="new">Новая</MenuItem>
                  <MenuItem value="manager_review">На рассмотрении</MenuItem>
                  <MenuItem value="assigned">Назначена</MenuItem>
                  <MenuItem value="in_progress">В работе</MenuItem>
                  <MenuItem value="completed">Завершена</MenuItem>
                  <MenuItem value="cancelled">Отменена</MenuItem>
                </Select>
              </FormControl>
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Приоритет</InputLabel>
                <Select
                  value={selectedRequest.priority}
                  onChange={(e) => setSelectedRequest({ ...selectedRequest, priority: e.target.value })}
                  label="Приоритет"
                >
                  <MenuItem value="low">Низкий</MenuItem>
                  <MenuItem value="normal">Обычный</MenuItem>
                  <MenuItem value="high">Высокий</MenuItem>
                  <MenuItem value="urgent">Срочный</MenuItem>
                </Select>
              </FormControl>
              <FormControl fullWidth>
                <InputLabel>Срочность</InputLabel>
                <Select
                  value={selectedRequest.urgency}
                  onChange={(e) => setSelectedRequest({ ...selectedRequest, urgency: e.target.value })}
                  label="Срочность"
                >
                  <MenuItem value="low">Низкая</MenuItem>
                  <MenuItem value="medium">Средняя</MenuItem>
                  <MenuItem value="high">Высокая</MenuItem>
                  <MenuItem value="critical">Критическая</MenuItem>
                </Select>
              </FormControl>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRequestDialogOpen(false)}>Отмена</Button>
          <Button
            onClick={() => {
              if (selectedRequest) {
                handleRequestStatusUpdate(selectedRequest.id, {
                  status: selectedRequest.status,
                  priority: selectedRequest.priority,
                  urgency: selectedRequest.urgency
                });
              }
              setRequestDialogOpen(false);
            }}
            variant="contained"
          >
            Сохранить
          </Button>
        </DialogActions>
      </Dialog>

      {/* Диалог создания пользователя */}
      <Dialog
        open={createUserDialogOpen}
        onClose={() => setCreateUserDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={1}>
            <People color="primary" />
            <Typography variant="h6">Создание нового пользователя</Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Имя пользователя *"
                  value={newUser.username}
                  onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Email *"
                  type="email"
                  value={newUser.email}
                  onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Пароль *"
                  type="password"
                  value={newUser.password}
                  onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth required>
                  <InputLabel>Роль *</InputLabel>
                  <Select
                    value={newUser.role}
                    onChange={(e) => setNewUser({ ...newUser, role: e.target.value as UserRole })}
                    label="Роль *"
                  >
                    <MenuItem value="admin">Администратор</MenuItem>
                    <MenuItem value="manager">Менеджер</MenuItem>
                    <MenuItem value="customer">Заказчик</MenuItem>
                    <MenuItem value="contractor">Исполнитель</MenuItem>
                    <MenuItem value="service_engineer">Сервисный инженер</MenuItem>
                    <MenuItem value="security">Служба безопасности</MenuItem>
                    <MenuItem value="hr">HR</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Имя *"
                  value={newUser.first_name}
                  onChange={(e) => setNewUser({ ...newUser, first_name: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Фамилия *"
                  value={newUser.last_name}
                  onChange={(e) => setNewUser({ ...newUser, last_name: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Отчество"
                  value={newUser.middle_name}
                  onChange={(e) => setNewUser({ ...newUser, middle_name: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Телефон"
                  value={newUser.phone}
                  onChange={(e) => setNewUser({ ...newUser, phone: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', pt: 1 }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={newUser.is_active}
                        onChange={(e) => setNewUser({ ...newUser, is_active: e.target.checked })}
                      />
                    }
                    label="Активный"
                  />
                  <FormControlLabel
                    control={
                      <Switch
                        checked={newUser.email_verified}
                        onChange={(e) => setNewUser({ ...newUser, email_verified: e.target.checked })}
                      />
                    }
                    label="Email подтвержден"
                  />
                </Box>
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateUserDialogOpen(false)}>
            Отмена
          </Button>
          <Button
            onClick={handleCreateUser}
            variant="contained"
            disabled={!newUser.username || !newUser.email || !newUser.password || !newUser.first_name || !newUser.last_name}
          >
            Создать пользователя
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AdminPanelPage;
