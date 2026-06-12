import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    Paper,
    Dialog,
    DialogContent,
    DialogTitle,
    DialogActions,
    Button,
    Snackbar,
    Alert,
    CircularProgress,
    IconButton
} from '@mui/material';
import {
    ArrowBack as ArrowBackIcon
} from '@mui/icons-material';

// Импортируем сервис для работы с API
import crmService from '../services/crmService';

// Импортируем компоненты CRM
import {
    ClientList,
    ClientForm,
    ClientDetails,
    SessionForm
} from '../components/crm';
import { generateId } from '../hooks/useElementId';

// Состояния экранов для CRM
const VIEWS = {
    LIST: 'list',
    ADD_CLIENT: 'add_client',
    EDIT_CLIENT: 'edit_client',
    VIEW_CLIENT: 'view_client',
    ADD_SESSION: 'add_session',
};

function CrmPage() {
    // Состояние приложения
    const [view, setView] = useState(VIEWS.LIST);
    const [clients, setClients] = useState([]);
    const [selectedClient, setSelectedClient] = useState(null);
    const [clientSessions, setClientSessions] = useState([]);
    const [clientNotes, setClientNotes] = useState([]);
    const [clientCalculations, setClientCalculations] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });
    const [confirmDialog, setConfirmDialog] = useState({ open: false, title: '', message: '', onConfirm: null });

    // Пагинация для списка клиентов
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [totalClients, setTotalClients] = useState(0);
    const [searchQuery, setSearchQuery] = useState('');

    // Загрузка списка клиентов при первой загрузке страницы
    useEffect(() => {
        loadClients();
    }, [page, rowsPerPage, searchQuery]);

    // Загрузка списка клиентов
    const loadClients = async () => {
        setLoading(true);
        setError(null);

        try {
            const data = await crmService.fetchClients(searchQuery, rowsPerPage, page * rowsPerPage);
            setClients(data);
            setTotalClients(data.length > 0 ? data.length + page * rowsPerPage : 0);
        } catch (err) {
            console.error("Ошибка при загрузке клиентов:", err);
            setError("Не удалось загрузить список клиентов. Пожалуйста, попробуйте позже.");
        } finally {
            setLoading(false);
        }
    };

    // Загрузка данных конкретного клиента
    const loadClientData = async (clientId) => {
        setLoading(true);
        setError(null);

        try {
            const client = await crmService.fetchClientById(clientId);
            setSelectedClient(client);

            // Загружаем дополнительные данные клиента
            const [sessions, notes, calculations] = await Promise.all([
                crmService.fetchClientSessions(clientId),
                crmService.fetchClientNotes(clientId),
                crmService.fetchClientCalculations(clientId)
            ]);

            setClientSessions(sessions);
            setClientNotes(notes);
            setClientCalculations(calculations);
        } catch (err) {
            console.error("Ошибка при загрузке данных клиента:", err);
            setError("Не удалось загрузить данные клиента. Пожалуйста, попробуйте позже.");
        } finally {
            setLoading(false);
        }
    };

    // Обработчики событий UI

    const handlePageChange = (event, newPage) => {
        setPage(newPage);
    };

    const handleRowsPerPageChange = (event) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
    };

    const handleSearch = (query) => {
        setSearchQuery(query);
        setPage(0);
    };

    const handleAddClick = () => {
        setSelectedClient(null);
        setView(VIEWS.ADD_CLIENT);
    };

    const handleEditClick = (clientId) => {
        const clientToEdit = clients.find(c => c.id === clientId);
        setSelectedClient(clientToEdit);
        setView(VIEWS.EDIT_CLIENT);
    };

    const handleViewClick = async (clientId) => {
        await loadClientData(clientId);
        setView(VIEWS.VIEW_CLIENT);
    };

    const handleDeleteClick = (clientId) => {
        setConfirmDialog({
            open: true,
            title: 'Удаление клиента',
            message: 'Вы действительно хотите удалить этого клиента? Это действие не может быть отменено.',
            onConfirm: () => confirmDeleteClient(clientId)
        });
    };

    const confirmDeleteClient = async (clientId) => {
        setConfirmDialog({ ...confirmDialog, open: false });
        setLoading(true);

        try {
            await crmService.deleteClient(clientId);

            // Обновляем список клиентов
            await loadClients();

            setNotification({
                open: true,
                message: 'Клиент успешно удален',
                severity: 'success'
            });
        } catch (err) {
            console.error("Ошибка при удалении клиента:", err);
            setNotification({
                open: true,
                message: 'Ошибка при удалении клиента',
                severity: 'error'
            });
        } finally {
            setLoading(false);
        }
    };

    const handleAddSessionClick = () => {
        setView(VIEWS.ADD_SESSION);
    };

    const handleBackClick = () => {
        // В зависимости от текущего view возвращаемся назад
        switch (view) {
            case VIEWS.VIEW_CLIENT:
                setView(VIEWS.LIST);
                break;
            case VIEWS.ADD_CLIENT:
            case VIEWS.EDIT_CLIENT:
                setView(VIEWS.LIST);
                break;
            case VIEWS.ADD_SESSION:
                setView(VIEWS.VIEW_CLIENT);
                break;
            default:
                setView(VIEWS.LIST);
        }
    };

    const handleSaveClient = async (clientData) => {
        setLoading(true);

        try {
            if (view === VIEWS.ADD_CLIENT) {
                // Создаем нового клиента
                const newClient = await crmService.createClient(clientData);
                setNotification({
                    open: true,
                    message: 'Клиент успешно добавлен',
                    severity: 'success'
                });
            } else if (view === VIEWS.EDIT_CLIENT) {
                // Обновляем существующего клиента
                const updatedClient = await crmService.updateClient(selectedClient.id, clientData);
                setNotification({
                    open: true,
                    message: 'Данные клиента успешно обновлены',
                    severity: 'success'
                });
            }

            // Обновляем список клиентов и возвращаемся к нему
            await loadClients();
            setView(VIEWS.LIST);
        } catch (err) {
            console.error("Ошибка при сохранении клиента:", err);
            setNotification({
                open: true,
                message: 'Ошибка при сохранении данных клиента',
                severity: 'error'
            });
        } finally {
            setLoading(false);
        }
    };

    const handleSaveSession = async (sessionData) => {
        setLoading(true);

        try {
            const newSession = await crmService.createSession(sessionData);

            // Обновляем список сессий клиента
            const sessions = await crmService.fetchClientSessions(selectedClient.id);
            setClientSessions(sessions);

            setNotification({
                open: true,
                message: 'Сессия успешно добавлена',
                severity: 'success'
            });

            // Возвращаемся к просмотру клиента
            setView(VIEWS.VIEW_CLIENT);
        } catch (err) {
            console.error("Ошибка при сохранении сессии:", err);
            setNotification({
                open: true,
                message: 'Ошибка при сохранении сессии',
                severity: 'error'
            });
        } finally {
            setLoading(false);
        }
    };

    const handleCloseNotification = () => {
        setNotification({ ...notification, open: false });
    };

    const handleCloseConfirmDialog = () => {
        setConfirmDialog({ ...confirmDialog, open: false });
    };

    // Отображение загрузки
    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }} data-element-id={generateId('crm', 'loading')}>
                <CircularProgress />
            </Box>
        );
    }

    // Функция рендеринга текущего представления
    const renderCurrentView = () => {
        switch (view) {
            case VIEWS.LIST:
                return (
                    <ClientList
                        clients={clients}
                        onSearch={handleSearch}
                        onPageChange={handlePageChange}
                        onRowsPerPageChange={handleRowsPerPageChange}
                        onAddClick={handleAddClick}
                        onEditClick={handleEditClick}
                        onDeleteClick={handleDeleteClick}
                        onViewClick={handleViewClick}
                        total={totalClients}
                        page={page}
                        rowsPerPage={rowsPerPage}
                    />
                );

            case VIEWS.ADD_CLIENT:
                return (
                    <Box>
                        <Box sx={{ mb: 3, display: 'flex', alignItems: 'center' }}>
                            <IconButton onClick={handleBackClick} sx={{ mr: 1 }}>
                                <ArrowBackIcon />
                            </IconButton>
                            <Typography variant="h5">Добавление нового клиента</Typography>
                        </Box>
                        <ClientForm
                            onSave={handleSaveClient}
                            onCancel={handleBackClick}
                        />
                    </Box>
                );

            case VIEWS.EDIT_CLIENT:
                return (
                    <Box>
                        <Box sx={{ mb: 3, display: 'flex', alignItems: 'center' }}>
                            <IconButton onClick={handleBackClick} sx={{ mr: 1 }}>
                                <ArrowBackIcon />
                            </IconButton>
                            <Typography variant="h5">Редактирование клиента</Typography>
                        </Box>
                        <ClientForm
                            client={selectedClient}
                            onSave={handleSaveClient}
                            onCancel={handleBackClick}
                        />
                    </Box>
                );

            case VIEWS.VIEW_CLIENT:
                return (
                    <ClientDetails
                        client={selectedClient}
                        sessions={clientSessions}
                        notes={clientNotes}
                        calculations={clientCalculations}
                        onEditClick={handleEditClick}
                        onBack={handleBackClick}
                        onAddSession={handleAddSessionClick}
                        onAddNote={() => console.log('Добавление заметки')}
                        onViewCalculation={(refId, type) => console.log('Просмотр расчета', refId, type)}
                    />
                );

            case VIEWS.ADD_SESSION:
                return (
                    <Box>
                        <Box sx={{ mb: 3, display: 'flex', alignItems: 'center' }}>
                            <IconButton onClick={handleBackClick} sx={{ mr: 1 }}>
                                <ArrowBackIcon />
                            </IconButton>
                            <Typography variant="h5">Добавление сессии</Typography>
                        </Box>
                        <SessionForm
                            clientId={selectedClient.id}
                            onSave={handleSaveSession}
                            onCancel={handleBackClick}
                        />
                    </Box>
                );

            default:
                return <Typography>Неизвестный режим просмотра</Typography>;
        }
    };

    return (
        <Box data-element-id={generateId('crm', 'page')}>
            <Typography variant="h4" gutterBottom data-element-id={generateId('crm', 'title')}>
                Система управления клиентами
            </Typography>

            {/* Сообщение об ошибке */}
            {error && (
                <Paper sx={{ p: 3, mb: 3, bgcolor: 'error.light', color: 'error.contrastText' }}>
                    <Typography>{error}</Typography>
                    <Button
                        variant="contained"
                        color="primary"
                        sx={{ mt: 2 }}
                        onClick={() => window.location.reload()}
                    >
                        Попробовать снова
                    </Button>
                </Paper>
            )}

            {/* Основное содержимое */}
            {renderCurrentView()}

            {/* Уведомления */}
            <Snackbar
                open={notification.open}
                autoHideDuration={6000}
                onClose={handleCloseNotification}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            >
                <Alert
                    onClose={handleCloseNotification}
                    severity={notification.severity}
                >
                    {notification.message}
                </Alert>
            </Snackbar>

            {/* Диалог подтверждения */}
            <Dialog
                open={confirmDialog.open}
                onClose={handleCloseConfirmDialog}
            >
                <DialogTitle>{confirmDialog.title}</DialogTitle>
                <DialogContent>
                    <Typography>{confirmDialog.message}</Typography>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseConfirmDialog} color="primary">
                        Отмена
                    </Button>
                    <Button onClick={confirmDialog.onConfirm} color="error" variant="contained">
                        Удалить
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
}

export default CrmPage;