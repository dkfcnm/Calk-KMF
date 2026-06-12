import React, { useState, useEffect, useCallback } from 'react';
import {
    Box, Typography, Paper, Button, TextField, Dialog, DialogTitle,
    DialogContent, DialogActions, IconButton, Alert, CircularProgress,
    Card, CardContent, Grid, Chip, Autocomplete
} from '@mui/material';
import {
    PersonAdd, Delete, Edit, Calculate
} from '@mui/icons-material';
import profileService from '../services/profileService';

function ProfilesPage() {
    const [profiles, setProfiles] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [openDialog, setOpenDialog] = useState(false);
    const [editingProfile, setEditingProfile] = useState(null);
    const [formData, setFormData] = useState({
        name: '', birth_date: '', birth_time: '', birth_city: '', notes: '',
        birth_city_lat: null, birth_city_lon: null, birth_timezone: ''
    });
    const [cityOptions, setCityOptions] = useState([]);
    const [cityLoading, setCityLoading] = useState(false);

    const loadProfiles = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await profileService.listProfiles();
            setProfiles(data.items || []);
        } catch (e) {
            setError('Ошибка загрузки профилей: ' + e.message);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        loadProfiles();
    }, [loadProfiles]);

    const handleOpenCreate = () => {
        setEditingProfile(null);
        setFormData({ name: '', birth_date: '', birth_time: '', birth_city: '', notes: '', birth_city_lat: null, birth_city_lon: null, birth_timezone: '' });
        setCityOptions([]);
        setOpenDialog(true);
    };

    const handleOpenEdit = (profile) => {
        setEditingProfile(profile);
        setFormData({
            name: profile.name || '',
            birth_date: profile.birth_date || '',
            birth_time: profile.birth_time || '',
            birth_city: profile.birth_city || '',
            notes: profile.notes || '',
            birth_city_lat: profile.birth_city_lat || null,
            birth_city_lon: profile.birth_city_lon || null,
            birth_timezone: profile.birth_timezone || '',
        });
        setOpenDialog(true);
    };

    const handleCloseDialog = () => {
        setOpenDialog(false);
    };

    const handleSave = async () => {
        try {
            if (editingProfile) {
                await profileService.updateProfile(editingProfile.id, formData);
            } else {
                await profileService.createProfile(formData);
            }
            setOpenDialog(false);
            loadProfiles();
        } catch (e) {
            setError('Ошибка сохранения: ' + e.message);
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm('Удалить профиль?')) return;
        try {
            await profileService.deleteProfile(id);
            loadProfiles();
        } catch (e) {
            setError('Ошибка удаления: ' + e.message);
        }
    };

    const handleCalculate = async (id) => {
        try {
            await profileService.calculateChart(id);
            loadProfiles();
        } catch (e) {
            setError('Ошибка расчета: ' + e.message);
        }
    };

    return (
        <Box data-element-id="profiles-page" sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h4" component="h1" data-element-id="profiles-title">
                    Профили
                </Typography>
                <Box>
                    <Button
                        variant="contained"
                        startIcon={<PersonAdd />}
                        onClick={handleOpenCreate}
                        data-element-id="profiles-add-btn"
                    >
                        Добавить профиль
                    </Button>
                </Box>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
                    {error}
                </Alert>
            )}

            {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                    <CircularProgress />
                </Box>
            ) : profiles.length === 0 ? (
                <Paper sx={{ p: 4, textAlign: 'center' }} data-element-id="profiles-empty">
                    <Typography color="text.secondary">
                        Профили не созданы. Нажмите «Добавить профиль» чтобы создать первый.
                    </Typography>
                </Paper>
            ) : (
                <Grid container spacing={2}>
                    {profiles.map((profile) => (
                        <Grid item xs={12} md={6} key={profile.id}>
                            <Card data-element-id={`profile-card-${profile.id}`}>
                                <CardContent>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                        <Box>
                                            <Typography variant="h6">{profile.name}</Typography>
                                            <Typography variant="body2" color="text.secondary">
                                                {profile.birth_date}{profile.birth_time ? ` ${profile.birth_time}` : ''}
                                            </Typography>
                                            {profile.birth_city && (
                                                <Typography variant="body2" color="text.secondary">
                                                    📍 {profile.birth_city}
                                                </Typography>
                                            )}
                                        </Box>
                                        <Box>
                                            <IconButton
                                                size="small"
                                                onClick={() => handleCalculate(profile.id)}
                                                title="Рассчитать карту"
                                                data-element-id={`profile-calc-${profile.id}`}
                                            >
                                                <Calculate />
                                            </IconButton>
                                            <IconButton
                                                size="small"
                                                onClick={() => handleOpenEdit(profile)}
                                                title="Редактировать"
                                                data-element-id={`profile-edit-${profile.id}`}
                                            >
                                                <Edit />
                                            </IconButton>
                                            <IconButton
                                                size="small"
                                                onClick={() => handleDelete(profile.id)}
                                                title="Удалить"
                                                data-element-id={`profile-delete-${profile.id}`}
                                            >
                                                <Delete />
                                            </IconButton>
                                        </Box>
                                    </Box>

                                    {profile.birth_chart && (
                                        <Box sx={{ mt: 1 }}>
                                            <Chip
                                                label={`${profile.birth_chart.year_pillar} ${profile.birth_chart.month_pillar} ${profile.birth_chart.day_pillar} ${profile.birth_chart.hour_pillar}`}
                                                size="small"
                                                color="primary"
                                                data-element-id={`profile-chart-${profile.id}`}
                                            />
                                            {profile.birth_chart.day_master && (
                                                <Chip
                                                    label={`Дневной господин: ${profile.birth_chart.day_master}`}
                                                    size="small"
                                                    sx={{ ml: 1 }}
                                                />
                                            )}
                                        </Box>
                                    )}

                                    {profile.notes && (
                                        <Typography variant="body2" sx={{ mt: 1 }}>
                                            {profile.notes}
                                        </Typography>
                                    )}
                                </CardContent>
                            </Card>
                        </Grid>
                    ))}
                </Grid>
            )}

            <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
                <DialogTitle>
                    {editingProfile ? 'Редактировать профиль' : 'Новый профиль'}
                </DialogTitle>
                <DialogContent>
                    <TextField
                        autoFocus
                        margin="dense"
                        label="Имя"
                        fullWidth
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        data-element-id="profile-form-name"
                    />
                    <TextField
                        margin="dense"
                        label="Дата рождения"
                        type="date"
                        fullWidth
                        InputLabelProps={{ shrink: true }}
                        value={formData.birth_date}
                        onChange={(e) => setFormData({ ...formData, birth_date: e.target.value })}
                        data-element-id="profile-form-date"
                    />
                    <TextField
                        margin="dense"
                        label="Время рождения"
                        type="time"
                        fullWidth
                        InputLabelProps={{ shrink: true }}
                        value={formData.birth_time}
                        onChange={(e) => setFormData({ ...formData, birth_time: e.target.value })}
                        data-element-id="profile-form-time"
                    />
                    <Autocomplete
                        freeSolo
                        options={cityOptions}
                        getOptionLabel={(option) => typeof option === 'string' ? option : option.city_name_ru || ''}
                        loading={cityLoading}
                        value={formData.birth_city}
                        inputValue={formData.birth_city}
                        onInputChange={async (event, newInputValue) => {
                            setFormData({ ...formData, birth_city: newInputValue });
                            if (newInputValue.length >= 2) {
                                setCityLoading(true);
                                try {
                                    const result = await profileService.searchCities(newInputValue);
                                    setCityOptions(result.cities || []);
                                } catch (e) {
                                    setCityOptions([]);
                                } finally {
                                    setCityLoading(false);
                                }
                            }
                        }}
                        onChange={(event, newValue) => {
                            if (newValue && typeof newValue === 'object') {
                                setFormData({
                                    ...formData,
                                    birth_city: newValue.city_name_ru,
                                    birth_city_lat: newValue.lat,
                                    birth_city_lon: newValue.lon,
                                    birth_timezone: newValue.timezone,
                                });
                            } else if (typeof newValue === 'string') {
                                setFormData({ ...formData, birth_city: newValue });
                            }
                        }}
                        renderInput={(params) => (
                            <TextField
                                {...params}
                                margin="dense"
                                label="Город рождения"
                                fullWidth
                                data-element-id="profile-form-city"
                            />
                        )}
                    />
                    <TextField
                        margin="dense"
                        label="Заметки"
                        fullWidth
                        multiline
                        rows={3}
                        value={formData.notes}
                        onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                        data-element-id="profile-form-notes"
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseDialog}>Отмена</Button>
                    <Button onClick={handleSave} variant="contained">
                        {editingProfile ? 'Сохранить' : 'Создать'}
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
}

export default ProfilesPage;
