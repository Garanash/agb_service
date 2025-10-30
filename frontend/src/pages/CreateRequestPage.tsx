import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Alert,
  CircularProgress,
} from '@mui/material';
import { Save, Send, LocationOn, Edit } from '@mui/icons-material';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { useAuth } from 'hooks/useAuth';
import { apiService } from 'services/api';
import LocationPicker from 'components/LocationPicker';

interface RequestForm {
  title: string;
  description: string;
  urgency: string;
  preferred_date: string;
  address: string;
  city: string;
  region: string;
  equipment_type: string;
  equipment_brand: string;
  equipment_model: string;
  problem_description: string;
  latitude?: number;
  longitude?: number;
}

const urgencyOptions = [
  { value: 'low', label: 'Низкая' },
  { value: 'medium', label: 'Средняя' },
  { value: 'high', label: 'Высокая' },
  { value: 'critical', label: 'Критическая' },
];

const equipmentTypes = [
  'Буровые установки',
  'Экскаваторы',
  'Погрузчики',
  'Самосвалы',
  'Бульдозеры',
  'Краны',
  'Компрессоры',
  'Генераторы',
  'Другое оборудование',
];

const equipmentBrands = [
  'Алмазгеобур',
  'Эпирог',
  'Бортлангир',
  'Катерпиллар',
  'Компани',
  'Либхерр',
  'Вольво',
  'Другие',
];

const CreateRequestPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [profileLoading, setProfileLoading] = useState(true);
  const [profileComplete, setProfileComplete] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [mapOpen, setMapOpen] = useState(false);
  const [selectedLocation, setSelectedLocation] = useState<{
    lat: number;
    lng: number;
    address: string;
  } | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    watch,
    setValue,
  } = useForm<RequestForm>();

  useEffect(() => {
    if (user?.role === 'customer') {
      checkProfileComplete();
    } else {
      setProfileLoading(false);
      setProfileComplete(true);
    }
  }, [user]);

  const checkProfileComplete = async () => {
    try {
      setProfileLoading(true);
      const profile = await apiService.getCustomerProfile();
      const isComplete =
        profile.company_name &&
        profile.company_name.trim().length >= 1 &&
        profile.phone &&
        profile.phone.length >= 10;
      setProfileComplete(isComplete);
    } catch (err: any) {
      setError('Ошибка проверки профиля компании');
      setProfileComplete(false);
    } finally {
      setProfileLoading(false);
    }
  };

  const onSubmit = async (data: RequestForm) => {
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      // Добавляем координаты к данным заявки
      const requestData = {
        ...data,
        latitude: selectedLocation?.lat,
        longitude: selectedLocation?.lng,
        address: selectedLocation?.address || data.address,
      };

      await apiService.createRepairRequest(requestData);
      setSuccess(true);
      reset();
      setSelectedLocation(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка создания заявки');
    } finally {
      setLoading(false);
    }
  };

  const handleLocationSelect = (location: {
    lat: number;
    lng: number;
    address: string;
  }) => {
    setSelectedLocation(location);
    // Пробрасываем адрес в форму для отображения и отправки
    setValue('address', location.address, { shouldValidate: true, shouldDirty: true });
  };

  if (profileLoading) {
    return (
      <Box display='flex' justifyContent='center' alignItems='center' minHeight='400px'>
        <CircularProgress />
      </Box>
    );
  }

  if (!profileComplete && user?.role === 'customer') {
    return (
      <Box sx={{ p: 3 }}>
        <Card>
          <CardContent>
            <Alert severity='warning' sx={{ mb: 2 }}>
              Для создания заявок необходимо заполнить профиль компании: название компании и телефон.
            </Alert>
            <Button
              variant='contained'
              startIcon={<Edit />}
              onClick={() => navigate('/customer/company-profile')}
            >
              Перейти к профилю компании
            </Button>
          </CardContent>
        </Card>
      </Box>
    );
  }

  if (success) {
    return (
      <Box sx={{ p: 3 }}>
        <Card>
          <CardContent>
            <Alert severity='success' sx={{ mb: 2 }}>
              Заявка успешно создана! Она будет рассмотрена менеджером в
              ближайшее время.
            </Alert>
            <Button
              variant='contained'
              onClick={() => setSuccess(false)}
              startIcon={<Send />}
            >
              Создать еще одну заявку
            </Button>
          </CardContent>
        </Card>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant='h4' gutterBottom>
        Создать заявку на сервис
      </Typography>

      {error && (
        <Alert severity='error' sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Card>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)}>
            <Grid container spacing={3}>
              {/* Основная информация */}
              <Grid item xs={12}>
                <Typography variant='h6' gutterBottom>
                  Основная информация
                </Typography>
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label='Название заявки'
                  {...register('title', { required: 'Название обязательно' })}
                  error={!!errors.title}
                  helperText={errors.title?.message as any}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <FormControl fullWidth error={!!errors.urgency}>
                  <InputLabel>Срочность</InputLabel>
                  <Select
                    {...register('urgency', {
                      required: 'Срочность обязательна',
                    })}
                    label='Срочность'
                  >
                    {urgencyOptions.map(option => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label='Описание проблемы'
                  {...register('description', {
                    required: 'Описание обязательно',
                  })}
                  error={!!errors.description}
                  helperText={errors.description?.message as any}
                  placeholder='Подробно опишите проблему с оборудованием...'
                />
              </Grid>

              {/* Информация об оборудовании */}
              <Grid item xs={12}>
                <Typography variant='h6' gutterBottom sx={{ mt: 2 }}>
                  Информация об оборудовании
                </Typography>
              </Grid>

              <Grid item xs={12} md={4}>
                <FormControl fullWidth error={!!errors.equipment_type}>
                  <InputLabel>Тип оборудования</InputLabel>
                  <Select
                    {...register('equipment_type')}
                    label='Тип оборудования'
                  >
                    {equipmentTypes.map(type => (
                      <MenuItem key={type} value={type}>
                        {type}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={4}>
                <FormControl fullWidth error={!!errors.equipment_brand}>
                  <InputLabel>Бренд оборудования</InputLabel>
                  <Select
                    {...register('equipment_brand')}
                    label='Бренд оборудования'
                  >
                    {equipmentBrands.map(brand => (
                      <MenuItem key={brand} value={brand}>
                        {brand}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label='Модель оборудования'
                  {...register('equipment_model')}
                  error={!!errors.equipment_model}
                  helperText={errors.equipment_model?.message as any}
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label='Детальное описание неисправности'
                  {...register('problem_description')}
                  error={!!errors.problem_description}
                  helperText={errors.problem_description?.message as any}
                  placeholder='Опишите симптомы, когда возникла проблема, что происходило перед поломкой...'
                />
              </Grid>

              {/* Местоположение */}
              <Grid item xs={12}>
                <Typography variant='h6' gutterBottom sx={{ mt: 2 }}>
                  Местоположение
                </Typography>
              </Grid>

              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label='Регион'
                  {...register('region', { required: 'Регион обязателен' })}
                  error={!!errors.region}
                  helperText={errors.region?.message as any}
                />
              </Grid>

              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label='Город'
                  {...register('city')}
                  error={!!errors.city}
                  helperText={errors.city?.message as any}
                />
              </Grid>

              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label='Адрес'
                  {...register('address')}
                  error={!!errors.address}
                  helperText={errors.address?.message as any}
                />
              </Grid>

              <Grid item xs={12} md={4}>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                    height: '100%',
                  }}
                >
                  <Button
                    variant='outlined'
                    startIcon={<LocationOn />}
                    onClick={() => setMapOpen(true)}
                    sx={{ height: '56px' }}
                  >
                    Выбрать на карте
                  </Button>
                  {selectedLocation && (
                    <Typography variant='caption' color='text.secondary'>
                      Место выбрано
                    </Typography>
                  )}
                </Box>
              </Grid>

              {/* Дополнительные параметры */}
              <Grid item xs={12}>
                <Typography variant='h6' gutterBottom sx={{ mt: 2 }}>
                  Дополнительные параметры
                </Typography>
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  type='datetime-local'
                  label='Предпочтительная дата выполнения'
                  InputLabelProps={{ shrink: true }}
                  {...register('preferred_date')}
                  error={!!errors.preferred_date}
                  helperText={errors.preferred_date?.message as any}
                />
              </Grid>

              {/* Кнопки */}
              <Grid item xs={12}>
                <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
                  <Button
                    type='submit'
                    variant='contained'
                    startIcon={
                      loading ? <CircularProgress size={20} /> : <Save />
                    }
                    disabled={loading}
                    sx={{ minWidth: 200 }}
                  >
                    {loading ? 'Создание...' : 'Создать заявку'}
                  </Button>

                  <Button
                    variant='outlined'
                    onClick={() => reset()}
                    disabled={loading}
                  >
                    Очистить форму
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </form>
        </CardContent>
      </Card>

      {/* Компонент выбора места на карте */}
      <LocationPicker
        open={mapOpen}
        onClose={() => setMapOpen(false)}
        onLocationSelect={handleLocationSelect}
      />
    </Box>
  );
};

export default CreateRequestPage;
