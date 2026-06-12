import React, { useState } from 'react';
import {
    Box,
    Paper,
    Typography,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TablePagination,
    TextField,
    InputAdornment,
    IconButton,
    Tooltip,
    Chip
} from '@mui/material';
import {
    Search as SearchIcon,
    Add as AddIcon,
    Edit as EditIcon,
    Delete as DeleteIcon,
    VisibilityOutlined as ViewIcon
} from '@mui/icons-material';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';

/**
 * Компонент для отображения списка клиентов с возможностью поиска
 * 
 * @param {Array} props.clients - список клиентов
 * @param {Function} props.onSearch - обработчик поиска
 * @param {Function} props.onPageChange - обработчик изменения страницы
 * @param {Function} props.onRowsPerPageChange - обработчик изменения количества строк на странице
 * @param {Function} props.onAddClick - обработчик добавления клиента
 * @param {Function} props.onEditClick - обработчик редактирования клиента
 * @param {Function} props.onDeleteClick - обработчик удаления клиента
 * @param {Function} props.onViewClick - обработчик просмотра клиента
 * @param {number} props.total - общее количество клиентов
 * @param {number} props.page - текущая страница
 * @param {number} props.rowsPerPage - количество строк на странице
 */
const ClientList = ({
    clients = [],
    onSearch,
    onPageChange,
    onRowsPerPageChange,
    onAddClick,
    onEditClick,
    onDeleteClick,
    onViewClick,
    total = 0,
    page = 0,
    rowsPerPage = 10,
}) => {
    const [searchQuery, setSearchQuery] = useState('');

    // Обработчик поиска
    const handleSearch = () => {
        if (onSearch) {
            onSearch(searchQuery);
        }
    };

    // Обработчик нажатия Enter в поле поиска
    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    };

    // Форматирование даты рождения
    const formatBirthDate = (birthDate) => {
        if (!birthDate) return 'Не указана';
        return format(new Date(birthDate), 'dd MMMM yyyy', { locale: ru });
    };

    return (
        <Box>
            <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h5" component="h2">
                    Клиенты
                </Typography>
                <Tooltip title="Добавить клиента">
                    <IconButton
                        color="primary"
                        onClick={onAddClick}
                        size="large"
                    >
                        <AddIcon />
                    </IconButton>
                </Tooltip>
            </Box>

            {/* Поисковая строка */}
            <Paper sx={{ p: 2, mb: 3 }}>
                <TextField
                    fullWidth
                    placeholder="Поиск по имени, email или телефону"
                    variant="outlined"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyPress={handleKeyPress}
                    InputProps={{
                        endAdornment: (
                            <InputAdornment position="end">
                                <IconButton onClick={handleSearch} edge="end">
                                    <SearchIcon />
                                </IconButton>
                            </InputAdornment>
                        ),
                    }}
                />
            </Paper>

            {/* Таблица клиентов */}
            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>ФИО</TableCell>
                            <TableCell>Контакты</TableCell>
                            <TableCell>Дата рождения</TableCell>
                            <TableCell>Создан</TableCell>
                            <TableCell align="right">Действия</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {clients.length > 0 ? (
                            clients.map((client) => (
                                <TableRow key={client.id} hover>
                                    <TableCell>{client.name}</TableCell>
                                    <TableCell>
                                        <Box>
                                            {client.email && (
                                                <Typography variant="body2" color="text.secondary" gutterBottom>
                                                    {client.email}
                                                </Typography>
                                            )}
                                            {client.phone && (
                                                <Typography variant="body2" color="text.secondary">
                                                    {client.phone}
                                                </Typography>
                                            )}
                                        </Box>
                                    </TableCell>
                                    <TableCell>
                                        {formatBirthDate(client.birth_date)}
                                        {client.birth_time && `, ${client.birth_time}`}
                                    </TableCell>
                                    <TableCell>
                                        {format(new Date(client.created_at), 'dd.MM.yyyy', { locale: ru })}
                                    </TableCell>
                                    <TableCell align="right">
                                        <Tooltip title="Просмотр">
                                            <IconButton
                                                size="small"
                                                onClick={() => onViewClick(client.id)}
                                            >
                                                <ViewIcon />
                                            </IconButton>
                                        </Tooltip>
                                        <Tooltip title="Редактировать">
                                            <IconButton
                                                size="small"
                                                onClick={() => onEditClick(client.id)}
                                            >
                                                <EditIcon />
                                            </IconButton>
                                        </Tooltip>
                                        <Tooltip title="Удалить">
                                            <IconButton
                                                size="small"
                                                color="error"
                                                onClick={() => onDeleteClick(client.id)}
                                            >
                                                <DeleteIcon />
                                            </IconButton>
                                        </Tooltip>
                                    </TableCell>
                                </TableRow>
                            ))
                        ) : (
                            <TableRow>
                                <TableCell colSpan={5} align="center">
                                    <Typography variant="body1" color="text.secondary" py={3}>
                                        {searchQuery
                                            ? 'По вашему запросу клиенты не найдены'
                                            : 'Список клиентов пуст'}
                                    </Typography>
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>

                {/* Пагинация */}
                <TablePagination
                    rowsPerPageOptions={[5, 10, 25]}
                    component="div"
                    count={total}
                    rowsPerPage={rowsPerPage}
                    page={page}
                    onPageChange={onPageChange}
                    onRowsPerPageChange={onRowsPerPageChange}
                    labelRowsPerPage="Строк на странице"
                    labelDisplayedRows={({ from, to, count }) => `${from}-${to} из ${count}`}
                />
            </TableContainer>
        </Box>
    );
};

export default ClientList;