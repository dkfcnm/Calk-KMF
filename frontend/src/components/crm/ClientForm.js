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
import { TimePicker } from '@mui/x-date-pickers/TimePicker';
import { ru } from 'date-fns/locale';
import { format } from 'date-fns';

/**
 * Компонент формы для добавления/редактирования клиента
 * 
 * @param {Object} props.client - данные клиента (null для нового клиента)
 * @param {Function} props.onSave - обработчик сохранения
 * @param {Function} props.onCancel - обработчик отмены
 */
const ClientForm = ({ client = null, onSave, onCancel }) => {
    // Начальные значения полей
    const initialFormData = {
        name: '',
        email: '',
        phone: '',
        birth_date: null,
        birth_time: null,
        notes: ''
    };

    // Состояния формы
    const [formData, setFormData] = useState(initialFormData);
    const [errors, setErrors] = useState({});
    const [submitAttempted, setSubmitAttempted] = useState(false);

    // Инициализация данных при редактировании существующего клиента
    useEffect(() => {
        if (client) {
            const birthTime = client.birth_time ?
                new Date(`2023-01-01T${client.birth_time}`) : null;

            setFormData({
                name: client.name || '',
                email: client.email || '',
                phone: client.phone || '',
                birth_date: client.birth_date ? new Date(client.birth_date) : null,
                birth_time: birthTime,
                notes: client.notes || ''
            });
        }
    }, [client]);

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

    // Обработчик изменения даты рождения
    const handleDateChange = (date) => {
        setFormData(prevData => ({
            ...prevData,
            birth_date: date
        }));

        if (errors.birth_date) {
            validateField('birth_date', date);
        }
    };

    // Обработчик изменения времени рождения
    const handleTimeChange = (time) => {
        setFormData(prevData => ({
            ...prevData,
            birth_time: time
        }));
    };

    // Валидация отдельного поля
    const validateField = (field, value) => {
        let error = null;

        switch (field) {
            case 'name':
                if (!value || value.trim() === '') {
                    error = 'ФИО обязательно для заполнения';
                } else if (value.length < 2) {
                    error = 'ФИО должно содержать не менее 2 символов';
                }
                break;

            case 'email':
                if (value && !/^\S+@\S+\.\S+$/.test(value)) {
                    error = 'Некорректный формат email';
                }
                break;

            case 'phone':
                if (value && !/^[\d\s()+\-]+$/.test(value)) {
                    error = 'Некорректный формат телефона';
                }
                break;

            case 'birth_date':
                if (value && value > new Date()) {
                    error = 'Дата рождения не может быть в будущем';
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
            name: validateField('name', formData.name),
            email: validateField('email', formData.email),
            phone: validateField('phone', formData.phone),
            birth_date: validateField('birth_date', formData.birth_date)
        };

        return Object.values(fieldValidations).every(isValid => isValid);
    };

    // Форматирование времени для отправки на сервер
    const formatTimeForSubmit = (timeDate) => {
        if (!timeDate) return null;
        return format(timeDate, 'HH:mm:ss');
    };

    // Обработчик отправки формы
    const handleSubmit = (event) => {
        event.preventDefault();
        setSubmitAttempted(true);

        if (validateForm()) {
            const dataToSubmit = {
                ...formData,
                birth_time: formatTimeForSubmit(formData.birth_time)
            };

            onSave(dataToSubmit);
        }
    };

    return (
        <Paper sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
                {client ? 'Редактирование клиента' : 'Добавление нового клиента'}
            </Typography>
            <Divider sx={{ mb: 3 }} />

            <Box component="form" onSubmit={handleSubmit} noValidate>
                <Grid container spacing={3}>
                    <Grid item xs={12}>
                        <TextField
                            label="ФИО клиента"
                            fullWidth
                            required
                            value={formData.name}
                            onChange={handleChange('name')}
                            error={Boolean(submitAttempted && errors.name)}
                            helperText={submitAttempted && errors.name}
                            onBlur={() => validateField('name', formData.name)}
                        />
                    </Grid>

                    <Grid item xs={12} md={6}>
                        <TextField
                            label="Email"
                            fullWidth
                            type="email"
                            value={formData.email}
                            onChange={handleChange('email')}
                            error={Boolean(submitAttempted && errors.email)}
                            helperText={submitAttempted && errors.email}
                            onBlur={() => validateField('email', formData.email)}
                        />
                    </Grid>

                    <Grid item xs={12} md={6}>
                        <TextField
                            label="Телефон"
                            fullWidth
                            value={formData.phone}
                            onChange={handleChange('phone')}
                            error={Boolean(submitAttempted && errors.phone)}
                            helperText={submitAttempted && errors.phone}
                            onBlur={() => validateField('phone', formData.phone)}
                        />
                    </Grid>

                    <Grid item xs={12} md={6}>
                        <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={ru}>
                            <DatePicker
                                label="Дата рождения"
                                value={formData.birth_date}
                                onChange={handleDateChange}
                                renderInput={(params) => (
                                    <TextField
                                        {...params}
                                        fullWidth
                                        error={Boolean(submitAttempted && errors.birth_date)}
                                        helperText={submitAttempted && errors.birth_date}
                                    />
                                )}
                                disableFuture
                            />
                        </LocalizationProvider>
                    </Grid>

                    <Grid item xs={12} md={6}>
                        <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={ru}>
                            <TimePicker
                                label="Время рождения"
                                value={formData.birth_time}
                                onChange={handleTimeChange}
                                renderInput={(params) => (
                                    <TextField
                                        {...params}
                                        fullWidth
                                    />
                                )}
                                ampm={false}
                            />
                        </LocalizationProvider>
                        <FormHelperText>
                            Используется для астрологических расчетов
                        </FormHelperText>
                    </Grid>

                    <Grid item xs={12}>
                        <TextField
                            label="Примечания"
                            fullWidth
                            multiline
                            rows={4}
                            value={formData.notes}
                            onChange={handleChange('notes')}
                        />
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
                                {client ? 'Сохранить изменения' : 'Добавить клиента'}
                            </Button>
                        </Box>
                    </Grid>
                </Grid>
            </Box>
        </Paper>
    );
};

export default ClientForm;