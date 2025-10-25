import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Card,
  CardContent,
  Fab,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Visibility,
  Build,
  Assignment,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useAuth } from 'hooks/useAuth';
import { apiService } from 'services/api';
import {
  RepairRequest,
  RepairRequestCreate,
  RepairRequestUpdate,
  RequestStatus,
  UserRole,
} from 'types/api';

const RepairRequestsPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [requests, setRequests] = useState<RepairRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingRequest, setEditingRequest] = useState<RepairRequest | null>(
    null,
  );
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const { register, handleSubmit, reset, formState: { errors } } = useForm<RepairRequestCreate>();

  useEffect(() => {
    fetchRequests();
  }, [page]);

  const fetchRequests = async () => {
    try {
      setLoading(true);
      const response = await apiService.getRepairRequests(page, 10);
      setRequests(response.items || []);
      setTotalPages(response.pages || 1);
    } catch (error) {
      console.error('Failed to fetch requests:', error);
      setRequests([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRequest = async (data: RepairRequestCreate) => {
    try {
      await apiService.createRepairRequest(data);
      setOpenDialog(false);
      reset();
      fetchRequests();
    } catch (error) {
      console.error('Failed to create request:', error);
    }
  };

  const handleUpdateRequest = async (data: RepairRequestUpdate) => {
    if (!editingRequest) return;

    try {
      await apiService.updateRepairRequest(editingRequest.id, data);
      setOpenDialog(false);
      setEditingRequest(null);
      reset();
      fetchRequests();
    } catch (error) {
      console.error('Failed to update request:', error);
    }
  };

  const handleDeleteRequest = async (id: number) => {
    if (window.confirm('Вы уверены, что хотите удалить эту заявку?')) {
      try {
        await apiService.deleteRepairRequest(id);
        fetchRequests();
      } catch (error) {
        console.error('Failed to delete request:', error);
      }
    }
  };

  const openCreateDialog = () => {
    setEditingRequest(null);
    reset();
    setOpenDialog(true);
  };

  const openEditDialog = (request: RepairRequest) => {
    setEditingRequest(request);
    reset({
      title: request.title,
      description: request.description,
      urgency: request.urgency,
      address: request.address,
      city: request.city,
      region: request.region,
    });
    setOpenDialog(true);
  };

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

  const canEdit = (request: RepairRequest) => {
    if (user?.role === UserRole.ADMIN) return true;
    if (user?.role === UserRole.CUSTOMER && request.customer_id === user.id)
      return true;
    if (user?.role === UserRole.SERVICE_ENGINEER) return true;
    return false;
  };

  const canDelete = (request: RepairRequest) => {
    if (user?.role === UserRole.ADMIN) return true;
    if (user?.role === UserRole.CUSTOMER && request.customer_id === user.id)
      return true;
    return false;
  };

  return (
    <Box>
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 3,
        }}
      >
        <Typography variant='h4'>Заявки на ремонт</Typography>
        {(user?.role === UserRole.CUSTOMER ||
          user?.role === UserRole.ADMIN) && (
          <Button
            variant='contained'
            startIcon={<Add />}
            onClick={openCreateDialog}
          >
            Создать заявку
          </Button>
        )}
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Название</TableCell>
              <TableCell>Описание</TableCell>
              <TableCell>Статус</TableCell>
              <TableCell>Дата создания</TableCell>
              <TableCell>Действия</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {requests?.map(request => (
              <TableRow key={request.id}>
                <TableCell>{request.title}</TableCell>
                <TableCell>
                  <Typography variant='body2' color='text.secondary'>
                    {request.description.length > 100
                      ? `${request.description.substring(0, 100)}...`
                      : request.description}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    label={getStatusText(request.status)}
                    color={getStatusColor(request.status)}
                    size='small'
                  />
                </TableCell>
                <TableCell>
                  {new Date(request.created_at).toLocaleDateString('ru-RU')}
                </TableCell>
                <TableCell>
                  <IconButton
                    onClick={() => navigate(`/repair-requests/${request.id}`)}
                    color='primary'
                  >
                    <Visibility />
                  </IconButton>
                  {canEdit(request) && (
                    <IconButton
                      onClick={() => openEditDialog(request)}
                      color='primary'
                    >
                      <Edit />
                    </IconButton>
                  )}
                  {canDelete(request) && (
                    <IconButton
                      onClick={() => handleDeleteRequest(request.id)}
                      color='error'
                    >
                      <Delete />
                    </IconButton>
                  )}
                </TableCell>
              </TableRow>
            ))}
            {(!requests || requests.length === 0) && (
              <TableRow>
                <TableCell colSpan={5} align='center'>
                  <Typography variant='body2' color='text.secondary'>
                    Нет заявок
                  </Typography>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Диалог создания/редактирования заявки */}
      <Dialog
        open={openDialog}
        onClose={() => setOpenDialog(false)}
        maxWidth='md'
        fullWidth
      >
        <DialogTitle>
          {editingRequest ? 'Редактировать заявку' : 'Создать заявку'}
        </DialogTitle>
        <form
          onSubmit={handleSubmit(
            editingRequest ? handleUpdateRequest : handleCreateRequest,
          )}
        >
          <DialogContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <TextField
                fullWidth
                label='Название'
                {...register('title', { required: 'Название обязательно' })}
                error={!!errors.title}
                helperText={errors.title?.message as any}
              />
              <TextField
                fullWidth
                multiline
                rows={4}
                label='Описание'
                {...register('description', {
                  required: 'Описание обязательно',
                })}
                error={!!errors.description}
                helperText={errors.description?.message as any}
              />
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <TextField
                  fullWidth
                  label='Срочность'
                  {...register('urgency')}
                />
                <TextField fullWidth label='Город' {...register('city')} />
              </Box>
              <TextField fullWidth label='Адрес' {...register('address')} />
              <TextField fullWidth label='Регион' {...register('region')} />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenDialog(false)}>Отмена</Button>
            <Button type='submit' variant='contained'>
              {editingRequest ? 'Сохранить' : 'Создать'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Плавающая кнопка для мобильных устройств */}
      {(user?.role === UserRole.CUSTOMER || user?.role === UserRole.ADMIN) && (
        <Fab
          color='primary'
          aria-label='add'
          sx={{ position: 'fixed', bottom: 16, right: 16 }}
          onClick={openCreateDialog}
        >
          <Add />
        </Fab>
      )}
    </Box>
  );
};

export default RepairRequestsPage;
