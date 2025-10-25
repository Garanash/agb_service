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
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Tooltip,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextareaAutosize,
} from '@mui/material';
import {
  Telegram,
  Send,
  Notifications,
  CheckCircle,
  Error,
  Info,
  Person,
  Assignment,
  Message,
  Settings,
} from '@mui/icons-material';
import { useAuth } from 'hooks/useAuth';
import { apiService } from 'services/api';
import ChatHistoryDialog from '../components/ChatHistoryDialog';

interface BotInfo {
  bot_configured: boolean;
  bot_info?: {
    id: number;
    username: string;
    first_name: string;
    can_join_groups: boolean;
    can_read_all_group_messages: boolean;
  };
  chat_configured: boolean;
  error?: string;
}

interface VerifiedContractor {
  contractor_id: number;
  name: string;
  telegram_username: string;
  phone: string;
  email: string;
  specializations: string[];
  availability_status: string;
}

interface BulkNotificationResult {
  total: number;
  successful: number;
  failed: number;
  errors: string[];
}

const TelegramBotPage: React.FC = () => {
  const { user } = useAuth();
  const [botInfo, setBotInfo] = useState<BotInfo | null>(null);
  const [verifiedContractors, setVerifiedContractors] = useState<
    VerifiedContractor[]
  >([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Диалоги
  const [notificationDialogOpen, setNotificationDialogOpen] = useState(false);
  const [bulkNotificationDialogOpen, setBulkNotificationDialogOpen] =
    useState(false);
  const [testDialogOpen, setTestDialogOpen] = useState(false);
  const [selectedContractor, setSelectedContractor] =
    useState<VerifiedContractor | null>(null);
  const [notificationMessage, setNotificationMessage] = useState('');
  const [bulkMessage, setBulkMessage] = useState('');
  const [selectedContractors, setSelectedContractors] = useState<number[]>([]);
  const [testResult, setTestResult] = useState<any>(null);

  // Состояние для истории чата
  const [chatHistoryOpen, setChatHistoryOpen] = useState(false);
  const [selectedTelegramUser, setSelectedTelegramUser] = useState<any>(null);
  const [unreadCounts, setUnreadCounts] = useState<any[]>([]);

  useEffect(() => {
    loadTelegramData();
  }, []);

  const loadTelegramData = async () => {
    try {
      setLoading(true);

      const [botInfoData, contractorsData, unreadData] = await Promise.all([
        apiService.getBotInfo(),
        apiService.getVerifiedContractorsForNotifications(),
        apiService.getUnreadCounts(),
      ]);

      setBotInfo(botInfoData);
      setVerifiedContractors(contractorsData);
      setUnreadCounts(unreadData.unread_counts || []);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'Ошибка загрузки данных Telegram бота',
      );
    } finally {
      setLoading(false);
    }
  };

  const handleOpenChatHistory = (contractor: VerifiedContractor) => {
    // Создаем объект telegram пользователя из данных исполнителя
    const telegramUser = {
      id: contractor.contractor_id,
      username: contractor.telegram_username,
      first_name: contractor.name.split(' ')[0] || '',
      last_name: contractor.name.split(' ').slice(1).join(' ') || '',
    };
    
    setSelectedTelegramUser(telegramUser);
    setChatHistoryOpen(true);
  };

  const handleCloseChatHistory = () => {
    setChatHistoryOpen(false);
    setSelectedTelegramUser(null);
    // Перезагружаем данные для обновления счетчиков
    loadTelegramData();
  };

  const getUnreadCountForContractor = (contractorId: number) => {
    const unreadData = unreadCounts.find(item => item.telegram_user_id === contractorId);
    return unreadData ? unreadData.unread_count : 0;
  };

  const handleSendNotification = async () => {
    if (!selectedContractor || !notificationMessage.trim()) return;

    try {
      await apiService.sendNotificationToContractor(
        selectedContractor.contractor_id,
        {
          message: notificationMessage,
        },
      );

      setNotificationDialogOpen(false);
      setNotificationMessage('');
      setSelectedContractor(null);
      setSuccess(
        `Уведомление отправлено исполнителю ${selectedContractor.name}`,
      );
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка отправки уведомления');
    }
  };

  const handleSendBulkNotification = async () => {
    if (!bulkMessage.trim()) return;

    try {
      const result: BulkNotificationResult =
        await apiService.sendBulkNotification({
          message: bulkMessage,
          contractor_ids:
            selectedContractors.length > 0 ? selectedContractors : undefined,
        });

      setBulkNotificationDialogOpen(false);
      setBulkMessage('');
      setSelectedContractors([]);
      setSuccess(
        `Массовая отправка завершена: ${result.successful}/${result.total} успешно`,
      );
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка массовой отправки');
    }
  };

  const handleTestConnection = async () => {
    try {
      const result = await apiService.testTelegramBotConnection();
      setTestResult(result);
      setTestDialogOpen(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка тестирования подключения');
    }
  };

  const getStatusColor = (status: string) => {
    const colors: { [key: string]: string } = {
      available: 'success',
      busy: 'warning',
      blocked: 'error',
    };
    return colors[status] || 'default';
  };

  const getStatusText = (status: string) => {
    const texts: { [key: string]: string } = {
      available: 'Доступен',
      busy: 'Занят',
      blocked: 'Заблокирован',
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
        Telegram бот
      </Typography>

      {error && (
        <Alert severity='error' sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert
          severity='success'
          sx={{ mb: 2 }}
          onClose={() => setSuccess(null)}
        >
          {success}
        </Alert>
      )}

      {/* Статус бота */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box
            display='flex'
            alignItems='center'
            justifyContent='space-between'
          >
            <Box display='flex' alignItems='center'>
              <Telegram
                color={botInfo?.bot_configured ? 'success' : 'error'}
                sx={{ mr: 2 }}
              />
              <Box>
                <Typography variant='h6'>Статус Telegram бота</Typography>
                <Typography variant='body2' color='text.secondary'>
                  {botInfo?.bot_configured
                    ? 'Настроен и готов к работе'
                    : 'Не настроен'}
                </Typography>
              </Box>
            </Box>
            <Box display='flex' gap={1}>
              <Button
                variant='outlined'
                startIcon={<Settings />}
                onClick={handleTestConnection}
              >
                Тестировать подключение
              </Button>
              <Button
                variant='contained'
                startIcon={<Notifications />}
                onClick={() => setBulkNotificationDialogOpen(true)}
                disabled={!botInfo?.bot_configured}
              >
                Массовая отправка
              </Button>
            </Box>
          </Box>

          {botInfo?.bot_info && (
            <Box sx={{ mt: 2 }}>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant='body2'>
                    <strong>Имя бота:</strong> {botInfo.bot_info.first_name}
                  </Typography>
                  <Typography variant='body2'>
                    <strong>Username:</strong> @{botInfo.bot_info.username}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant='body2'>
                    <strong>ID:</strong> {botInfo.bot_info.id}
                  </Typography>
                  <Typography variant='body2'>
                    <strong>Чат настроен:</strong>{' '}
                    {botInfo.chat_configured ? 'Да' : 'Нет'}
                  </Typography>
                </Grid>
              </Grid>
            </Box>
          )}

          {botInfo?.error && (
            <Alert severity='error' sx={{ mt: 2 }}>
              {botInfo.error}
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Проверенные исполнители */}
      <Card>
        <CardContent>
          <Box
            display='flex'
            alignItems='center'
            justifyContent='space-between'
            mb={2}
          >
            <Typography variant='h6'>
              Исполнители с Telegram ({verifiedContractors.length})
            </Typography>
            <Button
              variant='outlined'
              startIcon={<Message />}
              onClick={() => setBulkNotificationDialogOpen(true)}
              disabled={verifiedContractors.length === 0}
            >
              Отправить всем
            </Button>
          </Box>

          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Исполнитель</TableCell>
                  <TableCell>Telegram</TableCell>
                  <TableCell>Контактная информация</TableCell>
                  <TableCell>Специализации</TableCell>
                  <TableCell>Статус</TableCell>
                  <TableCell>Действия</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {verifiedContractors.map(contractor => (
                  <TableRow key={contractor.contractor_id}>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant='subtitle2'>
                          {contractor.name}
                        </Typography>
                        {getUnreadCountForContractor(contractor.contractor_id) > 0 && (
                          <Box
                            sx={{
                              width: 20,
                              height: 20,
                              bgcolor: 'error.main',
                              borderRadius: '50%',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              color: 'white',
                              fontSize: '12px',
                              fontWeight: 'bold',
                            }}
                          >
                            {getUnreadCountForContractor(contractor.contractor_id)}
                          </Box>
                        )}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant='body2'>
                        @{contractor.telegram_username}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant='body2'>
                        {contractor.phone}
                      </Typography>
                      <Typography variant='body2' color='text.secondary'>
                        {contractor.email}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {contractor.specializations.slice(0, 2).map(spec => (
                        <Chip
                          key={spec}
                          label={spec}
                          size='small'
                          sx={{ mr: 1, mb: 1 }}
                        />
                      ))}
                      {contractor.specializations.length > 2 && (
                        <Chip
                          label={`+${contractor.specializations.length - 2}`}
                          size='small'
                        />
                      )}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={getStatusText(contractor.availability_status)}
                        color={
                          getStatusColor(contractor.availability_status) as any
                        }
                        size='small'
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Tooltip title='История переписки'>
                          <IconButton
                            size='small'
                            onClick={() => handleOpenChatHistory(contractor)}
                          >
                            <Message />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title='Отправить уведомление'>
                          <IconButton
                            size='small'
                            onClick={() => {
                              setSelectedContractor(contractor);
                              setNotificationDialogOpen(true);
                            }}
                          >
                            <Send />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Диалог отправки уведомления */}
      <Dialog
        open={notificationDialogOpen}
        onClose={() => setNotificationDialogOpen(false)}
        maxWidth='md'
        fullWidth
      >
        <DialogTitle>Отправить уведомление</DialogTitle>
        <DialogContent>
          {selectedContractor && (
            <Box sx={{ mb: 2 }}>
              <Typography variant='subtitle1' gutterBottom>
                Исполнитель: {selectedContractor.name}
              </Typography>
              <Typography variant='body2' color='text.secondary'>
                Telegram: @{selectedContractor.telegram_username}
              </Typography>
            </Box>
          )}

          <TextField
            fullWidth
            multiline
            rows={4}
            label='Сообщение'
            value={notificationMessage}
            onChange={e => setNotificationMessage(e.target.value)}
            placeholder='Введите текст уведомления...'
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNotificationDialogOpen(false)}>
            Отмена
          </Button>
          <Button
            onClick={handleSendNotification}
            variant='contained'
            disabled={!notificationMessage.trim()}
          >
            Отправить
          </Button>
        </DialogActions>
      </Dialog>

      {/* Диалог массовой отправки */}
      <Dialog
        open={bulkNotificationDialogOpen}
        onClose={() => setBulkNotificationDialogOpen(false)}
        maxWidth='md'
        fullWidth
      >
        <DialogTitle>Массовая отправка уведомлений</DialogTitle>
        <DialogContent>
          <FormControl fullWidth margin='dense'>
            <InputLabel>Получатели</InputLabel>
            <Select
              multiple
              value={selectedContractors}
              onChange={e => setSelectedContractors(e.target.value as number[])}
              label='Получатели'
            >
              {verifiedContractors.map(contractor => (
                <MenuItem
                  key={contractor.contractor_id}
                  value={contractor.contractor_id}
                >
                  {contractor.name} (@{contractor.telegram_username})
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Typography
            variant='body2'
            color='text.secondary'
            sx={{ mt: 1, mb: 2 }}
          >
            {selectedContractors.length === 0
              ? 'Если не выбраны получатели, сообщение будет отправлено всем исполнителям'
              : `Выбрано получателей: ${selectedContractors.length}`}
          </Typography>

          <TextField
            fullWidth
            multiline
            rows={4}
            label='Сообщение'
            value={bulkMessage}
            onChange={e => setBulkMessage(e.target.value)}
            placeholder='Введите текст для массовой отправки...'
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBulkNotificationDialogOpen(false)}>
            Отмена
          </Button>
          <Button
            onClick={handleSendBulkNotification}
            variant='contained'
            disabled={!bulkMessage.trim()}
          >
            Отправить всем
          </Button>
        </DialogActions>
      </Dialog>

      {/* Диалог тестирования подключения */}
      <Dialog
        open={testDialogOpen}
        onClose={() => setTestDialogOpen(false)}
        maxWidth='sm'
        fullWidth
      >
        <DialogTitle>Тестирование подключения к Telegram боту</DialogTitle>
        <DialogContent>
          {testResult && (
            <Box>
              {testResult.success ? (
                <Alert severity='success' sx={{ mb: 2 }}>
                  <Typography variant='h6'>✅ Подключение успешно!</Typography>
                </Alert>
              ) : (
                <Alert severity='error' sx={{ mb: 2 }}>
                  <Typography variant='h6'>❌ Ошибка подключения</Typography>
                  <Typography variant='body2'>{testResult.error}</Typography>
                </Alert>
              )}

              {testResult.bot_info && (
                <Box>
                  <Typography variant='subtitle1' gutterBottom>
                    Информация о боте:
                  </Typography>
                  <Typography variant='body2'>
                    <strong>ID:</strong> {testResult.bot_info.id}
                  </Typography>
                  <Typography variant='body2'>
                    <strong>Имя:</strong> {testResult.bot_info.first_name}
                  </Typography>
                  <Typography variant='body2'>
                    <strong>Username:</strong> @{testResult.bot_info.username}
                  </Typography>
                  <Typography variant='body2'>
                    <strong>Может присоединяться к группам:</strong>{' '}
                    {testResult.bot_info.can_join_groups ? 'Да' : 'Нет'}
                  </Typography>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTestDialogOpen(false)}>Закрыть</Button>
        </DialogActions>
      </Dialog>

      {/* Диалог истории чата */}
      <ChatHistoryDialog
        open={chatHistoryOpen}
        onClose={handleCloseChatHistory}
        telegramUserId={selectedTelegramUser?.id || 0}
        telegramUser={selectedTelegramUser}
      />
    </Box>
  );
};

export default TelegramBotPage;
