import React, { useState } from 'react';
import {
  Container,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  CircularProgress,
  Link,
  InputAdornment,
  IconButton,
  Card,
  CardContent,
} from '@mui/material';
import { Visibility, VisibilityOff, Person, Lock } from '@mui/icons-material';
import { useForm } from 'react-hook-form';
import { useAuth } from 'hooks/useAuth';
import { LoginRequest } from 'types/api';
import Logo from 'components/Logo';

const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginRequest>();

  const onSubmit = async (data: LoginRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      await login(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка входа в систему');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClickShowPassword = () => {
    setShowPassword(!showPassword);
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
                Вход в систему
              </Typography>
              <Typography
                variant="body1"
                sx={{
                  color: '#666',
                }}
              >
                Войдите в свой аккаунт
              </Typography>
            </Box>

            {/* Форма */}
            <Box component="form" onSubmit={handleSubmit(onSubmit)}>
              {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                  {error}
                </Alert>
              )}

              {/* Имя пользователя */}
              <TextField
                fullWidth
                label="Имя пользователя"
                {...register('username', {
                  required: 'Введите имя пользователя',
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

              {/* Пароль */}
              <TextField
                fullWidth
                label="Пароль"
                type={showPassword ? 'text' : 'password'}
                {...register('password', {
                  required: 'Введите пароль',
                })}
                error={!!errors.password}
                helperText={errors.password?.message}
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

              {/* Кнопка входа */}
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
                  'Войти'
                )}
              </Button>

              {/* Ссылки */}
              <Box sx={{ textAlign: 'center', mt: 3 }}>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  Нет аккаунта?{' '}
                  <Link
                    component="button"
                    variant="body2"
                    onClick={() => window.location.href = '/register'}
                    sx={{
                      fontWeight: 'bold',
                      textDecoration: 'none',
                      '&:hover': {
                        textDecoration: 'underline',
                      },
                    }}
                  >
                    Зарегистрироваться
                  </Link>
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Нужна помощь с входом в систему?{' '}
                  <Link
                    component="button"
                    variant="body2"
                    sx={{
                      fontWeight: 'bold',
                      textDecoration: 'none',
                      '&:hover': {
                        textDecoration: 'underline',
                      },
                    }}
                  >
                    Обратитесь к администратору
                  </Link>
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
};

export default LoginPage;