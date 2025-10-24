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
  InputAdornment,
  IconButton,
  Card,
  CardContent,
} from '@mui/material';
import { Visibility, VisibilityOff, Person, Lock, Email, Business } from '@mui/icons-material';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import Logo from '../components/Logo';
import { useAuth } from 'hooks/useAuth';
import { UserRole } from 'types/api';

interface SimpleRegistrationForm {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  role: 'contractor' | 'customer';
}

const RegistrationPage: React.FC = () => {
  const { registerSimple } = useAuth();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [successDialogOpen, setSuccessDialogOpen] = useState(false);
  const [registeredEmail, setRegisteredEmail] = useState('');

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<SimpleRegistrationForm>();

  const password = watch('password');

  const onSubmit = async (data: SimpleRegistrationForm) => {
    setIsLoading(true);
    setError(null);

    try {
      await registerSimple({
        username: data.username,
        email: data.email,
        password: data.password,
        confirmPassword: data.confirmPassword,
        role: data.role,
      });
      
      setRegisteredEmail(data.email);
      setSuccessDialogOpen(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка регистрации');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClickShowPassword = () => {
    setShowPassword(!showPassword);
  };

  const handleClickShowConfirmPassword = () => {
    setShowConfirmPassword(!showConfirmPassword);
  };

  const handleCloseSuccessDialog = () => {
    setSuccessDialogOpen(false);
    navigate('/login');
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        backgroundColor: '#f5f5f5',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 2,
      }}
    >
      <Container maxWidth="sm">
        <Card
          sx={{
            borderRadius: 2,
            boxShadow: 3,
            overflow: 'hidden',
          }}
        >
          <CardContent sx={{ p: 4 }}>
            {/* Логотип и заголовок */}
            <Box
              sx={{
                textAlign: 'center',
                mb: 4,
              }}
            >
              <Logo />
              <Typography
                variant="h4"
                component="h1"
                sx={{
                  fontWeight: 'bold',
                  color: '#333',
                  mt: 2,
                  mb: 1,
                }}
              >
                Регистрация
              </Typography>
              <Typography
                variant="body1"
                sx={{
                  color: '#666',
                }}
              >
                Создайте аккаунт для доступа к системе
              </Typography>
            </Box>

            {/* Форма */}
            <Box component="form" onSubmit={handleSubmit(onSubmit)}>
              {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                  {error}
                </Alert>
              )}

              {/* Роль пользователя */}
              <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel>Роль</InputLabel>
                <Select
                  {...register('role', { required: 'Выберите роль' })}
                  label="Роль"
                  defaultValue="contractor"
                >
                  <MenuItem value="contractor">
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Person sx={{ mr: 1 }} />
                      Исполнитель
                    </Box>
                  </MenuItem>
                  <MenuItem value="customer">
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Business sx={{ mr: 1 }} />
                      Заказчик
                    </Box>
                  </MenuItem>
                </Select>
                {errors.role && (
                  <Typography variant="caption" color="error">
                    {errors.role.message}
                  </Typography>
                )}
              </FormControl>

              {/* Имя пользователя */}
              <TextField
                fullWidth
                label="Имя пользователя"
                {...register('username', {
                  required: 'Введите имя пользователя',
                  minLength: {
                    value: 3,
                    message: 'Минимум 3 символа',
                  },
                })}
                error={!!errors.username}
                helperText={errors.username?.message}
                sx={{ mb: 3 }}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Person />
                    </InputAdornment>
                  ),
                }}
              />

              {/* Email */}
              <TextField
                fullWidth
                label="Email"
                type="email"
                {...register('email', {
                  required: 'Введите email',
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: 'Неверный формат email',
                  },
                })}
                error={!!errors.email}
                helperText={errors.email?.message}
                sx={{ mb: 3 }}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Email />
                    </InputAdornment>
                  ),
                }}
              />

              {/* Пароль */}
              <TextField
                fullWidth
                label="Пароль"
                type={showPassword ? 'text' : 'password'}
                {...register('password', {
                  required: 'Введите пароль',
                  minLength: {
                    value: 6,
                    message: 'Минимум 6 символов',
                  },
                })}
                error={!!errors.password}
                helperText={errors.password?.message}
                sx={{ mb: 3 }}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Lock />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        aria-label="toggle password visibility"
                        onClick={handleClickShowPassword}
                        edge="end"
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />

              {/* Подтверждение пароля */}
              <TextField
                fullWidth
                label="Подтвердите пароль"
                type={showConfirmPassword ? 'text' : 'password'}
                {...register('confirmPassword', {
                  required: 'Подтвердите пароль',
                  validate: (value) =>
                    value === password || 'Пароли не совпадают',
                })}
                error={!!errors.confirmPassword}
                helperText={errors.confirmPassword?.message}
                sx={{ mb: 4 }}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Lock />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        aria-label="toggle confirm password visibility"
                        onClick={handleClickShowConfirmPassword}
                        edge="end"
                      >
                        {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />

              {/* Кнопка регистрации */}
              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                disabled={isLoading}
                sx={{
                  py: 1.5,
                  fontSize: '1.1rem',
                  fontWeight: 'bold',
                  borderRadius: 2,
                }}
              >
                {isLoading ? (
                  <CircularProgress size={24} color="inherit" />
                ) : (
                  'Зарегистрироваться'
                )}
              </Button>

              {/* Ссылка на вход */}
              <Box sx={{ textAlign: 'center', mt: 3 }}>
                <Typography variant="body2" color="text.secondary">
                  Уже есть аккаунт?{' '}
                  <Link
                    component="button"
                    variant="body2"
                    onClick={() => navigate('/login')}
                    sx={{
                      fontWeight: 'bold',
                      textDecoration: 'none',
                      '&:hover': {
                        textDecoration: 'underline',
                      },
                    }}
                  >
                    Войти
                  </Link>
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>

        {/* Диалог успешной регистрации */}
        <Alert
          severity="success"
          sx={{
            mt: 2,
            borderRadius: 2,
            display: successDialogOpen ? 'block' : 'none',
          }}
        >
          <Typography variant="h6" gutterBottom>
            ✓ Регистрация успешна!
          </Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>
            Спасибо за регистрацию в системе AGB SERVICE!
          </Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>
            Мы отправили вам на почту{' '}
            <strong>{registeredEmail}</strong>{' '}
            код подтверждения. Пожалуйста, проверьте вашу почту и перейдите по ссылке для активации аккаунта.
          </Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>
            Если письмо не пришло, проверьте папку "Спам" или обратитесь к администратору.
          </Typography>
          <Box sx={{ mt: 2 }}>
            <Button
              variant="contained"
              onClick={handleCloseSuccessDialog}
              sx={{ mr: 1 }}
            >
              Перейти к входу
            </Button>
            <Button
              variant="outlined"
              onClick={() => setSuccessDialogOpen(false)}
            >
              Остаться на странице
            </Button>
          </Box>
        </Alert>
      </Container>
    </Box>
  );
};

export default RegistrationPage;