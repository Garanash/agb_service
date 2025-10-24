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
  InputAdornment,
  IconButton,
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
        background:
          'linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 2,
        position: 'relative',
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background:
            'radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.15) 0%, transparent 50%), radial-gradient(circle at 40% 40%, rgba(120, 219, 255, 0.1) 0%, transparent 50%)',
          zIndex: 0,
        },
      }}
    >
      <Container
        component='main'
        maxWidth='sm'
        sx={{ position: 'relative', zIndex: 1 }}
      >
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          {/* Логотип и название */}
          <Box sx={{ mb: 4, textAlign: 'center' }}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mb: 2,
                gap: 2,
              }}
            >
              <Logo size={64} color='#FCB813' />
              <Typography
                component='h1'
                variant='h3'
                sx={{
                  fontWeight: 'bold',
                  color: 'white',
                  fontSize: '2.5rem',
                  letterSpacing: '0.02em',
                }}
              >
                AGB SERVICE
              </Typography>
            </Box>
            <Typography
              variant='h6'
              sx={{
                color: 'rgba(255, 255, 255, 0.7)',
                fontWeight: 400,
                fontSize: '1.1rem',
              }}
            >
              Агрегатор услуг и исполнителей
            </Typography>
          </Box>

          {/* Форма входа */}
          <Paper
            elevation={24}
            sx={{
              padding: 4,
              width: '100%',
              borderRadius: 3,
              background: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              boxShadow: '0 25px 50px rgba(0, 0, 0, 0.25)',
            }}
          >
            {error && (
              <Alert
                severity='error'
                sx={{
                  mb: 3,
                  borderRadius: 2,
                  backgroundColor: 'rgba(244, 67, 54, 0.1)',
                  border: '1px solid rgba(244, 67, 54, 0.2)',
                }}
              >
                {error}
              </Alert>
            )}

            <Box component='form' onSubmit={handleSubmit(onSubmit)} noValidate>
              <TextField
                margin='normal'
                required
                fullWidth
                id='username'
                label='Имя пользователя'
                placeholder='Введите имя пользователя'
                autoComplete='username'
                autoFocus
                {...register('username', {
                  required: 'Имя пользователя обязательно',
                })}
                error={!!errors.username}
                helperText={errors.username?.message}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position='start'>
                      <Person sx={{ color: 'rgba(0, 0, 0, 0.6)' }} />
                    </InputAdornment>
                  ),
                }}
                sx={{
                  mb: 2,
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                    backgroundColor: 'rgba(255, 255, 255, 0.8)',
                    '&:hover': {
                      backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    },
                    '&.Mui-focused': {
                      backgroundColor: 'white',
                    },
                  },
                  '& .MuiInputLabel-root': {
                    color: 'rgba(0, 0, 0, 0.7)',
                  },
                }}
              />

              <TextField
                margin='normal'
                required
                fullWidth
                label='Пароль'
                type={showPassword ? 'text' : 'password'}
                id='password'
                placeholder='Введите пароль'
                autoComplete='current-password'
                {...register('password', { required: 'Пароль обязателен' })}
                error={!!errors.password}
                helperText={errors.password?.message}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position='start'>
                      <Lock sx={{ color: 'rgba(0, 0, 0, 0.6)' }} />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position='end'>
                      <IconButton
                        aria-label='toggle password visibility'
                        onClick={handleClickShowPassword}
                        edge='end'
                        sx={{ color: 'rgba(0, 0, 0, 0.6)' }}
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
                sx={{
                  mb: 3,
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                    backgroundColor: 'rgba(255, 255, 255, 0.8)',
                    '&:hover': {
                      backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    },
                    '&.Mui-focused': {
                      backgroundColor: 'white',
                    },
                  },
                  '& .MuiInputLabel-root': {
                    color: 'rgba(0, 0, 0, 0.7)',
                  },
                }}
              />

              <Button
                type='submit'
                fullWidth
                variant='contained'
                disabled={isLoading}
                sx={{
                  mt: 2,
                  mb: 3,
                  py: 1.8,
                  borderRadius: 2,
                  background:
                    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  fontSize: '1.1rem',
                  fontWeight: 600,
                  textTransform: 'none',
                  boxShadow: '0 8px 32px rgba(102, 126, 234, 0.3)',
                  '&:hover': {
                    background:
                      'linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%)',
                    boxShadow: '0 12px 40px rgba(102, 126, 234, 0.4)',
                    transform: 'translateY(-2px)',
                  },
                  '&:active': {
                    transform: 'translateY(0px)',
                  },
                  transition: 'all 0.3s ease',
                }}
              >
                {isLoading ? (
                  <CircularProgress size={24} color='inherit' />
                ) : (
                  'Войти'
                )}
              </Button>

              {/* Ссылка на регистрацию */}
              <Box sx={{ textAlign: 'center', mb: 2 }}>
                <Typography
                  variant='body2'
                  sx={{ color: 'rgba(0, 0, 0, 0.7)' }}
                >
                  Нет аккаунта?{' '}
                  <Link
                    href='/register'
                    sx={{
                      color: '#667eea',
                      textDecoration: 'none',
                      fontWeight: 500,
                      '&:hover': {
                        textDecoration: 'underline',
                        color: '#5a6fd8',
                      },
                      transition: 'color 0.3s ease',
                    }}
                  >
                    Зарегистрироваться
                  </Link>
                </Typography>
              </Box>

              {/* Ссылка на помощь */}
              <Box sx={{ textAlign: 'center' }}>
                <Typography
                  variant='body2'
                  sx={{ color: 'rgba(0, 0, 0, 0.6)', fontSize: '0.9rem' }}
                >
                  Нужна помощь с входом в систему?{' '}
                  <Link
                    href='#'
                    sx={{
                      color: '#667eea',
                      textDecoration: 'none',
                      fontWeight: 500,
                      '&:hover': {
                        textDecoration: 'underline',
                        color: '#5a6fd8',
                      },
                      transition: 'color 0.3s ease',
                    }}
                  >
                    Обратитесь к администратору
                  </Link>
                </Typography>
              </Box>
            </Box>
          </Paper>

          {/* Копирайт */}
          <Typography
            variant='body2'
            sx={{
              mt: 4,
              textAlign: 'center',
              color: 'rgba(255, 255, 255, 0.6)',
              fontSize: '0.9rem',
            }}
          >
            © 2025 Алмазгеобур. Все права защищены.
          </Typography>
        </Box>
      </Container>
    </Box>
  );
};

export default LoginPage;
