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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextareaAutosize,
} from '@mui/material';
import {
  Description,
  Add,
  Download,
  Visibility,
  CheckCircle,
  Pending,
  Edit,
  ExpandMore,
  Person,
  Assignment,
  TrendingUp,
  FileDownload,
} from '@mui/icons-material';
import { useAuth } from 'hooks/useAuth';
import { apiService } from 'services/api';

interface VerifiedContractor {
  contractor_id: number;
  name: string;
  phone: string;
  email: string;
  specializations: string[];
  equipment_brands_experience: string[];
  work_regions: string[];
  hourly_rate?: number;
  availability_status: string;
  documents_count: number;
  pending_documents: number;
  completed_documents: number;
}

interface HRDocument {
  id: number;
  contractor_id: number;
  document_type: string;
  document_status: string;
  generated_by?: number;
  generated_at?: string;
  document_path?: string;
  created_at: string;
}

interface HRStats {
  total_documents: number;
  pending_count: number;
  generated_count: number;
  completed_count: number;
  recent_documents: number;
  avg_processing_time_hours: number;
  completion_rate: number;
  document_types: { [key: string]: number };
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
  security_verification: {
    status: string;
    verified_at?: string;
    verified_by?: number;
  };
  hr_documents: Array<{
    id: number;
    document_type: string;
    document_status: string;
    created_at: string;
    generated_at?: string;
    generated_by?: number;
  }>;
  activity_info: {
    registration_date: string;
    is_active: boolean;
  };
}

