import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { DebugModeProvider } from './contexts/DebugModeContext';
import { ElementIdMarkerProvider } from './contexts/ElementIdMarkerContext';
import { DisplaySettingsProvider, useDisplaySettings } from './contexts/DisplaySettingsContext';
import ElementIdMarkerLayer from './components/ElementIdMarkerLayer';
import ElementIdBadge from './components/ElementIdBadge';
import {
    Toolbar,
    Typography,
    Container,
    Box,
    Drawer,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Divider,
    CircularProgress
} from '@mui/material';
import {
    CalendarMonth as CalendarIcon,
    GridView as GridViewIcon,
    People as PeopleIcon,
    Person as PersonIcon,
    Home as HomeIcon,
    MenuBook as MenuBookIcon,
    Settings as SettingsIcon
} from '@mui/icons-material';

// Страницы (lazy loading для code splitting)
const HomePage = React.lazy(() => import('./pages/HomePage'));
const TongShuPage = React.lazy(() => import('./pages/TongShuPage'));
const QiMenPage = React.lazy(() => import('./pages/QiMenPage'));
const CrmPage = React.lazy(() => import('./pages/CrmPage'));
const ReferencesPage = React.lazy(() => import('./pages/ReferencesPage'));
const AdminPage = React.lazy(() => import('./pages/AdminPage'));
const ProfilesPage = React.lazy(() => import('./pages/ProfilesPage'));

// Ширина боковой панели
const drawerWidth = 240;

function AppContent() {
    const { theme } = useDisplaySettings();
    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <ElementIdMarkerLayer />
            <Box sx={{ display: 'flex' }}>
                {/* Боковое меню */}
                <Drawer
                    variant="permanent"
                    sx={{
                        width: drawerWidth,
                        flexShrink: 0,
                        '& .MuiDrawer-paper': {
                            width: drawerWidth,
                            boxSizing: 'border-box',
                        },
                    }}
                >
                    <Toolbar>
                        <Typography variant="h6" noWrap component="div">
                            КМФ Платформа
                        </Typography>
                    </Toolbar>
                    <Divider />
                    <List>
                        <ElementIdBadge id="nav:tab:home">
                            <ListItem button component={Link} to="/">
                                <ListItemIcon>
                                    <HomeIcon />
                                </ListItemIcon>
                                <ListItemText primary="Главная" />
                            </ListItem>
                        </ElementIdBadge>
                        <ElementIdBadge id="nav:tab:tongshu">
                            <ListItem button component={Link} to="/tongshu">
                                <ListItemIcon>
                                    <CalendarIcon />
                                </ListItemIcon>
                                <ListItemText primary="Тун Шу" />
                            </ListItem>
                        </ElementIdBadge>
                        <ElementIdBadge id="nav:tab:qimen">
                            <ListItem button component={Link} to="/qimen">
                                <ListItemIcon>
                                    <GridViewIcon />
                                </ListItemIcon>
                                <ListItemText primary="Ци Мэнь" />
                            </ListItem>
                        </ElementIdBadge>
                        <ElementIdBadge id="nav:tab:profiles">
                            <ListItem button component={Link} to="/profiles">
                                <ListItemIcon>
                                    <PersonIcon />
                                </ListItemIcon>
                                <ListItemText primary="Профили" />
                            </ListItem>
                        </ElementIdBadge>
                        <ElementIdBadge id="nav:tab:crm">
                            <ListItem button component={Link} to="/crm">
                                <ListItemIcon>
                                    <PeopleIcon />
                                </ListItemIcon>
                                <ListItemText primary="CRM" />
                            </ListItem>
                        </ElementIdBadge>
                        <ElementIdBadge id="nav:tab:references">
                            <ListItem button component={Link} to="/references">
                                <ListItemIcon>
                                    <MenuBookIcon />
                                </ListItemIcon>
                                <ListItemText primary="Справочники" />
                            </ListItem>
                        </ElementIdBadge>
                        <ElementIdBadge id="nav:tab:admin">
                            <ListItem button component={Link} to="/admin">
                                <ListItemIcon>
                                    <SettingsIcon />
                                </ListItemIcon>
                                <ListItemText primary="Администратор" />
                            </ListItem>
                        </ElementIdBadge>
                    </List>
                </Drawer>

                {/* Основное содержимое */}
                <Box
                    component="main"
                    sx={{
                        flexGrow: 1,
                        bgcolor: 'background.default',
                        p: 3,
                        width: { sm: `calc(100% - ${drawerWidth}px)` }
                    }}
                >
                    <Toolbar />
                    <Container>
                        <React.Suspense fallback={<Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>}>
                        <Routes>
                            <Route path="/" element={<HomePage />} />
                            <Route path="/tongshu" element={<TongShuPage />} />
                            <Route path="/qimen" element={<QiMenPage />} />
                            <Route path="/crm" element={<CrmPage />} />
                            <Route path="/references" element={<ReferencesPage />} />
                        <Route path="/admin" element={<AdminPage />} />
                            <Route path="/profiles" element={<ProfilesPage />} />
                        </Routes>
                        </React.Suspense>
                    </Container>
                </Box>
            </Box>
        </ThemeProvider>
    );
}

function App() {
    return (
        <DebugModeProvider>
        <ElementIdMarkerProvider>
        <DisplaySettingsProvider>
            <AppContent />
        </DisplaySettingsProvider>
        </ElementIdMarkerProvider>
        </DebugModeProvider>
    );
}

export default App;