import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Grid,
  Alert,
  CircularProgress,
} from '@mui/material';
import { Save } from '@mui/icons-material';
import { useAuth } from 'hooks/useAuth';
import { apiService } from 'services/api';
import { styled } from '@mui/material/styles';

interface CompanyProfile {
  company_name: string;
  contact_person: string;
  phone: string;
  email: string;
  address?: string;
  inn?: string;
  kpp?: string;
  ogrn?: string;
  equipment_brands?: string[];
  equipment_types?: string[];
  mining_operations?: string[];
  service_history?: string;
}

interface CustomerCompanyProfilePageProps {
  hideTitle?: boolean;
}

const CustomerCompanyProfilePage: React.FC<CustomerCompanyProfilePageProps> = ({ hideTitle = false }) => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [profile, setProfile] = useState<CompanyProfile>({
    company_name: '',
    contact_person: '',
    phone: '',
    email: '',
    address: '',
    inn: '',
    kpp: '',
    ogrn: '',
    equipment_brands: [],
    equipment_types: [],
    mining_operations: [],
    service_history: '',
  });

  // Форматирование телефона для отображения в реальном времени: +7 (XXX) XXX - XX - XX
  const formatPhoneDisplay = (digitsOnly: string): string => {
    const d = (digitsOnly || '').replace(/\D/g, '');
    if (!d) return '';
    
    let normalized = d;
    // Нормализация: 10 цифр -> добавляем 7, 8XXXXXXXXXX -> заменяем на 7
    if (normalized.length === 10) {
      normalized = '7' + normalized;
    } else if (normalized.length === 11 && normalized[0] === '8') {
      normalized = '7' + normalized.slice(1);
    } else if (normalized.length > 11) {
      normalized = normalized.slice(0, 11); // Ограничиваем до 11 цифр
    }
    
    // Постепенное форматирование при вводе
    if (normalized.length < 1) return '';
    if (normalized.length === 1) return `+${normalized}`;
    if (normalized.length <= 4) return `+${normalized[0]} (${normalized.slice(1)}`;
    if (normalized.length <= 7) {
      return `+${normalized[0]} (${normalized.slice(1, 4)}) ${normalized.slice(4)}`;
    }
    if (normalized.length <= 9) {
      return `+${normalized[0]} (${normalized.slice(1, 4)}) ${normalized.slice(4, 7)} - ${normalized.slice(7)}`;
    }
    // Полный формат: +7 (XXX) XXX - XX - XX
    return `+${normalized[0]} (${normalized.slice(1, 4)}) ${normalized.slice(4, 7)} - ${normalized.slice(7, 9)} - ${normalized.slice(9, 11)}`;
  };

  // Обработчик ввода: разрешаем только цифры, максимум 11
  const handlePhoneChange = (raw: string) => {
    const digits = raw.replace(/\D/g, '').slice(0, 11);
    setProfile(prev => ({ ...prev, phone: digits }));
  };

  const [phoneError, setPhoneError] = useState<string | null>(null);

  // Валидация телефона при изменении в реальном времени
  useEffect(() => {
    const digits = (profile.phone || '').replace(/\D/g, '');
    if (digits.length === 0) {
      setPhoneError(null);
    } else if (digits.length < 10) {
      setPhoneError('Введите минимум 10 цифр');
    } else if (digits.length === 10 || digits.length === 11) {
      setPhoneError(null);
    } else {
      setPhoneError('Телефон должен содержать 10-11 цифр');
    }
  }, [profile.phone]);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      const profileData = await apiService.getCustomerProfile();
      setProfile({
        company_name: profileData.company_name || '',
        contact_person: profileData.contact_person || '',
        phone: profileData.phone || '',
        email: profileData.email || '',
        address: profileData.address || '',
        inn: profileData.inn || '',
        kpp: profileData.kpp || '',
        ogrn: profileData.ogrn || '',
        equipment_brands: profileData.equipment_brands || [],
        equipment_types: profileData.equipment_types || [],
        mining_operations: profileData.mining_operations || [],
        service_history: profileData.service_history || '',
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка загрузки профиля');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!profile.company_name || profile.company_name.trim().length < 1) {
      setError('Название компании обязательно для заполнения');
      return;
    }
    if (!profile.phone || profile.phone.length < 10) {
      setError('Телефон должен содержать не менее 10 символов');
      return;
    }

    try {
      setSaving(true);
      setError(null);
      await apiService.updateCustomerProfile(profile as any);
      setSuccess('Профиль компании успешно сохранен');
      await loadProfile();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка сохранения профиля');
    } finally {
      setSaving(false);
    }
  };

  const isProfileComplete = () => {
    return (
      profile.company_name &&
      profile.company_name.trim().length >= 1 &&
      profile.phone &&
      profile.phone.length >= 10
    );
  };

  if (loading) {
    return (
      <Box display='flex' justifyContent='center' alignItems='center' minHeight='400px'>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: hideTitle ? 0 : 3 }}>
      {!hideTitle && (
        <Typography variant='h4' gutterBottom>
          Профиль компании
        </Typography>
      )}

      {!isProfileComplete() && (
        <Alert severity='warning' sx={{ mb: 2 }}>
          Для создания заявок необходимо заполнить обязательные поля: название компании и телефон.
        </Alert>
      )}

      {error && (
        <Alert severity='error' sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity='success' sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      <Card>
        <CardContent>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant='h6' gutterBottom>
                Основная информация
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label='Название компании *'
                value={profile.company_name}
                onChange={(e) =>
                  setProfile({ ...profile, company_name: e.target.value })
                }
                required
                error={!profile.company_name || profile.company_name.trim().length < 1}
                helperText={
                  !profile.company_name || profile.company_name.trim().length < 1
                    ? 'Обязательное поле'
                    : ''
                }
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label='Контактное лицо'
                value={profile.contact_person}
                onChange={(e) =>
                  setProfile({ ...profile, contact_person: e.target.value })
                }
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label='Телефон *'
                value={formatPhoneDisplay(profile.phone)}
                onChange={(e) => handlePhoneChange(e.target.value)}
                required
                error={!!phoneError || (!profile.phone || profile.phone.replace(/\D/g, '').length < 10)}
                helperText={
                  phoneError || (!profile.phone || profile.phone.replace(/\D/g, '').length < 10
                    ? 'Введите минимум 10 цифр телефона'
                    : '')
                }
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label='Email'
                type='email'
                value={profile.email}
                onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                disabled
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label='Адрес'
                value={profile.address || ''}
                onChange={(e) => setProfile({ ...profile, address: e.target.value })}
                multiline
                rows={2}
              />
            </Grid>

            <Grid item xs={12}>
              <Typography variant='h6' gutterBottom sx={{ mt: 2 }}>
                Реквизиты
              </Typography>
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label='ИНН'
                value={profile.inn || ''}
                onChange={(e) => setProfile({ ...profile, inn: e.target.value })}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label='КПП'
                value={profile.kpp || ''}
                onChange={(e) => setProfile({ ...profile, kpp: e.target.value })}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label='ОГРН'
                value={profile.ogrn || ''}
                onChange={(e) => setProfile({ ...profile, ogrn: e.target.value })}
              />
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
                <Button
                  variant='contained'
                  startIcon={saving ? <CircularProgress size={20} /> : <Save />}
                  onClick={handleSave}
                  disabled={saving || !isProfileComplete()}
                >
                  {saving ? 'Сохранение...' : 'Сохранить профиль'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
};

export default CustomerCompanyProfilePage;

