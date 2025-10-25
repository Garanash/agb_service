import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Avatar,
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
  Business,
  Phone,
  Email,
  LocationOn,
} from '@mui/icons-material';
import { useForm } from 'react-hook-form';
import { useAuth } from 'hooks/useAuth';
import { apiService } from 'services/api';
import {
  CustomerProfile,
  CustomerProfileCreate,
  UserRole,
  User,
} from 'types/api';

const CustomersPage: React.FC = () => {
  const { user } = useAuth();
  const [customers, setCustomers] = useState<User[]>([]);
  const [customerProfiles, setCustomerProfiles] = useState<CustomerProfile[]>(
    [],
  );
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingCustomer, setEditingCustomer] =
    useState<CustomerProfile | null>(null);

  // Пагинация
  const [page, setPage] = useState(1);
  const itemsPerPage = 10;

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<CustomerProfileCreate>();

  useEffect(() => {
    fetchCustomers();
  }, []);

  const fetchCustomers = async () => {
    try {
      setLoading(true);
      // Получаем пользователей-заказчиков
      const users = await apiService.getAllCustomers(100, 0);
      setCustomers(users);

      // Получаем профили заказчиков
      try {
        const profiles = await apiService.getAllCustomerProfiles(100, 0);
        setCustomerProfiles(profiles);
      } catch (error) {
        console.warn('Failed to fetch customer profiles:', error);
        // Не критично, если профили не загрузились
      }
    } catch (error) {
      console.error('Failed to fetch customers:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCustomer = async (data: CustomerProfileCreate) => {
    try {
      await apiService.createCustomerProfile(data);
      setOpenDialog(false);
      reset();
      fetchCustomers();
    } catch (error) {
      console.error('Failed to create customer:', error);
    }
  };

  const handleUpdateCustomer = async (data: CustomerProfileCreate) => {
    if (!editingCustomer) return;

    try {
      await apiService.updateCustomerProfile(data);
      setOpenDialog(false);
      setEditingCustomer(null);
      reset();
      fetchCustomers();
    } catch (error) {
      console.error('Failed to update customer:', error);
    }
  };

  const openCreateDialog = () => {
    setEditingCustomer(null);
    reset();
    setOpenDialog(true);
  };

  const openEditDialog = (customer: CustomerProfile) => {
    setEditingCustomer(customer);
    reset({
      company_name: customer.company_name,
      contact_person: customer.contact_person,
      phone: customer.phone,
      email: customer.email,
      address: customer.address,
      inn: customer.inn,
      kpp: customer.kpp,
      ogrn: customer.ogrn,
    });
    setOpenDialog(true);
  };

  const canEdit = () => {
    return user?.role === UserRole.ADMIN || user?.role === UserRole.CUSTOMER;
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
        <Typography variant='h4'>Заказчики</Typography>
        {canEdit() && (
          <Button
            variant='contained'
            startIcon={<Add />}
            onClick={openCreateDialog}
          >
            Добавить заказчика
          </Button>
        )}
      </Box>

      {loading ? (
        <Typography>Загрузка...</Typography>
      ) : customers.length === 0 ? (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 4 }}>
            <Business sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant='h6' color='text.secondary' gutterBottom>
              Нет заказчиков
            </Typography>
            <Typography variant='body2' color='text.secondary'>
              Добавьте первого заказчика в систему
            </Typography>
            {canEdit() && (
              <Button
                variant='contained'
                startIcon={<Add />}
                onClick={openCreateDialog}
                sx={{ mt: 2 }}
              >
                Добавить заказчика
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
                <TableCell>Логин</TableCell>
                <TableCell>Имя</TableCell>
                <TableCell>Компания</TableCell>
                <TableCell>Контактное лицо</TableCell>
                <TableCell>Телефон</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Адрес</TableCell>
                <TableCell>ИНН</TableCell>
                <TableCell>Действия</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {customers
                .slice((page - 1) * itemsPerPage, page * itemsPerPage)
                .map(customer => (
                  <TableRow
                    key={customer.id}
                    sx={{
                      '&:hover': {
                        backgroundColor: '#f5f5f5',
                      },
                    }}
                  >
                    <TableCell>
                      <Typography variant='body2' fontWeight='bold'>
                        #{customer.id}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography
                        variant='body2'
                        fontWeight='medium'
                        color='primary'
                      >
                        @{customer.username}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Avatar sx={{ mr: 2, width: 32, height: 32 }}>
                          <Business />
                        </Avatar>
                        <Typography variant='body2' fontWeight='medium'>
                          {customer.first_name} {customer.last_name}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      {(() => {
                        const profile = customerProfiles.find(
                          cp => cp.user_id === customer.id,
                        );
                        return profile ? (
                          <Typography variant='body2' fontWeight='medium'>
                            {profile.company_name}
                          </Typography>
                        ) : (
                          <Typography variant='body2' color='text.secondary'>
                            Не указано
                          </Typography>
                        );
                      })()}
                    </TableCell>
                    <TableCell>
                      {(() => {
                        const profile = customerProfiles.find(
                          cp => cp.user_id === customer.id,
                        );
                        return profile ? (
                          <Typography variant='body2'>
                            {profile.contact_person}
                          </Typography>
                        ) : (
                          <Typography variant='body2' color='text.secondary'>
                            {customer.first_name} {customer.last_name}
                          </Typography>
                        );
                      })()}
                    </TableCell>
                    <TableCell>
                      {(() => {
                        const profile = customerProfiles.find(
                          cp => cp.user_id === customer.id,
                        );
                        return (
                          <Typography variant='body2'>
                            {profile?.phone || customer.phone || '-'}
                          </Typography>
                        );
                      })()}
                    </TableCell>
                    <TableCell>
                      {(() => {
                        const profile = customerProfiles.find(
                          cp => cp.user_id === customer.id,
                        );
                        return (
                          <Typography variant='body2'>
                            {profile?.email || customer.email}
                          </Typography>
                        );
                      })()}
                    </TableCell>
                    <TableCell>
                      {(() => {
                        const profile = customerProfiles.find(
                          cp => cp.user_id === customer.id,
                        );
                        return (
                          <Typography
                            variant='body2'
                            noWrap
                            sx={{ maxWidth: 200 }}
                          >
                            {profile?.address || '-'}
                          </Typography>
                        );
                      })()}
                    </TableCell>
                    <TableCell>
                      {(() => {
                        const profile = customerProfiles.find(
                          cp => cp.user_id === customer.id,
                        );
                        return (
                          <Typography variant='body2'>
                            {profile?.inn || '-'}
                          </Typography>
                        );
                      })()}
                    </TableCell>
                    <TableCell>
                      {canEdit() && (
                        <IconButton
                          onClick={() => openEditDialog(customer as any)}
                          color='primary'
                          size='small'
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

      {customers.length > itemsPerPage && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
          <Pagination
            count={Math.ceil(customers.length / itemsPerPage)}
            page={page}
            onChange={(e, newPage) => setPage(newPage)}
            color='primary'
          />
        </Box>
      )}

      {/* Диалог создания/редактирования заказчика */}
      <Dialog
        open={openDialog}
        onClose={() => setOpenDialog(false)}
        maxWidth='md'
        fullWidth
      >
        <DialogTitle>
          {editingCustomer ? 'Редактировать заказчика' : 'Добавить заказчика'}
        </DialogTitle>
        <form
          onSubmit={handleSubmit(
            editingCustomer ? handleUpdateCustomer : handleCreateCustomer,
          )}
        >
          <DialogContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <TextField
                fullWidth
                label='Название компании'
                {...register('company_name', {
                  required: 'Название компании обязательно',
                })}
                error={!!errors.company_name}
                helperText={errors.company_name?.message}
              />
              <TextField
                fullWidth
                label='Контактное лицо'
                {...register('contact_person', {
                  required: 'Контактное лицо обязательно',
                })}
                error={!!errors.contact_person}
                helperText={errors.contact_person?.message}
              />
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <TextField
                  fullWidth
                  label='Телефон'
                  {...register('phone', { required: 'Телефон обязателен' })}
                  error={!!errors.phone}
                  helperText={errors.phone?.message}
                />
                <TextField
                  fullWidth
                  label='Email'
                  type='email'
                  {...register('email', { required: 'Email обязателен' })}
                  error={!!errors.email}
                  helperText={errors.email?.message}
                />
              </Box>
              <TextField fullWidth label='Адрес' {...register('address')} />
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <TextField fullWidth label='ИНН' {...register('inn')} />
                <TextField fullWidth label='КПП' {...register('kpp')} />
                <TextField fullWidth label='ОГРН' {...register('ogrn')} />
              </Box>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenDialog(false)}>Отмена</Button>
            <Button type='submit' variant='contained'>
              {editingCustomer ? 'Сохранить' : 'Добавить'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Плавающая кнопка для мобильных устройств */}
      {canEdit() && (
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

export default CustomersPage;
