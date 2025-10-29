import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Tooltip,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Avatar,
} from '@mui/material';
import {
  Security,
  CheckCircle,
  Cancel,
  Person,
  Assignment,
  TrendingUp,
  Warning,
  ExpandMore,
  Visibility,
  Edit,
  Block,
  Check,
  Star,
  Schedule,
  LocationOn,
  Business,
  Build,
} from '@mui/icons-material';
import { useAuth } from 'hooks/useAuth';
import { apiService } from 'services/api';

interface PendingVerification {
  id: number;
  contractor_id: number;
  verification_status?: string;
  overall_status?: string;
  verification_notes?: string;
  checked_by?: number;
  checked_at?: string;
  created_at: string;
  contractor?: {
    id: number;
    first_name?: string;
    last_name?: string;
    phone?: string;
    email?: string;
    specializations?: string[] | Array<{specialization: string; level: string}>;
    equipment_brands_experience?: string[];
    certifications?: string[];
    work_regions?: string[];
    hourly_rate?: number;
  };
}

interface SecurityStats {
  total_verifications: number;
  pending_count: number;
  approved_count: number;
  rejected_count: number;
  recent_verifications: number;
  avg_processing_time_hours: number;
  approval_rate: number;
}

interface ContractorDetails {
  contractor_id: number;
  user_id: number;
  personal_info: {
    first_name: string;
    last_name: string;
    patronymic?: string;
    phone: string;
    email: string;
    telegram_username?: string;
  };
  professional_info: {
    specializations: string[];
    equipment_brands_experience: string[];
    certifications: string[];
    work_regions: string[];
    hourly_rate?: number;
    availability_status: string;
  };
  verification_info: {
    status: string;
    created_at?: string;
    checked_at?: string;
    checked_by?: number;
    verification_notes?: string;
  };
  activity_info: {
    requests_count: number;
    registration_date: string;
    is_active: boolean;
  };
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role='tabpanel'
      hidden={value !== index}
      id={`security-tabpanel-${index}`}
      aria-labelledby={`security-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const SecurityVerificationPage: React.FC = () => {
  const { user } = useAuth();
  const [pendingVerifications, setPendingVerifications] = useState<
    PendingVerification[]
  >([]);
  const [verifiedContractors, setVerifiedContractors] = useState<any[]>([]);
  const [rejectedContractors, setRejectedContractors] = useState<any[]>([]);
  const [stats, setStats] = useState<SecurityStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState(0);

  // Диалоги
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [approvalDialogOpen, setApprovalDialogOpen] = useState(false);
  const [rejectionDialogOpen, setRejectionDialogOpen] = useState(false);
  const [selectedContractor, setSelectedContractor] =
    useState<ContractorDetails | null>(null);
  const [verificationNotes, setVerificationNotes] = useState('');
  const [rejectionReason, setRejectionReason] = useState('');

  useEffect(() => {
    loadSecurityData();
  }, []);

  const loadSecurityData = async () => {
    try {
      setLoading(true);

      const [pendingData, verifiedData, rejectedData, statsData] =
        await Promise.all([
          apiService.getPendingVerifications('security'),
          apiService.getVerifiedContractors(),
          apiService.getRejectedContractors(),
          apiService.getSecurityStatistics(),
        ]);

      setPendingVerifications(pendingData);
      setVerifiedContractors(verifiedData);
      setRejectedContractors(rejectedData);
      setStats(statsData);
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          'Ошибка загрузки данных службы безопасности',
      );
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = async (contractorId: number) => {
    try {
      const details = await apiService.getContractorProfileDetails(contractorId);
      // Преобразуем данные из ContractorProfileExtended в формат ContractorDetails
      const contractorDetails: ContractorDetails = {
        contractor_id: contractorId,
        user_id: details.user_id || 0,
        personal_info: {
          first_name: details.first_name || '',
          last_name: details.last_name || '',
          patronymic: details.patronymic,
          phone: details.phone || '',
          email: details.email || '',
          telegram_username: details.telegram_username,
        },
        professional_info: {
          specializations: (details.specializations || []).map((s: any) => 
            typeof s === 'string' ? s : s.specialization || ''
          ),
          equipment_brands_experience: details.equipment_brands_experience || [],
          certifications: details.certifications || [],
          work_regions: details.work_regions || [],
          hourly_rate: details.hourly_rate,
          availability_status: details.availability_status || 'unknown',
        },
        education_info: Array.isArray(details.education_records) ? details.education_records.map((ed: any) => ({
          institution_name: ed.institution_name || '',
          degree: ed.degree || '',
          field_of_study: ed.specialization || '',
          graduation_year: ed.graduation_year || 0,
        })) : [],
        experience_info: [],
        verification_info: {
          status: details.verification?.overall_status || 'pending',
          created_at: details.verification?.created_at,
          checked_at: details.verification?.security_checked_at,
          checked_by: details.verification?.security_checked_by,
          verification_notes: details.verification?.security_notes,
        },
        activity_info: {
          requests_count: 0,
          registration_date: details.created_at || '',
          is_active: true,
        },
      };
      setSelectedContractor(contractorDetails);
      setDetailsDialogOpen(true);
    } catch (err: any) {
      console.error('Ошибка загрузки деталей:', err);
      setError(
        err.response?.data?.detail || 'Ошибка загрузки деталей исполнителя',
      );
    }
  };

  const handleApproveContractor = async () => {
    if (!selectedContractor) return;

    try {
      await apiService.approveContractor(selectedContractor.contractor_id, {
        verification_notes: verificationNotes,
      });

      setApprovalDialogOpen(false);
      setVerificationNotes('');
      setSelectedContractor(null);
      await loadSecurityData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка одобрения исполнителя');
    }
  };

  const handleRejectContractor = async () => {
    if (!selectedContractor || !rejectionReason.trim()) return;

    try {
      await apiService.rejectContractor(selectedContractor.contractor_id, {
        verification_notes: rejectionReason,
      });

      setRejectionDialogOpen(false);
      setRejectionReason('');
      setSelectedContractor(null);
      await loadSecurityData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка отклонения исполнителя');
    }
  };

  const getStatusColor = (status: string) => {
    const colors: { [key: string]: string } = {
      pending: 'warning',
      approved: 'success',
      rejected: 'error',
      not_verified: 'default',
    };
    return colors[status] || 'default';
  };

  const getStatusText = (status: string) => {
    const texts: { [key: string]: string } = {
      pending: 'Ожидает проверки',
      approved: 'Одобрен',
      rejected: 'Отклонен',
      not_verified: 'Не проверен',
    };
    return texts[status] || status;
  };

  if (loading) {
    return (
      <Box
        display='flex'
        justifyContent='center'
        alignItems='center'
        minHeight='400px'
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant='h4' gutterBottom>
        Служба безопасности
      </Typography>

      {error && (
        <Alert severity='error' sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Статистика СБ */}
      {stats && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <Box>
                    <Typography variant='h4' component='div'>
                      {stats.total_verifications}
                    </Typography>
                    <Typography variant='body2' color='text.secondary'>
                      Всего проверок
                    </Typography>
                    <Typography variant='caption' color='text.secondary'>
                      За все время
                    </Typography>
                  </Box>
                  <Assignment sx={{ fontSize: 40, color: 'primary.main' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <Box>
                    <Typography variant='h4' component='div'>
                      {stats.pending_count}
                    </Typography>
                    <Typography variant='body2' color='text.secondary'>
                      Ожидают проверки
                    </Typography>
                    <Typography variant='caption' color='warning.main'>
                      Требуют внимания
                    </Typography>
                  </Box>
                  <Warning sx={{ fontSize: 40, color: 'warning.main' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <Box>
                    <Typography variant='h4' component='div'>
                      {stats.approved_count}
                    </Typography>
                    <Typography variant='body2' color='text.secondary'>
                      Одобрено
                    </Typography>
                    <Typography variant='caption' color='success.main'>
                      Проверены
                    </Typography>
                  </Box>
                  <CheckCircle sx={{ fontSize: 40, color: 'success.main' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <Box>
                    <Typography variant='h4' component='div'>
                      {stats.approval_rate}%
                    </Typography>
                    <Typography variant='body2' color='text.secondary'>
                      Процент одобрения
                    </Typography>
                    <Typography variant='caption' color='text.secondary'>
                      Эффективность
                    </Typography>
                  </Box>
                  <TrendingUp sx={{ fontSize: 40, color: 'info.main' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Табы */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs
          value={tabValue}
          onChange={(e, newValue) => setTabValue(newValue)}
        >
          <Tab label={`Ожидают проверки (${pendingVerifications.length})`} />
          <Tab label={`Одобренные (${verifiedContractors.length})`} />
          <Tab label={`Отклоненные (${rejectedContractors.length})`} />
        </Tabs>
      </Box>

      {/* Ожидают проверки */}
      <TabPanel value={tabValue} index={0}>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Исполнитель</TableCell>
                <TableCell>Контактная информация</TableCell>
                <TableCell>Специализации</TableCell>
                <TableCell>Оборудование</TableCell>
                <TableCell>Регионы работы</TableCell>
                <TableCell>Статус</TableCell>
                <TableCell>Дата подачи</TableCell>
                <TableCell>Действия</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {pendingVerifications.map(verification => (
                <TableRow key={verification.id || verification.contractor_id}>
                  <TableCell>
                    <Typography variant='subtitle2'>
                      {verification.contractor?.first_name || 'Не указано'}{' '}
                      {verification.contractor?.last_name || ''}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant='body2'>
                      {verification.contractor?.phone || 'Не указан'}
                    </Typography>
                    <Typography variant='body2' color='text.secondary'>
                      {verification.contractor?.email || 'Не указан'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {(() => {
                      const specs = verification.contractor?.specializations;
                      if (!specs || !Array.isArray(specs) || specs.length === 0) {
                        return <Typography variant="body2" color="text.secondary">Не указаны</Typography>;
                      }
                      
                      // Преобразуем в массив строк
                      const specLabels = specs.map((spec: any) => 
                        typeof spec === 'string' ? spec : (spec.specialization || spec)
                      );
                      
                      return (
                        <>
                          {specLabels.slice(0, 2).map((spec: string, idx: number) => (
                            <Chip
                              key={idx}
                              label={spec}
                              size='small'
                              sx={{ mr: 1, mb: 1 }}
                            />
                          ))}
                          {specLabels.length > 2 && (
                            <Chip
                              label={`+${specLabels.length - 2}`}
                              size='small'
                            />
                          )}
                        </>
                      );
                    })()}
                  </TableCell>
                  <TableCell>
                    {verification.contractor?.equipment_brands_experience
                      ?.slice(0, 2)
                      .map(brand => (
                        <Chip
                          key={brand}
                          label={brand}
                          size='small'
                          color='secondary'
                          sx={{ mr: 1, mb: 1 }}
                        />
                      ))}
                    {verification.contractor?.equipment_brands_experience &&
                      verification.contractor.equipment_brands_experience
                        .length > 2 && (
                        <Chip
                          label={`+${verification.contractor.equipment_brands_experience.length - 2}`}
                          size='small'
                          color='secondary'
                        />
                      )}
                  </TableCell>
                  <TableCell>
                    {verification.contractor?.work_regions
                      ?.slice(0, 2)
                      .map(region => (
                        <Chip
                          key={region}
                          label={region}
                          size='small'
                          color='info'
                          sx={{ mr: 1, mb: 1 }}
                        />
                      ))}
                    {verification.contractor?.work_regions &&
                      verification.contractor.work_regions.length > 2 && (
                        <Chip
                          label={`+${verification.contractor.work_regions.length - 2}`}
                          size='small'
                          color='info'
                        />
                      )}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={getStatusText(verification.verification_status || verification.overall_status || 'pending')}
                      color={
                        getStatusColor(verification.verification_status || verification.overall_status || 'pending') as any
                      }
                      size='small'
                    />
                  </TableCell>
                  <TableCell>
                    {verification.created_at ? new Date(verification.created_at).toLocaleDateString('ru-RU') : '-'}
                  </TableCell>
                  <TableCell>
                    <Tooltip title='Просмотреть детали'>
                      <IconButton
                        size='small'
                        onClick={() =>
                          handleViewDetails(verification.contractor_id)
                        }
                      >
                        <Visibility />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>

      {/* Одобренные */}
      <TabPanel value={tabValue} index={1}>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Исполнитель</TableCell>
                <TableCell>Контактная информация</TableCell>
                <TableCell>Специализации</TableCell>
                <TableCell>Оборудование</TableCell>
                <TableCell>Регионы работы</TableCell>
                <TableCell>Дата одобрения</TableCell>
                <TableCell>Действия</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {verifiedContractors.map(contractor => (
                <TableRow key={contractor.contractor_id}>
                  <TableCell>
                    <Typography variant='subtitle2'>
                      {contractor.name}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant='body2'>{contractor.phone}</Typography>
                    <Typography variant='body2' color='text.secondary'>
                      {contractor.email}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {contractor.specializations?.slice(0, 2).map(spec => (
                      <Chip
                        key={spec}
                        label={spec}
                        size='small'
                        sx={{ mr: 1, mb: 1 }}
                      />
                    ))}
                    {contractor.specializations &&
                      contractor.specializations.length > 2 && (
                        <Chip
                          label={`+${contractor.specializations.length - 2}`}
                          size='small'
                        />
                      )}
                  </TableCell>
                  <TableCell>
                    {contractor.equipment_brands_experience
                      ?.slice(0, 2)
                      .map(brand => (
                        <Chip
                          key={brand}
                          label={brand}
                          size='small'
                          color='secondary'
                          sx={{ mr: 1, mb: 1 }}
                        />
                      ))}
                    {contractor.equipment_brands_experience &&
                      contractor.equipment_brands_experience.length > 2 && (
                        <Chip
                          label={`+${contractor.equipment_brands_experience.length - 2}`}
                          size='small'
                          color='secondary'
                        />
                      )}
                  </TableCell>
                  <TableCell>
                    {contractor.work_regions?.slice(0, 2).map(region => (
                      <Chip
                        key={region}
                        label={region}
                        size='small'
                        color='info'
                        sx={{ mr: 1, mb: 1 }}
                      />
                    ))}
                    {contractor.work_regions &&
                      contractor.work_regions.length > 2 && (
                        <Chip
                          label={`+${contractor.work_regions.length - 2}`}
                          size='small'
                          color='info'
                        />
                      )}
                  </TableCell>
                  <TableCell>
                    {contractor.verified_at
                      ? new Date(contractor.verified_at).toLocaleDateString()
                      : 'Неизвестно'}
                  </TableCell>
                  <TableCell>
                    <Tooltip title='Просмотреть детали'>
                      <IconButton
                        size='small'
                        onClick={() =>
                          handleViewDetails(contractor.contractor_id)
                        }
                      >
                        <Visibility />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>

      {/* Отклоненные */}
      <TabPanel value={tabValue} index={2}>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Исполнитель</TableCell>
                <TableCell>Контактная информация</TableCell>
                <TableCell>Причина отклонения</TableCell>
                <TableCell>Дата отклонения</TableCell>
                <TableCell>Действия</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rejectedContractors.map(contractor => (
                <TableRow key={contractor.contractor_id}>
                  <TableCell>
                    <Typography variant='subtitle2'>
                      {contractor.name}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant='body2'>{contractor.phone}</Typography>
                    <Typography variant='body2' color='text.secondary'>
                      {contractor.email}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant='body2' color='error'>
                      {contractor.rejection_reason || 'Не указана'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {contractor.rejected_at
                      ? new Date(contractor.rejected_at).toLocaleDateString()
                      : 'Неизвестно'}
                  </TableCell>
                  <TableCell>
                    <Tooltip title='Просмотреть детали'>
                      <IconButton
                        size='small'
                        onClick={() =>
                          handleViewDetails(contractor.contractor_id)
                        }
                      >
                        <Visibility />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>

      {/* Диалог деталей исполнителя */}
      <Dialog
        open={detailsDialogOpen}
        onClose={() => setDetailsDialogOpen(false)}
        maxWidth='md'
        fullWidth
      >
        <DialogTitle>Детальная информация об исполнителе</DialogTitle>
        <DialogContent>
          {selectedContractor && (
            <Box>
              <Accordion defaultExpanded>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant='h6'>Личная информация</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <Typography variant='body2'>
                        <strong>ФИО:</strong>{' '}
                        {selectedContractor.personal_info.first_name}{' '}
                        {selectedContractor.personal_info.last_name}{' '}
                        {selectedContractor.personal_info.patronymic}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant='body2'>
                        <strong>Телефон:</strong>{' '}
                        {selectedContractor.personal_info.phone}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant='body2'>
                        <strong>Email:</strong>{' '}
                        {selectedContractor.personal_info.email}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant='body2'>
                        <strong>Telegram:</strong>{' '}
                        {selectedContractor.personal_info.telegram_username ||
                          'Не указан'}
                      </Typography>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant='h6'>
                    Профессиональная информация
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    <Grid item xs={12}>
                      <Typography variant='body2'>
                        <strong>Специализации:</strong>
                      </Typography>
                      <Box sx={{ mt: 1 }}>
                        {selectedContractor.professional_info.specializations.map(
                          spec => (
                            <Chip
                              key={spec}
                              label={spec}
                              size='small'
                              sx={{ mr: 1, mb: 1 }}
                            />
                          ),
                        )}
                      </Box>
                    </Grid>
                    <Grid item xs={12}>
                      <Typography variant='body2'>
                        <strong>Опыт с брендами:</strong>
                      </Typography>
                      <Box sx={{ mt: 1 }}>
                        {selectedContractor.professional_info.equipment_brands_experience.map(
                          brand => (
                            <Chip
                              key={brand}
                              label={brand}
                              size='small'
                              sx={{ mr: 1, mb: 1 }}
                            />
                          ),
                        )}
                      </Box>
                    </Grid>
                    <Grid item xs={12}>
                      <Typography variant='body2'>
                        <strong>Регионы работы:</strong>
                      </Typography>
                      <Box sx={{ mt: 1 }}>
                        {selectedContractor.professional_info.work_regions.map(
                          region => (
                            <Chip
                              key={region}
                              label={region}
                              size='small'
                              sx={{ mr: 1, mb: 1 }}
                            />
                          ),
                        )}
                      </Box>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant='body2'>
                        <strong>Почасовая ставка:</strong>{' '}
                        {selectedContractor.professional_info.hourly_rate ||
                          'Не указана'}{' '}
                        руб/час
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant='body2'>
                        <strong>Статус доступности:</strong>{' '}
                        {
                          selectedContractor.professional_info
                            .availability_status
                        }
                      </Typography>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant='h6'>Информация о проверке</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <Typography variant='body2'>
                        <strong>Статус:</strong>{' '}
                        {getStatusText(
                          selectedContractor.verification_info.status,
                        )}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant='body2'>
                        <strong>Дата подачи:</strong>{' '}
                        {selectedContractor.verification_info.created_at
                          ? new Date(
                              selectedContractor.verification_info.created_at,
                            ).toLocaleDateString()
                          : 'Неизвестно'}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant='body2'>
                        <strong>Дата проверки:</strong>{' '}
                        {selectedContractor.verification_info.checked_at
                          ? new Date(
                              selectedContractor.verification_info.checked_at,
                            ).toLocaleDateString()
                          : 'Не проверен'}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant='body2'>
                        <strong>Проверил:</strong>{' '}
                        {selectedContractor.verification_info.checked_by ||
                          'Неизвестно'}
                      </Typography>
                    </Grid>
                    {selectedContractor.verification_info
                      .verification_notes && (
                      <Grid item xs={12}>
                        <Typography variant='body2'>
                          <strong>Примечания:</strong>{' '}
                          {
                            selectedContractor.verification_info
                              .verification_notes
                          }
                        </Typography>
                      </Grid>
                    )}
                  </Grid>
                </AccordionDetails>
              </Accordion>

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant='h6'>Активность</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <Typography variant='body2'>
                        <strong>Количество заявок:</strong>{' '}
                        {selectedContractor.activity_info.requests_count}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant='body2'>
                        <strong>Дата регистрации:</strong>{' '}
                        {new Date(
                          selectedContractor.activity_info.registration_date,
                        ).toLocaleDateString()}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant='body2'>
                        <strong>Активен:</strong>{' '}
                        {selectedContractor.activity_info.is_active
                          ? 'Да'
                          : 'Нет'}
                      </Typography>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsDialogOpen(false)}>Закрыть</Button>
          {selectedContractor?.verification_info.status === 'pending' && (
            <>
              <Button
                color='error'
                onClick={() => {
                  setDetailsDialogOpen(false);
                  setRejectionDialogOpen(true);
                }}
                startIcon={<Cancel />}
              >
                Отклонить
              </Button>
              <Button
                color='success'
                onClick={() => {
                  setDetailsDialogOpen(false);
                  setApprovalDialogOpen(true);
                }}
                startIcon={<Check />}
              >
                Одобрить
              </Button>
            </>
          )}
        </DialogActions>
      </Dialog>

      {/* Диалог одобрения */}
      <Dialog
        open={approvalDialogOpen}
        onClose={() => setApprovalDialogOpen(false)}
        maxWidth='sm'
        fullWidth
      >
        <DialogTitle>Одобрить исполнителя</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            multiline
            rows={3}
            label='Примечания к одобрению'
            value={verificationNotes}
            onChange={e => setVerificationNotes(e.target.value)}
            placeholder='Дополнительные комментарии к одобрению...'
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setApprovalDialogOpen(false)}>Отмена</Button>
          <Button
            onClick={handleApproveContractor}
            variant='contained'
            color='success'
          >
            Одобрить
          </Button>
        </DialogActions>
      </Dialog>

      {/* Диалог отклонения */}
      <Dialog
        open={rejectionDialogOpen}
        onClose={() => setRejectionDialogOpen(false)}
        maxWidth='sm'
        fullWidth
      >
        <DialogTitle>Отклонить исполнителя</DialogTitle>
        <DialogContent>
          <Alert severity='warning' sx={{ mb: 2 }}>
            При отклонении исполнитель будет заблокирован и не сможет отвечать
            на заявки.
          </Alert>
          <TextField
            fullWidth
            multiline
            rows={3}
            label='Причина отклонения *'
            value={rejectionReason}
            onChange={e => setRejectionReason(e.target.value)}
            placeholder='Укажите причину отклонения...'
            required
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRejectionDialogOpen(false)}>Отмена</Button>
          <Button
            onClick={handleRejectContractor}
            variant='contained'
            color='error'
            disabled={!rejectionReason.trim()}
          >
            Отклонить
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SecurityVerificationPage;
