import React, { useState } from 'react';
import {
  AppBar,
  Box,
  CssBaseline,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Avatar,
  Divider,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  Build,
  People,
  Business,
  AccountCircle,
  Logout,
  Edit,
  Telegram,
  Settings,
  Person,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from 'hooks/useAuth';
import { UserRole } from 'types/api';
import Logo from 'components/Logo';
import DevelopmentBanner from 'components/common/DevelopmentBanner';

const drawerWidth = 240;

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [profileMenuAnchor, setProfileMenuAnchor] =
    useState<null | HTMLElement>(null);
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleProfileClick = (event: React.MouseEvent<HTMLElement>) => {
    setProfileMenuAnchor(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setProfileMenuAnchor(null);
  };

  const handleEditProfile = () => {
    handleProfileMenuClose();
    navigate('/profile');
  };

  const handleProfileSettings = () => {
    handleProfileMenuClose();
    navigate('/profile/settings');
  };

  const handleLogoutClick = () => {
    handleProfileMenuClose();
    logout();
    navigate('/login');
  };

  const menuItems = [
    {
      text: 'Главная',
      icon: <Dashboard />,
      path: '/',
    },
  ];

  // Меню для исполнителя - только 3 вкладки
  if (user?.role === UserRole.CONTRACTOR) {
    menuItems.push({
      text: 'Архив заявок',
      icon: <Build />,
      path: '/contractor/archive',
    });
    menuItems.push({
      text: 'Профиль исполнителя',
      icon: <Person />,
      path: '/contractor/profile',
    });
  }

  // Добавляем пункты меню для админа
  if (user?.role === UserRole.ADMIN) {
    menuItems.push({
      text: 'Исполнители',
      icon: <People />,
      path: '/contractors',
    });
  }

  if (user?.role === UserRole.CUSTOMER || user?.role === UserRole.ADMIN) {
    menuItems.push({
      text: 'Заказчики',
      icon: <Business />,
      path: '/customers',
    });
  }

  // Меню для заказчика
  if (user?.role === UserRole.CUSTOMER) {
    menuItems.push({
      text: 'Профиль компании',
      icon: <Business />,
      path: '/customer/company-profile',
    });
    menuItems.push({
      text: 'Личный кабинет',
      icon: <Person />,
      path: '/customer/cabinet',
    });
  }

  // Меню для менеджера
  if (user?.role === UserRole.MANAGER || user?.role === UserRole.ADMIN) {
    menuItems.push({
      text: 'Управление заявками',
      icon: <Build />,
      path: '/manager/requests',
    });
    menuItems.push({
      text: 'Подтверждение исполнителей',
      icon: <People />,
      path: '/manager/verification',
    });
    menuItems.push({
      text: 'Календарь',
      icon: <Dashboard />,
      path: '/manager/calendar',
    });
    menuItems.push({
      text: 'Telegram бот',
      icon: <Telegram />,
      path: '/telegram/bot',
    });
  }

  // Меню для службы безопасности
  if (user?.role === UserRole.SECURITY || user?.role === UserRole.ADMIN) {
    menuItems.push({
      text: 'Проверка исполнителей',
      icon: <People />,
      path: '/security/verification',
    });
  }

  // Меню для HR
  if (user?.role === UserRole.HR || user?.role === UserRole.ADMIN) {
    menuItems.push({
      text: 'Документы HR',
      icon: <Business />,
      path: '/hr/documents',
    });
  }

  // Меню для администратора
  if (user?.role === UserRole.ADMIN) {
    menuItems.push({
      text: 'Админ панель',
      icon: <Settings />,
      path: '/admin/panel',
    });
  }

  const drawer = (
    <div>
      <Toolbar>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Logo size={32} color='#FCB813' />
          <Typography variant='h6' noWrap component='div'>
            AGB SERVICE
          </Typography>
        </Box>
      </Toolbar>
      <Divider />
      <List>
        {menuItems.map(item => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => navigate(item.path)}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>

      {/* Профиль пользователя внизу сайдбара */}
      <Box sx={{ mt: 'auto', p: 2 }}>
        <Divider sx={{ mb: 2 }} />
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            p: 1,
            borderRadius: 1,
            cursor: 'pointer',
            '&:hover': {
              backgroundColor: 'action.hover',
            },
          }}
          onClick={handleProfileClick}
        >
          <Avatar sx={{ width: 32, height: 32 }}>
            <AccountCircle />
          </Avatar>
          <Box sx={{ flex: 1 }}>
            <Typography variant='body2' sx={{ fontWeight: 'bold' }}>
              {user?.first_name} {user?.last_name}
            </Typography>
            <Typography variant='caption' color='text.secondary'>
              {user?.role === UserRole.ADMIN
                ? 'Администратор'
                : user?.role === UserRole.CUSTOMER
                  ? 'Заказчик'
                  : user?.role === UserRole.CONTRACTOR
                    ? 'Исполнитель'
                    : user?.role === UserRole.SERVICE_ENGINEER
                      ? 'Сервисный инженер'
                      : user?.role === UserRole.MANAGER
                        ? 'Менеджер'
                        : user?.role === UserRole.SECURITY
                          ? 'Служба безопасности'
                          : user?.role === UserRole.HR
                            ? 'Отдел кадров'
                            : 'Пользователь'}
            </Typography>
          </Box>
        </Box>
      </Box>
    </div>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar
        position='fixed'
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
          display: { xs: 'block', sm: 'none' }, // Скрываем на больших экранах
        }}
      >
        <Toolbar>
          <IconButton
            color='inherit'
            aria-label='open drawer'
            edge='start'
            onClick={handleDrawerToggle}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Box
            sx={{ display: 'flex', alignItems: 'center', gap: 1, flexGrow: 1 }}
          >
            <Logo size={32} color='#FCB813' />
            <Typography variant='h6' noWrap component='div'>
              AGB SERVICE
            </Typography>
          </Box>
        </Toolbar>
      </AppBar>

      <Box
        component='nav'
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
        aria-label='mailbox folders'
      >
        <Drawer
          variant='temporary'
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
            },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant='permanent'
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      <Box
        component='main'
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
        }}
      >
        <DevelopmentBanner />
        {children}
      </Box>

      {/* Выпадающее меню профиля */}
      <Menu
        anchorEl={profileMenuAnchor}
        open={Boolean(profileMenuAnchor)}
        onClose={handleProfileMenuClose}
        anchorOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
      >
        <MenuItem onClick={handleEditProfile}>
          <ListItemIcon>
            <Edit fontSize='small' />
          </ListItemIcon>
          <ListItemText>Изменить профиль</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleProfileSettings}>
          <ListItemIcon>
            <Settings fontSize='small' />
          </ListItemIcon>
          <ListItemText>Настройки профиля</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleLogoutClick}>
          <ListItemIcon>
            <Logout fontSize='small' />
          </ListItemIcon>
          <ListItemText>Выйти из профиля</ListItemText>
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default Layout;
