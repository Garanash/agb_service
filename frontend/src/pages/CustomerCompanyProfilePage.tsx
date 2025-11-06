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
  Autocomplete,
  Chip,
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

// Список брендов горнодобывающей техники на иностранном языке
const EQUIPMENT_BRANDS = [
  'Caterpillar',
  'Komatsu',
  'Hitachi',
  'Volvo',
  'Liebherr',
  'Atlas Copco',
  'Sandvik',
  'Epiroc',
  'Boart Longyear',
  'JCB',
  'Case',
  'John Deere',
  'Terex',
  'Bucyrus',
  'P&H',
  'Joy Global',
  'Sany',
  'XCMG',
  'Zoomlion',
  'Liebherr Mining',
];

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
  // Эта функция используется только для нормализации уже существующих номеров (при загрузке)
  const normalizePhoneDigits = (value: string): string => {
    if (!value) return '';
    
    // Извлекаем только цифры
    let digits = value.replace(/\D/g, '');
    
    // Если первая цифра 8, заменяем на 7
    if (digits.length > 0 && digits[0] === '8') {
      digits = '7' + digits.slice(1);
    }
    
    // Если 10 цифр (без кода страны), добавляем 7 в начало
    if (digits.length === 10 && digits[0] !== '7') {
      digits = '7' + digits;
    }
    
    // Если не начинается с 7 и больше 10 цифр, убираем лишние и добавляем 7
    if (digits.length > 0 && digits[0] !== '7') {
      // Если больше 10 цифр, оставляем только последние 10 и добавляем 7
      if (digits.length > 10) {
        digits = '7' + digits.slice(-10);
      } else {
        digits = '7' + digits;
      }
    }
    
    // Ограничиваем до 11 цифр (7 + 10 цифр номера)
    return digits.slice(0, 11);
  };

  // Форматирование телефона для отображения: +7 (XXX) XXX - XX - XX
  const formatPhoneDisplay = (digits: string): string => {
    // Если поле пустое, возвращаем пустую строку (без +7)
    if (!digits || digits.trim() === '') return '';
    
    const d = normalizePhoneDigits(digits);
    if (!d || d.length === 0) return '';
    
    // Форматируем по мере ввода
    // Всегда должно быть +7 в начале после нормализации
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
    
    // Если поле было полностью очищено, сбрасываем телефон
    if (inputValue === '' || inputValue.trim() === '') {
      setProfile(prev => ({ ...prev, phone: '' }));
      return;
    }
    
    // Извлекаем только цифры из ввода
    let rawDigits = inputValue.replace(/\D/g, '');
    
    // Если первая цифра 8, удаляем её (будет заменена на 7)
    if (rawDigits.length > 0 && rawDigits[0] === '8') {
      rawDigits = rawDigits.slice(1);
    }
    
    // Добавляем 7 в начало, если есть хотя бы одна цифра
    // Но только если ещё нет 7 в начале
    if (rawDigits.length > 0) {
      if (rawDigits[0] !== '7') {
        rawDigits = '7' + rawDigits;
      }
    }
    
    // Ограничиваем до 11 цифр
    const newDigits = rawDigits.slice(0, 11);
    
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
      setError(null); // Очищаем предыдущие ошибки
      const profileData = await apiService.getCustomerProfile();
      // Нормализуем телефон при загрузке - оставляем только цифры
      // Если телефон есть, нормализуем его, иначе оставляем пустым
      let phoneDigits = '';
      if (profileData.phone && profileData.phone.trim()) {
        phoneDigits = normalizePhoneDigits(profileData.phone);
      }
      
      setProfile({
        company_name: profileData.company_name || '',
        contact_person: profileData.contact_person || '',
        phone: phoneDigits, // Сохраняем только цифры или пустую строку
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
      // Игнорируем ошибки, связанные с профилем исполнителя (это не относится к заказчику)
      const errorMessage = err.response?.data?.detail || err.message || 'Ошибка загрузки профиля';
      if (!errorMessage.includes('исполнителя') && !errorMessage.includes('contractor')) {
        setError(errorMessage);
      } else {
        console.warn('Игнорируем ошибку, не относящуюся к профилю заказчика:', errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  // Валидация ИНН
  const validateINN = (inn: string): string | null => {
    if (!inn || inn.trim() === '') return null; // ИНН не обязателен
    const digits = inn.replace(/\D/g, '');
    if (digits.length !== 10 && digits.length !== 12) {
      return 'ИНН должен содержать 10 или 12 цифр';
    }
    if (!/^\d+$/.test(digits)) {
      return 'ИНН должен содержать только цифры';
    }
    return null;
  };

  // Валидация КПП
  const validateKPP = (kpp: string): string | null => {
    if (!kpp || kpp.trim() === '') return null; // КПП не обязателен
    const digits = kpp.replace(/\D/g, '');
    if (digits.length !== 9) {
      return 'КПП должен содержать 9 цифр';
    }
    if (!/^\d+$/.test(digits)) {
      return 'КПП должен содержать только цифры';
    }
    return null;
  };

  // Валидация ОГРН
  const validateOGRN = (ogrn: string): string | null => {
    if (!ogrn || ogrn.trim() === '') return null; // ОГРН не обязателен
    const digits = ogrn.replace(/\D/g, '');
    if (digits.length !== 13 && digits.length !== 15) {
      return 'ОГРН должен содержать 13 (для ЮЛ) или 15 (для ИП) цифр';
    }
    if (!/^\d+$/.test(digits)) {
      return 'ОГРН должен содержать только цифры';
    }
    return null;
  };

  const [innError, setInnError] = useState<string | null>(null);
  const [kppError, setKppError] = useState<string | null>(null);
  const [ogrnError, setOgrnError] = useState<string | null>(null);

  const handleSave = async () => {
    // Валидация обязательных полей
    if (!profile.company_name || profile.company_name.trim().length < 1) {
      setError('Название компании обязательно для заполнения');
      return;
    }
    
    const phoneDigits = normalizePhoneDigits(profile.phone || '');
    if (!phoneDigits || phoneDigits.length < 11) {
      setError('Телефон должен содержать 11 цифр (включая код страны 7)');
      return;
    }

    // Валидация ИНН, КПП, ОГРН
    const innValidation = validateINN(profile.inn || '');
    const kppValidation = validateKPP(profile.kpp || '');
    const ogrnValidation = validateOGRN(profile.ogrn || '');

    if (innValidation) {
      setInnError(innValidation);
      setError(innValidation);
      return;
    }
    if (kppValidation) {
      setKppError(kppValidation);
      setError(kppValidation);
      return;
    }
    if (ogrnValidation) {
      setOgrnError(ogrnValidation);
      setError(ogrnValidation);
      return;
    }

    // Очищаем ошибки валидации
    setInnError(null);
    setKppError(null);
    setOgrnError(null);
    setError(null);

    try {
      setSaving(true);
      setSuccess(null);
      
      // Подготавливаем данные для отправки
      const dataToSend: any = {
        company_name: profile.company_name.trim(),
        contact_person: profile.contact_person?.trim() || '',
        phone: phoneDigits, // Отправляем только цифры, бэкенд сам отформатирует
        email: profile.email || '',
        address: profile.address?.trim() || '',
        inn: profile.inn?.replace(/\D/g, '') || null,
        kpp: profile.kpp?.replace(/\D/g, '') || null,
        ogrn: profile.ogrn?.replace(/\D/g, '') || null,
        equipment_brands: profile.equipment_brands || [],
        equipment_types: profile.equipment_types || [],
        mining_operations: profile.mining_operations || [],
        service_history: profile.service_history || '',
      };

      // Убираем null значения для необязательных полей
      if (!dataToSend.inn) delete dataToSend.inn;
      if (!dataToSend.kpp) delete dataToSend.kpp;
      if (!dataToSend.ogrn) delete dataToSend.ogrn;

      await apiService.updateCustomerProfile(dataToSend);
      setSuccess('Профиль компании успешно сохранен');
      
      // Перезагружаем профиль после сохранения
      setTimeout(async () => {
        try {
          await loadProfile();
        } catch (loadErr: any) {
          // Игнорируем ошибки при перезагрузке профиля после сохранения
          console.warn('Ошибка при перезагрузке профиля после сохранения:', loadErr);
        }
      }, 500);
      
    } catch (err: any) {
      console.error('Ошибка сохранения профиля:', err);
      
      // Обрабатываем разные форматы ошибок FastAPI
      let errorMessage = 'Ошибка сохранения профиля';
      
      if (err.response) {
        const errorData = err.response.data;
        
        // Если это объект с полями валидации (422)
        if (errorData && typeof errorData === 'object') {
          if (errorData.detail) {
            // Если detail - это массив ошибок валидации
            if (Array.isArray(errorData.detail)) {
              const validationErrors = errorData.detail
                .map((item: any) => {
                  if (typeof item === 'object' && item.msg) {
                    return `${item.loc?.join('.') || 'Поле'}: ${item.msg}`;
                  }
                  return String(item);
                })
                .join(', ');
              errorMessage = validationErrors || 'Ошибка валидации данных';
            } else {
              // Если detail - строка
              errorMessage = String(errorData.detail);
            }
          } else if (errorData.message) {
            errorMessage = String(errorData.message);
          }
        }
      } else if (err.message) {
        errorMessage = String(err.message);
      }
      
      setError(errorMessage);
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
                Техника и оборудование
              </Typography>
            </Grid>

            <Grid item xs={12}>
              <Autocomplete
                multiple
                options={EQUIPMENT_BRANDS}
                value={profile.equipment_brands || []}
                onChange={(event, newValue) => {
                  setProfile({ ...profile, equipment_brands: newValue });
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label='Бренды техники'
                    placeholder='Выберите бренды'
                  />
                )}
                renderTags={(value, getTagProps) =>
                  value.map((option, index) => (
                    <Chip
                      label={option}
                      {...getTagProps({ index })}
                      key={option}
                    />
                  ))
                }
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
                onChange={(e) => {
                  const value = e.target.value.replace(/\D/g, ''); // Только цифры
                  // Ограничиваем до 12 цифр (максимум для ИНН)
                  const limitedValue = value.slice(0, 12);
                  setProfile({ ...profile, inn: limitedValue });
                  setInnError(validateINN(limitedValue));
                }}
                error={!!innError}
                helperText={innError || '10 цифр (ЮЛ) или 12 цифр (ИП)'}
                inputProps={{
                  inputMode: 'numeric' as const,
                  maxLength: 12,
                }}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label='КПП'
                value={profile.kpp || ''}
                onChange={(e) => {
                  const value = e.target.value.replace(/\D/g, ''); // Только цифры
                  // Ограничиваем до 9 цифр
                  const limitedValue = value.slice(0, 9);
                  setProfile({ ...profile, kpp: limitedValue });
                  setKppError(validateKPP(limitedValue));
                }}
                error={!!kppError}
                helperText={kppError || '9 цифр'}
                inputProps={{
                  inputMode: 'numeric' as const,
                  maxLength: 9,
                }}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label='ОГРН'
                value={profile.ogrn || ''}
                onChange={(e) => {
                  const value = e.target.value.replace(/\D/g, ''); // Только цифры
                  // Ограничиваем до 15 цифр (максимум для ОГРН)
                  const limitedValue = value.slice(0, 15);
                  setProfile({ ...profile, ogrn: limitedValue });
                  setOgrnError(validateOGRN(limitedValue));
                }}
                error={!!ogrnError}
                helperText={ogrnError || '13 цифр (ЮЛ) или 15 цифр (ИП)'}
                inputProps={{
                  inputMode: 'numeric' as const,
                  maxLength: 15,
                }}
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

