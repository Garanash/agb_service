import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Avatar,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  IconButton,
  CircularProgress,
  Alert,
  Card,
  CardContent,
} from '@mui/material';
import {
  PhotoCamera,
  Delete,
  Upload,
  Close,
} from '@mui/icons-material';
import { apiService } from '../services/api';

interface AvatarUploadProps {
  currentAvatarUrl?: string;
  userName: string;
  onAvatarChange: (avatarUrl: string | null) => void;
  size?: number;
}

const AvatarUpload: React.FC<AvatarUploadProps> = ({
  currentAvatarUrl,
  userName,
  onAvatarChange,
  size = 128,
}) => {
  const [avatarUrl, setAvatarUrl] = useState<string | null>(currentAvatarUrl || null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setAvatarUrl(currentAvatarUrl || null);
  }, [currentAvatarUrl]);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Проверяем тип файла
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      setError('Неподдерживаемый формат файла. Разрешены: JPG, PNG, GIF, WebP');
      return;
    }

    // Проверяем размер файла (5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError('Файл слишком большой. Максимальный размер: 5MB');
      return;
    }

    uploadAvatar(file);
  };

  const uploadAvatar = async (file: File) => {
    setIsUploading(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await apiService.uploadAvatar(file);
      setAvatarUrl(result.avatar_url);
      onAvatarChange(result.avatar_url);
      setSuccess('Аватар успешно загружен!');
      setIsDialogOpen(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка загрузки аватара');
    } finally {
      setIsUploading(false);
    }
  };

  const removeAvatar = async () => {
    setIsUploading(true);
    setError(null);
    setSuccess(null);

    try {
      await apiService.removeAvatar();
      setAvatarUrl(null);
      onAvatarChange(null);
      setSuccess('Аватар удален!');
      setIsDialogOpen(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка удаления аватара');
    } finally {
      setIsUploading(false);
    }
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
      {/* Аватар */}
      <Box sx={{ position: 'relative' }}>
        <Avatar
          src={avatarUrl ? `${process.env.REACT_APP_API_URL || 'http://91.222.236.58:3000'}${avatarUrl}` : undefined}
          sx={{
            width: size,
            height: size,
            fontSize: size * 0.4,
            bgcolor: 'primary.main',
            cursor: 'pointer',
          }}
          onClick={() => setIsDialogOpen(true)}
        >
          {!avatarUrl && getInitials(userName)}
        </Avatar>
        
        {/* Кнопка камеры */}
        <IconButton
          sx={{
            position: 'absolute',
            bottom: 0,
            right: 0,
            bgcolor: 'primary.main',
            color: 'white',
            '&:hover': {
              bgcolor: 'primary.dark',
            },
            width: 32,
            height: 32,
          }}
          onClick={() => setIsDialogOpen(true)}
        >
          <PhotoCamera sx={{ fontSize: 16 }} />
        </IconButton>
      </Box>

      {/* Кнопка изменения аватара */}
      <Button
        variant="outlined"
        startIcon={<PhotoCamera />}
        onClick={() => setIsDialogOpen(true)}
        size="small"
      >
        Изменить аватар
      </Button>

      {/* Скрытый input для выбора файла */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileSelect}
        style={{ display: 'none' }}
      />

      {/* Диалог управления аватаром */}
      <Dialog
        open={isDialogOpen}
        onClose={() => !isUploading && setIsDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Typography variant="h6">Управление аватаром</Typography>
            <IconButton
              onClick={() => setIsDialogOpen(false)}
              disabled={isUploading}
            >
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>

        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2, py: 2 }}>
            {/* Текущий аватар */}
            <Avatar
              src={avatarUrl ? `${process.env.REACT_APP_API_URL || 'http://91.222.236.58:3000'}${avatarUrl}` : undefined}
              sx={{
                width: 120,
                height: 120,
                fontSize: 48,
                bgcolor: 'primary.main',
              }}
            >
              {!avatarUrl && getInitials(userName)}
            </Avatar>

            {/* Сообщения об ошибках/успехе */}
            {error && (
              <Alert severity="error" sx={{ width: '100%' }}>
                {error}
              </Alert>
            )}
            {success && (
              <Alert severity="success" sx={{ width: '100%' }}>
                {success}
              </Alert>
            )}

            {/* Информация о требованиях */}
            <Typography variant="body2" color="text.secondary" textAlign="center">
              Поддерживаемые форматы: JPG, PNG, GIF, WebP
              <br />
              Максимальный размер: 5MB
            </Typography>
          </Box>
        </DialogContent>

        <DialogActions sx={{ p: 2, gap: 1 }}>
          <Button
            onClick={openFileDialog}
            variant="contained"
            startIcon={<Upload />}
            disabled={isUploading}
            fullWidth
          >
            {isUploading ? <CircularProgress size={20} /> : 'Загрузить новый'}
          </Button>
          
          {avatarUrl && (
            <Button
              onClick={removeAvatar}
              variant="outlined"
              color="error"
              startIcon={<Delete />}
              disabled={isUploading}
              fullWidth
            >
              {isUploading ? <CircularProgress size={20} /> : 'Удалить аватар'}
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AvatarUpload;
