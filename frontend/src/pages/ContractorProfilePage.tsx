import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Divider,
  Stepper,
  Step,
  StepLabel,
  StepContent,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Upload as UploadIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { useForm, useFieldArray } from 'react-hook-form';
import { useAuth } from 'hooks/useAuth';
import { apiService } from 'services/api';
import DevelopmentBanner from 'components/common/DevelopmentBanner';

interface EducationRecord {
  id?: number;
  institution_name: string;
  degree: string;
  specialization: string;
  graduation_year?: number;
  diploma_number?: string;
  document_path?: string;
}

interface DocumentRecord {
  id?: number;
  document_type: string;
  document_name: string;
  document_path: string;
  verification_status: string;
  verification_notes?: string;
}

interface ContractorProfileForm {
  // Личные данные
  first_name: string;
  last_name: string;
  patronymic: string;
  phone: string;
  email: string;
  
  // Паспортные данные
  passport_series: string;
  passport_number: string;
  passport_issued_by: string;
  passport_issued_date: string;
  passport_issued_code: string;
  birth_date: string;
  birth_place: string;
  
  // ИНН
  inn: string;
  
  // Профессиональная информация
  specializations: string[];
  equipment_brands_experience: string[];
  certifications: string[];
  work_regions: string[];
  hourly_rate: number;
  general_description: string;
  
  // Контакты
  telegram_username: string;
  website: string;
  
  // Банковские данные
  bank_name: string;
  bank_account: string;
  bank_bik: string;
}

