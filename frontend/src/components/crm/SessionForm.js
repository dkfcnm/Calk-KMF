import React, { useState, useEffect } from 'react';
import {
    Box,
    TextField,
    Button,
    Grid,
    Paper,
    Typography,
    Divider,
    FormHelperText
} from '@mui/material';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { ru } from 'date-fns/locale';

/**
 * Компонент формы для добавления/редактирования сессии клиента
 * 
 * @param {Object} props.session - данные сессии (null для новой сессии)
 * @param {number} props.clientId - ID клиента
 * @param {Function} props.onSave - обработчик сохранения
 * @param {Function} props.onCancel - обработчик отмены
 */
const SessionForm = ({ session = null, clientId, onSave, onCancel }) => {
    // Начальные значения полей
    const initialFormData = {
        client_id: clientId,
        date: new Date(),
        notes: '',
        summary: ''
    };

    // Состояния формы
    const [formData, setFormData] = useState(initialFormData);
    const [errors, setErrors] = useState({});
    const [submitAttempted, setSubmitAttempted] = useState(false);

    // Инициализация данных при редактировании существующей сессии
    useEffect(() => {
        if (session) {
            setFormData({
                client_id: session.client_id || clientId,
                date: session.date ? new Date(session.date) : new Date(),
                notes: session.notes || '',
                summary: session.summary || ''
            });
        }
    }, [session, clientId]);

    // Обработчик изменения полей
    const handleChange = (field) => (event) => {
        const value = event.target.value;

        setFormData(prevData => ({
            ...prevData,
            [field]: value
        }));

        // Если поле было с ошибкой, выполняем повторную валидацию
        if (errors[field]) {
            validateField(field, value);
        }
    };

    // Обработчик изменения даты сессии
    const handleDateChange = (date) => {
        setFormData(prevData => ({
            ...prevData,
            date: date
        }));

        if (errors.date) {
            validateField('date', date);
        }
    };

    // Валидация отдельного поля
    const validateField = (field, value) => {
        let error = null;

        switch (field) {
            case 'date':
                if (!value) {
                    error = 'Дата сессии обязательна для заполнения';
                }
                break;

            default:
                break;
        }

        setErrors(prevErrors => ({
            ...prevErrors,
            [field]: error
        }));

        return !error;
    };

    // Валидация всей формы
    const validateForm = () => {
        const fieldValidations = {
            date: validateField('date', formData.date),
        };

        return Object.values(fieldValidations).every(isValid => isValid);
    };

    // Обработчик отправки формы
    const handleSubmit = (event) => {
        event.preventDefault();
        setSubmitAttempted(true);

        if (validateForm()) {
            onSave(formData);
        }
    };

    return (
        <Paper sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
                {session ? 'Редактирование сессии' : 'Новая сессия'}
            </Typography>
            <Divider sx={{ mb: 3 }} />

            <Box component="form" onSubmit={handleSubmit} noValidate>
                <Grid container spacing={3}>
                    <Grid item xs={12}>
                        <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={ru}>
                            <DatePicker
                                label="Дата сессии"
                                value={formData.date}
                                onChange={handleDateChange}
                                renderInput={(params) => (
                                    <TextField
                                        {...params}
                                        fullWidth
                                        error={Boolean(submitAttempted && errors.date)}
                                        helperText={submitAttempted && errors.date}
                                    />
                                )}
                            />
                        </LocalizationProvider>
                    </Grid>

                    <Grid item xs={12}>
                        <TextField
                            label="Итоги сессии"
                            fullWidth
                            multiline
                            rows={2}
                            value={formData.summary}
                            onChange={handleChange('summary')}
                        />
                        <FormHelperText>
                            Краткий итог выполненной работы
                        </FormHelperText>
                    </Grid>

                    <Grid item xs={12}>
                        <TextField
                            label="Заметки"
                            fullWidth
                            multiline
                            rows={4}
                            value={formData.notes}
                            onChange={handleChange('notes')}
                        />
                        <FormHelperText>
                            Подробные записи о ходе сессии
                        </FormHelperText>
                    </Grid>

                    <Grid item xs={12}>
                        <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
                            <Button
                                variant="outlined"
                                onClick={onCancel}
                            >
                                Отмена
                            </Button>
                            <Button
                                variant="contained"
                                type="submit"
                                color="primary"
                            >
                                {session ? 'Сохранить изменения' : 'Добавить сессию'}
                            </Button>
                        </Box>
                    </Grid>
                </Grid>
            </Box>
        </Paper>
    );
};

export default SessionForm;