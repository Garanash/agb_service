import React, { useState, useEffect, useRef } from 'react';
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

  const phoneInputRef = useRef<HTMLInputElement>(null);
  const [phoneError, setPhoneError] = useState<string | null>(null);
  const [phoneFocused, setPhoneFocused] = useState(false);

  // Нормализация: извлекаем только цифры и нормализуем формат
  const normalizePhoneDigits = (value: string): string => {
    if (!value) return '';
    
    // Извлекаем только цифры
    let digits = value.replace(/\D/g, '');
    
    // Если начинается с 8, заменяем на 7
    if (digits.length > 0 && digits[0] === '8') {
      digits = '7' + digits.slice(1);
    }
    
    // Если 10 цифр, добавляем 7 в начало
    if (digits.length === 10) {
      digits = '7' + digits;
    }
    
    // Ограничиваем до 11 цифр
    return digits.slice(0, 11);
  };

  // Форматирование телефона для отображения: +7 (XXX) XXX - XX - XX
  const formatPhoneDisplay = (digits: string): string => {
    const d = normalizePhoneDigits(digits);
    if (!d) return '';
    
    // Форматируем по мере ввода
    if (d.length === 0) return '';
    if (d.length === 1) return `+${d}`;
    if (d.length <= 4) return `+${d[0]} (${d.slice(1)}`;
    if (d.length <= 7) return `+${d[0]} (${d.slice(1, 4)}) ${d.slice(4)}`;
    if (d.length <= 9) return `+${d[0]} (${d.slice(1, 4)}) ${d.slice(4, 7)} - ${d.slice(7)}`;
    
    // Полный формат: +7 (XXX) XXX - XX - XX
    return `+${d[0]} (${d.slice(1, 4)}) ${d.slice(4, 7)} - ${d.slice(7, 9)} - ${d.slice(9, 11)}`;
  };

  // Вычисление новой позиции курсора после форматирования
  const getCursorPosition = (
    oldFormatted: string,
    newFormatted: string,
    oldCursorPos: number,
    oldDigits: string,
    newDigits: string
  ): number => {
    // Если длина цифр уменьшилась, это удаление
    if (newDigits.length < oldDigits.length) {
      // Считаем количество цифр до курсора в старой строке
      let digitsBeforeCursor = 0;
      for (let i = 0; i < oldCursorPos && i < oldFormatted.length; i++) {
        if (/\d/.test(oldFormatted[i])) {
          digitsBeforeCursor++;
        }
      }
      
      // Находим позицию в новой строке для такого же количества цифр
      let newPos = 0;
      let digitCount = 0;
      for (let i = 0; i < newFormatted.length && digitCount < digitsBeforeCursor; i++) {
        if (/\d/.test(newFormatted[i])) {
          digitCount++;
        }
        newPos = i + 1;
      }
      return newPos;
    }
    
    // При добавлении - позиция после последней цифры
    let digitsCount = 0;
    let pos = newFormatted.length;
    for (let i = 0; i < newFormatted.length; i++) {
      if (/\d/.test(newFormatted[i])) {
        digitsCount++;
        if (digitsCount === newDigits.length) {
          pos = i + 1;
          break;
        }
      }
    }
    return pos;
  };

  // Обработчик изменения телефона
  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const input = e.target;
    const inputValue = input.value;
    const cursorPosition = input.selectionStart || 0;
    
    // Сохраняем старые значения
    const oldDigits = normalizePhoneDigits(profile.phone || '');
    const oldFormatted = formatPhoneDisplay(profile.phone || '');
    
    // Извлекаем новые цифры
    let newDigits = normalizePhoneDigits(inputValue);
    
    // Ограничиваем до 11 цифр
    if (newDigits.length > 11) {
      newDigits = newDigits.slice(0, 11);
    }
    
    // Обновляем state
    setProfile(prev => ({ ...prev, phone: newDigits }));
    
    // Вычисляем новую позицию курсора после форматирования
    const newFormatted = formatPhoneDisplay(newDigits);
    const newCursorPos = getCursorPosition(
      oldFormatted,
      newFormatted,
      cursorPosition,
      oldDigits,
      newDigits
    );
    
    // Устанавливаем позицию курсора после обновления DOM
    setTimeout(() => {
      if (phoneInputRef.current) {
        phoneInputRef.current.setSelectionRange(newCursorPos, newCursorPos);
      }
    }, 0);
  };

  // Обработчик вставки (Ctrl+V / Cmd+V)
  const handlePhonePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
    const pastedText = e.clipboardData.getData('text/plain') || e.clipboardData.getData('text');
    const digits = normalizePhoneDigits(pastedText);
    
    if (digits.length <= 11) {
      setProfile(prev => ({ ...prev, phone: digits }));
      
      // Устанавливаем курсор в конец после вставки
      setTimeout(() => {
        if (phoneInputRef.current) {
          const formatted = formatPhoneDisplay(digits);
          phoneInputRef.current.setSelectionRange(formatted.length, formatted.length);
        }
      }, 0);
    }
  };

  // Обработчик клавиатуры (удаление, backspace)
  const handlePhoneKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    // Разрешаем удаление, backspace, стрелки, tab, escape
    if (
      ['Backspace', 'Delete', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Tab', 'Escape']
        .includes(e.key) ||
      (e.ctrlKey || e.metaKey) && ['a', 'c', 'v', 'x'].includes(e.key.toLowerCase())
    ) {
      return;
    }
    
    // Разрешаем только цифры
    if (!/[0-9]/.test(e.key) && !e.key.startsWith('Arrow') && !e.metaKey && !e.ctrlKey) {
      e.preventDefault();
    }
  };

  // Валидация телефона
  useEffect(() => {
    const digits = normalizePhoneDigits(profile.phone || '');
    
    if (!digits) {
      setPhoneError(null);
      return;
    }
    
    if (digits.length < 10) {
      const remaining = 10 - digits.length;
      setPhoneError(`Осталось ввести ${remaining} ${remaining === 1 ? 'цифру' : remaining < 5 ? 'цифры' : 'цифр'}`);
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
      // Нормализуем телефон при загрузке - оставляем только цифры
      const phoneDigits = normalizePhoneDigits(profileData.phone || '');
      setProfile({
        company_name: profileData.company_name || '',
        contact_person: profileData.contact_person || '',
        phone: phoneDigits, // Сохраняем только цифры
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
                inputRef={phoneInputRef}
                fullWidth
                label='Телефон *'
                value={formatPhoneDisplay(profile.phone || '')}
                onChange={handlePhoneChange}
                onPaste={handlePhonePaste}
                onKeyDown={handlePhoneKeyDown}
                onFocus={() => setPhoneFocused(true)}
                onBlur={() => setPhoneFocused(false)}
                required
                placeholder={phoneFocused ? '' : '+7 (999) 123 - 45 - 67'}
                error={!!phoneError && (profile.phone?.length || 0) > 0}
                helperText={
                  phoneError 
                    ? phoneError 
                    : phoneFocused 
                    ? 'Введите номер телефона. Начните с цифр (можно без +7)' 
                    : 'Формат: +7 (XXX) XXX - XX - XX'
                }
                inputProps={{
                  maxLength: 24, // Максимальная длина отформатированного номера
                  inputMode: 'tel' as const,
                  autoComplete: 'tel',
                }}
                sx={{
                  '& .MuiInputBase-input': {
                    fontFamily: 'monospace',
                    letterSpacing: phoneFocused ? '0.5px' : '0px',
                  },
                }}
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

