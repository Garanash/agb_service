import React from 'react';
import {
  Card,
  CardContent,
  Box,
  Typography,
  Avatar,
  Chip,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  Badge,
} from '@mui/material';
import { MoreVert } from '@mui/icons-material';

interface ModernListItemProps {
  id: string | number;
  title: string;
  subtitle?: string;
  description?: string;
  status?: {
    label: string;
    color: 'success' | 'warning' | 'error' | 'info' | 'default';
  };
  avatar?: {
    icon: React.ReactNode;
    color?: string;
  };
  metadata?: Array<{
    icon: React.ReactNode;
    text: string;
  }>;
  onAction?: () => void;
}

interface ModernListProps {
  title: string;
  items: ModernListItemProps[];
  emptyMessage?: string;
  emptyIcon?: React.ReactNode;
}

const ModernList: React.FC<ModernListProps> = ({
  title,
  items,
  emptyMessage = 'Нет элементов',
  emptyIcon,
}) => {
  return (
    <Card
      sx={{
        borderRadius: 3,
        boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255,255,255,0.2)',
        background: 'rgba(255,255,255,0.9)',
      }}
    >
      <CardContent sx={{ p: 3 }}>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            mb: 3,
          }}
        >
          <Typography
            variant='h6'
            sx={{ fontWeight: 'bold', color: 'text.primary' }}
          >
            {title}
          </Typography>
          <Badge badgeContent={items.length} color='primary'>
            <Box />
          </Badge>
        </Box>

        <List sx={{ p: 0 }}>
          {items.map((item, index) => (
            <React.Fragment key={item.id}>
              <ListItem
                sx={{
                  p: 2,
                  borderRadius: 2,
                  mb: 1,
                  bgcolor: 'rgba(0,0,0,0.02)',
                  '&:hover': {
                    bgcolor: 'rgba(0,0,0,0.05)',
                    transform: 'translateY(-2px)',
                    transition: 'all 0.2s ease-in-out',
                  },
                }}
              >
                {item.avatar && (
                  <Avatar
                    sx={{
                      bgcolor: item.avatar.color || 'primary.main',
                      mr: 2,
                      width: 40,
                      height: 40,
                    }}
                  >
                    {item.avatar.icon}
                  </Avatar>
                )}

                <ListItemText
                  primary={
                    <Typography
                      variant='subtitle1'
                      sx={{ fontWeight: 'bold', mb: 0.5 }}
                    >
                      {item.title}
                    </Typography>
                  }
                  secondary={
                    <Box>
                      {item.subtitle && (
                        <Typography
                          variant='body2'
                          color='text.secondary'
                          sx={{ mb: 1 }}
                        >
                          {item.subtitle}
                        </Typography>
                      )}
                      {item.description && (
                        <Typography
                          variant='body2'
                          color='text.secondary'
                          sx={{ mb: 1 }}
                        >
                          {item.description}
                        </Typography>
                      )}
                      {item.metadata && (
                        <Box
                          sx={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 2,
                            flexWrap: 'wrap',
                          }}
                        >
                          {item.metadata.map((meta, metaIndex) => (
                            <Box
                              key={metaIndex}
                              sx={{ display: 'flex', alignItems: 'center' }}
                            >
                              {meta.icon}
                              <Typography
                                variant='caption'
                                color='text.secondary'
                                sx={{ ml: 0.5 }}
                              >
                                {meta.text}
                              </Typography>
                            </Box>
                          ))}
                        </Box>
                      )}
                    </Box>
                  }
                />

                <ListItemSecondaryAction>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {item.status && (
                      <Chip
                        label={item.status.label}
                        color={item.status.color}
                        size='small'
                        sx={{
                          fontWeight: 'bold',
                          borderRadius: 2,
                        }}
                      />
                    )}
                    {item.onAction && (
                      <IconButton size='small' onClick={item.onAction}>
                        <MoreVert />
                      </IconButton>
                    )}
                  </Box>
                </ListItemSecondaryAction>
              </ListItem>
              {index < items.length - 1 && <Divider sx={{ mx: 2 }} />}
            </React.Fragment>
          ))}

          {items.length === 0 && (
            <ListItem sx={{ p: 3, textAlign: 'center' }}>
              <Box sx={{ width: '100%' }}>
                {emptyIcon && (
                  <Avatar
                    sx={{
                      bgcolor: 'grey.100',
                      width: 64,
                      height: 64,
                      mx: 'auto',
                      mb: 2,
                    }}
                  >
                    {emptyIcon}
                  </Avatar>
                )}
                <Typography variant='h6' color='text.secondary' sx={{ mb: 1 }}>
                  {emptyMessage}
                </Typography>
              </Box>
            </ListItem>
          )}
        </List>
      </CardContent>
    </Card>
  );
};

export default ModernList;
