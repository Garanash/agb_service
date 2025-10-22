import React, { useState } from 'react';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  CircularProgress,
  Link,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  FormControlLabel,
  FormGroup,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  DialogContentText,
} from '@mui/material';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import Logo from '../components/Logo';
import { useAuth } from 'hooks/useAuth';
import { UserRole } from 'types/api';

interface ContractorForm {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  firstName: string;
  lastName: string;
  patronymic: string;
  phone: string;
  specializations: string[];
  // Новые поля для специализации по обслуживанию техники
  equipmentBrandsExperience: string[];
  certifications: string[];
  workRegions: string[];
  hourlyRate: number;
  telegramUsername: string;
}

interface CustomerForm {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  companyName: string;
  region: string;
  phone: string;
  innOrOgrn: string;
  // Новые поля для горнодобывающей техники
  equipmentBrands: string[];
  equipmentTypes: string[];
  miningOperations: string[];
  serviceHistory: string;
}

const specializations = [
  'Электрика',
  'Гидравлика',
  'Ходовая часть',
  'Двигатели',
  'Трансмиссия',
  'Системы управления',
  'Пневматика',
  'Сварка',
  'Механика',
  'Электроника',
  'Другие специализации'
];

// Константы для горнодобывающей техники
const equipmentBrands = [
  'Алмазгеобур',
  'Эпирог',
  'Бортлангир',
  'Катерпиллар',
  'Компани',
  'Либхерр',
  'Вольво',
  'Другие'
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
  'Другое оборудование'
];

const miningOperations = [
  'Геологоразведочные работы',
  'Буровзрывные работы',
  'Подземные горные работы',
  'Открытые горные работы',
  'Обогащение полезных ископаемых',
  'Транспортировка',
  'Складские операции',
  'Другие виды работ'
];

// Константы для исполнителей
const certifications = [
  'Сертификат сварщика',
  'Сертификат электрика',
  'Сертификат гидравлика',
  'Сертификат по технике безопасности',
  'Сертификат по работе с грузоподъемными механизмами',
  'Сертификат по работе с опасными веществами',
  'Другие сертификаты'
];

const workRegions = [
  'Москва и область',
  'Санкт-Петербург и область',
  'Центральный федеральный округ',
  'Северо-Западный федеральный округ',
  'Южный федеральный округ',
  'Приволжский федеральный округ',
  'Уральский федеральный округ',
  'Сибирский федеральный округ',
  'Дальневосточный федеральный округ',
  'Другие регионы'
];