const ContractorProfilePage: React.FC = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [educationRecords, setEducationRecords] = useState<EducationRecord[]>([]);
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [verificationStatus, setVerificationStatus] = useState<string>('incomplete');
  const [activeStep, setActiveStep] = useState(0);
  
  // Диалоги
  const [educationDialogOpen, setEducationDialogOpen] = useState(false);
  const [documentDialogOpen, setDocumentDialogOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const {
    register,
    handleSubmit,
    control,
    setValue,
    watch,
    formState: { errors },
  } = useForm<any>({
    defaultValues: {
      specializations: [],
      equipment_brands_experience: [],
      certifications: [],
      work_regions: [],
    },
  });

  const { fields: specializationFields, append: appendSpecialization, remove: removeSpecialization } = useFieldArray({
    control,
    name: 'specializations',
  });

  const { fields: equipmentFields, append: appendEquipment, remove: removeEquipment } = useFieldArray({
    control,
    name: 'equipment_brands_experience',
  });

  const { fields: certificationFields, append: appendCertification, remove: removeCertification } = useFieldArray({
    control,
    name: 'certifications',
  });

  const { fields: regionFields, append: appendRegion, remove: removeRegion } = useFieldArray({
    control,
    name: 'work_regions',
  });

  useEffect(() => {
    if (user) {
      loadContractorProfile();
    }
  }, [user]);

  const loadContractorProfile = async () => {
    try {
      setLoading(true);
      
      // Используем apiService вместо прямого fetch
      const profile = await apiService.getContractorProfile() as any;
      
      // Заполняем форму данными профиля
      if (profile.first_name) setValue('first_name', profile.first_name);
      if (profile.last_name) setValue('last_name', profile.last_name);
      if (profile.patronymic) setValue('patronymic', profile.patronymic);
      if (profile.phone) setValue('phone', profile.phone);
      if (profile.email) setValue('email', profile.email);
      if (profile.passport_series) setValue('passport_series', profile.passport_series);
      if (profile.passport_number) setValue('passport_number', profile.passport_number);
      if (profile.passport_issued_by) setValue('passport_issued_by', profile.passport_issued_by);
      if (profile.passport_issued_date) setValue('passport_issued_date', profile.passport_issued_date);
      if (profile.passport_issued_code) setValue('passport_issued_code', profile.passport_issued_code);
      if (profile.birth_date) setValue('birth_date', profile.birth_date);
      if (profile.birth_place) setValue('birth_place', profile.birth_place);
      if (profile.inn) setValue('inn', profile.inn);
      if (profile.general_description) setValue('general_description', profile.general_description);
      if (profile.telegram_username) setValue('telegram_username', profile.telegram_username);
      if (profile.website) setValue('website', profile.website);
      if (profile.bank_account) setValue('bank_account', profile.bank_account);
      if (profile.bank_bik) setValue('bank_bik', profile.bank_bik);
      
    } catch (err: any) {
      console.error('Error loading contractor profile:', err);
      setError(err.response?.data?.detail || 'Ошибка загрузки профиля');
    } finally {
      setLoading(false);
    }
  };

  const onSubmit = async (data: ContractorProfileForm) => {
    try {
      setSaving(true);
      setError(null);
      
      console.log('Submitting profile data:', data);
      console.log('User contractor profile ID:', user?.contractor_profile_id);
      
      if (!user?.contractor_profile_id) {
        setError('Профиль исполнителя не найден');
        return;
      }
      
      await apiService.updateContractorProfile(user.contractor_profile_id, data);
      setSuccess('Профиль успешно обновлен!');
      
    } catch (err: any) {
      console.error('Error saving profile:', err);
      setError(err.response?.data?.detail || 'Ошибка сохранения профиля');
    } finally {
      setSaving(false);
    }
  };

  const addEducationRecord = async (educationData: EducationRecord) => {
    try {
      const newRecord = await apiService.addEducationRecord(user!.contractor_profile!.id, educationData);
      setEducationRecords([...educationRecords, newRecord]);
      setEducationDialogOpen(false);
      setSuccess('Запись об образовании добавлена!');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка добавления образования');
    }
  };

  const deleteEducationRecord = async (educationId: number) => {
    try {
      await apiService.deleteEducationRecord(educationId);
      setEducationRecords(educationRecords.filter(record => record.id !== educationId));
      setSuccess('Запись об образовании удалена!');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка удаления образования');
    }
  };

  const uploadDocument = async (documentType: string, documentName: string, file: File) => {
    try {
      const formData = new FormData();
      formData.append('document_type', documentType);
      formData.append('document_name', documentName);
      formData.append('file', file);
      
      const newDocument = await apiService.uploadContractorDocument(user!.contractor_profile!.id, formData);
      setDocuments([...documents, newDocument]);
      setDocumentDialogOpen(false);
      setSelectedFile(null);
      setSuccess('Документ загружен!');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка загрузки документа');
    }
  };

  const deleteDocument = async (documentId: number) => {
    try {
      await apiService.deleteContractorDocument(documentId);
      setDocuments(documents.filter(doc => doc.id !== documentId));
      setSuccess('Документ удален!');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка удаления документа');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'success';
      case 'pending': return 'warning';
      case 'rejected': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved': return <CheckCircleIcon />;
      case 'pending': return <WarningIcon />;
      case 'rejected': return <WarningIcon />;
      default: return <InfoIcon />;
    }
  };

  const steps = [
    {
      label: 'Личные данные',
      description: 'Основная информация о вас',
    },
    {
      label: 'Паспортные данные',
      description: 'Обязательно для проверки СБ',
    },
    {
      label: 'Образование',
      description: 'Ваше образование и квалификация',
    },
    {
      label: 'Документы',
      description: 'Загрузите необходимые документы',
    },
    {
      label: 'Профессиональная информация',
      description: 'Ваш опыт и специализация',
    },
  ];

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <DevelopmentBanner />
      
      <Typography variant="h4" component="h1" gutterBottom>
        Профиль исполнителя
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

      {/* Статус верификации */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={2}>
            <Typography variant="h6">Статус верификации:</Typography>
            <Chip
              label={verificationStatus}
              color={getStatusColor(verificationStatus) as any}
              icon={getStatusIcon(verificationStatus)}
            />
          </Box>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            {verificationStatus === 'incomplete' && 'Заполните все обязательные поля для начала проверки'}
            {verificationStatus === 'pending_security' && 'Профиль ожидает проверки службой безопасности'}
            {verificationStatus === 'pending_manager' && 'Профиль ожидает одобрения менеджера'}
            {verificationStatus === 'approved' && 'Профиль полностью верифицирован'}
            {verificationStatus === 'rejected' && 'Профиль отклонен, требуется доработка'}
          </Typography>
        </CardContent>
      </Card>

      <Paper sx={{ p: 3 }}>
        <Box component="form" onSubmit={handleSubmit(onSubmit)}>
          <Stepper activeStep={activeStep} orientation="vertical">
            {/* Шаг 1: Личные данные */}
            <Step>
              <StepLabel>Личные данные</StepLabel>
              <StepContent>
                <Grid container spacing={3}>
                  <Grid item xs={12} sm={4}>
                    <TextField
                      fullWidth
                      label="Фамилия *"
                      {...register('last_name', { required: 'Фамилия обязательна' })}
                      error={!!errors.last_name}
                      helperText={errors.last_name?.message as any}
                    />
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <TextField
                      fullWidth
                      label="Имя *"
                      {...register('first_name', { required: 'Имя обязательно' })}
                      error={!!errors.first_name}
                      helperText={errors.first_name?.message as any}
                    />
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <TextField
                      fullWidth
                      label="Отчество"
                      {...register('patronymic')}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Телефон *"
                      {...register('phone', { required: 'Телефон обязателен' })}
                      error={!!errors.phone}
                      helperText={errors.phone?.message as any}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Email *"
                      type="email"
                      {...register('email', { 
                        required: 'Email обязателен',
                        pattern: {
                          value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                          message: 'Некорректный формат email'
                        }
                      })}
                      error={!!errors.email}
                      helperText={errors.email?.message as any}
                    />
                  </Grid>
                </Grid>
                <Box sx={{ mt: 2 }}>
                  <Button
                    variant="contained"
                    onClick={() => setActiveStep(1)}
                  >
                    Далее
                  </Button>
                </Box>
              </StepContent>
            </Step>

            {/* Шаг 2: Паспортные данные */}
            <Step>
              <StepLabel>Паспортные данные</StepLabel>
              <StepContent>
                <Alert severity="info" sx={{ mb: 3 }}>
                  Паспортные данные и ИНН обязательны для проверки службой безопасности
                </Alert>
                <Grid container spacing={3}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Серия паспорта *"
                      {...register('passport_series', { required: 'Серия паспорта обязательна' })}
                      error={!!errors.passport_series}
                      helperText={errors.passport_series?.message as any}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Номер паспорта *"
                      {...register('passport_number', { required: 'Номер паспорта обязателен' })}
                      error={!!errors.passport_number}
                      helperText={errors.passport_number?.message as any}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Кем выдан *"
                      {...register('passport_issued_by', { required: 'Кем выдан обязателен' })}
                      error={!!errors.passport_issued_by}
                      helperText={errors.passport_issued_by?.message as any}
                    />
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <TextField
                      fullWidth
                      label="Дата выдачи *"
                      {...register('passport_issued_date', { required: 'Дата выдачи обязательна' })}
                      error={!!errors.passport_issued_date}
                      helperText={errors.passport_issued_date?.message as any}
                    />
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <TextField
                      fullWidth
                      label="Код подразделения *"
                      {...register('passport_issued_code', { required: 'Код подразделения обязателен' })}
                      error={!!errors.passport_issued_code}
                      helperText={errors.passport_issued_code?.message as any}
                    />
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <TextField
                      fullWidth
                      label="ИНН *"
                      {...register('inn', { required: 'ИНН обязателен' })}
                      error={!!errors.inn}
                      helperText={errors.inn?.message as any}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Дата рождения *"
                      {...register('birth_date', { required: 'Дата рождения обязательна' })}
                      error={!!errors.birth_date}
                      helperText={errors.birth_date?.message as any}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Место рождения *"
                      {...register('birth_place', { required: 'Место рождения обязательно' })}
                      error={!!errors.birth_place}
                      helperText={errors.birth_place?.message as any}
                    />
                  </Grid>
                </Grid>
                <Box sx={{ mt: 2 }}>
                  <Button
                    variant="outlined"
                    onClick={() => setActiveStep(0)}
                    sx={{ mr: 1 }}
                  >
                    Назад
                  </Button>
                  <Button
                    variant="contained"
                    onClick={() => setActiveStep(2)}
                  >
                    Далее
                  </Button>
                </Box>
              </StepContent>
            </Step>

            {/* Шаг 3: Образование */}
            <Step>
              <StepLabel>Образование</StepLabel>
              <StepContent>
                <Box sx={{ mb: 3 }}>
                  <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={() => setEducationDialogOpen(true)}
                  >
                    Добавить образование
                  </Button>
                </Box>
                
                {educationRecords.map((record, index) => (
                  <Card key={record.id || index} sx={{ mb: 2 }}>
                    <CardContent>
                      <Typography variant="h6">{record.institution_name}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {record.degree} - {record.specialization}
                      </Typography>
                      {record.graduation_year && (
                        <Typography variant="body2">
                          Год окончания: {record.graduation_year}
                        </Typography>
                      )}
                    </CardContent>
                    <CardActions>
                      <IconButton
                        color="error"
                        onClick={() => record.id && deleteEducationRecord(record.id)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </CardActions>
                  </Card>
                ))}
                
                <Box sx={{ mt: 2 }}>
                  <Button
                    variant="outlined"
                    onClick={() => setActiveStep(1)}
                    sx={{ mr: 1 }}
                  >
                    Назад
                  </Button>
                  <Button
                    variant="contained"
                    onClick={() => setActiveStep(3)}
                  >
                    Далее
                  </Button>
                </Box>
              </StepContent>
            </Step>

            {/* Шаг 4: Документы */}
            <Step>
              <StepLabel>Документы</StepLabel>
              <StepContent>
                <Alert severity="info" sx={{ mb: 3 }}>
                  Загрузите копии документов для проверки. Поддерживаются форматы: PDF, JPG, PNG, DOC, DOCX
                </Alert>
                
                <Box sx={{ mb: 3 }}>
                  <Button
                    variant="contained"
                    startIcon={<UploadIcon />}
                    onClick={() => setDocumentDialogOpen(true)}
                  >
                    Загрузить документ
                  </Button>
                </Box>
                
                {documents.map((doc, index) => (
                  <Card key={doc.id || index} sx={{ mb: 2 }}>
                    <CardContent>
                      <Box display="flex" alignItems="center" gap={2}>
                        <Typography variant="h6">{doc.document_name}</Typography>
                        <Chip
                          label={doc.verification_status}
                          color={getStatusColor(doc.verification_status) as any}
                          size="small"
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary">
                        Тип: {doc.document_type}
                      </Typography>
                      {doc.verification_notes && (
                        <Typography variant="body2" color="text.secondary">
                          Комментарий: {doc.verification_notes}
                        </Typography>
                      )}
                    </CardContent>
                    <CardActions>
                      <IconButton
                        color="error"
                        onClick={() => doc.id && deleteDocument(doc.id)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </CardActions>
                  </Card>
                ))}
                
                <Box sx={{ mt: 2 }}>
                  <Button
                    variant="outlined"
                    onClick={() => setActiveStep(2)}
                    sx={{ mr: 1 }}
                  >
                    Назад
                  </Button>
                  <Button
                    variant="contained"
                    onClick={() => setActiveStep(4)}
                  >
                    Далее
                  </Button>
                </Box>
              </StepContent>
            </Step>

            {/* Шаг 5: Профессиональная информация */}
            <Step>
              <StepLabel>Профессиональная информация</StepLabel>
              <StepContent>
                <Grid container spacing={3}>
                  <Grid item xs={12}>
                    <Typography variant="h6" gutterBottom>
                      Специализации
                    </Typography>
                    {specializationFields.map((field, index) => (
                      <Box key={field.id} display="flex" alignItems="center" gap={1} sx={{ mb: 1 }}>
                        <TextField
                          fullWidth
                          {...register(`specializations.${index}` as const)}
                          placeholder="Введите специализацию"
                        />
                        <IconButton onClick={() => removeSpecialization(index)}>
                          <DeleteIcon />
                        </IconButton>
                      </Box>
                    ))}
                    <Button
                      variant="outlined"
                      startIcon={<AddIcon />}
                      onClick={() => appendSpecialization('')}
                    >
                      Добавить специализацию
                    </Button>
                  </Grid>
                  
                  <Grid item xs={12}>
                    <Typography variant="h6" gutterBottom>
                      Опыт с брендами оборудования
                    </Typography>
                    {equipmentFields.map((field, index) => (
                      <Box key={field.id} display="flex" alignItems="center" gap={1} sx={{ mb: 1 }}>
                        <TextField
                          fullWidth
                          {...register(`equipment_brands_experience.${index}` as const)}
                          placeholder="Введите бренд оборудования"
                        />
                        <IconButton onClick={() => removeEquipment(index)}>
                          <DeleteIcon />
                        </IconButton>
                      </Box>
                    ))}
                    <Button
                      variant="outlined"
                      startIcon={<AddIcon />}
                      onClick={() => appendEquipment('')}
                    >
                      Добавить бренд
                    </Button>
                  </Grid>
                  
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      multiline
                      rows={4}
                      label="Общее описание"
                      {...register('general_description')}
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Почасовая ставка"
                      type="number"
                      {...register('hourly_rate', { valueAsNumber: true })}
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Telegram"
                      {...register('telegram_username')}
                    />
                  </Grid>
                </Grid>
                
                <Box sx={{ mt: 2 }}>
                  <Button
                    variant="outlined"
                    onClick={() => setActiveStep(3)}
                    sx={{ mr: 1 }}
                  >
                    Назад
                  </Button>
                  <Button
                    type="submit"
                    variant="contained"
                    disabled={saving}
                  >
                    {saving ? <CircularProgress size={24} /> : 'Сохранить профиль'}
                  </Button>
                </Box>
              </StepContent>
            </Step>
          </Stepper>
        </Box>
      </Paper>

      {/* Диалог добавления образования */}
      <Dialog open={educationDialogOpen} onClose={() => setEducationDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Добавить образование</DialogTitle>
        <DialogContent>
          <EducationForm onSubmit={addEducationRecord} />
        </DialogContent>
      </Dialog>

      {/* Диалог загрузки документа */}
      <Dialog open={documentDialogOpen} onClose={() => setDocumentDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Загрузить документ</DialogTitle>
        <DialogContent>
          <DocumentUploadForm onSubmit={uploadDocument} />
        </DialogContent>
      </Dialog>
    </Container>
  );
};

// Компонент формы образования
const EducationForm: React.FC<{ onSubmit: (data: EducationRecord) => void }> = ({ onSubmit }) => {
  const { register, handleSubmit, formState: { errors } } = useForm<EducationRecord>();

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)}>
      <TextField
        fullWidth
        label="Название учебного заведения *"
        {...register('institution_name', { required: 'Название обязательно' })}
        error={!!errors.institution_name}
        helperText={errors.institution_name?.message as any}
        sx={{ mb: 2 }}
      />
      <TextField
        fullWidth
        label="Степень/квалификация *"
        {...register('degree', { required: 'Степень обязательна' })}
        error={!!errors.degree}
        helperText={errors.degree?.message as any}
        sx={{ mb: 2 }}
      />
      <TextField
        fullWidth
        label="Специализация *"
        {...register('specialization', { required: 'Специализация обязательна' })}
        error={!!errors.specialization}
        helperText={errors.specialization?.message as any}
        sx={{ mb: 2 }}
      />
      <TextField
        fullWidth
        label="Год окончания"
        type="number"
        {...register('graduation_year', { valueAsNumber: true })}
        sx={{ mb: 2 }}
      />
      <TextField
        fullWidth
        label="Номер диплома"
        {...register('diploma_number')}
        sx={{ mb: 2 }}
      />
      <DialogActions>
        <Button type="submit" variant="contained">
          Добавить
        </Button>
      </DialogActions>
    </Box>
  );
};

// Компонент загрузки документа
const DocumentUploadForm: React.FC<{ onSubmit: (type: string, name: string, file: File) => void }> = ({ onSubmit }) => {
  const [documentType, setDocumentType] = useState('');
  const [documentName, setDocumentName] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      if (!documentName) {
        setDocumentName(file.name);
      }
    }
  };

  const handleSubmit = () => {
    if (documentType && documentName && selectedFile) {
      onSubmit(documentType, documentName, selectedFile);
    }
  };

  return (
    <Box>
      <FormControl fullWidth sx={{ mb: 2 }}>
        <InputLabel>Тип документа *</InputLabel>
        <Select
          value={documentType}
          onChange={(e) => setDocumentType(e.target.value)}
          label="Тип документа *"
        >
          <MenuItem value="passport">Паспорт</MenuItem>
          <MenuItem value="inn">ИНН</MenuItem>
          <MenuItem value="safety_certificate">Сертификат ТБ</MenuItem>
          <MenuItem value="education_diploma">Диплом об образовании</MenuItem>
          <MenuItem value="work_experience">Справка о стаже</MenuItem>
          <MenuItem value="other">Другое</MenuItem>
        </Select>
      </FormControl>
      
      <TextField
        fullWidth
        label="Название документа *"
        value={documentName}
        onChange={(e) => setDocumentName(e.target.value)}
        sx={{ mb: 2 }}
      />
      
      <input
        type="file"
        accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
        onChange={handleFileChange}
        style={{ marginBottom: '16px' }}
      />
      
      {selectedFile && (
        <Typography variant="body2" color="text.secondary">
          Выбран файл: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
        </Typography>
      )}
      
      <DialogActions>
        <Button onClick={handleSubmit} variant="contained" disabled={!documentType || !documentName || !selectedFile}>
          Загрузить
        </Button>
      </DialogActions>
    </Box>
  );
};

export default ContractorProfilePage;
