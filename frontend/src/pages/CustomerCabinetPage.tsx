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
  TextareaAutosize,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Visibility,
  Cancel,
  CheckCircle,
  Pending,
  Build,
  TrendingUp,
  Person,
  Business,
  ExpandMore,
  Save,
  Close,
} from '@mui/icons-material';
import { useAuth } from 'hooks/useAuth';
import { apiService } from 'services/api';
import { RequestStatus } from 'types/api';

interface CustomerProfile {
  user_info: {
    id: number;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
    phone: string;
    created_at: string;
  };
  company_info: {
    company_name: string;
    contact_person: string;
    phone: string;
    email: string;
    address: string;
    inn: string;
    ogrn: string;
  };
  equipment_info: {
    equipment_brands: string[];
    equipment_types: string[];
    mining_operations: string[];
    service_history: string;
  };
}

interface CustomerRequest {
  id: number;
  title: string;
  description: string;
  urgency?: string;
  preferred_date?: string;
  address?: string;
  city?: string;
  region?: string;
  equipment_type?: string;
  equipment_brand?: string;
  equipment_model?: string;
  problem_description?: string;
  priority?: string;
  status: RequestStatus;
  created_at: string;
  updated_at?: string;
  processed_at?: string;
}

interface CustomerStats {
  total_requests: number;
  status_counts: { [key: string]: number };
  recent_requests: number;
  avg_processing_time_hours: number;
  completion_rate: number;
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
      id={`customer-tabpanel-${index}`}
      aria-labelledby={`customer-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const CustomerCabinetPage: React.FC = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState<CustomerProfile | null>(null);
  const [requests, setRequests] = useState<CustomerRequest[]>([]);
  const [stats, setStats] = useState<CustomerStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState(0);
  
  // Диалоги
  const [profileDialogOpen, setProfileDialogOpen] = useState(false);
  const [requestDialogOpen, setRequestDialogOpen] = useState(false);
  const [viewRequestDialogOpen, setViewRequestDialogOpen] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState<CustomerRequest | null>(null);
  const [editingProfile, setEditingProfile] = useState<Partial<CustomerProfile>>({});
  const [newRequest, setNewRequest] = useState({
    title: '',
    description: '',
    urgency: '',
    preferred_date: '',
    address: '',
    city: '',
    region: '',
    equipment_type: '',
    equipment_brand: '',
    equipment_model: '',
    problem_description: '',
    priority: 'normal'
  });

  useEffect(() => {
    loadCustomerData();
  }, []);

  const loadCustomerData = async () => {
    try {
      setLoading(true);
      
      const [profileData, requestsData, statsData] = await Promise.all([
        apiService.getCustomerProfile(),
        apiService.getCustomerRequests(),
        apiService.getCustomerStatistics()
      ]);
      
      setProfile(profileData);
      setRequests(requestsData);
      setStats(statsData);
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка загрузки данных кабинета');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProfile = async () => {
    try {
      await apiService.updateCustomerProfile(editingProfile);
      setProfileDialogOpen(false);
      setEditingProfile({});
      await loadCustomerData();
      setSuccess('Профиль успешно обновлен');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка обновления профиля');
    }
  };

  const handleCreateRequest = async () => {
    try {
      await apiService.createCustomerRequest(newRequest);
      setRequestDialogOpen(false);
      setNewRequest({
        title: '',
        description: '',
        urgency: '',
        preferred_date: '',
        address: '',
        city: '',
        region: '',
        equipment_type: '',
        equipment_brand: '',
        equipment_model: '',
        problem_description: '',
        priority: 'normal'
      });
      await loadCustomerData();
      setSuccess('Заявка успешно создана');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка создания заявки');
    }
  };

  const handleCancelRequest = async (requestId: number) => {
    try {
      await apiService.cancelCustomerRequest(requestId);
      await loadCustomerData();
      setSuccess('Заявка успешно отменена');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка отмены заявки');
    }
  };

  const getStatusColor = (status: RequestStatus) => {
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

  const getStatusText = (status: RequestStatus) => {
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

  const getUrgencyText = (urgency?: string) => {
    const texts: { [key: string]: string } = {
      'low': 'Низкая',
      'medium': 'Средняя',
      'high': 'Высокая',
      'critical': 'Критическая'
    };
    return texts[urgency || ''] || 'Не указана';
  };

  const canEditRequest = (status: RequestStatus) => {
    return status === RequestStatus.NEW;
  };

  const canCancelRequest = (status: RequestStatus) => {
    return status === RequestStatus.NEW || status === RequestStatus.MANAGER_REVIEW;
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
        Личный кабинет заказчика
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

      {/* Статистика */}
      {stats && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <Build color="primary" sx={{ mr: 2 }} />
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
                  <CheckCircle color="success" sx={{ mr: 2 }} />
                  <Box>
                    <Typography variant="h4">{stats.status_counts.completed || 0}</Typography>
                    <Typography color="text.secondary">Завершено</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <Pending color="warning" sx={{ mr: 2 }} />
                  <Box>
                    <Typography variant="h4">{stats.status_counts.new || 0}</Typography>
                    <Typography color="text.secondary">Новых</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <TrendingUp color="info" sx={{ mr: 2 }} />
                  <Box>
                    <Typography variant="h4">{stats.completion_rate}%</Typography>
                    <Typography color="text.secondary">Процент завершения</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Табы */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
          <Tab label={`Мои заявки (${requests.length})`} />
          <Tab label="Профиль" />
        </Tabs>
      </Box>

      {/* Заявки */}
      <TabPanel value={tabValue} index={0}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Мои заявки</Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setRequestDialogOpen(true)}
          >
            Создать заявку
          </Button>
        </Box>
        
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Заявка</TableCell>
                <TableCell>Оборудование</TableCell>
                <TableCell>Статус</TableCell>
                <TableCell>Срочность</TableCell>
                <TableCell>Дата создания</TableCell>
                <TableCell>Действия</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {requests.map((request) => (
                <TableRow key={request.id}>
                  <TableCell>
                    <Typography variant="subtitle2">
                      #{request.id} {request.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {request.description.substring(0, 100)}...
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {request.equipment_type || 'Не указано'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {request.equipment_brand || 'Бренд не указан'}
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
                    <Typography variant="body2">
                      {getUrgencyText(request.urgency)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {new Date(request.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <Tooltip title="Просмотреть">
                      <IconButton
                        size="small"
                        onClick={() => {
                          setSelectedRequest(request);
                          setViewRequestDialogOpen(true);
                        }}
                      >
                        <Visibility />
                      </IconButton>
                    </Tooltip>
                    {canEditRequest(request.status) && (
                      <Tooltip title="Редактировать">
                        <IconButton size="small">
                          <Edit />
                        </IconButton>
                      </Tooltip>
                    )}
                    {canCancelRequest(request.status) && (
                      <Tooltip title="Отменить">
                        <IconButton
                          size="small"
                          onClick={() => handleCancelRequest(request.id)}
                        >
                          <Cancel />
                        </IconButton>
                      </Tooltip>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>

      {/* Профиль */}
      <TabPanel value={tabValue} index={1}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Профиль компании</Typography>
          <Button
            variant="outlined"
            startIcon={<Edit />}
            onClick={() => {
              setEditingProfile(profile || {});
              setProfileDialogOpen(true);
            }}
          >
            Редактировать
          </Button>
        </Box>
        
        {profile && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Информация о пользователе
                  </Typography>
                  <Typography variant="body2">
                    <strong>Имя:</strong> {profile.user_info.first_name} {profile.user_info.last_name}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Email:</strong> {profile.user_info.email}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Телефон:</strong> {profile.user_info.phone}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Дата регистрации:</strong> {new Date(profile.user_info.created_at).toLocaleDateString()}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Информация о компании
                  </Typography>
                  <Typography variant="body2">
                    <strong>Название:</strong> {profile.company_info.company_name}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Контактное лицо:</strong> {profile.company_info.contact_person}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Адрес:</strong> {profile.company_info.address || 'Не указан'}
                  </Typography>
                  <Typography variant="body2">
                    <strong>ИНН:</strong> {profile.company_info.inn || 'Не указан'}
                  </Typography>
                  <Typography variant="body2">
                    <strong>ОГРН:</strong> {profile.company_info.ogrn || 'Не указан'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Информация об оборудовании
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={4}>
                      <Typography variant="subtitle2">Бренды техники:</Typography>
                      <Box sx={{ mt: 1 }}>
                        {profile.equipment_info.equipment_brands.map((brand) => (
                          <Chip key={brand} label={brand} size="small" sx={{ mr: 1, mb: 1 }} />
                        ))}
                      </Box>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Typography variant="subtitle2">Типы оборудования:</Typography>
                      <Box sx={{ mt: 1 }}>
                        {profile.equipment_info.equipment_types.map((type) => (
                          <Chip key={type} label={type} size="small" sx={{ mr: 1, mb: 1 }} />
                        ))}
                      </Box>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Typography variant="subtitle2">Виды горных работ:</Typography>
                      <Box sx={{ mt: 1 }}>
                        {profile.equipment_info.mining_operations.map((operation) => (
                          <Chip key={operation} label={operation} size="small" sx={{ mr: 1, mb: 1 }} />
                        ))}
                      </Box>
                    </Grid>
                  </Grid>
                  {profile.equipment_info.service_history && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="subtitle2">История обслуживания:</Typography>
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        {profile.equipment_info.service_history}
                      </Typography>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}
      </TabPanel>

      {/* Диалог редактирования профиля */}
      <Dialog open={profileDialogOpen} onClose={() => setProfileDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Редактирование профиля</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Имя"
                value={editingProfile.user_info?.first_name || ''}
                onChange={(e) => setEditingProfile({
                  ...editingProfile,
                  user_info: { ...editingProfile.user_info, first_name: e.target.value }
                })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Фамилия"
                value={editingProfile.user_info?.last_name || ''}
                onChange={(e) => setEditingProfile({
                  ...editingProfile,
                  user_info: { ...editingProfile.user_info, last_name: e.target.value }
                })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Телефон"
                value={editingProfile.user_info?.phone || ''}
                onChange={(e) => setEditingProfile({
                  ...editingProfile,
                  user_info: { ...editingProfile.user_info, phone: e.target.value }
                })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Название компании"
                value={editingProfile.company_info?.company_name || ''}
                onChange={(e) => setEditingProfile({
                  ...editingProfile,
                  company_info: { ...editingProfile.company_info, company_name: e.target.value }
                })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Контактное лицо"
                value={editingProfile.company_info?.contact_person || ''}
                onChange={(e) => setEditingProfile({
                  ...editingProfile,
                  company_info: { ...editingProfile.company_info, contact_person: e.target.value }
                })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Адрес"
                value={editingProfile.company_info?.address || ''}
                onChange={(e) => setEditingProfile({
                  ...editingProfile,
                  company_info: { ...editingProfile.company_info, address: e.target.value }
                })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="ИНН"
                value={editingProfile.company_info?.inn || ''}
                onChange={(e) => setEditingProfile({
                  ...editingProfile,
                  company_info: { ...editingProfile.company_info, inn: e.target.value }
                })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="ОГРН"
                value={editingProfile.company_info?.ogrn || ''}
                onChange={(e) => setEditingProfile({
                  ...editingProfile,
                  company_info: { ...editingProfile.company_info, ogrn: e.target.value }
                })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="История обслуживания"
                value={editingProfile.equipment_info?.service_history || ''}
                onChange={(e) => setEditingProfile({
                  ...editingProfile,
                  equipment_info: { ...editingProfile.equipment_info, service_history: e.target.value }
                })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setProfileDialogOpen(false)}>Отмена</Button>
          <Button onClick={handleUpdateProfile} variant="contained">
            Сохранить
          </Button>
        </DialogActions>
      </Dialog>

      {/* Диалог создания заявки */}
      <Dialog open={requestDialogOpen} onClose={() => setRequestDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Создание новой заявки</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Название заявки"
                value={newRequest.title}
                onChange={(e) => setNewRequest({ ...newRequest, title: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Описание проблемы"
                value={newRequest.description}
                onChange={(e) => setNewRequest({ ...newRequest, description: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Срочность</InputLabel>
                <Select
                  value={newRequest.urgency}
                  onChange={(e) => setNewRequest({ ...newRequest, urgency: e.target.value })}
                  label="Срочность"
                >
                  <MenuItem value="low">Низкая</MenuItem>
                  <MenuItem value="medium">Средняя</MenuItem>
                  <MenuItem value="high">Высокая</MenuItem>
                  <MenuItem value="critical">Критическая</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Предпочтительная дата"
                type="datetime-local"
                value={newRequest.preferred_date}
                onChange={(e) => setNewRequest({ ...newRequest, preferred_date: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Тип оборудования"
                value={newRequest.equipment_type}
                onChange={(e) => setNewRequest({ ...newRequest, equipment_type: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Бренд оборудования"
                value={newRequest.equipment_brand}
                onChange={(e) => setNewRequest({ ...newRequest, equipment_brand: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Модель оборудования"
                value={newRequest.equipment_model}
                onChange={(e) => setNewRequest({ ...newRequest, equipment_model: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Город"
                value={newRequest.city}
                onChange={(e) => setNewRequest({ ...newRequest, city: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Адрес"
                value={newRequest.address}
                onChange={(e) => setNewRequest({ ...newRequest, address: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={2}
                label="Детальное описание проблемы"
                value={newRequest.problem_description}
                onChange={(e) => setNewRequest({ ...newRequest, problem_description: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRequestDialogOpen(false)}>Отмена</Button>
          <Button
            onClick={handleCreateRequest}
            variant="contained"
            disabled={!newRequest.title || !newRequest.description}
          >
            Создать заявку
          </Button>
        </DialogActions>
      </Dialog>

      {/* Диалог просмотра заявки */}
      <Dialog open={viewRequestDialogOpen} onClose={() => setViewRequestDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Заявка #{selectedRequest?.id}</DialogTitle>
        <DialogContent>
          {selectedRequest && (
            <Box>
              <Typography variant="h6" gutterBottom>
                {selectedRequest.title}
              </Typography>
              <Typography variant="body1" paragraph>
                {selectedRequest.description}
              </Typography>
              
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2">Статус:</Typography>
                  <Chip
                    label={getStatusText(selectedRequest.status)}
                    color={getStatusColor(selectedRequest.status) as any}
                    size="small"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2">Срочность:</Typography>
                  <Typography variant="body2">{getUrgencyText(selectedRequest.urgency)}</Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2">Оборудование:</Typography>
                  <Typography variant="body2">
                    {selectedRequest.equipment_type || 'Не указано'} - {selectedRequest.equipment_brand || 'Бренд не указан'}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2">Местоположение:</Typography>
                  <Typography variant="body2">
                    {selectedRequest.address || 'Не указано'}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2">Дата создания:</Typography>
                  <Typography variant="body2">
                    {new Date(selectedRequest.created_at).toLocaleString()}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2">Предпочтительная дата:</Typography>
                  <Typography variant="body2">
                    {selectedRequest.preferred_date ? new Date(selectedRequest.preferred_date).toLocaleString() : 'Не указана'}
                  </Typography>
                </Grid>
              </Grid>
              
              {selectedRequest.problem_description && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2">Детальное описание проблемы:</Typography>
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    {selectedRequest.problem_description}
                  </Typography>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewRequestDialogOpen(false)}>Закрыть</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CustomerCabinetPage;
