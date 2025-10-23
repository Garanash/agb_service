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

const drawerWidth = 240;

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [profileMenuAnchor, setProfileMenuAnchor] = useState<null | HTMLElement>(null);
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

  // Добавляем "Заявки на ремонт" только для не-админов
  if (user?.role !== UserRole.ADMIN) {
    menuItems.push({
      text: 'Заявки на ремонт',
      icon: <Build />,
      path: '/repair-requests',
    });
  }

  // Добавляем пункты меню в зависимости от роли пользователя
  if (user?.role === UserRole.CONTRACTOR || user?.role === UserRole.ADMIN) {
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
    <Box sx={{ 
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column',
      background: 'linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%)'
    }}>
      <Toolbar sx={{ 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white'
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Logo size={32} color="#FCB813" />
          <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 'bold' }}>
            AGB SERVICE
          </Typography>
        </Box>
      </Toolbar>
      <Divider />
      <List sx={{ flex: 1, py: 2 }}>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding sx={{ px: 2, mb: 0.5 }}>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => navigate(item.path)}
              sx={{
                borderRadius: 2,
                mx: 1,
                '&.Mui-selected': {
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%)',
                  },
                  '& .MuiListItemIcon-root': {
                    color: 'white',
                  },
                },
                '&:hover': {
                  background: 'rgba(102, 126, 234, 0.1)',
                  transform: 'translateX(4px)',
                  transition: 'all 0.2s ease-in-out'
                },
                transition: 'all 0.2s ease-in-out'
              }}
            >
              <ListItemIcon sx={{ minWidth: 40 }}>{item.icon}</ListItemIcon>
              <ListItemText 
                primary={item.text} 
                primaryTypographyProps={{ 
                  fontWeight: location.pathname === item.path ? 'bold' : 'normal' 
                }}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      
      {/* Современный профиль пользователя внизу сайдбара */}
      <Box sx={{ mt: 'auto', p: 2 }}>
        <Divider sx={{ mb: 2 }} />
        <Box 
          sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: 1, 
            p: 2,
            borderRadius: 2,
            cursor: 'pointer',
            background: 'rgba(255,255,255,0.8)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255,255,255,0.2)',
            '&:hover': {
              backgroundColor: 'rgba(102, 126, 234, 0.1)',
              transform: 'translateY(-2px)',
              boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
            },
            transition: 'all 0.3s ease-in-out'
          }}
          onClick={handleProfileClick}
        >
          <Avatar sx={{ 
            width: 40, 
            height: 40,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white'
          }}>
            <AccountCircle />
          </Avatar>
          <Box sx={{ flex: 1 }}>
            <Typography variant="body2" sx={{ fontWeight: 'bold', color: 'text.primary' }}>
              {user?.first_name} {user?.last_name}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {user?.role === UserRole.ADMIN ? 'Администратор' :
               user?.role === UserRole.CUSTOMER ? 'Заказчик' :
               user?.role === UserRole.CONTRACTOR ? 'Исполнитель' :
               user?.role === UserRole.SERVICE_ENGINEER ? 'Сервисный инженер' :
               user?.role === UserRole.MANAGER ? 'Менеджер' :
               user?.role === UserRole.SECURITY ? 'Служба безопасности' :
               user?.role === UserRole.HR ? 'Отдел кадров' : 'Пользователь'}
            </Typography>
          </Box>
        </Box>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
          display: { xs: 'block', sm: 'none' }, // Скрываем на больших экранах
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexGrow: 1 }}>
            <Logo size={32} color="#FCB813" />
            <Typography variant="h6" noWrap component="div">
              AGB SERVICE
            </Typography>
          </Box>
        </Toolbar>
      </AppBar>

      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
        aria-label="mailbox folders"
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
          minHeight: '100vh'
        }}
      >
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
            <Edit fontSize="small" />
          </ListItemIcon>
          <ListItemText>Изменить профиль</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleLogoutClick}>
          <ListItemIcon>
            <Logout fontSize="small" />
          </ListItemIcon>
          <ListItemText>Выйти из профиля</ListItemText>
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default Layout;
