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
  Help as ClarifyIcon,
  Close as RejectIcon,
  CheckCircle as ApproveIcon,
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
    patronymic?: string;
    phone?: string;
    email?: string;
    inn?: string;
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
    passport_series?: string;
    passport_number?: string;
    passport_issued_by?: string;
    passport_issued_date?: string;
    passport_issued_code?: string;
    birth_date?: string;
    birth_place?: string;
    inn?: string;
  };
  professional_info: {
    specializations: string[];
    equipment_brands_experience: string[];
    certifications: string[];
    work_regions: string[];
    hourly_rate?: number;
    availability_status: string;
  };
  education_records?: Array<{
    id?: number;
    institution_name: string;
    specialization?: string;
    graduation_year?: number;
    degree?: string;
    diploma_number?: string;
  }>;
  documents?: Array<{
    id: number;
    document_name: string;
    document_type: string;
    document_path: string;
    verification_status: string;
  }>;
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
  const [clarificationDialogOpen, setClarificationDialogOpen] = useState(false);
  const [selectedContractor, setSelectedContractor] =
    useState<ContractorDetails | null>(null);
  const [verificationNotes, setVerificationNotes] = useState('');
  const [rejectionReason, setRejectionReason] = useState('');
  const [clarificationNotes, setClarificationNotes] = useState('');

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
          passport_series: details.passport_series,
          passport_number: details.passport_number,
          passport_issued_by: details.passport_issued_by,
          passport_issued_date: details.passport_issued_date,
          passport_issued_code: details.passport_issued_code,
          birth_date: details.birth_date,
          birth_place: details.birth_place,
          inn: details.inn,
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
        education_records: details.education_records || [],
        documents: details.documents || [],
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
      setDetailsDialogOpen(false);
      setVerificationNotes('');
      setSelectedContractor(null);
      await loadSecurityData();
      setError(null);
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
      setDetailsDialogOpen(false);
      setRejectionReason('');
      setSelectedContractor(null);
      await loadSecurityData();
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка отклонения исполнителя');
    }
  };

  const handleClarifyData = async () => {
    if (!selectedContractor || !clarificationNotes.trim()) return;

    try {
      await apiService.requestClarification(selectedContractor.contractor_id, {
        notes: clarificationNotes,
      });

      setClarificationDialogOpen(false);
      setDetailsDialogOpen(false);
      setClarificationNotes('');
      setSelectedContractor(null);
      await loadSecurityData();
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка запроса уточнения данных');
    }
  };

  const getStatusColor = (status: string) => {
    const colors: { [key: string]: string } = {
      pending: 'warning',
      approved: 'success',
      rejected: 'error',
      not_verified: 'default',
      incomplete: 'default',
      pending_security: 'warning',
      'pending-security': 'warning',
      pending_manager: 'info',
      'pending-manager': 'info',
    };
    return colors[status?.toLowerCase()] || 'default';
  };

  const getStatusText = (status: string) => {
    const texts: { [key: string]: string } = {
      pending: 'Ожидает проверки',
      approved: 'Одобрен',
      rejected: 'Отклонен',
      not_verified: 'Не проверен',
      incomplete: 'Не завершен',
      pending_security: 'Ожидает проверки СБ',
      pending_manager: 'Ожидает одобрения менеджера',
      approved: 'Одобрен',
    };
    // Если статус в формате "PENDING_SECURITY", преобразуем в lowercase
    const statusKey = status?.toLowerCase().replace('_', '') || '';
    return texts[status?.toLowerCase()] || texts[statusKey] || status || 'Неизвестно';
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
                <TableCell>ФИО</TableCell>
                <TableCell>ИНН</TableCell>
                <TableCell>Специализации</TableCell>
                <TableCell>Дата подачи</TableCell>
                <TableCell>Действия</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {pendingVerifications.map(verification => (
                <TableRow key={verification.id || verification.contractor_id}>
                  <TableCell>
                    <Typography variant='subtitle2'>
                      {verification.contractor?.last_name || ''}{' '}
                      {verification.contractor?.first_name || 'Не указано'}{' '}
                      {verification.contractor?.patronymic || ''}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant='body2'>
                      {verification.contractor?.inn || 'Не указан'}
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
                          {specLabels.slice(0, 3).map((spec: string, idx: number) => (
                            <Chip
                              key={idx}
                              label={spec}
                              size='small'
                              sx={{ mr: 0.5, mb: 0.5 }}
                            />
                          ))}
                          {specLabels.length > 3 && (
                            <Chip
                              label={`+${specLabels.length - 3}`}
                              size='small'
                            />
                          )}
                        </>
                      );
                    })()}
                  </TableCell>
                  <TableCell>
                    {verification.created_at ? new Date(verification.created_at).toLocaleDateString('ru-RU') : '-'}
                  </TableCell>
                  <TableCell>
                    <Box display="flex" gap={1} flexWrap="wrap">
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
                      {(!verification.security_check_passed && (verification.overall_status === 'pending_security' || verification.verification_status === 'pending')) && (
                        <>
                          <Tooltip title='Согласовать'>
                            <IconButton
                              size='small'
                              color='success'
                              onClick={() => {
                                setSelectedContractor({
                                  contractor_id: verification.contractor_id,
                                  user_id: verification.contractor?.id || 0,
                                  personal_info: {
                                    first_name: verification.contractor?.first_name || '',
                                    last_name: verification.contractor?.last_name || '',
                                    patronymic: verification.contractor?.patronymic,
                                    phone: verification.contractor?.phone || '',
                                    email: verification.contractor?.email || '',
                                  },
                                  professional_info: {
                                    specializations: [],
                                    equipment_brands_experience: [],
                                    certifications: [],
                                    work_regions: [],
                                    availability_status: 'unknown',
                                  },
                                  verification_info: {
                                    status: verification.overall_status || verification.verification_status || 'pending',
                                  },
                                  activity_info: {
                                    requests_count: 0,
                                    registration_date: verification.created_at || '',
                                    is_active: true,
                                  },
                                } as ContractorDetails);
                                setApprovalDialogOpen(true);
                              }}
                            >
                              <ApproveIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title='Уточнить данные'>
                            <IconButton
                              size='small'
                              color='warning'
                              onClick={() => {
                                setSelectedContractor({
                                  contractor_id: verification.contractor_id,
                                  user_id: verification.contractor?.id || 0,
                                  personal_info: {
                                    first_name: verification.contractor?.first_name || '',
                                    last_name: verification.contractor?.last_name || '',
                                    phone: verification.contractor?.phone || '',
                                    email: verification.contractor?.email || '',
                                  },
                                  professional_info: {
                                    specializations: [],
                                    equipment_brands_experience: [],
                                    certifications: [],
                                    work_regions: [],
                                    availability_status: 'unknown',
                                  },
                                  verification_info: {
                                    status: verification.overall_status || verification.verification_status || 'pending',
                                  },
                                  activity_info: {
                                    requests_count: 0,
                                    registration_date: verification.created_at || '',
                                    is_active: true,
                                  },
                                } as ContractorDetails);
                                setClarificationDialogOpen(true);
                              }}
                            >
                              <ClarifyIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title='Отклонить'>
                            <IconButton
                              size='small'
                              color='error'
                              onClick={() => {
                                setSelectedContractor({
                                  contractor_id: verification.contractor_id,
                                  user_id: verification.contractor?.id || 0,
                                  personal_info: {
                                    first_name: verification.contractor?.first_name || '',
                                    last_name: verification.contractor?.last_name || '',
                                    phone: verification.contractor?.phone || '',
                                    email: verification.contractor?.email || '',
                                  },
                                  professional_info: {
                                    specializations: [],
                                    equipment_brands_experience: [],
                                    certifications: [],
                                    work_regions: [],
                                    availability_status: 'unknown',
                                  },
                                  verification_info: {
                                    status: verification.overall_status || verification.verification_status || 'pending',
                                  },
                                  activity_info: {
                                    requests_count: 0,
                                    registration_date: verification.created_at || '',
                                    is_active: true,
                                  },
                                } as ContractorDetails);
                                setRejectionDialogOpen(true);
                              }}
                            >
                              <RejectIcon />
                            </IconButton>
                          </Tooltip>
                        </>
                      )}
                    </Box>
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
        maxWidth='lg'
        fullWidth
        PaperProps={{
          sx: {
            maxHeight: '90vh',
            overflow: 'auto'
          }
        }}
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
                        {selectedContractor.personal_info.last_name}{' '}
                        {selectedContractor.personal_info.first_name}{' '}
                        {selectedContractor.personal_info.patronymic || ''}
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
                    <Grid item xs={12} md={6}>
                      <Typography variant='body2'>
                        <strong>ИНН:</strong>{' '}
                        {selectedContractor.personal_info.inn || 'Не указан'}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant='body2'>
                        <strong>Дата рождения:</strong>{' '}
                        {selectedContractor.personal_info.birth_date
                          ? new Date(selectedContractor.personal_info.birth_date).toLocaleDateString('ru-RU')
                          : 'Не указана'}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant='body2'>
                        <strong>Место рождения:</strong>{' '}
                        {selectedContractor.personal_info.birth_place || 'Не указано'}
                      </Typography>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant='h6'>Паспортные данные</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <Typography variant='body2'>
                        <strong>Серия:</strong>{' '}
                        {selectedContractor.personal_info.passport_series || 'Не указана'}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant='body2'>
                        <strong>Номер:</strong>{' '}
                        {selectedContractor.personal_info.passport_number || 'Не указан'}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant='body2'>
                        <strong>Выдан:</strong>{' '}
                        {selectedContractor.personal_info.passport_issued_by || 'Не указано'}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant='body2'>
                        <strong>Дата выдачи:</strong>{' '}
                        {selectedContractor.personal_info.passport_issued_date
                          ? new Date(selectedContractor.personal_info.passport_issued_date).toLocaleDateString('ru-RU')
                          : 'Не указана'}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant='body2'>
                        <strong>Код подразделения:</strong>{' '}
                        {selectedContractor.personal_info.passport_issued_code || 'Не указан'}
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
                  <Typography variant='h6'>Образование</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  {selectedContractor.education_records && selectedContractor.education_records.length > 0 ? (
                    <Grid container spacing={2}>
                      {selectedContractor.education_records.map((edu, idx) => (
                        <Grid item xs={12} key={idx}>
                          <Box sx={{ p: 2, border: '1px solid #ddd', borderRadius: 1 }}>
                            <Typography variant='body1'><strong>{edu.institution_name}</strong></Typography>
                            <Typography variant='body2'>{edu.specialization || 'Не указана специальность'}</Typography>
                            <Typography variant='body2' color='text.secondary'>
                              Год окончания: {edu.graduation_year || 'Не указан'}
                            </Typography>
                            {edu.diploma_number && (
                              <Typography variant='body2' color='text.secondary'>
                                Номер диплома: {edu.diploma_number}
                              </Typography>
                            )}
                          </Box>
                        </Grid>
                      ))}
                    </Grid>
                  ) : (
                    <Typography variant='body2' color='text.secondary'>Нет данных об образовании</Typography>
                  )}
                </AccordionDetails>
              </Accordion>

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant='h6'>Документы</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  {selectedContractor.documents && selectedContractor.documents.length > 0 ? (
                    <Grid container spacing={2}>
                      {selectedContractor.documents.map((doc) => (
                        <Grid item xs={12} key={doc.id}>
                          <Box sx={{ p: 2, border: '1px solid #ddd', borderRadius: 1 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                              <Box sx={{ flex: 1, minWidth: 0 }}>
                                <Typography variant='body1'><strong>{doc.document_name}</strong></Typography>
                                <Typography variant='body2' color='text.secondary'>
                                Тип: {(() => {
                                  const typeMap: { [key: string]: string } = {
                                    'passport': 'Паспорт',
                                    'inn': 'ИНН',
                                    'safety_certificate': 'Сертификат ТБ',
                                    'education_diploma': 'Диплом об образовании',
                                    'work_experience': 'Справка о стаже',
                                    'other': 'Другое',
                                  };
                                  return typeMap[doc.document_type] || doc.document_type;
                                })()}
                              </Typography>
                              </Box>
                            </Box>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 1 }}>
                              <Chip
                                label={(() => {
                                  const statusMap: { [key: string]: string } = {
                                    'pending': 'Ожидает проверки',
                                    'approved': 'Одобрен',
                                    'rejected': 'Отклонен',
                                    'verified': 'Проверен',
                                    'not_verified': 'Не проверен',
                                  };
                                  return statusMap[doc.verification_status?.toLowerCase()] || doc.verification_status || 'Неизвестно';
                                })()}
                                size='small'
                                color={getStatusColor(doc.verification_status) as any}
                              />
                              <Button
                                variant='outlined'
                                size='small'
                                onClick={() => {
                                  let docPath = doc.document_path;
                                  if (docPath.startsWith('/app/uploads/')) {
                                    docPath = docPath.replace('/app/uploads/', '/uploads/');
                                  } else if (!docPath.startsWith('/uploads/')) {
                                    docPath = docPath.startsWith('uploads/') ? `/${docPath}` : `/uploads/${docPath}`;
                                  }
                                  const docUrl = `http://91.222.236.58:8000${docPath}`;
                                  window.open(docUrl, '_blank');
                                }}
                              >
                                Просмотреть
                              </Button>
                            </Box>
                          </Box>
                        </Grid>
                      ))}
                    </Grid>
                  ) : (
                    <Typography variant='body2' color='text.secondary'>Документы не загружены</Typography>
                  )}
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
                variant='contained'
                onClick={() => {
                  setDetailsDialogOpen(false);
                  setRejectionDialogOpen(true);
                }}
                startIcon={<RejectIcon />}
              >
                Отклонить
              </Button>
              <Button
                color='warning'
                variant='contained'
                onClick={() => {
                  setDetailsDialogOpen(false);
                  setClarificationDialogOpen(true);
                }}
                startIcon={<ClarifyIcon />}
              >
                Уточнить данные
              </Button>
              <Button
                color='success'
                variant='contained'
                onClick={() => {
                  setDetailsDialogOpen(false);
                  setApprovalDialogOpen(true);
                }}
                startIcon={<ApproveIcon />}
              >
                Согласовать
              </Button>
            </>
          )}
        </DialogActions>
      </Dialog>

      {/* Диалог уточнения данных */}
      <Dialog
        open={clarificationDialogOpen}
        onClose={() => setClarificationDialogOpen(false)}
        maxWidth='sm'
        fullWidth
      >
        <DialogTitle>Уточнить данные</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            multiline
            rows={5}
            label='Какие данные необходимо уточнить'
            value={clarificationNotes}
            onChange={(e) => setClarificationNotes(e.target.value)}
            sx={{ mt: 2 }}
            placeholder='Укажите, какие именно данные необходимо дополнить для проверки СБ...'
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setClarificationDialogOpen(false)}>Отмена</Button>
          <Button
            onClick={handleClarifyData}
            variant='contained'
            color='warning'
            disabled={!clarificationNotes.trim()}
          >
            Отправить запрос
          </Button>
        </DialogActions>
      </Dialog>

      {/* Диалог одобрения */}
      <Dialog
        open={approvalDialogOpen}
        onClose={() => setApprovalDialogOpen(false)}
        maxWidth='sm'
        fullWidth
      >
        <DialogTitle>Согласовать исполнителя</DialogTitle>
        <DialogContent>
          <Alert severity='success' sx={{ mb: 2 }}>
            Исполнителю будет отправлено письмо с подтверждением о том, что его профиль активен и он может просматривать и откликаться на заявки.
          </Alert>
          <TextField
            fullWidth
            multiline
            rows={3}
            label='Примечания (необязательно)'
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
            Согласовать
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
            После отклонения профиль исполнителя будет заблокирован, и ему будет отправлено уведомление на почту.
          </Alert>
          <TextField
            fullWidth
            multiline
            rows={4}
            label='Причина отклонения *'
            value={rejectionReason}
            onChange={e => setRejectionReason(e.target.value)}
            placeholder='Укажите причину отклонения профиля...'
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