const RegistrationPage: React.FC = () => {
  const navigate = useNavigate();
  const { registerCustomer, registerContractor } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedRole, setSelectedRole] = useState<'contractor' | 'customer'>('contractor');
  const [showSuccessDialog, setShowSuccessDialog] = useState(false);
  const [registeredEmail, setRegisteredEmail] = useState<string>('');

  const contractorForm = useForm<ContractorForm>();
  const customerForm = useForm<CustomerForm>();

  const onSubmitContractor = async (data: ContractorForm) => {
    setIsLoading(true);
    setError(null);

    try {
      await registerContractor({
        username: data.username,
        email: data.email,
        password: data.password,
        first_name: data.firstName,
        last_name: data.lastName,
        middle_name: data.patronymic,
        phone: data.phone,
        specializations: data.specializations,
        equipment_brands_experience: data.equipmentBrandsExperience,
        certifications: data.certifications,
        work_regions: data.workRegions,
        hourly_rate: data.hourlyRate,
        telegram_username: data.telegramUsername,
      });
      setRegisteredEmail(data.email);
      setShowSuccessDialog(true);
      contractorForm.reset();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка регистрации');
    } finally {
      setIsLoading(false);
    }
  };

  const onSubmitCustomer = async (data: CustomerForm) => {
    setIsLoading(true);
    setError(null);

    try {
      await registerCustomer({
        username: data.username,
        email: data.email,
        password: data.password,
        first_name: data.companyName,
        last_name: '',
        phone: data.phone,
        company_name: data.companyName,
        region: data.region,
        inn_or_ogrn: data.innOrOgrn,
        equipment_brands: data.equipmentBrands,
        equipment_types: data.equipmentTypes,
        mining_operations: data.miningOperations,
        service_history: data.serviceHistory,
      });
      setRegisteredEmail(data.email);
      setShowSuccessDialog(true);
      customerForm.reset();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка регистрации');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 2,
      }}
    >
      <Container component="main" maxWidth="md">
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          {/* Логотип */}
          {/* Заголовок */}
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1, mb: 2 }}>
            <Logo size={40} color="#FCB813" />
            <Typography
              component="h1"
              variant="h5"
              sx={{
                fontWeight: 'bold',
                color: '#1a1a1a',
              }}
            >
              AGB SERVICE
            </Typography>
          </Box>

          {/* Форма регистрации */}
          <Paper
            elevation={8}
            sx={{
              padding: 2,
              borderRadius: 3,
              backdropFilter: 'blur(10px)',
              backgroundColor: 'rgba(255, 255, 255, 0.7)',
              boxShadow: '0 8px 32px 0 rgba( 31, 38, 135, 0.37 )',
              border: '1px solid rgba(255, 255, 255, 0.18)',
              width: '100%',
              maxWidth: 600,
            }}
          >
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            {/* Выбор типа пользователя */}
            <FormControl fullWidth margin="normal" required>
              <InputLabel id="role-select-label">Я</InputLabel>
              <Select
                labelId="role-select-label"
                id="role-select"
                value={selectedRole}
                label="Я"
                onChange={(e) => setSelectedRole(e.target.value as 'contractor' | 'customer')}
              >
                <MenuItem value="contractor">Исполнитель</MenuItem>
                <MenuItem value="customer">Заказчик</MenuItem>
              </Select>
            </FormControl>

            {/* Форма для исполнителя */}
            {selectedRole === 'contractor' && (
              <Box component="form" onSubmit={contractorForm.handleSubmit(onSubmitContractor)} noValidate>
                <TextField
                  margin="dense"
                  required
                  fullWidth
                  id="username"
                  label="Имя пользователя"
                  autoComplete="username"
                  autoFocus
                  {...contractorForm.register('username', { required: 'Имя пользователя обязательно' })}
                  error={!!contractorForm.formState.errors.username}
                  helperText={contractorForm.formState.errors.username?.message}
                />

                <TextField
                  margin="dense"
                  required
                  fullWidth
                  label="Email"
                  type="email"
                  id="email"
                  autoComplete="email"
                  {...contractorForm.register('email', { required: 'Email обязателен' })}
                  error={!!contractorForm.formState.errors.email}
                  helperText={contractorForm.formState.errors.email?.message}
                />

                <TextField
                  margin="dense"
                  required
                  fullWidth
                  label="Пароль"
                  type="password"
                  id="password"
                  autoComplete="new-password"
                  {...contractorForm.register('password', { required: 'Пароль обязателен', minLength: { value: 6, message: 'Пароль должен быть не менее 6 символов' } })}
                  error={!!contractorForm.formState.errors.password}
                  helperText={contractorForm.formState.errors.password?.message}
                />

                <TextField
                  margin="dense"
                  required
                  fullWidth
                  label="Подтвердите пароль"
                  type="password"
                  id="confirmPassword"
                  autoComplete="new-password"
                  {...contractorForm.register('confirmPassword', { 
                    required: 'Подтверждение пароля обязательно',
                    validate: value => value === contractorForm.watch('password') || 'Пароли не совпадают'
                  })}
                  error={!!contractorForm.formState.errors.confirmPassword}
                  helperText={contractorForm.formState.errors.confirmPassword?.message}
                />

                <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
                  <TextField
                    fullWidth
                    label="Фамилия"
                    {...contractorForm.register('lastName', { required: 'Фамилия обязательна' })}
                    error={!!contractorForm.formState.errors.lastName}
                    helperText={contractorForm.formState.errors.lastName?.message}
                  />
                  <TextField
                    fullWidth
                    label="Имя"
                    {...contractorForm.register('firstName', { required: 'Имя обязательно' })}
                    error={!!contractorForm.formState.errors.firstName}
                    helperText={contractorForm.formState.errors.firstName?.message}
                  />
                </Box>
                
                <TextField
                  margin="dense"
                  fullWidth
                  label="Отчество"
                  {...contractorForm.register('patronymic')}
                />

                <TextField
                  margin="dense"
                  required
                  fullWidth
                  label="Телефон"
                  {...contractorForm.register('phone', { required: 'Телефон обязателен' })}
                  error={!!contractorForm.formState.errors.phone}
                  helperText={contractorForm.formState.errors.phone?.message}
                />

                <Box sx={{ mt: 1, mb: 1 }}>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    Специализация:
                  </Typography>
                  <FormGroup>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {specializations.map((spec) => (
                        <FormControlLabel
                          key={spec}
                          control={
                            <Checkbox
                              {...contractorForm.register('specializations')}
                              value={spec}
                              size="small"
                            />
                          }
                          label={spec}
                          sx={{ 
                            margin: 0,
                            '& .MuiFormControlLabel-label': { fontSize: '0.875rem' }
                          }}
                        />
                      ))}
                    </Box>
                  </FormGroup>
                </Box>

                {/* Новые поля для специализации по обслуживанию техники */}
                <Typography variant="h6" sx={{ mt: 2, mb: 1, color: '#1976d2' }}>
                  Профессиональная информация
                </Typography>

                <FormControl fullWidth margin="dense">
                  <InputLabel>Опыт работы с брендами техники</InputLabel>
                  <Select
                    multiple
                    value={contractorForm.watch('equipmentBrandsExperience') || []}
                    onChange={(e) => contractorForm.setValue('equipmentBrandsExperience', e.target.value as string[])}
                    renderValue={(selected) => (selected as string[]).join(', ')}
                  >
                    {equipmentBrands.map((brand) => (
                      <MenuItem key={brand} value={brand}>
                        <Checkbox checked={(contractorForm.watch('equipmentBrandsExperience') || []).indexOf(brand) > -1} />
                        {brand}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <FormControl fullWidth margin="dense">
                  <InputLabel>Сертификаты и квалификации</InputLabel>
                  <Select
                    multiple
                    value={contractorForm.watch('certifications') || []}
                    onChange={(e) => contractorForm.setValue('certifications', e.target.value as string[])}
                    renderValue={(selected) => (selected as string[]).join(', ')}
                  >
                    {certifications.map((cert) => (
                      <MenuItem key={cert} value={cert}>
                        <Checkbox checked={(contractorForm.watch('certifications') || []).indexOf(cert) > -1} />
                        {cert}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <FormControl fullWidth margin="dense">
                  <InputLabel>Регионы работы</InputLabel>
                  <Select
                    multiple
                    value={contractorForm.watch('workRegions') || []}
                    onChange={(e) => contractorForm.setValue('workRegions', e.target.value as string[])}
                    renderValue={(selected) => (selected as string[]).join(', ')}
                  >
                    {workRegions.map((region) => (
                      <MenuItem key={region} value={region}>
                        <Checkbox checked={(contractorForm.watch('workRegions') || []).indexOf(region) > -1} />
                        {region}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
                  <TextField
                    fullWidth
                    label="Почасовая ставка (руб.)"
                    type="number"
                    {...contractorForm.register('hourlyRate', { 
                      required: 'Почасовая ставка обязательна',
                      min: { value: 0, message: 'Ставка должна быть положительной' }
                    })}
                    error={!!contractorForm.formState.errors.hourlyRate}
                    helperText={contractorForm.formState.errors.hourlyRate?.message}
                  />
                  <TextField
                    fullWidth
                    label="Telegram username"
                    placeholder="@username"
                    {...contractorForm.register('telegramUsername')}
                  />
                </Box>

                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  sx={{
                    mt: 1,
                    mb: 0.5,
                    background: 'linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%)',
                    boxShadow: '0 3px 5px 2px rgba(255, 105, 135, .3)',
                    color: 'white',
                    py: 1,
                    fontWeight: 'bold',
                  }}
                  disabled={isLoading}
                >
                  {isLoading ? <CircularProgress size={24} color="inherit" /> : 'Зарегистрироваться'}
                </Button>
              </Box>
            )}

            {/* Форма для заказчика */}
            {selectedRole === 'customer' && (
              <Box component="form" onSubmit={customerForm.handleSubmit(onSubmitCustomer)} noValidate>
                <TextField
                  margin="dense"
                  required
                  fullWidth
                  id="username"
                  label="Имя пользователя"
                  autoComplete="username"
                  autoFocus
                  {...customerForm.register('username', { required: 'Имя пользователя обязательно' })}
                  error={!!customerForm.formState.errors.username}
                  helperText={customerForm.formState.errors.username?.message}
                />

                <TextField
                  margin="dense"
                  required
                  fullWidth
                  label="Email"
                  type="email"
                  id="email"
                  autoComplete="email"
                  {...customerForm.register('email', { required: 'Email обязателен' })}
                  error={!!customerForm.formState.errors.email}
                  helperText={customerForm.formState.errors.email?.message}
                />

                <TextField
                  margin="dense"
                  required
                  fullWidth
                  label="Пароль"
                  type="password"
                  id="password"
                  autoComplete="new-password"
                  {...customerForm.register('password', { required: 'Пароль обязателен', minLength: { value: 6, message: 'Пароль должен быть не менее 6 символов' } })}
                  error={!!customerForm.formState.errors.password}
                  helperText={customerForm.formState.errors.password?.message}
                />

                <TextField
                  margin="dense"
                  required
                  fullWidth
                  label="Подтвердите пароль"
                  type="password"
                  id="confirmPassword"
                  autoComplete="new-password"
                  {...customerForm.register('confirmPassword', { 
                    required: 'Подтверждение пароля обязательно',
                    validate: value => value === customerForm.watch('password') || 'Пароли не совпадают'
                  })}
                  error={!!customerForm.formState.errors.confirmPassword}
                  helperText={customerForm.formState.errors.confirmPassword?.message}
                />

                <TextField
                  margin="dense"
                  required
                  fullWidth
                  label="Название компании"
                  {...customerForm.register('companyName', { required: 'Название компании обязательно' })}
                  error={!!customerForm.formState.errors.companyName}
                  helperText={customerForm.formState.errors.companyName?.message}
                />

                <TextField
                  margin="dense"
                  required
                  fullWidth
                  label="Регион"
                  {...customerForm.register('region', { required: 'Регион обязателен' })}
                  error={!!customerForm.formState.errors.region}
                  helperText={customerForm.formState.errors.region?.message}
                />

                <TextField
                  margin="dense"
                  required
                  fullWidth
                  label="Телефон"
                  {...customerForm.register('phone', { required: 'Телефон обязателен' })}
                  error={!!customerForm.formState.errors.phone}
                  helperText={customerForm.formState.errors.phone?.message}
                />

                <TextField
                  margin="dense"
                  required
                  fullWidth
                  label="ИНН или ОГРН"
                  {...customerForm.register('innOrOgrn', { required: 'ИНН или ОГРН обязателен' })}
                  error={!!customerForm.formState.errors.innOrOgrn}
                  helperText={customerForm.formState.errors.innOrOgrn?.message}
                />

                {/* Новые поля для горнодобывающей техники */}
                <Typography variant="h6" sx={{ mt: 2, mb: 1, color: '#1976d2' }}>
                  Информация о технике
                </Typography>

                <FormControl fullWidth margin="dense">
                  <InputLabel>Бренды техники</InputLabel>
                  <Select
                    multiple
                    value={customerForm.watch('equipmentBrands') || []}
                    onChange={(e) => customerForm.setValue('equipmentBrands', e.target.value as string[])}
                    renderValue={(selected) => (selected as string[]).join(', ')}
                  >
                    {equipmentBrands.map((brand) => (
                      <MenuItem key={brand} value={brand}>
                        <Checkbox checked={(customerForm.watch('equipmentBrands') || []).indexOf(brand) > -1} />
                        {brand}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <FormControl fullWidth margin="dense">
                  <InputLabel>Типы оборудования</InputLabel>
                  <Select
                    multiple
                    value={customerForm.watch('equipmentTypes') || []}
                    onChange={(e) => customerForm.setValue('equipmentTypes', e.target.value as string[])}
                    renderValue={(selected) => (selected as string[]).join(', ')}
                  >
                    {equipmentTypes.map((type) => (
                      <MenuItem key={type} value={type}>
                        <Checkbox checked={(customerForm.watch('equipmentTypes') || []).indexOf(type) > -1} />
                        {type}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <FormControl fullWidth margin="dense">
                  <InputLabel>Виды горных работ</InputLabel>
                  <Select
                    multiple
                    value={customerForm.watch('miningOperations') || []}
                    onChange={(e) => customerForm.setValue('miningOperations', e.target.value as string[])}
                    renderValue={(selected) => (selected as string[]).join(', ')}
                  >
                    {miningOperations.map((operation) => (
                      <MenuItem key={operation} value={operation}>
                        <Checkbox checked={(customerForm.watch('miningOperations') || []).indexOf(operation) > -1} />
                        {operation}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <TextField
                  margin="dense"
                  fullWidth
                  multiline
                  rows={3}
                  label="История обслуживания"
                  placeholder="Опишите ваш опыт работы с горнодобывающей техникой..."
                  {...customerForm.register('serviceHistory')}
                />

                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  sx={{
                    mt: 1,
                    mb: 0.5,
                    background: 'linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%)',
                    boxShadow: '0 3px 5px 2px rgba(255, 105, 135, .3)',
                    color: 'white',
                    py: 1,
                    fontWeight: 'bold',
                  }}
                  disabled={isLoading}
                >
                  {isLoading ? <CircularProgress size={24} color="inherit" /> : 'Зарегистрироваться'}
                </Button>
              </Box>
            )}

            {/* Ссылка на вход */}
            <Box sx={{ textAlign: 'center', mt: 0.5 }}>
              <Typography variant="body2" color="text.secondary">
                Уже есть аккаунт?{' '}
                <Link
                  href="/login"
                  sx={{
                    color: '#1976d2',
                    textDecoration: 'none',
                    fontWeight: 500,
                    '&:hover': {
                      textDecoration: 'underline',
                    },
                  }}
                >
                  Войти
                </Link>
              </Typography>
            </Box>
          </Paper>

          {/* Копирайт */}
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{
              mt: 1,
              textAlign: 'center',
              opacity: 0.7,
            }}
          >
            © 2025 Neurofork. Все права защищены.
          </Typography>
        </Box>
      </Container>

      {/* Модальное окно успешной регистрации */}
      <Dialog
        open={showSuccessDialog}
        onClose={() => setShowSuccessDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle sx={{ textAlign: 'center', pb: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 2 }}>
            <Box
              sx={{
                width: 60,
                height: 60,
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #4caf50 0%, #8bc34a 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mr: 2,
              }}
            >
              <Typography
                variant="h4"
                sx={{
                  color: 'white',
                  fontWeight: 'bold',
                }}
              >
                ✓
              </Typography>
            </Box>
          </Box>
          <Typography variant="h5" sx={{ fontWeight: 'bold', color: '#2e7d32' }}>
            Регистрация успешна!
          </Typography>
        </DialogTitle>
        <DialogContent sx={{ textAlign: 'center', pt: 1 }}>
          <DialogContentText sx={{ mb: 2, fontSize: '1.1rem' }}>
            Спасибо за регистрацию в системе AGB SERVICE!
          </DialogContentText>
          <DialogContentText sx={{ mb: 2 }}>
            Мы отправили вам на почту <strong>{registeredEmail}</strong> код подтверждения.
            Пожалуйста, проверьте вашу почту и перейдите по ссылке для активации аккаунта.
          </DialogContentText>
          <DialogContentText sx={{ fontSize: '0.9rem', color: 'text.secondary' }}>
            Если письмо не пришло, проверьте папку "Спам" или обратитесь к администратору.
          </DialogContentText>
        </DialogContent>
        <DialogActions sx={{ justifyContent: 'center', pb: 3 }}>
          <Button
            onClick={() => navigate('/login')}
            variant="contained"
            sx={{
              background: 'linear-gradient(135deg, #1976d2 0%, #42a5f5 100%)',
              px: 4,
              py: 1,
              fontWeight: 'bold',
            }}
          >
            Перейти к входу
          </Button>
          <Button
            onClick={() => setShowSuccessDialog(false)}
            variant="outlined"
            sx={{ px: 4, py: 1 }}
          >
            Остаться на странице
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default RegistrationPage;