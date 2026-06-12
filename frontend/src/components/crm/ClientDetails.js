import React from 'react';
import {
    Box,
    Paper,
    Typography,
    Grid,
    Divider,
    Chip,
    Button,
    List,
    ListItem,
    ListItemText,
    IconButton,
    Card,
    CardContent,
    CardHeader,
    Tooltip,
    Tab,
    Tabs,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow
} from '@mui/material';
import {
    Add as AddIcon,
    Edit as EditIcon,
    Delete as DeleteIcon,
    CalendarToday as CalendarIcon,
    Note as NoteIcon
} from '@mui/icons-material';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';

/**
 * Компонент для отображения детальной информации о клиенте
 * 
 * @param {Object} props.client - данные клиента
 * @param {Array} props.sessions - сессии клиента
 * @param {Array} props.notes - заметки клиента
 * @param {Array} props.calculations - расчеты клиента
 * @param {Function} props.onEditClick - обработчик редактирования
 * @param {Function} props.onBack - обработчик возврата к списку
 * @param {Function} props.onAddSession - обработчик добавления сессии
 * @param {Function} props.onAddNote - обработчик добавления заметки
 * @param {Function} props.onViewCalculation - обработчик просмотра расчета
 */
const ClientDetails = ({
    client,
    sessions = [],
    notes = [],
    calculations = [],
    onEditClick,
    onBack,
    onAddSession,
    onAddNote,
    onViewCalculation
}) => {
    // Состояние для текущей активной вкладки
    const [activeTab, setActiveTab] = React.useState(0);

    if (!client) {
        return (
            <Paper sx={{ p: 3, textAlign: 'center' }}>
                <Typography>Клиент не найден</Typography>
                <Button variant="outlined" onClick={onBack} sx={{ mt: 2 }}>
                    Вернуться к списку
                </Button>
            </Paper>
        );
    }

    // Форматирование даты
    const formatDate = (dateStr) => {
        if (!dateStr) return 'Не указана';
        return format(new Date(dateStr), 'dd MMMM yyyy', { locale: ru });
    };

    // Форматирование даты и времени
    const formatDateTime = (dateTimeStr) => {
        if (!dateTimeStr) return '';
        return format(new Date(dateTimeStr), 'dd.MM.yyyy HH:mm', { locale: ru });
    };

    // Обработчик изменения вкладки
    const handleTabChange = (event, newValue) => {
        setActiveTab(newValue);
    };

    return (
        <Box>
            {/* Верхняя часть с основной информацией о клиенте */}
            <Paper sx={{ p: 3, mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Box>
                        <Typography variant="h5" gutterBottom>
                            {client.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            ID: {client.id} | Создан: {formatDateTime(client.created_at)}
                        </Typography>
                    </Box>

                    <Box>
                        <Button
                            variant="outlined"
                            onClick={onBack}
                            sx={{ mr: 1 }}
                        >
                            Назад
                        </Button>
                        <Button
                            variant="contained"
                            startIcon={<EditIcon />}
                            onClick={() => onEditClick(client.id)}
                        >
                            Редактировать
                        </Button>
                    </Box>
                </Box>

                <Divider sx={{ mb: 2 }} />

                <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                        <Typography variant="subtitle1" gutterBottom>
                            Контактная информация
                        </Typography>
                        <Box sx={{ ml: 2 }}>
                            {client.email && (
                                <Typography variant="body2" gutterBottom>
                                    <strong>Email:</strong> {client.email}
                                </Typography>
                            )}
                            {client.phone && (
                                <Typography variant="body2">
                                    <strong>Телефон:</strong> {client.phone}
                                </Typography>
                            )}
                        </Box>
                    </Grid>

                    <Grid item xs={12} md={6}>
                        <Typography variant="subtitle1" gutterBottom>
                            Дата рождения
                        </Typography>
                        <Box sx={{ ml: 2 }}>
                            <Typography variant="body2">
                                <strong>Дата:</strong> {formatDate(client.birth_date)}
                            </Typography>
                            {client.birth_time && (
                                <Typography variant="body2">
                                    <strong>Время:</strong> {client.birth_time}
                                </Typography>
                            )}
                        </Box>
                    </Grid>

                    {client.notes && (
                        <Grid item xs={12}>
                            <Typography variant="subtitle1" gutterBottom>
                                Примечания
                            </Typography>
                            <Typography variant="body2" sx={{ ml: 2 }}>
                                {client.notes}
                            </Typography>
                        </Grid>
                    )}
                </Grid>
            </Paper>

            {/* Вкладки для разных типов данных */}
            <Paper sx={{ mb: 3 }}>
                <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                    <Tabs
                        value={activeTab}
                        onChange={handleTabChange}
                        aria-label="client data tabs"
                    >
                        <Tab label="Сессии" id="sessions-tab" />
                        <Tab label="Заметки" id="notes-tab" />
                        <Tab label="Расчеты" id="calculations-tab" />
                    </Tabs>
                </Box>

                {/* Панель сессий */}
                <TabPanel value={activeTab} index={0}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                        <Typography variant="h6">
                            Сессии клиента
                        </Typography>
                        <Button
                            variant="outlined"
                            startIcon={<AddIcon />}
                            onClick={onAddSession}
                        >
                            Добавить сессию
                        </Button>
                    </Box>

                    {sessions.length > 0 ? (
                        <TableContainer>
                            <Table>
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Дата</TableCell>
                                        <TableCell>Итоги</TableCell>
                                        <TableCell>Заметки</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {sessions.map((session) => (
                                        <TableRow key={session.id} hover>
                                            <TableCell>
                                                {formatDate(session.date)}
                                            </TableCell>
                                            <TableCell>
                                                {session.summary || 'Нет итогов'}
                                            </TableCell>
                                            <TableCell>
                                                {session.notes ? (
                                                    session.notes.length > 100
                                                        ? `${session.notes.substring(0, 100)}...`
                                                        : session.notes
                                                ) : 'Нет заметок'}
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    ) : (
                        <Typography variant="body1" sx={{ py: 3, textAlign: 'center' }}>
                            У клиента пока нет сессий
                        </Typography>
                    )}
                </TabPanel>

                {/* Панель заметок */}
                <TabPanel value={activeTab} index={1}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                        <Typography variant="h6">
                            Заметки
                        </Typography>
                        <Button
                            variant="outlined"
                            startIcon={<AddIcon />}
                            onClick={onAddNote}
                        >
                            Добавить заметку
                        </Button>
                    </Box>

                    {notes.length > 0 ? (
                        <Grid container spacing={2}>
                            {notes.map((note) => (
                                <Grid item xs={12} key={note.id}>
                                    <Card variant="outlined">
                                        <CardHeader
                                            subheader={formatDateTime(note.created_at)}
                                            action={
                                                <Tooltip title="Удалить">
                                                    <IconButton color="error" size="small">
                                                        <DeleteIcon fontSize="small" />
                                                    </IconButton>
                                                </Tooltip>
                                            }
                                        />
                                        <CardContent>
                                            <Typography variant="body2">
                                                {note.note_text}
                                            </Typography>
                                            {note.calculation_id && (
                                                <Chip
                                                    label="Связан с расчетом"
                                                    size="small"
                                                    clickable
                                                    onClick={() => onViewCalculation(note.calculation_id)}
                                                    sx={{ mt: 1 }}
                                                />
                                            )}
                                        </CardContent>
                                    </Card>
                                </Grid>
                            ))}
                        </Grid>
                    ) : (
                        <Typography variant="body1" sx={{ py: 3, textAlign: 'center' }}>
                            У клиента пока нет заметок
                        </Typography>
                    )}
                </TabPanel>

                {/* Панель расчетов */}
                <TabPanel value={activeTab} index={2}>
                    <Box sx={{ mb: 2 }}>
                        <Typography variant="h6">
                            Связанные расчеты
                        </Typography>
                    </Box>

                    {calculations.length > 0 ? (
                        <TableContainer>
                            <Table>
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Тип расчета</TableCell>
                                        <TableCell>ID расчета</TableCell>
                                        <TableCell>Примечания</TableCell>
                                        <TableCell>Действия</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {calculations.map((calc, index) => (
                                        <TableRow key={index} hover>
                                            <TableCell>
                                                {calc.calculation_type === 'tongshu' ? 'Тун Шу' :
                                                    calc.calculation_type === 'qimen' ? 'Ци Мэнь' :
                                                        'Другой'}
                                            </TableCell>
                                            <TableCell>
                                                {calc.reference_id}
                                            </TableCell>
                                            <TableCell>
                                                {calc.notes || 'Нет примечаний'}
                                            </TableCell>
                                            <TableCell>
                                                <Button
                                                    variant="outlined"
                                                    size="small"
                                                    onClick={() => onViewCalculation(calc.reference_id, calc.calculation_type)}
                                                >
                                                    Просмотр
                                                </Button>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    ) : (
                        <Typography variant="body1" sx={{ py: 3, textAlign: 'center' }}>
                            У клиента пока нет связанных расчетов
                        </Typography>
                    )}
                </TabPanel>
            </Paper>
        </Box>
    );
};

// Вспомогательный компонент для вкладок
const TabPanel = ({ children, value, index, ...other }) => {
    return (
        <div
            role="tabpanel"
            hidden={value !== index}
            id={`tabpanel-${index}`}
            aria-labelledby={`tab-${index}`}
            {...other}
        >
            {value === index && (
                <Box sx={{ p: 3 }}>
                    {children}
                </Box>
            )}
        </div>
    );
};

export default ClientDetails;