interface DocumentType {
  type: string;
  name: string;
  description: string;
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
      id={`hr-tabpanel-${index}`}
      aria-labelledby={`hr-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const HRDocumentsPage: React.FC = () => {
  const { user } = useAuth();
  const [verifiedContractors, setVerifiedContractors] = useState<
    VerifiedContractor[]
  >([]);
  const [contractorDocuments, setContractorDocuments] = useState<HRDocument[]>(
    [],
  );
  const [stats, setStats] = useState<HRStats | null>(null);
  const [documentTypes, setDocumentTypes] = useState<DocumentType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState(0);

  // Диалоги
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [createDocumentDialogOpen, setCreateDocumentDialogOpen] =
    useState(false);
  const [viewDocumentDialogOpen, setViewDocumentDialogOpen] = useState(false);
  const [selectedContractor, setSelectedContractor] =
    useState<ContractorDetails | null>(null);
  const [selectedDocument, setSelectedDocument] = useState<HRDocument | null>(
    null,
  );
  const [documentContent, setDocumentContent] = useState('');
  const [newDocumentType, setNewDocumentType] = useState('');
  const [customDocumentContent, setCustomDocumentContent] = useState('');

  useEffect(() => {
    loadHRData();
  }, []);

  const loadHRData = async () => {
    try {
      setLoading(true);

      const [contractorsData, statsData, typesData] = await Promise.all([
        apiService.getVerifiedContractorsForHR(),
        apiService.getHRStatistics(),
        apiService.getAvailableDocumentTypes(),
      ]);

      setVerifiedContractors(contractorsData);
      setStats(statsData);
      setDocumentTypes(typesData);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'Ошибка загрузки данных HR отдела',
      );
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = async (contractorId: number) => {
    try {
      const details = await apiService.getContractorDetailsForHR(contractorId);
      setSelectedContractor(details);
      setDetailsDialogOpen(true);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'Ошибка загрузки деталей исполнителя',
      );
    }
  };

  const handleViewDocuments = async (contractorId: number) => {
    try {
      const documents = await apiService.getContractorDocuments(contractorId);
      setContractorDocuments(documents);
      setTabValue(1); // Переключаемся на вкладку документов
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'Ошибка загрузки документов исполнителя',
      );
    }
  };

  const handleCreateDocument = async () => {
    if (!selectedContractor || !newDocumentType) return;

    try {
      await apiService.createDocumentRequest(selectedContractor.contractor_id, {
        document_type: newDocumentType,
      });

      setCreateDocumentDialogOpen(false);
      setNewDocumentType('');
      await loadHRData();
      await handleViewDocuments(selectedContractor.contractor_id);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка создания документа');
    }
  };

  const handleGenerateDocument = async (documentId: number) => {
    try {
      await apiService.generateDocument(documentId, {
        document_content: customDocumentContent || undefined,
      });

      await loadHRData();
      if (selectedContractor) {
        await handleViewDocuments(selectedContractor.contractor_id);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка генерации документа');
    }
  };

  const handleCompleteDocument = async (documentId: number) => {
    try {
      await apiService.completeDocument(documentId);

      await loadHRData();
      if (selectedContractor) {
        await handleViewDocuments(selectedContractor.contractor_id);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка завершения документа');
    }
  };

  const handleViewDocumentContent = async (documentId: number) => {
    try {
      const response = await apiService.getDocumentContent(documentId);
      setDocumentContent(response.content);
      setViewDocumentDialogOpen(true);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'Ошибка загрузки содержимого документа',
      );
    }
  };

  const handleDownloadDocument = async (documentId: number) => {
    try {
      const response = await apiService.downloadDocument(documentId);

      // Создаем blob и скачиваем файл
      const blob = new Blob([response], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `document_${documentId}.txt`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка скачивания документа');
    }
  };

  const getStatusColor = (status: string) => {
    const colors: { [key: string]: string } = {
      pending: 'warning',
      generated: 'info',
      completed: 'success',
    };
    return colors[status] || 'default';
  };

  const getStatusText = (status: string) => {
    const texts: { [key: string]: string } = {
      pending: 'Ожидает генерации',
      generated: 'Сгенерирован',
      completed: 'Завершен',
    };
    return texts[status] || status;
  };

  const getDocumentTypeName = (type: string) => {
    const docType = documentTypes.find(dt => dt.type === type);
    return docType ? docType.name : type;
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
        HR документы
      </Typography>

      {error && (
        <Alert severity='error' sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Статистика */}
      {stats && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display='flex' alignItems='center'>
                  <Description color='primary' sx={{ mr: 2 }} />
                  <Box>
                    <Typography variant='h4'>
                      {stats.total_documents}
                    </Typography>
                    <Typography color='text.secondary'>
                      Всего документов
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display='flex' alignItems='center'>
                  <Pending color='warning' sx={{ mr: 2 }} />
                  <Box>
                    <Typography variant='h4'>{stats.pending_count}</Typography>
                    <Typography color='text.secondary'>
                      Ожидают генерации
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display='flex' alignItems='center'>
                  <CheckCircle color='success' sx={{ mr: 2 }} />
                  <Box>
                    <Typography variant='h4'>
                      {stats.completed_count}
                    </Typography>
                    <Typography color='text.secondary'>Завершены</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display='flex' alignItems='center'>
                  <TrendingUp color='info' sx={{ mr: 2 }} />
                  <Box>
                    <Typography variant='h4'>
                      {stats.completion_rate}%
                    </Typography>
                    <Typography color='text.secondary'>
                      Процент завершения
                    </Typography>
                  </Box>
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
          <Tab
            label={`Проверенные исполнители (${verifiedContractors.length})`}
          />
          <Tab label={`Документы (${contractorDocuments.length})`} />
        </Tabs>
      </Box>

      {/* Проверенные исполнители */}
      <TabPanel value={tabValue} index={0}>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Исполнитель</TableCell>
                <TableCell>Контактная информация</TableCell>
                <TableCell>Специализации</TableCell>
                <TableCell>Документы</TableCell>
                <TableCell>Статус</TableCell>
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
                    {contractor.specializations && contractor.specializations.length > 0 ? (
                      <>
                        {contractor.specializations.slice(0, 2).map((spec: string | {specialization: string; level: string}, idx: number) => {
                          const specLabel = typeof spec === 'string' ? spec : spec.specialization || '';
                          const specKey = typeof spec === 'string' ? spec : `${spec.specialization}-${idx}`;
                          return (
                            <Chip
                              key={specKey}
                              label={specLabel}
                              size='small'
                              sx={{ mr: 1, mb: 1 }}
                            />
                          );
                        })}
                        {contractor.specializations.length > 2 && (
                          <Chip
                            label={`+${contractor.specializations.length - 2}`}
                            size='small'
                          />
                        )}
                      </>
                    ) : (
                      <Typography variant='body2' color='text.secondary'>
                        Не указано
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    <Typography variant='body2'>
                      Всего: {contractor.documents_count}
                    </Typography>
                    <Typography variant='body2' color='text.secondary'>
                      Ожидают: {contractor.pending_documents}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={
                        contractor.availability_status === 'available'
                          ? 'Доступен'
                          : 'Занят'
                      }
                      color={
                        contractor.availability_status === 'available'
                          ? 'success'
                          : 'warning'
                      }
                      size='small'
                    />
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
                    <Tooltip title='Документы'>
                      <IconButton
                        size='small'
                        onClick={() =>
                          handleViewDocuments(contractor.contractor_id)
                        }
                      >
                        <Description />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>

      {/* Документы */}
      <TabPanel value={tabValue} index={1}>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Тип документа</TableCell>
                <TableCell>Статус</TableCell>
                <TableCell>Дата создания</TableCell>
                <TableCell>Дата генерации</TableCell>
                <TableCell>Действия</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {contractorDocuments.map(document => (
                <TableRow key={document.id}>
                  <TableCell>
                    <Typography variant='subtitle2'>
                      {getDocumentTypeName(document.document_type)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={getStatusText(document.document_status)}
                      color={getStatusColor(document.document_status) as any}
                      size='small'
                    />
                  </TableCell>
                  <TableCell>
                    {new Date(document.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    {document.generated_at
                      ? new Date(document.generated_at).toLocaleDateString()
                      : '-'}
                  </TableCell>
                  <TableCell>
                    {document.document_status === 'pending' && (
                      <Tooltip title='Генерировать документ'>
                        <IconButton
                          size='small'
                          onClick={() => handleGenerateDocument(document.id)}
                        >
                          <Add />
                        </IconButton>
                      </Tooltip>
                    )}
                    {document.document_status === 'generated' && (
                      <>
                        <Tooltip title='Просмотреть содержимое'>
                          <IconButton
                            size='small'
                            onClick={() =>
                              handleViewDocumentContent(document.id)
                            }
                          >
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title='Скачать документ'>
                          <IconButton
                            size='small'
                            onClick={() => handleDownloadDocument(document.id)}
                          >
                            <FileDownload />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title='Завершить документ'>
                          <IconButton
                            size='small'
                            onClick={() => handleCompleteDocument(document.id)}
                          >
                            <CheckCircle />
                          </IconButton>
                        </Tooltip>
                      </>
                    )}
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
                        {selectedContractor.professional_info.specializations && selectedContractor.professional_info.specializations.length > 0 ? (
                          selectedContractor.professional_info.specializations.map(
                            (spec: string | {specialization: string; level: string}, idx: number) => {
                              const specLabel = typeof spec === 'string' ? spec : spec.specialization || '';
                              const specKey = typeof spec === 'string' ? spec : `${spec.specialization}-${idx}`;
                              return (
                                <Chip
                                  key={specKey}
                                  label={specLabel}
                                  size='small'
                                  sx={{ mr: 1, mb: 1 }}
                                />
                              );
                            }
                          )
                        ) : (
                          <Typography variant='body2' color='text.secondary'>
                            Не указано
                          </Typography>
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
                  <Typography variant='h6'>HR документы</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <List dense>
                    {selectedContractor.hr_documents.map(doc => (
                      <ListItem key={doc.id}>
                        <ListItemText
                          primary={getDocumentTypeName(doc.document_type)}
                          secondary={`Статус: ${getStatusText(doc.document_status)} • Создан: ${new Date(doc.created_at).toLocaleDateString()}`}
                        />
                        <ListItemSecondaryAction>
                          <Chip
                            label={getStatusText(doc.document_status)}
                            color={getStatusColor(doc.document_status) as any}
                            size='small'
                          />
                        </ListItemSecondaryAction>
                      </ListItem>
                    ))}
                  </List>
                </AccordionDetails>
              </Accordion>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsDialogOpen(false)}>Закрыть</Button>
          <Button
            variant='contained'
            onClick={() => {
              setDetailsDialogOpen(false);
              setCreateDocumentDialogOpen(true);
            }}
            startIcon={<Add />}
          >
            Создать документ
          </Button>
        </DialogActions>
      </Dialog>

      {/* Диалог создания документа */}
      <Dialog
        open={createDocumentDialogOpen}
        onClose={() => setCreateDocumentDialogOpen(false)}
        maxWidth='sm'
        fullWidth
      >
        <DialogTitle>Создать документ</DialogTitle>
        <DialogContent>
          <FormControl fullWidth margin='dense'>
            <InputLabel>Тип документа</InputLabel>
            <Select
              value={newDocumentType}
              onChange={e => setNewDocumentType(e.target.value)}
              label='Тип документа'
            >
              {documentTypes.map(type => (
                <MenuItem key={type.type} value={type.type}>
                  <Box>
                    <Typography variant='body2'>{type.name}</Typography>
                    <Typography variant='caption' color='text.secondary'>
                      {type.description}
                    </Typography>
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDocumentDialogOpen(false)}>
            Отмена
          </Button>
          <Button
            onClick={handleCreateDocument}
            variant='contained'
            disabled={!newDocumentType}
          >
            Создать
          </Button>
        </DialogActions>
      </Dialog>

      {/* Диалог просмотра содержимого документа */}
      <Dialog
        open={viewDocumentDialogOpen}
        onClose={() => setViewDocumentDialogOpen(false)}
        maxWidth='md'
        fullWidth
      >
        <DialogTitle>Содержимое документа</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            multiline
            rows={20}
            value={documentContent}
            InputProps={{
              readOnly: true,
            }}
            variant='outlined'
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDocumentDialogOpen(false)}>
            Закрыть
          </Button>
          <Button
            variant='contained'
            onClick={() => {
              const blob = new Blob([documentContent], { type: 'text/plain' });
              const url = window.URL.createObjectURL(blob);
              const link = document.createElement('a');
              link.href = url;
              link.download = `document_${selectedDocument?.id || 'content'}.txt`;
              document.body.appendChild(link);
              link.click();
              document.body.removeChild(link);
              window.URL.revokeObjectURL(url);
            }}
            startIcon={<FileDownload />}
          >
            Скачать
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default HRDocumentsPage;
