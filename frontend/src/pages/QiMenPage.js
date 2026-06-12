import React, { useState, useEffect } from 'react';
import {
    Typography,
    Box,
    Paper,
    Grid,
    ToggleButtonGroup,
    ToggleButton,
    TextField,
    Button,
    CircularProgress,
    Tabs,
    Tab,
    Card,
    CardContent,
    Divider,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    Chip
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { ru } from 'date-fns/locale';
import { format } from 'date-fns';

import qimenService from '../services/qimenService';
import { generateId } from '../hooks/useElementId';

import {
    QimenGridV2,
    PalaceExtendedInfo,
    QimenSummaryPanel
} from '../components/qimen';

// Уровни раскладов
const LEVEL_TABS = {
    HOUR: 'hour',
    DAY: 'day',
    MONTH: 'month',
    YEAR: 'year'
};

const LEVEL_LABELS = {
    [LEVEL_TABS.HOUR]: 'Час',
    [LEVEL_TABS.DAY]: 'День',
    [LEVEL_TABS.MONTH]: 'Месяц',
    [LEVEL_TABS.YEAR]: 'Год'
};

// 12 китайских часов (двухчасовые интервалы)
const CHINESE_HOURS = [
    { label: '23:00 – 01:00 (Цзы)', value: 0 },
    { label: '01:00 – 03:00 (Чоу)', value: 1 },
    { label: '03:00 – 05:00 (Инь)', value: 2 },
    { label: '05:00 – 07:00 (Мао)', value: 3 },
    { label: '07:00 – 09:00 (Чэнь)', value: 4 },
    { label: '09:00 – 11:00 (Сы)', value: 5 },
    { label: '11:00 – 13:00 (У)', value: 6 },
    { label: '13:00 – 15:00 (Вэй)', value: 7 },
    { label: '15:00 – 17:00 (Шэнь)', value: 8 },
    { label: '17:00 – 19:00 (Ю)', value: 9 },
    { label: '19:00 – 21:00 (Сюй)', value: 10 },
    { label: '21:00 – 23:00 (Хай)', value: 11 },
];

function QimenPage() {
    // Состояние компонента
    const [levelTab, setLevelTab] = useState(LEVEL_TABS.HOUR);
    const [method, setMethod] = useState('zhirun');
    const [selectedDate, setSelectedDate] = useState(new Date());
    const [selectedHourIndex, setSelectedHourIndex] = useState(0);
    const [allLevelsData, setAllLevelsData] = useState(null);
    const [chartData, setChartData] = useState(null);
    const [selectedPalace, setSelectedPalace] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Загрузка данных при изменении даты, метода или уровня
    useEffect(() => {
        let isCancelled = false;

        const loadData = async () => {
            if (isCancelled) return;
            setLoading(true);
            setError(null);
            setSelectedPalace(null);

            try {
                // Загружаем все уровни за один запрос
                const data = await qimenService.fetchAllLevels(method, selectedDate);
                if (isCancelled) return;
                setAllLevelsData(data);

                // Устанавливаем текущий расклад в зависимости от выбранного уровня
                updateChartForLevel(data, levelTab, selectedHourIndex);
            } catch (err) {
                if (isCancelled) return;
                console.error('Ошибка при загрузке раскладов:', err);
                setError('Не удалось загрузить расклады. Пожалуйста, попробуйте позже.');
            } finally {
                if (!isCancelled) setLoading(false);
            }
        };

        loadData();

        return () => {
            isCancelled = true;
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [selectedDate, method]);

    // Обновляем отображаемый расклад при смене уровня или часа
    useEffect(() => {
        if (allLevelsData) {
            updateChartForLevel(allLevelsData, levelTab, selectedHourIndex);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [levelTab, selectedHourIndex]);

    const updateChartForLevel = (data, level, hourIdx) => {
        setSelectedPalace(null);
        if (level === LEVEL_TABS.HOUR) {
            const hours = data.hours || [];
            if (hours.length > 0 && hourIdx < hours.length) {
                setChartData(hours[hourIdx]);
            } else if (hours.length > 0) {
                setChartData(hours[0]);
            } else {
                setChartData(null);
            }
        } else if (level === LEVEL_TABS.DAY) {
            setChartData(data.day);
        } else if (level === LEVEL_TABS.MONTH) {
            setChartData(data.month);
        } else if (level === LEVEL_TABS.YEAR) {
            setChartData(data.year);
        }
    };

    // Обработчик клика по дворцу
    const handlePalaceClick = (palaceNo) => {
        setSelectedPalace(palaceNo);
    };

    // Получение данных выбранного дворца
    const getSelectedPalaceData = () => {
        if (!chartData || !selectedPalace || !chartData.palaces) return null;
        return chartData.palaces[selectedPalace];
    };

    // Отображение загрузки
    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }} data-element-id={generateId('qimen', 'loading')}>
                <CircularProgress />
            </Box>
        );
    }

    return (
        <Box data-element-id={generateId('qimen', 'page')}>
            <Typography variant="h4" component="h1" gutterBottom data-element-id={generateId('qimen', 'title')}>
                Расклады Ци Мэнь
            </Typography>

            {/* Панель управления */}
            <Paper sx={{ mb: 3, p: 2 }}>
                <Grid container spacing={3} alignItems="center">
                    {/* Методология */}
                    <Grid item xs={12} md={4}>
                        <Typography variant="subtitle1" gutterBottom>
                            Методология расчета
                        </Typography>
                        <ToggleButtonGroup
                            value={method}
                            exclusive
                            onChange={(e, newMethod) => {
                                if (newMethod !== null) {
                                    setMethod(newMethod);
                                }
                            }}
                            aria-label="методология расчета"
                            fullWidth
                        >
                            <ToggleButton value="zhirun">
                                Джи Жэнь
                            </ToggleButton>
                            <ToggleButton value="chauby">
                                Чай Бу
                            </ToggleButton>
                        </ToggleButtonGroup>
                    </Grid>

                    {/* Дата */}
                    <Grid item xs={12} md={4}>
                        <Typography variant="subtitle1" gutterBottom>
                            Дата
                        </Typography>
                        <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={ru}>
                            <DatePicker
                                label="Выберите дату"
                                value={selectedDate}
                                onChange={(newDate) => {
                                    if (newDate) setSelectedDate(newDate);
                                }}
                                renderInput={(params) => <TextField {...params} fullWidth />}
                                format="dd.MM.yyyy"
                            />
                        </LocalizationProvider>
                    </Grid>

                    {/* Уровень расклада */}
                    <Grid item xs={12} md={4}>
                        <Typography variant="subtitle1" gutterBottom>
                            Уровень расклада
                        </Typography>
                        <Tabs
                            value={levelTab}
                            onChange={(e, newTab) => setLevelTab(newTab)}
                            aria-label="уровень расклада"
                            variant="fullWidth"
                        >
                            <Tab label="Час" value={LEVEL_TABS.HOUR} />
                            <Tab label="День" value={LEVEL_TABS.DAY} />
                            <Tab label="Месяц" value={LEVEL_TABS.MONTH} />
                            <Tab label="Год" value={LEVEL_TABS.YEAR} />
                        </Tabs>
                    </Grid>
                </Grid>

                {/* Селектор часа (только для уровня Час) */}
                {levelTab === LEVEL_TABS.HOUR && (
                    <Box sx={{ mt: 2 }}>
                        <FormControl fullWidth>
                            <InputLabel id="hour-select-label">Двухчасовой интервал</InputLabel>
                            <Select
                                labelId="hour-select-label"
                                value={selectedHourIndex}
                                label="Двухчасовой интервал"
                                onChange={(e) => setSelectedHourIndex(e.target.value)}
                            >
                                {CHINESE_HOURS.map((h) => (
                                    <MenuItem key={h.value} value={h.value}>
                                        {h.label}
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </Box>
                )}

                {/* Информация о загруженных данных */}
                {allLevelsData && (
                    <Box sx={{ mt: 2 }}>
                        <Divider />
                        <Box sx={{ mt: 1, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                            {allLevelsData.year && (
                                <Chip
                                    size="small"
                                    label={`Год: ${allLevelsData.year.chart_num} ${allLevelsData.year.yin_yang}`}
                                    color={levelTab === LEVEL_TABS.YEAR ? 'primary' : 'default'}
                                    variant={levelTab === LEVEL_TABS.YEAR ? 'filled' : 'outlined'}
                                    onClick={() => setLevelTab(LEVEL_TABS.YEAR)}
                                    sx={{ cursor: 'pointer' }}
                                />
                            )}
                            {allLevelsData.month && (
                                <Chip
                                    size="small"
                                    label={`Месяц: ${allLevelsData.month.chart_num} ${allLevelsData.month.yin_yang}`}
                                    color={levelTab === LEVEL_TABS.MONTH ? 'primary' : 'default'}
                                    variant={levelTab === LEVEL_TABS.MONTH ? 'filled' : 'outlined'}
                                    onClick={() => setLevelTab(LEVEL_TABS.MONTH)}
                                    sx={{ cursor: 'pointer' }}
                                />
                            )}
                            {allLevelsData.day && (
                                <Chip
                                    size="small"
                                    label={`День: ${allLevelsData.day.chart_num} ${allLevelsData.day.yin_yang}`}
                                    color={levelTab === LEVEL_TABS.DAY ? 'primary' : 'default'}
                                    variant={levelTab === LEVEL_TABS.DAY ? 'filled' : 'outlined'}
                                    onClick={() => setLevelTab(LEVEL_TABS.DAY)}
                                    sx={{ cursor: 'pointer' }}
                                />
                            )}
                            {allLevelsData.hours && allLevelsData.hours[selectedHourIndex] && (
                                <Chip
                                    size="small"
                                    label={`Час: ${allLevelsData.hours[selectedHourIndex].chart_num} ${allLevelsData.hours[selectedHourIndex].yin_yang}`}
                                    color={levelTab === LEVEL_TABS.HOUR ? 'primary' : 'default'}
                                    variant={levelTab === LEVEL_TABS.HOUR ? 'filled' : 'outlined'}
                                    onClick={() => setLevelTab(LEVEL_TABS.HOUR)}
                                    sx={{ cursor: 'pointer' }}
                                />
                            )}
                        </Box>
                    </Box>
                )}
            </Paper>

            {/* Сообщение об ошибке */}
            {error && (
                <Paper sx={{ p: 3, bgcolor: 'error.light', color: 'error.contrastText', mb: 3 }}>
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

            {/* Отображение расклада */}
            {!error && chartData && (
                <Grid container spacing={3}>
                    <Grid item xs={12} lg={3}>
                        <QimenSummaryPanel chart={chartData} />
                    </Grid>

                    <Grid item xs={12} lg={6}>
                        <QimenGridV2
                            chart={chartData}
                            selectedPalace={selectedPalace}
                            onPalaceClick={handlePalaceClick}
                            levelLabel={LEVEL_LABELS[levelTab]}
                        />
                    </Grid>

                    <Grid item xs={12} lg={3}>
                        <PalaceExtendedInfo palace={getSelectedPalaceData()} chart={chartData} />
                    </Grid>
                </Grid>
            )}

            {/* Нет данных */}
            {!error && !chartData && !loading && (
                <Paper sx={{ p: 3, textAlign: 'center' }}>
                    <Typography color="text.secondary">
                        Нет данных для выбранной даты и уровня
                    </Typography>
                </Paper>
            )}
        </Box>
    );
}

export default QimenPage;
