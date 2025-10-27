import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
  Button,
  Grid,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
} from '@mui/material';
import {
  Build,
  LocationOn,
  AccessTime,
  AttachMoney,
  Close,
} from '@mui/icons-material';
import { apiService } from '../services/api';
import { RepairRequest, RequestStatus } from '../types/api';

const ContractorArchivePage: React.FC = () => {
  const [requests, setRequests] = useState<RepairRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedRequest, setSelectedRequest] =
    useState<RepairRequest | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);

  useEffect(() => {
    loadArchive();
  }, []);

  const loadArchive = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Получаем все заявки и фильтруем только выполненные
      const response = await apiService.getRepairRequests();
      const allRequests = Array.isArray(response) ? response : response.items || [];
      const completedRequests = allRequests.filter(
        (req) => req.status === RequestStatus.COMPLETED
      );
      
      setRequests(completedRequests);
    } catch (err: any) {
      console.error('Error loading archive:', err);
      setError('Ошибка загрузки архива заявок');
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = (request: RepairRequest) => {
    setSelectedRequest(request);
    setDetailsOpen(true);
  };

  const handleCloseDetails = () => {
    setDetailsOpen(false);
    setSelectedRequest(null);
  };

  const getStatusColor = (status: RequestStatus) => {
    switch (status) {
      case RequestStatus.COMPLETED:
        return 'success';
      case RequestStatus.CANCELLED:
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusLabel = (status: RequestStatus) => {
    switch (status) {
      case RequestStatus.COMPLETED:
        return 'Выполнено';
      case RequestStatus.CANCELLED:
        return 'Отменено';
      default:
        return status;
    }
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto' }}>
      <Typography variant='h4' gutterBottom sx={{ mb: 4 }}>
        Архив заявок
      </Typography>

      {loading ? (
        <Box display='flex' justifyContent='center' alignItems='center' sx={{ minHeight: 400 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity='error'>{error}</Alert>
      ) : requests.length === 0 ? (
        <Alert severity='info'>Архив заявок пуст</Alert>
      ) : (
        <Grid container spacing={3}>
          {requests.map((request) => (
            <Grid item xs={12} md={6} key={request.id}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant='h6' component='h2'>
                      {request.title}
                    </Typography>
                    <Chip
                      label={getStatusLabel(request.status)}
                      color={getStatusColor(request.status) as any}
                      size='small'
                    />
                  </Box>

                  <Typography variant='body2' color='text.secondary' sx={{ mb: 2 }}>
                    {request.description}
                  </Typography>

                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    {request.address && (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <LocationOn fontSize='small' color='action' />
                        <Typography variant='body2' color='text.secondary'>
                          {request.address}
                        </Typography>
                      </Box>
                    )}

                    {request.priority && (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <AccessTime fontSize='small' color='action' />
                        <Typography variant='body2' color='text.secondary'>
                          Приоритет: {request.priority}
                        </Typography>
                      </Box>
                    )}

                    {request.final_price && (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <AttachMoney fontSize='small' color='action' />
                        <Typography variant='body2' color='text.secondary'>
                          Стоимость: {request.final_price} ₽
                        </Typography>
                      </Box>
                    )}
                  </Box>

                  <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
                    <Button
                      variant='outlined'
                      size='small'
                      onClick={() => handleViewDetails(request)}
                    >
                      Подробнее
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Диалог с подробной информацией */}
      <Dialog open={detailsOpen} onClose={handleCloseDetails} maxWidth='md' fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant='h6'>Детали заявки</Typography>
            <IconButton onClick={handleCloseDetails}>
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedRequest && (
            <Box>
              <Typography variant='h6' gutterBottom>
                {selectedRequest.title}
              </Typography>
              
              <Typography variant='body2' color='text.secondary' sx={{ mb: 2 }}>
                {selectedRequest.description}
              </Typography>

              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Typography variant='body2'><strong>Статус:</strong> {getStatusLabel(selectedRequest.status)}</Typography>
                {selectedRequest.address && <Typography variant='body2'><strong>Адрес:</strong> {selectedRequest.address}</Typography>}
                {selectedRequest.priority && <Typography variant='body2'><strong>Приоритет:</strong> {selectedRequest.priority}</Typography>}
                {selectedRequest.final_price && <Typography variant='body2'><strong>Стоимость:</strong> {selectedRequest.final_price} ₽</Typography>}
                {selectedRequest.equipment_type && <Typography variant='body2'><strong>Тип оборудования:</strong> {selectedRequest.equipment_type}</Typography>}
                {selectedRequest.equipment_brand && <Typography variant='body2'><strong>Бренд:</strong> {selectedRequest.equipment_brand}</Typography>}
                {selectedRequest.created_at && <Typography variant='body2'><strong>Дата создания:</strong> {new Date(selectedRequest.created_at).toLocaleString('ru-RU')}</Typography>}
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDetails}>Закрыть</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ContractorArchivePage;

