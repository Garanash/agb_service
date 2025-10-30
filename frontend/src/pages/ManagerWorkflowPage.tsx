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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
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
  Divider,
  Pagination,
} from '@mui/material';
import {
  Assignment,
  PersonAdd,
  Send,
  CheckCircle,
  Cancel,
  PlayArrow,
  Stop,
  Edit,
  Delete,
  Visibility,
} from '@mui/icons-material';
import { useAuth } from 'hooks/useAuth';
import { RepairRequest, RequestStatus, User } from 'types/api';
import { apiService } from 'services/api';

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
      id={`workflow-tabpanel-${index}`}
      aria-labelledby={`workflow-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const ManagerWorkflowPage: React.FC = () => {
  const { user } = useAuth();
  const [requests, setRequests] = useState<RepairRequest[]>([]);
  const [availableRequests, setAvailableRequests] = useState<RepairRequest[]>(
    [],
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState(0);

  // Пагинация
  const [myRequestsPage, setMyRequestsPage] = useState(1);
  const [availableRequestsPage, setAvailableRequestsPage] = useState(1);
  const itemsPerPage = 10;

  // Диалоги
  const [assignDialogOpen, setAssignDialogOpen] = useState(false);
  const [clarifyDialogOpen, setClarifyDialogOpen] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState<RepairRequest | null>(
    null,
  );
  const [clarificationText, setClarificationText] = useState('');
  const [contractorId, setContractorId] = useState<number | ''>('');
  
  // Поля для редактирования заявки
  const [editedTitle, setEditedTitle] = useState('');
  const [editedDescription, setEditedDescription] = useState('');
  const [editedEquipment, setEditedEquipment] = useState('');
  const [editedAddress, setEditedAddress] = useState('');

  useEffect(() => {
    loadRequests();
  }, []);

  const loadRequests = async () => {
    try {
      setLoading(true);
      const [myRequests, available] = await Promise.all([
        apiService.getWorkflowRequests(),
        apiService.getAvailableRequests(),
      ]);
      setRequests(myRequests);
      setAvailableRequests(available);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка загрузки заявок');
    } finally {
      setLoading(false);
    }
  };

  const handleAssignToManager = async (requestId: number) => {
    try {
      await apiService.assignToManager(requestId, user?.id || 0);
      await loadRequests();
      setAssignDialogOpen(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка назначения заявки');
    }
  };

  const handleAddClarification = async () => {
    if (!selectedRequest) return;

    try {
      // Обновляем данные заявки
      await apiService.updateRepairRequest(selectedRequest.id, {
        title: editedTitle,
        description: editedDescription,
        equipment_type: editedEquipment,
        address: editedAddress,
      });
      
      // Добавляем уточнение если есть комментарий
      if (clarificationText.trim()) {
        await apiService.addClarification(selectedRequest.id, {
          clarification_details: clarificationText,
        });
      }
      
      await loadRequests();
      setClarifyDialogOpen(false);
      setClarificationText('');
      setEditedTitle('');
      setEditedDescription('');
      setEditedEquipment('');
      setEditedAddress('');
      setSelectedRequest(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка редактирования заявки');
    }
  };

  const handleAdminEditOpen = (request: RepairRequest) => {
    setSelectedRequest(request);
    setEditedTitle(request.title);
    setEditedDescription(request.description || '');
    setEditedEquipment(request.equipment_type || '');
    setEditedAddress(request.address || '');
    setClarifyDialogOpen(true);
  };

  const handleAdminDelete = async (requestId: number) => {
    try {
      // Простое подтверждение удаления
      // eslint-disable-next-line no-alert
      const confirmed = window.confirm('Удалить заявку безвозвратно?');
      if (!confirmed) return;
      await apiService.deleteRepairRequest(requestId);
      await loadRequests();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка удаления заявки');
    }
  };

  const handleSendToContractors = async (requestId: number) => {
    try {
      await apiService.sendToContractors(requestId);
      await loadRequests();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка отправки исполнителям');
    }
  };

  const handleAssignContractor = async () => {
    if (!selectedRequest || !contractorId) return;

    try {
      await apiService.assignContractor(selectedRequest.id, {
        contractor_id: contractorId,
      });
      await loadRequests();
      setContractorId('');
      setSelectedRequest(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка назначения исполнителя');
    }
  };

  const getStatusColor = (status: string) => {
    const colors: { [key: string]: string } = {
      new: 'default',
      manager_review: 'primary',
      clarification: 'warning',
      sent_to_contractors: 'info',
      contractor_responses: 'secondary',
      assigned: 'success',
      in_progress: 'info',
      completed: 'success',
      cancelled: 'error',
    };
    return colors[status] || 'default';
  };

  const getStatusText = (status: string) => {
    const texts: { [key: string]: string } = {
      new: 'Новая',
      manager_review: 'На рассмотрении',
      clarification: 'Уточнение',
      sent_to_contractors: 'Отправлена исполнителям',
      contractor_responses: 'Отклики получены',
      assigned: 'Назначена',
      in_progress: 'В работе',
      completed: 'Завершена',
      cancelled: 'Отменена',
    };
    return texts[status] || status;
  };

  const canAssignContractor = (request: RepairRequest) => {
    return (
      request.status === RequestStatus.SENT_TO_CONTRACTORS ||
      request.status === RequestStatus.CONTRACTOR_RESPONSES
    );
  };

  const canSendToContractors = (request: RepairRequest) => {
    return (
      request.status === RequestStatus.MANAGER_REVIEW ||
      request.status === RequestStatus.CLARIFICATION
    );
  };

  const canAddClarification = (request: RepairRequest) => {
    return request.status === RequestStatus.MANAGER_REVIEW;
  };

  if (loading) {
    return (
      <Box
        display='flex'
        justifyContent='center'
        alignItems='center'
        minHeight='400px'
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant='h4' gutterBottom>
        Управление заявками
      </Typography>

      {error && (
        <Alert severity='error' sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs
          value={tabValue}
          onChange={(e, newValue) => setTabValue(newValue)}
        >
          <Tab label='Мои заявки' />
          <Tab label='Доступные заявки' />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        <TableContainer sx={{ mt: 2 }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Название</TableCell>
                <TableCell>Описание</TableCell>
                <TableCell>Оборудование</TableCell>
                <TableCell>Адрес</TableCell>
                <TableCell>Статус</TableCell>
                <TableCell>Дата создания</TableCell>
                <TableCell>Действия</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {requests
                .slice(
                  (myRequestsPage - 1) * itemsPerPage,
                  myRequestsPage * itemsPerPage,
                )
                .map(request => (
                  <TableRow
                    key={request.id}
                    sx={{
                      '&:hover': {
                        backgroundColor: '#f5f5f5',
                      },
                    }}
                  >
                    <TableCell>
                      <Typography variant='body2' fontWeight='bold'>
                        #{request.id}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant='body2' noWrap sx={{ maxWidth: 200 }}>
                        {request.title}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant='body2' noWrap sx={{ maxWidth: 300 }}>
                        {request.description}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant='body2'>
                        {request.equipment_type || '-'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant='body2'>
                        {request.address || '-'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={getStatusText(request.status)}
                        color={getStatusColor(request.status) as any}
                        size='small'
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant='body2'>
                        {new Date(request.created_at).toLocaleDateString(
                          'ru-RU',
                          {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                          },
                        )}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        {canAddClarification(request) && (
                          <Button
                            size='small'
                            startIcon={<Edit />}
                            onClick={() => {
                              setSelectedRequest(request);
                              setEditedTitle(request.title);
                              setEditedDescription(request.description || '');
                              setEditedEquipment(request.equipment_type || '');
                              setEditedAddress(request.address || '');
                              setClarifyDialogOpen(true);
                            }}
                          >
                            Уточнить
                          </Button>
                        )}

                        {user?.role === 'admin' && (
                          <>
                            <Button
                              size='small'
                              startIcon={<Edit />}
                              onClick={() => handleAdminEditOpen(request)}
                            >
                              Редактировать
                            </Button>
                            <Button
                              size='small'
                              color='error'
                              startIcon={<Delete />}
                              onClick={() => handleAdminDelete(request.id)}
                            >
                              Удалить
                            </Button>
                          </>
                        )}

                        {canSendToContractors(request) && (
                          <Button
                            size='small'
                            startIcon={<Send />}
                            onClick={() => handleSendToContractors(request.id)}
                          >
                            Отправить
                          </Button>
                        )}

                        {canAssignContractor(request) && (
                          <Button
                            size='small'
                            startIcon={<PersonAdd />}
                            onClick={() => setSelectedRequest(request)}
                          >
                            Назначить
                          </Button>
                        )}
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </TableContainer>

        {requests.length > itemsPerPage && (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
            <Pagination
              count={Math.ceil(requests.length / itemsPerPage)}
              page={myRequestsPage}
              onChange={(e, page) => setMyRequestsPage(page)}
              color='primary'
            />
          </Box>
        )}
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <TableContainer sx={{ mt: 2 }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Название</TableCell>
                <TableCell>Описание</TableCell>
                <TableCell>Оборудование</TableCell>
                <TableCell>Адрес</TableCell>
                <TableCell>Статус</TableCell>
                <TableCell>Дата создания</TableCell>
                <TableCell>Действия</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {availableRequests
                .slice(
                  (availableRequestsPage - 1) * itemsPerPage,
                  availableRequestsPage * itemsPerPage,
                )
                .map(request => (
                  <TableRow
                    key={request.id}
                    sx={{
                      '&:hover': {
                        backgroundColor: '#f5f5f5',
                      },
                    }}
                  >
                    <TableCell>
                      <Typography variant='body2' fontWeight='bold'>
                        #{request.id}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant='body2' noWrap sx={{ maxWidth: 200 }}>
                        {request.title}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant='body2' noWrap sx={{ maxWidth: 300 }}>
                        {request.description}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant='body2'>
                        {request.equipment_type || '-'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant='body2'>
                        {request.address || '-'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip label='Доступна' color='default' size='small' />
                    </TableCell>
                    <TableCell>
                      <Typography variant='body2'>
                        {new Date(request.created_at).toLocaleDateString(
                          'ru-RU',
                          {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                          },
                        )}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Button
                        size='small'
                        variant='contained'
                        startIcon={<Assignment />}
                        onClick={() => handleAssignToManager(request.id)}
                      >
                        Взять
                      </Button>
                      {user?.role === 'admin' && (
                        <Box component='span' sx={{ ml: 1, display: 'inline-flex', gap: 1 }}>
                          <Button
                            size='small'
                            startIcon={<Edit />}
                            onClick={() => handleAdminEditOpen(request)}
                          >
                            Редактировать
                          </Button>
                          <Button
                            size='small'
                            color='error'
                            startIcon={<Delete />}
                            onClick={() => handleAdminDelete(request.id)}
                          >
                            Удалить
                          </Button>
                        </Box>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </TableContainer>

        {availableRequests.length > itemsPerPage && (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
            <Pagination
              count={Math.ceil(availableRequests.length / itemsPerPage)}
              page={availableRequestsPage}
              onChange={(e, page) => setAvailableRequestsPage(page)}
              color='primary'
            />
          </Box>
        )}
      </TabPanel>

      {/* Диалог добавления уточнений */}
      <Dialog
        open={clarifyDialogOpen}
        onClose={() => setClarifyDialogOpen(false)}
        maxWidth='md'
        fullWidth
      >
        <DialogTitle>Уточнить заявку</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin='dense'
            label='Название заявки'
            fullWidth
            value={editedTitle}
            onChange={e => setEditedTitle(e.target.value)}
            required
            sx={{ mb: 2 }}
          />
          <TextField
            margin='dense'
            label='Описание'
            fullWidth
            multiline
            rows={3}
            value={editedDescription}
            onChange={e => setEditedDescription(e.target.value)}
            sx={{ mb: 2 }}
          />
          <TextField
            margin='dense'
            label='Техника'
            fullWidth
            value={editedEquipment}
            onChange={e => setEditedEquipment(e.target.value)}
            sx={{ mb: 2 }}
          />
          <TextField
            margin='dense'
            label='Адрес'
            fullWidth
            value={editedAddress}
            onChange={e => setEditedAddress(e.target.value)}
            sx={{ mb: 2 }}
          />
          <TextField
            margin='dense'
            label='Комментарий'
            fullWidth
            multiline
            rows={3}
            value={clarificationText}
            onChange={e => setClarificationText(e.target.value)}
            placeholder='Добавьте комментарий...'
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setClarifyDialogOpen(false)}>Отмена</Button>
          <Button onClick={handleAddClarification} variant='contained'>
            Сохранить
          </Button>
        </DialogActions>
      </Dialog>

      {/* Диалог назначения исполнителя */}
      <Dialog
        open={!!selectedRequest && canAssignContractor(selectedRequest!)}
        onClose={() => setSelectedRequest(null)}
        maxWidth='sm'
        fullWidth
      >
        <DialogTitle>Назначить исполнителя</DialogTitle>
        <DialogContent>
          <FormControl fullWidth margin='dense'>
            <InputLabel>Исполнитель</InputLabel>
            <Select
              value={contractorId}
              onChange={e => setContractorId(e.target.value as number)}
            >
              {/* Здесь должен быть список доступных исполнителей */}
              <MenuItem value={1}>Исполнитель 1</MenuItem>
              <MenuItem value={2}>Исполнитель 2</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedRequest(null)}>Отмена</Button>
          <Button onClick={handleAssignContractor} variant='contained'>
            Назначить
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ManagerWorkflowPage;
