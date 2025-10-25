import React, { useState, useEffect } from 'react';
import {
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  List,
  ListItem,
  ListItemText,
  Avatar,
  Chip,
  Divider,
  CircularProgress,
  Alert,
  IconButton,
} from '@mui/material';
import {
  Close,
  Person,
  Bot,
  MarkAsUnread,
} from '@mui/icons-material';
import { apiService } from '../services/api';

interface ChatHistoryDialogProps {
  open: boolean;
  onClose: () => void;
  telegramUserId: number;
  telegramUser: any;
}

const ChatHistoryDialog: React.FC<ChatHistoryDialogProps> = ({
  open,
  onClose,
  telegramUserId,
  telegramUser,
}) => {
  const [messages, setMessages] = useState<any[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open && telegramUserId) {
      loadChatHistory();
    }
  }, [open, telegramUserId]);

  const loadChatHistory = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await apiService.getChatHistory(telegramUserId);
      setMessages(data.messages);
      setUnreadCount(data.unread_count);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка загрузки истории чата');
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsRead = async () => {
    try {
      await apiService.markMessagesRead(telegramUserId);
      setUnreadCount(0);
      // Обновляем сообщения, чтобы убрать статус "непрочитанное"
      loadChatHistory();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка отметки сообщений как прочитанных');
    }
  };

  const formatMessageTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getUserDisplayName = () => {
    if (!telegramUser) return 'Пользователь';
    
    const parts = [telegramUser.first_name, telegramUser.last_name].filter(Boolean);
    return parts.length > 0 ? parts.join(' ') : telegramUser.username || 'Пользователь';
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          height: '80vh',
          maxHeight: '80vh',
        },
      }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar sx={{ bgcolor: 'primary.main' }}>
              <Person />
            </Avatar>
            <Box>
              <Typography variant="h6">
                История переписки с {getUserDisplayName()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                @{telegramUser?.username || 'без username'}
              </Typography>
            </Box>
          </Box>
          <IconButton onClick={onClose}>
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ p: 0 }}>
        {error && (
          <Alert severity="error" sx={{ m: 2 }}>
            {error}
          </Alert>
        )}

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Box sx={{ height: '100%', overflow: 'auto' }}>
            {messages.length === 0 ? (
              <Box sx={{ p: 4, textAlign: 'center' }}>
                <Typography variant="body1" color="text.secondary">
                  История переписки пуста
                </Typography>
              </Box>
            ) : (
              <List sx={{ p: 0 }}>
                {messages.map((message, index) => (
                  <React.Fragment key={message.id}>
                    <ListItem
                      sx={{
                        flexDirection: message.is_from_bot ? 'row-reverse' : 'row',
                        alignItems: 'flex-start',
                        py: 2,
                        px: 3,
                      }}
                    >
                      <Avatar
                        sx={{
                          bgcolor: message.is_from_bot ? 'primary.main' : 'secondary.main',
                          mr: message.is_from_bot ? 0 : 2,
                          ml: message.is_from_bot ? 2 : 0,
                        }}
                      >
                        {message.is_from_bot ? <Bot /> : <Person />}
                      </Avatar>
                      
                      <Box
                        sx={{
                          maxWidth: '70%',
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: message.is_from_bot ? 'flex-end' : 'flex-start',
                        }}
                      >
                        <Box
                          sx={{
                            bgcolor: message.is_from_bot ? 'primary.main' : 'grey.100',
                            color: message.is_from_bot ? 'white' : 'text.primary',
                            p: 2,
                            borderRadius: 2,
                            mb: 1,
                            position: 'relative',
                          }}
                        >
                          <Typography variant="body1" sx={{ wordBreak: 'break-word' }}>
                            {message.message_text}
                          </Typography>
                          
                          {!message.is_from_bot && !message.is_read && (
                            <Box
                              sx={{
                                position: 'absolute',
                                top: -8,
                                right: -8,
                                width: 16,
                                height: 16,
                                bgcolor: 'error.main',
                                borderRadius: '50%',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                              }}
                            >
                              <Typography variant="caption" sx={{ color: 'white', fontSize: '10px' }}>
                                !
                              </Typography>
                            </Box>
                          )}
                        </Box>
                        
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="caption" color="text.secondary">
                            {formatMessageTime(message.created_at)}
                          </Typography>
                          {message.message_type !== 'text' && (
                            <Chip
                              label={message.message_type}
                              size="small"
                              variant="outlined"
                            />
                          )}
                        </Box>
                      </Box>
                    </ListItem>
                    {index < messages.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            )}
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ p: 2, justifyContent: 'space-between' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {unreadCount > 0 && (
            <>
              <Chip
                icon={<MarkAsUnread />}
                label={`${unreadCount} непрочитанных`}
                color="error"
                variant="outlined"
              />
              <Button
                variant="outlined"
                color="primary"
                onClick={handleMarkAsRead}
                size="small"
              >
                Отметить как прочитанные
              </Button>
            </>
          )}
        </Box>
        
        <Button onClick={onClose} variant="contained">
          Закрыть
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ChatHistoryDialog;
