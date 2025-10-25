import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  TextField,
  Alert,
  CircularProgress,
  Divider,
} from '@mui/material';
import {
  Save,
  Person,
  Email,
  Phone,
  Business,
} from '@mui/icons-material';
import { useAuth } from '../hooks/useAuth';
import { apiService } from '../services/api';
import AvatarUpload from '../components/AvatarUpload';

const ProfileSettingsPage: React.FC = () => {
  const { user, updateUser } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);

  // Форма профиля
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    middle_name: '',
    email: '',
    phone: '',
    position: '',
  });

  useEffect(() => {
    if (user) {
      setFormData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        middle_name: user.middle_name || '',
        email: user.email || '',
        phone: user.phone || '',
        position: user.position || '',
      });
      setAvatarUrl(user.avatar_url || null);
    }
  }, [user]);

  const handleInputChange = (field: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.value,
    }));
  };

  const handleAvatarChange = (newAvatarUrl: string | null) => {
    setAvatarUrl(newAvatarUrl);
    if (updateUser) {
      updateUser({ ...user, avatar_url: newAvatarUrl });
    }
  };

  const handleSave = async () => {
    if (!user) return;

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      // Обновляем профиль пользователя
      const updatedUser = await apiService.updateUser(user.id, formData);
      
      if (updateUser) {
        updateUser(updatedUser);
      }
      
      setSuccess('Профиль успешно обновлен!');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка обновления профиля');
    } finally {
      setLoading(false);
    }
  };

  const getUserDisplayName = () => {
    if (!user) return 'Пользователь';
    
    const parts = [user.first_name, user.last_name].filter(Boolean);
    return parts.length > 0 ? parts.join(' ') : user.username;
  };

  const getRoleDisplayName = (role: string) => {
    const roleMap: Record<string, string> = {
      admin: 'Администратор',
      manager: 'Менеджер',
      contractor: 'Исполнитель',
      customer: 'Заказчик',
      security: 'Служба безопасности',
      hr: 'HR специалист',
    };
    return roleMap[role] || role;
  };

  if (!user) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold', mb: 4 }}>
        Настройки профиля
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }}>
          {success}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Левая колонка - Аватар и основная информация */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent sx={{ textAlign: 'center', p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Аватар
              </Typography>
              
              <AvatarUpload
                currentAvatarUrl={avatarUrl}
                userName={getUserDisplayName()}
                onAvatarChange={handleAvatarChange}
                size={120}
              />

              <Divider sx={{ my: 2 }} />

              <Box sx={{ textAlign: 'left' }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  <Person sx={{ fontSize: 16, mr: 1, verticalAlign: 'middle' }} />
                  Имя пользователя
                </Typography>
                <Typography variant="body1" sx={{ mb: 2 }}>
                  {user.username}
                </Typography>

                <Typography variant="body2" color="text.secondary" gutterBottom>
                  <Business sx={{ fontSize: 16, mr: 1, verticalAlign: 'middle' }} />
                  Роль
                </Typography>
                <Typography variant="body1" sx={{ mb: 2 }}>
                  {getRoleDisplayName(user.role)}
                </Typography>

                <Typography variant="body2" color="text.secondary" gutterBottom>
                  <Email sx={{ fontSize: 16, mr: 1, verticalAlign: 'middle' }} />
                  Email подтвержден
                </Typography>
                <Typography variant="body1" color={user.email_verified ? 'success.main' : 'error.main'}>
                  {user.email_verified ? 'Да' : 'Нет'}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Правая колонка - Форма редактирования */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Личная информация
              </Typography>

              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Имя"
                    value={formData.first_name}
                    onChange={handleInputChange('first_name')}
                    InputProps={{
                      startAdornment: <Person sx={{ mr: 1, color: 'action.active' }} />,
                    }}
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Фамилия"
                    value={formData.last_name}
                    onChange={handleInputChange('last_name')}
                    InputProps={{
                      startAdornment: <Person sx={{ mr: 1, color: 'action.active' }} />,
                    }}
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Отчество"
                    value={formData.middle_name}
                    onChange={handleInputChange('middle_name')}
                    InputProps={{
                      startAdornment: <Person sx={{ mr: 1, color: 'action.active' }} />,
                    }}
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Должность"
                    value={formData.position}
                    onChange={handleInputChange('position')}
                    InputProps={{
                      startAdornment: <Business sx={{ mr: 1, color: 'action.active' }} />,
                    }}
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Email"
                    type="email"
                    value={formData.email}
                    onChange={handleInputChange('email')}
                    InputProps={{
                      startAdornment: <Email sx={{ mr: 1, color: 'action.active' }} />,
                    }}
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Телефон"
                    value={formData.phone}
                    onChange={handleInputChange('phone')}
                    InputProps={{
                      startAdornment: <Phone sx={{ mr: 1, color: 'action.active' }} />,
                    }}
                  />
                </Grid>
              </Grid>

              <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
                <Button
                  variant="contained"
                  startIcon={loading ? <CircularProgress size={20} /> : <Save />}
                  onClick={handleSave}
                  disabled={loading}
                  size="large"
                >
                  {loading ? 'Сохранение...' : 'Сохранить изменения'}
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default ProfileSettingsPage;
