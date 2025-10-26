import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Paper,
  Typography,
  Button,
  CircularProgress,
  Alert,
} from '@mui/material';
import { CheckCircle, Error } from '@mui/icons-material';
import { apiService } from '../services/api';

const VerifyEmailPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(true);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const verifyEmail = async () => {
      const token = searchParams.get('token');

      if (!token) {
        setError('Отсутствует токен подтверждения');
        setIsLoading(false);
        return;
      }

      try {
        await apiService.verifyEmail(token);
        setSuccess(true);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Ошибка подтверждения email');
      } finally {
        setIsLoading(false);
      }
    };

    verifyEmail();
  }, [searchParams]);

  const handleGoToLogin = () => {
    navigate('/login');
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#f5f5f5',
        padding: 2,
      }}
    >
      <Container maxWidth='sm'>
        <Paper
          elevation={3}
          sx={{
            padding: 4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            textAlign: 'center',
          }}
        >
          {isLoading && (
            <>
              <CircularProgress sx={{ mb: 3 }} />
              <Typography variant='h6' gutterBottom>
                Подтверждение email...
              </Typography>
            </>
          )}

          {success && !isLoading && (
            <>
              <CheckCircle sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
              <Typography variant='h4' gutterBottom color='success.main'>
                Email подтвержден!
              </Typography>
              <Typography variant='body1' sx={{ mb: 3, textAlign: 'center' }}>
                Спасибо! Ваша почта подтверждена.
              </Typography>
              <Typography variant='body2' sx={{ mb: 3, color: 'text.secondary' }}>
                Теперь вы можете входить в систему со своим логином и паролем.
              </Typography>
              <Button
                variant='contained'
                size='large'
                onClick={handleGoToLogin}
                sx={{ mt: 2 }}
              >
                Перейти к входу
              </Button>
            </>
          )}

          {error && !isLoading && (
            <>
              <Error sx={{ fontSize: 80, color: 'error.main', mb: 2 }} />
              <Typography variant='h5' gutterBottom color='error'>
                Ошибка подтверждения
              </Typography>
              <Alert severity='error' sx={{ mt: 2, mb: 2, width: '100%' }}>
                {error}
              </Alert>
              <Typography variant='body2' sx={{ mb: 2 }}>
                Возможные причины:
              </Typography>
              <Typography variant='body2' component='ul' sx={{ textAlign: 'left' }}>
                <li>Ссылка подтверждения недействительна</li>
                <li>Ссылка подтверждения устарела (действительна 24 часа)</li>
                <li>Email уже был подтвержден ранее</li>
              </Typography>
              <Button
                variant='contained'
                size='large'
                onClick={() => navigate('/register')}
                sx={{ mt: 3 }}
              >
                Вернуться к регистрации
              </Button>
            </>
          )}
        </Paper>
      </Container>
    </Box>
  );
};

export default VerifyEmailPage;

