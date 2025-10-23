import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Avatar,
  Button,
  TextField,
  Divider,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
} from '@mui/material';
import {
  Person,
  Email,
  Phone,
  Business,
  Edit,
  Save,
  Cancel,
  AccountCircle,
  CheckCircle,
} from '@mui/icons-material';
import { useForm } from 'react-hook-form';
import { useAuth } from 'hooks/useAuth';
import { apiService } from 'services/api';
import { UserRole } from 'types/api';

const ProfilePage: React.FC = () => {
  const { user, refreshUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({
    defaultValues: {
      first_name: user?.first_name || '',
      last_name: user?.last_name || '',
      middle_name: user?.middle_name || '',
      phone: user?.phone || '',
      position: user?.position || '',
    },
  });

  useEffect(() => {
    if (user) {
      reset({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        middle_name: user.middle_name || '',
        phone: user.phone || '',
        position: user.position || '',
      });
    }
  }, [user, reset]);

  const handleSave = async (data: any) => {
    setLoading(true);
    try {
      // Здесь должен быть API для обновления профиля пользователя
      // Пока просто обновляем локально
      await refreshUser();
      setIsEditing(false);
    } catch (error) {
      console.error('Failed to update profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    reset({
      first_name: user?.first_name || '',
      last_name: user?.last_name || '',
      middle_name: user?.middle_name || '',
      phone: user?.phone || '',
      position: user?.position || '',
    });
    setIsEditing(false);
  };

  const getRoleText = (role: UserRole) => {
    switch (role) {
      case UserRole.ADMIN:
        return 'Администратор';
      case UserRole.CUSTOMER:
        return 'Заказчик';
      case UserRole.CONTRACTOR:
        return 'Исполнитель';
      case UserRole.SERVICE_ENGINEER:
        return 'Сервисный инженер';
      default:
        return 'Пользователь';
    }
  };

  const getRoleColor = (role: UserRole) => {
    switch (role) {
      case UserRole.ADMIN:
        return 'error';
      case UserRole.CUSTOMER:
        return 'primary';
      case UserRole.CONTRACTOR:
        return 'success';
      case UserRole.SERVICE_ENGINEER:
        return 'warning';
      default:
        return 'default';
    }
  };

  if (!user) {
    return <Typography>Загрузка...</Typography>;
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Мой профиль
      </Typography>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {/* Основная информация */}
        <Box sx={{ flex: '2 1 400px', minWidth: '400px' }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">Основная информация</Typography>
                <Button
                  variant={isEditing ? 'outlined' : 'contained'}
                  startIcon={isEditing ? <Cancel /> : <Edit />}
                  onClick={isEditing ? handleCancel : () => setIsEditing(true)}
                >
                  {isEditing ? 'Отмена' : 'Редактировать'}
                </Button>
              </Box>

              <form onSubmit={handleSubmit(handleSave)}>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                    <TextField
                      fullWidth
                      label="Имя"
                      {...register('first_name')}
                      disabled={!isEditing}
                    />
                    <TextField
                      fullWidth
                      label="Фамилия"
                      {...register('last_name')}
                      disabled={!isEditing}
                    />
                    <TextField
                      fullWidth
                      label="Отчество"
                      {...register('middle_name')}
                      disabled={!isEditing}
                    />
                  </Box>
                  <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                    <TextField
                      fullWidth
                      label="Телефон"
                      {...register('phone')}
                      disabled={!isEditing}
                    />
                    <TextField
                      fullWidth
                      label="Должность"
                      {...register('position')}
                      disabled={!isEditing}
                    />
                  </Box>
                </Box>

                {isEditing && (
                  <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                    <Button
                      type="submit"
                      variant="contained"
                      startIcon={<Save />}
                      disabled={loading}
                    >
                      Сохранить
                    </Button>
                  </Box>
                )}
              </form>
            </CardContent>
          </Card>
        </Box>

        {/* Информация о пользователе */}
        <Box sx={{ flex: '1 1 300px', minWidth: '300px' }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ width: 80, height: 80, mb: 2 }}>
                  <AccountCircle sx={{ fontSize: 60 }} />
                </Avatar>
                <Typography variant="h6">
                  {user.first_name} {user.last_name}
                </Typography>
                <Chip
                  label={getRoleText(user.role)}
                  color={getRoleColor(user.role)}
                  size="small"
                  sx={{ mt: 1 }}
                />
              </Box>

              <Divider sx={{ my: 2 }} />

              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <Email />
                  </ListItemIcon>
                  <ListItemText
                    primary="Email"
                    secondary={user.email}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <Person />
                  </ListItemIcon>
                  <ListItemText
                    primary="Имя пользователя"
                    secondary={user.username}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <Business />
                  </ListItemIcon>
                  <ListItemText
                    primary="Статус"
                    secondary={user.is_active ? 'Активен' : 'Неактивен'}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <Email />
                  </ListItemIcon>
                  <ListItemText
                    primary="Email подтвержден"
                    secondary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {user.email_verified ? (
                          <>
                            <Chip
                              label="Подтвержден"
                              color="success"
                              size="small"
                              icon={<CheckCircle />}
                            />
                          </>
                        ) : (
                          <>
                            <Chip
                              label="Не подтвержден"
                              color="error"
                              size="small"
                              icon={<Cancel />}
                            />
                          </>
                        )}
                      </Box>
                    }
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <Person />
                  </ListItemIcon>
                  <ListItemText
                    primary="Дата регистрации"
                    secondary={new Date(user.created_at).toLocaleDateString('ru-RU')}
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>

          {/* Дополнительная информация в зависимости от роли */}
          {user.role === UserRole.CUSTOMER && (
            <Card sx={{ mt: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Информация о компании
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Здесь будет отображаться информация о профиле заказчика
                </Typography>
                <Button
                  variant="outlined"
                  fullWidth
                  sx={{ mt: 2 }}
                  onClick={() => {/* Переход к редактированию профиля заказчика */}}
                >
                  Редактировать профиль компании
                </Button>
              </CardContent>
            </Card>
          )}

          {user.role === UserRole.CONTRACTOR && (
            <Card sx={{ mt: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Профиль исполнителя
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Здесь будет отображаться информация о профиле исполнителя
                </Typography>
                <Button
                  variant="outlined"
                  fullWidth
                  sx={{ mt: 2 }}
                  onClick={() => {/* Переход к редактированию профиля исполнителя */}}
                >
                  Редактировать профиль исполнителя
                </Button>
              </CardContent>
            </Card>
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default ProfilePage;
