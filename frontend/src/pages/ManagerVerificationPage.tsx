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
  List,
  ListItem,
  ListItemText,
  IconButton,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Avatar,
} from '@mui/material';
import {
  People,
  CheckCircle,
  Cancel,
  ExpandMore,
  Visibility,
  Check,
  Schedule,
  LocationOn,
  Build,
  School,
  WorkHistory,
} from '@mui/icons-material';
import { useAuth } from 'hooks/useAuth';
import { apiService } from 'services/api';

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
  education_info: {
    institution_name: string;
    degree: string;
    field_of_study: string;
    graduation_year: number;
  }[];
  experience_info: {
    company_name: string;
    position: string;
    start_date: string;
    end_date?: string;
    responsibilities: string;
  }[];
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

const ManagerVerificationPage: React.FC = () => {
  const { user } = useAuth();
  const [pendingVerifications, setPendingVerifications] = useState<any[]>([]);
  const [verifiedContractors, setVerifiedContractors] = useState<any[]>([]);
  const [rejectedContractors, setRejectedContractors] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Диалоги
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [approvalDialogOpen, setApprovalDialogOpen] = useState(false);
  const [rejectionDialogOpen, setRejectionDialogOpen] = useState(false);
  const [selectedContractor, setSelectedContractor] = useState<ContractorDetails | null>(null);
  const [verificationNotes, setVerificationNotes] = useState('');
  const [rejectionReason, setRejectionReason] = useState('');

  useEffect(() => {
    loadManagerData();
  }, []);

  const loadManagerData = async () => {
    try {
      setLoading(true);
      
      // Загружаем данные о подтвержденных и отклоненных исполнителях
      const profiles = await apiService.getContractorProfiles();
      setPendingVerifications(profiles.filter((p: any) => !p.manager_verified));
      setVerifiedContractors(profiles.filter((p: any) => p.manager_verified));
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'Ошибка загрузки данных'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = async (contractorId: number) => {
    try {
      const details = await apiService.getContractorProfileDetails(contractorId);
      setSelectedContractor(details);
      setDetailsDialogOpen(true);
    } catch (err: any) {
      setError('Ошибка загрузки деталей исполнителя');
    }
  };

  const handleApprove = (contractorId: number) => {
    setSelectedContractor({ contractor_id: contractorId } as ContractorDetails);
    setVerificationNotes('');
    setApprovalDialogOpen(true);
  };

  const handleReject = (contractorId: number) => {
    setSelectedContractor({ contractor_id: contractorId } as ContractorDetails);
    setRejectionReason('');
    setRejectionDialogOpen(true);
  };

  const confirmApprove = async () => {
    if (!selectedContractor) return;

    try {
      await apiService.verifyContractorByManager(
        selectedContractor.contractor_id,
        verificationNotes
      );
      setApprovalDialogOpen(false);
      loadManagerData();
    } catch (err: any) {
      setError('Ошибка подтверждения исполнителя');
    }
  };

  const confirmReject = async () => {
    if (!selectedContractor) return;

    try {
      await apiService.rejectContractorByManager(
        selectedContractor.contractor_id,
        rejectionReason
      );
      setRejectionDialogOpen(false);
      loadManagerData();
    } catch (err: any) {
      setError('Ошибка отклонения исполнителя');
    }
  };

  if (loading) {
    return (
      <Box display='flex' justifyContent='center' alignItems='center' minHeight='400px'>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant='h4' gutterBottom>
        Подтверждение исполнителей
      </Typography>

      {error && (
        <Alert severity='error' sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3} sx={{ mt: 2 }}>
        {/* Статистика */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant='h6' gutterBottom>
                Ожидают подтверждения
              </Typography>
              <Typography variant='h3' color='warning.main'>
                {pendingVerifications.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant='h6' gutterBottom>
                Подтверждено
              </Typography>
              <Typography variant='h3' color='success.main'>
                {verifiedContractors.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant='h6' gutterBottom>
                Отклонено
              </Typography>
              <Typography variant='h3' color='error.main'>
                {rejectedContractors.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Ожидающие подтверждения */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant='h6' gutterBottom>
                Исполнители, ожидающие подтверждения
              </Typography>
              
              {pendingVerifications.length === 0 ? (
                <Typography color='text.secondary'>
                  Нет исполнителей, ожидающих подтверждения
                </Typography>
              ) : (
                <List>
                  {pendingVerifications.map((contractor) => (
                    <React.Fragment key={contractor.id}>
                      <ListItem>
                        <Avatar sx={{ mr: 2 }}>
                          {contractor.first_name?.[0]?.toUpperCase() || 'U'}
                        </Avatar>
                        <ListItemText
                          primary={`${contractor.first_name} ${contractor.last_name}`}
                          secondary={
                            <>
                              <Typography component='span' variant='body2'>
                                Email: {contractor.email}
                              </Typography>
                              <br />
                              <Typography component='span' variant='body2'>
                                Телефон: {contractor.phone}
                              </Typography>
                            </>
                          }
                        />
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Button
                            variant='outlined'
                            startIcon={<Visibility />}
                            onClick={() => handleViewDetails(contractor.id)}
                          >
                            Подробнее
                          </Button>
                          <Button
                            variant='contained'
                            color='success'
                            startIcon={<CheckCircle />}
                            onClick={() => handleApprove(contractor.id)}
                          >
                            Подтвердить
                          </Button>
                          <Button
                            variant='contained'
                            color='error'
                            startIcon={<Cancel />}
                            onClick={() => handleReject(contractor.id)}
                          >
                            Отклонить
                          </Button>
                        </Box>
                      </ListItem>
                      <Divider />
                    </React.Fragment>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Диалог подтверждения */}
      <Dialog open={approvalDialogOpen} onClose={() => setApprovalDialogOpen(false)} maxWidth='sm' fullWidth>
        <DialogTitle>Подтвердить исполнителя</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            multiline
            rows={4}
            label='Комментарий'
            value={verificationNotes}
            onChange={(e) => setVerificationNotes(e.target.value)}
            placeholder='Добавьте комментарий к подтверждению...'
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setApprovalDialogOpen(false)}>Отмена</Button>
          <Button onClick={confirmApprove} variant='contained' color='success'>
            Подтвердить
          </Button>
        </DialogActions>
      </Dialog>

      {/* Диалог отклонения */}
      <Dialog open={rejectionDialogOpen} onClose={() => setRejectionDialogOpen(false)} maxWidth='sm' fullWidth>
        <DialogTitle>Отклонить исполнителя</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            multiline
            rows={4}
            label='Причина отклонения'
            value={rejectionReason}
            onChange={(e) => setRejectionReason(e.target.value)}
            placeholder='Укажите причину отклонения...'
            sx={{ mt: 2 }}
            required
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRejectionDialogOpen(false)}>Отмена</Button>
          <Button onClick={confirmReject} variant='contained' color='error'>
            Отклонить
          </Button>
        </DialogActions>
      </Dialog>

      {/* Диалог деталей */}
      <Dialog open={detailsDialogOpen} onClose={() => setDetailsDialogOpen(false)} maxWidth='md' fullWidth>
        <DialogTitle>Детали исполнителя</DialogTitle>
        <DialogContent>
          {selectedContractor && (
            <Box>
              <Typography variant='h6' gutterBottom>
                Личная информация
              </Typography>
              <Typography>
                {selectedContractor.personal_info?.first_name}{' '}
                {selectedContractor.personal_info?.last_name}
              </Typography>
              <Typography>
                Email: {selectedContractor.personal_info?.email}
              </Typography>
              <Typography>
                Телефон: {selectedContractor.personal_info?.phone}
              </Typography>

              <Divider sx={{ my: 2 }} />

              <Typography variant='h6' gutterBottom>
                Образование
              </Typography>
              {selectedContractor.education_info?.length > 0 ? (
                selectedContractor.education_info.map((edu, idx) => (
                  <Box key={idx} sx={{ mb: 2 }}>
                    <Typography fontWeight='bold'>{edu.institution_name}</Typography>
                    <Typography>{edu.degree} - {edu.field_of_study}</Typography>
                    <Typography color='text.secondary'>
                      {edu.graduation_year}
                    </Typography>
                  </Box>
                ))
              ) : (
                <Typography color='text.secondary'>Нет данных об образовании</Typography>
              )}

              <Divider sx={{ my: 2 }} />

              <Typography variant='h6' gutterBottom>
                Опыт работы
              </Typography>
              {selectedContractor.experience_info?.length > 0 ? (
                selectedContractor.experience_info.map((exp, idx) => (
                  <Box key={idx} sx={{ mb: 2 }}>
                    <Typography fontWeight='bold'>{exp.company_name}</Typography>
                    <Typography>{exp.position}</Typography>
                    <Typography color='text.secondary'>
                      {exp.start_date} - {exp.end_date || 'По настоящее время'}
                    </Typography>
                    <Typography>{exp.responsibilities}</Typography>
                  </Box>
                ))
              ) : (
                <Typography color='text.secondary'>Нет данных об опыте работы</Typography>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsDialogOpen(false)}>Закрыть</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ManagerVerificationPage;

