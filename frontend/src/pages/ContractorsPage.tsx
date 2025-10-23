import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Avatar,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Fab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Pagination,
} from '@mui/material';
import {
  Add,
  Edit,
  Person,
  Phone,
  Email,
  Business,
  Assignment,
} from '@mui/icons-material';
import { useForm } from 'react-hook-form';
import { useAuth } from 'hooks/useAuth';
import { apiService } from 'services/api';
import { ContractorProfile, ContractorProfileCreate, UserRole, User } from 'types/api';

const ContractorsPage: React.FC = () => {
  const { user } = useAuth();
  const [contractors, setContractors] = useState<ContractorProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingContractor, setEditingContractor] = useState<ContractorProfile | null>(null);
  
  // Пагинация
  const [page, setPage] = useState(1);
  const itemsPerPage = 10;

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ContractorProfileCreate>();

  useEffect(() => {
    fetchContractors();
  }, []);

  const fetchContractors = async () => {
    try {
      setLoading(true);
      console.log('Fetching contractor profiles...');
      // Временно используем старый API, который работает
      const users = await apiService.getAllContractors(100, 0);
      console.log('Received users:', users);
      
      // Преобразуем User[] в ContractorProfile[] для отображения
      const profiles: ContractorProfile[] = users.map(user => ({
        id: 0, // Будет установлен на бэкенде
        user_id: user.id,
        last_name: user.last_name || '',
        first_name: user.first_name || '',
        patronymic: user.middle_name || '',
        phone: user.phone || '',
        email: user.email || '',
        telegram_username: '', // Будет загружено отдельно
        website: '',
        general_description: '',
        created_at: user.created_at,
        updated_at: user.updated_at,
      }));
      
      setContractors(profiles);
    } catch (error) {
      console.error('Failed to fetch contractors:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateContractor = async (data: ContractorProfileCreate) => {
    try {
      await apiService.createContractorProfile(data);
      setOpenDialog(false);
      reset();
      fetchContractors();
    } catch (error) {
      console.error('Failed to create contractor:', error);
    }
  };

  const handleUpdateContractor = async (data: ContractorProfileCreate) => {
    if (!editingContractor) return;
    
    try {
      if (user?.role === UserRole.ADMIN) {
        // Для администратора используем специальный endpoint
        await apiService.updateContractorProfileByAdmin(editingContractor.user_id, data);
      } else {
        // Для исполнителя используем обычный endpoint
        await apiService.updateContractorProfile(data);
      }
      setOpenDialog(false);
      setEditingContractor(null);
      reset();
      fetchContractors();
    } catch (error) {
      console.error('Failed to update contractor:', error);
    }
  };

  const openCreateDialog = () => {
    setEditingContractor(null);
    reset();
    setOpenDialog(true);
  };

  const openEditDialog = (contractor: ContractorProfile) => {
    setEditingContractor(contractor);
    reset({
      last_name: contractor.last_name,
      first_name: contractor.first_name,
      patronymic: contractor.patronymic,
      phone: contractor.phone,
      email: contractor.email,
      telegram_username: contractor.telegram_username,
      website: contractor.website,
      general_description: contractor.general_description,
    });
    setOpenDialog(true);
  };

  const canEdit = () => {
    return user?.role === UserRole.ADMIN || user?.role === UserRole.CONTRACTOR;
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Исполнители
        </Typography>
        {canEdit() && (
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={openCreateDialog}
          >
            Добавить исполнителя
          </Button>
        )}
      </Box>

      {loading ? (
        <Typography>Загрузка...</Typography>
      ) : contractors.length === 0 ? (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 4 }}>
            <Person sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              Нет исполнителей
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Добавьте первого исполнителя в систему
            </Typography>
            {canEdit() && (
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={openCreateDialog}
                sx={{ mt: 2 }}
              >
                Добавить исполнителя
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <TableContainer sx={{ mt: 2 }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Имя</TableCell>
                <TableCell>Телефон</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Telegram</TableCell>
                <TableCell>Описание</TableCell>
                <TableCell>Действия</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {contractors
                .slice((page - 1) * itemsPerPage, page * itemsPerPage)
                .map((contractor) => (
                <TableRow
                  key={contractor.id}
                  sx={{
                    '&:hover': {
                      backgroundColor: '#f5f5f5',
                    }
                  }}
                >
                  <TableCell>
                    <Typography variant="body2" fontWeight="bold">
                      #{contractor.id}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Avatar sx={{ mr: 2, width: 32, height: 32 }}>
                        <Person />
                      </Avatar>
                      <Typography variant="body2" fontWeight="medium">
                        {contractor.first_name} {contractor.last_name}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {contractor.phone || '-'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {contractor.email || '-'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {contractor.telegram_username || '-'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" noWrap sx={{ maxWidth: 300 }}>
                      {contractor.general_description || '-'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {canEdit() && (
                      <IconButton
                        onClick={() => openEditDialog(contractor)}
                        color="primary"
                        size="small"
                      >
                        <Edit />
                      </IconButton>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
      
      {contractors.length > itemsPerPage && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
          <Pagination
            count={Math.ceil(contractors.length / itemsPerPage)}
            page={page}
            onChange={(e, newPage) => setPage(newPage)}
            color="primary"
          />
        </Box>
      )}

      {/* Диалог создания/редактирования исполнителя */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingContractor ? 'Редактировать исполнителя' : 'Добавить исполнителя'}
        </DialogTitle>
        <form onSubmit={handleSubmit(editingContractor ? handleUpdateContractor : handleCreateContractor)}>
          <DialogContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <TextField
                  fullWidth
                  label="Фамилия"
                  {...register('last_name')}
                />
                <TextField
                  fullWidth
                  label="Имя"
                  {...register('first_name')}
                />
                <TextField
                  fullWidth
                  label="Отчество"
                  {...register('patronymic')}
                />
              </Box>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <TextField
                  fullWidth
                  label="Телефон"
                  {...register('phone')}
                />
                <TextField
                  fullWidth
                  label="Email"
                  type="email"
                  {...register('email')}
                />
              </Box>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <TextField
                  fullWidth
                  label="Telegram"
                  {...register('telegram_username')}
                />
                <TextField
                  fullWidth
                  label="Веб-сайт"
                  {...register('website')}
                />
              </Box>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Описание"
                {...register('general_description')}
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenDialog(false)}>Отмена</Button>
            <Button type="submit" variant="contained">
              {editingContractor ? 'Сохранить' : 'Добавить'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Плавающая кнопка для мобильных устройств */}
      {canEdit() && (
        <Fab
          color="primary"
          aria-label="add"
          sx={{ position: 'fixed', bottom: 16, right: 16 }}
          onClick={openCreateDialog}
        >
          <Add />
        </Fab>
      )}
    </Box>
  );
};

export default ContractorsPage;
