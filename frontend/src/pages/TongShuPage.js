import React, { useState, useEffect, useMemo } from 'react';
import {
    Typography,
    Box,
    Paper,
    Grid,
    Tabs,
    Tab,
    Card,
    CardContent,
    CardHeader,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Chip,
    Button,
    CircularProgress,
    TextField,
    Tooltip,
    IconButton,
    ToggleButtonGroup,
    ToggleButton,
    FormControl,
    InputLabel,
    Select,
    MenuItem
} from '@mui/material';
import {
    ChevronLeft as ChevronLeftIcon,
    ChevronRight as ChevronRightIcon,
    ViewModule as GridViewIcon,
    ViewList as ListViewIcon,
    ExpandMore as ExpandMoreIcon,
    ExpandLess as ExpandLessIcon
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { ru } from 'date-fns/locale';
import {
    format,
    parseISO,
    startOfWeek,
    startOfMonth,
    endOfMonth,
    isSameDay,
    addMonths,
    subMonths,
    setYear,
    setMonth
} from 'date-fns';

import tongShuService from '../services/tongShuService';
import refsService from '../services/refsService';
import fengShuiService from '../services/fengShuiService';
import profileService from '../services/profileService';
import CalendarGrid from '../components/tongshu/MonthlyCalendar/CalendarGrid';
import FlyingStarsGrid from '../components/fengshui/FlyingStarsGrid';
import { generateId } from '../hooks/useElementId';

const VIEW_MODES = {
    DAY: 0,
    WEEK: 1,
    MONTH: 2,
    YEAR: 3
};

const MONTH_NAMES = [
    'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
    'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
];

// Color coding for belt type
const getBeltColor = (beltType) => {
    switch (beltType) {
        case 'yellow': return 'success';
        case 'black': return 'error';
        default: return 'default';
    }
};

// Color coding for officer category
const getOfficerColor = (category) => {
    switch (category) {
        case 'auspicious': return 'success';
        case 'inauspicious': return 'error';
        default: return 'warning';
    }
};

// Color coding for constellation nature
const getConstellationColor = (nature) => {
    switch (nature) {
        case 'auspicious': return 'success';
        case 'inauspicious': return 'error';
        default: return 'warning';
    }
};

function renderPillar(pillar, stemColors, branchColors) {
    if (!pillar || pillar.length < 2) return <Typography component="span">{pillar}</Typography>;
    const stem = pillar[0];
    const branch = pillar[1];
    return (
        <Box component="span">
            <Typography component="span" sx={{ color: stemColors[stem] || 'inherit', fontWeight: 'bold' }}>{stem}</Typography>
            <Typography component="span" sx={{ color: branchColors[branch] || 'inherit', fontWeight: 'bold' }}>{branch}</Typography>
        </Box>
    );
}

function TongShuPage() {
    const [viewMode, setViewMode] = useState(VIEW_MODES.MONTH);
    const [selectedDate, setSelectedDate] = useState(new Date(2026, 4, 16)); // May 16, 2026
    const [tongShuData, setTongShuData] = useState(null);
    const [flyingStarsData, setFlyingStarsData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [monthViewMode, setMonthViewMode] = useState('grid'); // 'grid' | 'table'
    const [refsData, setRefsData] = useState({ elements: [], stems: [], branches: [] });
    const [profiles, setProfiles] = useState([]);
    const [selectedProfile, setSelectedProfile] = useState(null);
    const [personalizedData, setPersonalizedData] = useState(null);
    const [hoursData, setHoursData] = useState(null);

    useEffect(() => {
        const loadRefs = async () => {
            try {
                const [elements, stems, branches] = await Promise.all([
                    refsService.fetchElements(),
                    refsService.fetchHeavenlyStems(),
                    refsService.fetchEarthlyBranches(),
                ]);
                setRefsData({ elements, stems, branches });
            } catch (err) {
                console.error('Failed to load reference colors', err);
            }
        };
        loadRefs();
    }, []);

    // Load profiles list
    useEffect(() => {
        const loadProfiles = async () => {
            try {
                const data = await profileService.listProfiles(0, 100);
                setProfiles(data.items || []);
            } catch (err) {
                console.error('Failed to load profiles', err);
            }
        };
        loadProfiles();
    }, []);

    const elementColors = useMemo(() => {
        const map = {};
        refsData.elements.forEach(el => {
            if (el.element_name_ru) map[el.element_name_ru] = el.color_hex;
            if (el.element_name_en) map[el.element_name_en] = el.color_hex;
            if (el.element_char) map[el.element_char] = el.color_hex;
        });
        return map;
    }, [refsData.elements]);

    const stemColors = useMemo(() => {
        const map = {};
        refsData.stems.forEach(s => {
            if (s.stem_char) map[s.stem_char] = s.color_hex;
        });
        return map;
    }, [refsData.stems]);

    const branchColors = useMemo(() => {
        const map = {};
        refsData.branches.forEach(b => {
            if (b.branch_char) map[b.branch_char] = b.color_hex;
        });
        return map;
    }, [refsData.branches]);

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            setError(null);

            try {
                let data;
                switch (viewMode) {
                    case VIEW_MODES.DAY:
                        data = await tongShuService.fetchDailyDayData(format(selectedDate, 'yyyy-MM-dd'));
                        break;
                    case VIEW_MODES.WEEK:
                        const weekStart = startOfWeek(selectedDate, { weekStartsOn: 1 });
                        data = await tongShuService.fetchDailyWeekData(format(weekStart, 'yyyy-MM-dd'));
                        break;
                    case VIEW_MODES.MONTH:
                        const monthStart = startOfMonth(selectedDate);
                        data = await tongShuService.fetchDailyMonthData(monthStart.getFullYear(), monthStart.getMonth() + 1);
                        break;
                    case VIEW_MODES.YEAR:
                        data = await tongShuService.fetchDailyYearData(selectedDate.getFullYear());
                        break;
                    default:
                        data = await tongShuService.fetchDailyDayData(format(selectedDate, 'yyyy-MM-dd'));
                }
                setTongShuData(data);
            } catch (err) {
                console.error("Ошибка при загрузке данных:", err);
                setError("Не удалось загрузить данные Тун Шу. Возможно, данные для выбранного периода ещё не сгенерированы.");
            } finally {
                setLoading(false);
            }
        };

        loadData();
    }, [viewMode, selectedDate]);

    // Загрузка данных Летящих Звезд для дневного вида
    useEffect(() => {
        const loadFlyingStars = async () => {
            if (viewMode !== VIEW_MODES.DAY) {
                setFlyingStarsData(null);
                return;
            }
            try {
                const chart = await fengShuiService.fetchFlyingStarsChart(format(selectedDate, 'yyyy-MM-dd'));
                setFlyingStarsData(chart);
            } catch (err) {
                console.error("Ошибка при загрузке Летящих Звезд:", err);
                setFlyingStarsData(null);
            }
        };

        loadFlyingStars();
    }, [viewMode, selectedDate]);

    // Загрузка почасовых данных для дневного вида
    useEffect(() => {
        const loadHours = async () => {
            if (viewMode !== VIEW_MODES.DAY) {
                setHoursData(null);
                return;
            }
            try {
                const data = await tongShuService.fetchHoursData(format(selectedDate, 'yyyy-MM-dd'));
                setHoursData(data);
            } catch (err) {
                console.error("Ошибка при загрузке почасовых данных:", err);
                setHoursData(null);
            }
        };

        loadHours();
    }, [viewMode, selectedDate]);

    // Загрузка персонализированных данных для дневного вида
    useEffect(() => {
        const loadPersonalized = async () => {
            if (viewMode !== VIEW_MODES.DAY || !selectedProfile) {
                setPersonalizedData(null);
                return;
            }
            try {
                const data = await tongShuService.fetchPersonalizedDayData(
                    format(selectedDate, 'yyyy-MM-dd'),
                    selectedProfile.id
                );
                setPersonalizedData(data);
            } catch (err) {
                console.error("Ошибка при загрузке персонализированных данных:", err);
                setPersonalizedData(null);
            }
        };

        loadPersonalized();
    }, [viewMode, selectedDate, selectedProfile]);

    // Navigation handlers for month view
    const handlePrevMonth = () => setSelectedDate(prev => subMonths(prev, 1));
    const handleNextMonth = () => setSelectedDate(prev => addMonths(prev, 1));
    const handleMonthChange = (monthIdx) => setSelectedDate(prev => setMonth(prev, monthIdx));
    const handleYearChange = (year) => setSelectedDate(prev => setYear(prev, year));

    // Click on calendar cell -> switch to Day view
    const handleDateClick = (date) => {
        setSelectedDate(date);
        setViewMode(VIEW_MODES.DAY);
    };

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
                <CircularProgress />
            </Box>
        );
    }

    const currentYear = selectedDate.getFullYear();
    const currentMonthIdx = selectedDate.getMonth();

    return (
        <Box>
            <Typography variant="h4" component="h1" gutterBottom>
                Календарь Тун Шу
            </Typography>

            <Paper sx={{ mb: 3, p: 2 }}>
                <Grid container spacing={2} alignItems="center">
                    {/* Tabs */}
                    <Grid item xs={12} md={viewMode === VIEW_MODES.DAY ? 6 : 12}>
                        <Tabs
                            value={viewMode}
                            onChange={(e, newValue) => setViewMode(newValue)}
                            aria-label="режимы просмотра"
                        >
                            <Tab label="День" value={VIEW_MODES.DAY} data-element-id={generateId('tongshu', 'tab', 'day')} />
                            <Tab label="Неделя" value={VIEW_MODES.WEEK} data-element-id={generateId('tongshu', 'tab', 'week')} />
                            <Tab label="Месяц" value={VIEW_MODES.MONTH} data-element-id={generateId('tongshu', 'tab', 'month')} />
                            <Tab label="Год" value={VIEW_MODES.YEAR} data-element-id={generateId('tongshu', 'tab', 'year')} />
                        </Tabs>
                    </Grid>

                    {/* DatePicker + Profile selector — only on Day view */}
                    {viewMode === VIEW_MODES.DAY && (
                        <>
                            <Grid item xs={12} md={4}>
                                <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={ru}>
                                    <DatePicker
                                        label="Выберите дату"
                                        value={selectedDate}
                                        onChange={(newDate) => newDate && setSelectedDate(newDate)}
                                        renderInput={(params) => <TextField {...params} fullWidth inputProps={{ ...params.inputProps, 'data-element-id': generateId('tongshu', 'datepicker', 'day') }} />}
                                        inputFormat="dd.MM.yyyy"
                                    />
                                </LocalizationProvider>
                            </Grid>
                            <Grid item xs={12} md={2}>
                                <FormControl fullWidth size="small">
                                    <InputLabel>Профиль</InputLabel>
                                    <Select
                                        value={selectedProfile ? selectedProfile.id : ''}
                                        label="Профиль"
                                        onChange={(e) => {
                                            const pid = e.target.value;
                                            const profile = profiles.find(p => p.id === pid);
                                            setSelectedProfile(profile || null);
                                        }}
                                    >
                                        <MenuItem value=""><em>Без профиля</em></MenuItem>
                                        {profiles.map(p => (
                                            <MenuItem key={p.id} value={p.id}>
                                                {p.name} {p.birth_chart ? `(${p.birth_chart.day_master})` : ''}
                                            </MenuItem>
                                        ))}
                                    </Select>
                                </FormControl>
                            </Grid>
                        </>
                    )}
                </Grid>
            </Paper>

            {error ? (
                <Paper sx={{ p: 3, bgcolor: 'error.light', color: 'error.contrastText' }}>
                    <Typography>{error}</Typography>
                    <Button
                        variant="contained"
                        color="primary"
                        sx={{ mt: 2 }}
                        onClick={() => window.location.reload()}
                        data-element-id={generateId('tongshu', 'action', 'retry')}
                    >
                        Попробовать снова
                    </Button>
                </Paper>
            ) : (
                <>
                    {viewMode === VIEW_MODES.DAY && tongShuData && (
                        <DailyDayView 
                            data={tongShuData} 
                            elementColors={elementColors} 
                            stemColors={stemColors} 
                            branchColors={branchColors} 
                            flyingStarsData={flyingStarsData}
                            personalizedData={personalizedData}
                            hoursData={hoursData}
                        />
                    )}
                    {viewMode === VIEW_MODES.WEEK && tongShuData && (
                        <DailyWeekView data={tongShuData} selectedDate={selectedDate} stemColors={stemColors} branchColors={branchColors} />
                    )}
                    {viewMode === VIEW_MODES.MONTH && tongShuData && (
                        <>
                            {/* Month navigation bar */}
                            <Paper sx={{ mb: 2, p: 2, display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
                                <IconButton onClick={handlePrevMonth} size="large" data-element-id={generateId('tongshu', 'nav', 'prev_month')}>
                                    <ChevronLeftIcon />
                                </IconButton>

                                <FormControl sx={{ minWidth: 140 }} size="small">
                                    <InputLabel>Месяц</InputLabel>
                                    <Select
                                        value={currentMonthIdx}
                                        label="Месяц"
                                        onChange={(e) => handleMonthChange(e.target.value)}
                                        inputProps={{ 'data-element-id': generateId('tongshu', 'select', 'month') }}
                                    >
                                        {MONTH_NAMES.map((name, idx) => (
                                            <MenuItem key={idx} value={idx}>{name}</MenuItem>
                                        ))}
                                    </Select>
                                </FormControl>

                                <FormControl sx={{ minWidth: 100 }} size="small">
                                    <InputLabel>Год</InputLabel>
                                    <Select
                                        value={currentYear}
                                        label="Год"
                                        onChange={(e) => handleYearChange(e.target.value)}
                                        inputProps={{ 'data-element-id': generateId('tongshu', 'select', 'year') }}
                                    >
                                        {Array.from({ length: 201 }, (_, i) => 1900 + i).map(year => (
                                            <MenuItem key={year} value={year}>{year}</MenuItem>
                                        ))}
                                    </Select>
                                </FormControl>

                                <Typography variant="h6" sx={{ flex: 1, textAlign: 'center' }}>
                                    {format(selectedDate, 'LLLL yyyy', { locale: ru })}
                                </Typography>

                                <ToggleButtonGroup
                                    value={monthViewMode}
                                    exclusive
                                    onChange={(e, val) => val && setMonthViewMode(val)}
                                    size="small"
                                >
                                    <ToggleButton value="grid" title="Сетка" data-element-id={generateId('tongshu', 'view_mode', 'grid')}>
                                        <GridViewIcon fontSize="small" />
                                    </ToggleButton>
                                    <ToggleButton value="table" title="Таблица" data-element-id={generateId('tongshu', 'view_mode', 'table')}>
                                        <ListViewIcon fontSize="small" />
                                    </ToggleButton>
                                </ToggleButtonGroup>

                                <IconButton onClick={handleNextMonth} size="large" data-element-id={generateId('tongshu', 'nav', 'next_month')}>
                                    <ChevronRightIcon />
                                </IconButton>
                            </Paper>

                            {monthViewMode === 'grid' ? (
                                <CalendarGrid
                                    data={tongShuData}
                                    selectedDate={selectedDate}
                                    currentDate={new Date()}
                                    onDateClick={handleDateClick}
                                    stemColors={stemColors}
                                    branchColors={branchColors}
                                />
                            ) : (
                                <DailyMonthView data={tongShuData} selectedDate={selectedDate} onDateClick={handleDateClick} stemColors={stemColors} branchColors={branchColors} />
                            )}
                        </>
                    )}
                    {viewMode === VIEW_MODES.YEAR && tongShuData && (
                        <DailyYearView data={tongShuData} selectedDate={selectedDate} stemColors={stemColors} branchColors={branchColors} />
                    )}
                </>
            )}
        </Box>
    );
}

// ---------------------------------------------------------------------------
// Day View
// ---------------------------------------------------------------------------
function HourlySlotRow({ slot, index, stemColors, branchColors, expanded, onToggle }) {
    return (
        <>
            <TableRow
                onClick={onToggle}
                sx={{
                    cursor: 'pointer',
                    bgcolor: expanded ? 'action.selected' : 'inherit',
                    '&:hover': { bgcolor: 'action.hover' }
                }}
            >
                <TableCell sx={{ py: 0.5 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        {expanded ? <ExpandLessIcon fontSize="small" sx={{ mr: 0.5 }} /> : <ExpandMoreIcon fontSize="small" sx={{ mr: 0.5 }} />}
                        <Typography variant="body2">{slot.time_str?.substring(0, 5) || `${index * 2}:00`}</Typography>
                    </Box>
                </TableCell>
                <TableCell sx={{ py: 0.5, fontWeight: 'bold' }}>
                    {renderPillar(slot.hour_pillar, stemColors, branchColors)}
                </TableCell>
                <TableCell sx={{ py: 0.5 }}>
                    {slot.ten_god && <Chip label={slot.ten_god} size="small" color="primary" variant="outlined" sx={{ fontSize: '0.7rem' }} />}
                </TableCell>
                <TableCell sx={{ py: 0.5 }}>
                    {slot.qi_phase && (
                        <Tooltip title={`Балл: ${slot.qi_phase_score || 0}`}>
                            <Chip label={slot.qi_phase} size="small" color="info" variant="outlined" sx={{ fontSize: '0.7rem' }} />
                        </Tooltip>
                    )}
                </TableCell>
            </TableRow>
            {expanded && (
                <TableRow>
                    <TableCell colSpan={4} sx={{ py: 1, bgcolor: 'background.default' }}>
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, pl: 2 }}>
                            {slot.hidden_stems && slot.hidden_stems.length > 0 && (
                                <Box>
                                    <Typography variant="caption" color="text.secondary">Скрытые стволы:</Typography>{' '}
                                    {slot.hidden_stems.map((hs, i) => (
                                        <Chip
                                            key={i}
                                            label={`${hs.stem} (${hs.percentage}%)`}
                                            size="small"
                                            color={hs.is_main ? 'primary' : 'default'}
                                            sx={{ mr: 0.5, fontSize: '0.7rem' }}
                                        />
                                    ))}
                                </Box>
                            )}
                            {slot.symbolic_stars && slot.symbolic_stars.length > 0 && (
                                <Box>
                                    <Typography variant="caption" color="text.secondary">Шэнь Ша:</Typography>{' '}
                                    {slot.symbolic_stars.map((star, i) => (
                                        <Tooltip key={i} title={star.notes || ''}>
                                            <Chip
                                                label={star.name}
                                                size="small"
                                                color={star.name.includes('煞') || star.name.includes('死') || star.name.includes('亡') ? 'error' : 'default'}
                                                sx={{ mr: 0.5, mb: 0.5, fontSize: '0.7rem' }}
                                            />
                                        </Tooltip>
                                    ))}
                                </Box>
                            )}
                        </Box>
                    </TableCell>
                </TableRow>
            )}
        </>
    );
}

function DailyDayView({ data, elementColors, stemColors, branchColors, flyingStarsData, personalizedData, hoursData }) {
    const [expandedHour, setExpandedHour] = useState(null);

    if (!data) return null;

    const pd = personalizedData;
    const profile = pd?.profile;

    const handleToggleHour = (index) => {
        setExpandedHour(expandedHour === index ? null : index);
    };

    return (
        <Card data-element-id={generateId('tongshu', 'card', 'dayview')}>
            <CardHeader
                title={`${data.day_pillar} — ${data.calendar_date ? data.calendar_date.split('-').reverse().join('.') : ''}`}
                subheader={`${data.year_pillar} (год), ${data.month_pillar} (месяц)`}
            />
            <CardContent>
                {profile && (
                    <Box sx={{ mb: 2, p: 1, bgcolor: 'primary.light', borderRadius: 1 }}>
                        <Typography variant="body2" sx={{ color: 'primary.contrastText' }}>
                            Профиль: <strong>{profile.name}</strong> | Дневной господин: <strong>{profile.day_master}</strong> ({profile.day_master_element})
                        </Typography>
                    </Box>
                )}
                <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                        <Typography variant="subtitle1" gutterBottom>Основные показатели:</Typography>
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                            <Box><strong>Столп дня:</strong> {renderPillar(data.day_pillar, stemColors, branchColors)}</Box>
                            <Box><strong>Столп месяца:</strong> {renderPillar(data.month_pillar, stemColors, branchColors)}</Box>
                            <Box><strong>Столп года:</strong> {renderPillar(data.year_pillar, stemColors, branchColors)}</Box>
                            <Box><strong>Сезон:</strong> {data.solar_term_char} ({data.solar_term_name_ru})</Box>
                            <Box><strong>На Инь:</strong> <Typography component="span" sx={{ color: elementColors[data.nayin_element] || 'inherit', fontWeight: 'bold' }}>{data.nayin_name}</Typography></Box>
                            <Box>
                                <strong>12 Офицеров:</strong>{' '}
                                <Chip
                                    label={`${data.day_officer_char} (${data.day_officer_name_ru})`}
                                    color={getOfficerColor(data.day_officer_category)}
                                    size="small"
                                    data-element-id={generateId('tongshu', 'chip', 'officer')}
                                />
                            </Box>
                            <Box>
                                <strong>28 Созвездий:</strong>{' '}
                                <Tooltip title={data.constellation_direction}>
                                    <Chip
                                        label={`${data.constellation_char} (${data.constellation_name_ru})`}
                                        color={getConstellationColor(data.constellation_nature)}
                                        size="small"
                                        data-element-id={generateId('tongshu', 'chip', 'constellation')}
                                    />
                                </Tooltip>
                            </Box>
                            <Box>
                                <strong>Пояс:</strong>{' '}
                                <Chip
                                    label={data.belt_type === 'yellow' ? 'Жёлтый' : data.belt_type === 'black' ? 'Чёрный' : 'Нейтральный'}
                                    color={getBeltColor(data.belt_type)}
                                    size="small"
                                    data-element-id={generateId('tongshu', 'chip', 'belt')}
                                />
                                {data.belt_stars && data.belt_stars.length > 0 && (
                                    <Typography variant="caption" display="block" color="text.secondary" sx={{ mt: 0.5 }}>
                                        {data.belt_stars.join(', ')}
                                    </Typography>
                                )}
                            </Box>
                            {data.black_rabbit_star && (
                                <Box>
                                    <strong>Чёрный Кролик:</strong>{' '}
                                    <Chip
                                        label={`${data.black_rabbit_star} (${data.black_rabbit_score >= 0 ? '+' : ''}${data.black_rabbit_score})`}
                                        size="small"
                                        color={data.black_rabbit_score > 0 ? 'success' : data.black_rabbit_score < 0 ? 'error' : 'default'}
                                        data-element-id={generateId('tongshu', 'chip', 'blackrabbit')}
                                    />
                                </Box>
                            )}
                        </Box>
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <Typography variant="subtitle1" gutterBottom>Луна и фазы:</Typography>
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                            <Box><strong>Фаза:</strong> {pd?.moon?.phase_name || data.moon_phase_name}</Box>
                            <Box><strong>Видимость:</strong> {pd?.moon?.phase_pct ?? data.moon_phase_pct}%</Box>
                            <Box><strong>Лунный день:</strong> {data.lunar_day ? `${data.lunar_day} (${data.lunar_month ? data.lunar_month + ' лунный мес.' : ''})` : '—'}</Box>
                        </Box>

                        {pd && pd.san_qi && (
                            <Box sx={{ mt: 2 }}>
                                <Typography variant="subtitle1" gutterBottom>Три мистика (三奇):</Typography>
                                <Chip
                                    label={pd.san_qi}
                                    size="small"
                                    color="success"
                                    data-element-id={generateId('tongshu', 'chip', 'sanqi')}
                                />
                            </Box>
                        )}

                        {(pd?.great_sun?.mountain || data.great_sun_mountain) && (
                            <Box sx={{ mt: 2 }}>
                                <Typography variant="subtitle1" gutterBottom>Большое Солнце (太阳到山):</Typography>
                                <Chip
                                    label={
                                        pd?.great_sun?.mountain
                                            ? `${pd.great_sun.mountain} — ${pd.great_sun.mountain_name}`
                                            : `${data.great_sun_mountain} — ${data.great_sun_mountain_name}`
                                    }
                                    size="small"
                                    color="warning"
                                    data-element-id={generateId('tongshu', 'chip', 'greatsun')}
                                />
                            </Box>
                        )}

                        {(pd?.symbolic_stars?.length > 0 || data.symbolic_stars?.length > 0) && (
                            <Box sx={{ mt: 2 }}>
                                <Typography variant="subtitle1" gutterBottom>Символические звёзды (神煞):</Typography>
                                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                    {(pd?.symbolic_stars || data.symbolic_stars || []).map((star, i) => (
                                        <Tooltip key={i} title={star.notes || ''}>
                                            <Chip
                                                label={star.name}
                                                size="small"
                                                color={star.name.includes('煞') || star.name.includes('死') || star.name.includes('亡') ? 'error' : 'default'}
                                                sx={{ mr: 0.5, mb: 0.5 }}
                                                data-element-id={generateId('tongshu', 'chip', `shensha-${i}`)}
                                            />
                                        </Tooltip>
                                    ))}
                                </Box>
                            </Box>
                        )}

                        {pd && pd.hidden_stems && (
                            <Box sx={{ mt: 2 }}>
                                <Typography variant="subtitle1" gutterBottom>Скрытые стволы:</Typography>
                                {['year', 'month', 'day', 'hour'].map(pillar => (
                                    <Box key={pillar} sx={{ mb: 0.5 }}>
                                        <Typography variant="body2" component="span" sx={{ textTransform: 'capitalize', fontWeight: 'bold' }}>
                                            {pillar === 'year' ? 'Год' : pillar === 'month' ? 'Месяц' : pillar === 'day' ? 'День' : 'Час'}:
                                        </Typography>{' '}
                                        {pd.hidden_stems[pillar]?.map((hs, i) => (
                                            <Chip
                                                key={i}
                                                label={`${hs.stem} (${hs.percentage}%)`}
                                                size="small"
                                                color={hs.is_main ? 'primary' : 'default'}
                                                sx={{ mr: 0.5 }}
                                            />
                                        )) || '—'}
                                    </Box>
                                ))}
                            </Box>
                        )}

                        {pd && pd.personalized_ten_gods && (
                            <Box sx={{ mt: 2 }}>
                                <Typography variant="subtitle1" gutterBottom>Персонализированные 10 Богов:</Typography>
                                {['year', 'month', 'day', 'hour'].map(pillar => (
                                    <Box key={pillar} sx={{ mb: 0.5 }}>
                                        <Typography variant="body2" component="span" sx={{ textTransform: 'capitalize' }}>
                                            {pillar === 'year' ? 'Год' : pillar === 'month' ? 'Месяц' : pillar === 'day' ? 'День' : 'Час'}:
                                        </Typography>{' '}
                                        <Chip
                                            label={pd.personalized_ten_gods[pillar] || '—'}
                                            size="small"
                                            color="secondary"
                                        />
                                    </Box>
                                ))}
                            </Box>
                        )}

                        {pd && pd.personalized_qi_phases && (
                            <Box sx={{ mt: 2 }}>
                                <Typography variant="subtitle1" gutterBottom>Персонализированные фазы Ци:</Typography>
                                {['year', 'month', 'day', 'hour'].map(pillar => (
                                    <Box key={pillar} sx={{ mb: 0.5 }}>
                                        <Typography variant="body2" component="span" sx={{ textTransform: 'capitalize' }}>
                                            {pillar === 'year' ? 'Год' : pillar === 'month' ? 'Месяц' : pillar === 'day' ? 'День' : 'Час'}:
                                        </Typography>{' '}
                                        <Chip
                                            label={pd.personalized_qi_phases[pillar] || '—'}
                                            size="small"
                                            variant="outlined"
                                        />
                                    </Box>
                                ))}
                            </Box>
                        )}
                    </Grid>
                </Grid>

                {/* Почасовые слоты */}
                {hoursData && hoursData.length > 0 && (
                    <Box sx={{ mt: 3 }}>
                        <Typography variant="subtitle1" gutterBottom>Почасовые слоты (12 двухчасовых периодов):</Typography>
                        <TableContainer component={Paper} variant="outlined">
                            <Table size="small">
                                <TableHead>
                                    <TableRow sx={{ bgcolor: 'action.hover' }}>
                                        <TableCell sx={{ py: 0.5, fontWeight: 'bold' }}>Время</TableCell>
                                        <TableCell sx={{ py: 0.5, fontWeight: 'bold' }}>Столп часа</TableCell>
                                        <TableCell sx={{ py: 0.5, fontWeight: 'bold' }}>10 Богов</TableCell>
                                        <TableCell sx={{ py: 0.5, fontWeight: 'bold' }}>Фаза Ци</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {hoursData.map((slot, index) => (
                                        <HourlySlotRow
                                            key={index}
                                            slot={slot}
                                            index={index}
                                            stemColors={stemColors}
                                            branchColors={branchColors}
                                            expanded={expandedHour === index}
                                            onToggle={() => handleToggleHour(index)}
                                        />
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </Box>
                )}

                {/* Летящие Звёзды */}
                {flyingStarsData && (
                    <Box sx={{ mt: 3 }}>
                        <Typography variant="subtitle1" gutterBottom>Летящие Звёзды:</Typography>
                        {flyingStarsData.palaces && (
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                                Г: {flyingStarsData.palaces.N?.year_star || '—'};
                                {' '}М: {flyingStarsData.palaces.N?.month_star || '—'};
                                {' '}Д: {flyingStarsData.palaces.N?.day_star || '—'}
                            </Typography>
                        )}
                        <FlyingStarsGrid chartData={flyingStarsData} compact />
                    </Box>
                )}
            </CardContent>
        </Card>
    );
}

// ---------------------------------------------------------------------------
// Week View
// ---------------------------------------------------------------------------
function DailyWeekView({ data, selectedDate, stemColors, branchColors }) {
    if (!Array.isArray(data) || data.length === 0) return null;

    return (
        <TableContainer component={Paper}>
            <Table>
                <TableHead>
                    <TableRow>
                        <TableCell>Дата</TableCell>
                        <TableCell>Столп дня</TableCell>
                        <TableCell>Сезон</TableCell>
                        <TableCell>12 Офицеров</TableCell>
                        <TableCell>28 Созвездий</TableCell>
                        <TableCell>Пояс</TableCell>
                        <TableCell>Луна</TableCell>
                        <TableCell>Шэнь Ша</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {data.map((day, dayIndex) => {
                        const d = parseISO(day.calendar_date);
                        const isSelected = isSameDay(d, selectedDate);
                        return (
                            <TableRow
                                key={day.calendar_date}
                                sx={{ bgcolor: isSelected ? 'action.selected' : 'inherit' }}
                                data-element-id={generateId('tongshu', 'week_row', dayIndex)}
                            >
                                <TableCell sx={{ fontWeight: isSelected ? 'bold' : 'normal' }}>
                                    {format(d, 'dd.MM EEEE', { locale: ru })}
                                </TableCell>
                                <TableCell>{renderPillar(day.day_pillar, stemColors, branchColors)}</TableCell>
                                <TableCell>{day.solar_term_char}</TableCell>
                                <TableCell>
                                    <Chip
                                        label={`${day.day_officer_char} (${day.day_officer_name_ru})`}
                                        color={getOfficerColor(day.day_officer_category)}
                                        size="small"
                                    />
                                </TableCell>
                                <TableCell>
                                    <Tooltip title={day.constellation_direction}>
                                        <Chip
                                            label={`${day.constellation_char} (${day.constellation_name_ru})`}
                                            color={getConstellationColor(day.constellation_nature)}
                                            size="small"
                                        />
                                    </Tooltip>
                                </TableCell>
                                <TableCell>
                                    <Chip
                                        label={day.belt_type === 'yellow' ? 'Ж' : day.belt_type === 'black' ? 'Ч' : 'Н'}
                                        color={getBeltColor(day.belt_type)}
                                        size="small"
                                    />
                                </TableCell>
                                <TableCell>{day.moon_phase_name}</TableCell>
                                <TableCell>
                                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                        {(day.symbolic_stars || []).slice(0, 3).map((star, i) => (
                                            <Chip key={i} label={star.name} size="small" sx={{ fontSize: '0.7rem' }} />
                                        ))}
                                        {(day.symbolic_stars || []).length > 3 && (
                                            <Chip label={`+${day.symbolic_stars.length - 3}`} size="small" variant="outlined" sx={{ fontSize: '0.7rem' }} />
                                        )}
                                    </Box>
                                </TableCell>
                            </TableRow>
                        );
                    })}
                </TableBody>
            </Table>
        </TableContainer>
    );
}

// ---------------------------------------------------------------------------
// Month View (Table mode) with filters
// ---------------------------------------------------------------------------
function DailyMonthView({ data, selectedDate, onDateClick, stemColors, branchColors }) {
    const [searchText, setSearchText] = useState('');
    const [officerFilter, setOfficerFilter] = useState('');
    const [beltFilter, setBeltFilter] = useState('');

    if (!Array.isArray(data) || data.length === 0) return null;

    const monthName = format(selectedDate, 'LLLL yyyy', { locale: ru });

    // Apply filters
    const filteredData = data.filter(day => {
        const matchesSearch = !searchText || [
            day.day_pillar,
            day.day_officer_name_ru,
            day.constellation_name_ru,
            day.solar_term_name_ru,
            day.moon_phase_name,
            ...(day.symbolic_stars || []).map(s => s.name)
        ].some(field => field && field.toLowerCase().includes(searchText.toLowerCase()));

        const matchesOfficer = !officerFilter || day.day_officer_category === officerFilter;
        const matchesBelt = !beltFilter || day.belt_type === beltFilter;

        return matchesSearch && matchesOfficer && matchesBelt;
    });

    return (
        <>
            <Box sx={{ mb: 2 }}>
                <Typography variant="h5" component="h2" gutterBottom>
                    {monthName}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    {filteredData.length} из {data.length} дней
                </Typography>
            </Box>

            {/* Filters */}
            <Paper sx={{ mb: 2, p: 2 }}>
                <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} md={4}>
                        <TextField
                            fullWidth
                            size="small"
                            label="Поиск"
                            placeholder="Столп, офицер, созвездие..."
                            value={searchText}
                            onChange={(e) => setSearchText(e.target.value)}
                            inputProps={{ 'data-element-id': generateId('tongshu', 'search', 'month') }}
                        />
                    </Grid>
                    <Grid item xs={6} md={3}>
                        <FormControl fullWidth size="small">
                            <InputLabel>12 Офицеров</InputLabel>
                            <Select
                                value={officerFilter}
                                label="12 Офицеров"
                                onChange={(e) => setOfficerFilter(e.target.value)}
                                inputProps={{ 'data-element-id': generateId('tongshu', 'filter', 'officer') }}
                            >
                                <MenuItem value="">Все</MenuItem>
                                <MenuItem value="auspicious">Благоприятный</MenuItem>
                                <MenuItem value="mixed">Смешанный</MenuItem>
                                <MenuItem value="inauspicious">Неблагоприятный</MenuItem>
                            </Select>
                        </FormControl>
                    </Grid>
                    <Grid item xs={6} md={3}>
                        <FormControl fullWidth size="small">
                            <InputLabel>Пояс</InputLabel>
                            <Select
                                value={beltFilter}
                                label="Пояс"
                                onChange={(e) => setBeltFilter(e.target.value)}
                                inputProps={{ 'data-element-id': generateId('tongshu', 'filter', 'belt') }}
                            >
                                <MenuItem value="">Все</MenuItem>
                                <MenuItem value="yellow">Жёлтый</MenuItem>
                                <MenuItem value="black">Чёрный</MenuItem>
                                <MenuItem value="neutral">Нейтральный</MenuItem>
                            </Select>
                        </FormControl>
                    </Grid>
                    <Grid item xs={12} md={2}>
                        <Button
                            variant="outlined"
                            size="small"
                            fullWidth
                            onClick={() => { setSearchText(''); setOfficerFilter(''); setBeltFilter(''); }}
                            data-element-id={generateId('tongshu', 'action', 'reset_filters')}
                        >
                            Сбросить
                        </Button>
                    </Grid>
                </Grid>
            </Paper>

            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>Дата</TableCell>
                            <TableCell>День недели</TableCell>
                            <TableCell>Столп дня</TableCell>
                            <TableCell>Сезон</TableCell>
                            <TableCell>12 Офицеров</TableCell>
                            <TableCell>28 Созвездий</TableCell>
                            <TableCell>Пояс</TableCell>
                            <TableCell>Луна</TableCell>
                            <TableCell>Шэнь Ша</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {filteredData.map((day, rowIndex) => {
                            const d = parseISO(day.calendar_date);
                            const isSelected = isSameDay(d, selectedDate);
                            return (
                                <TableRow
                                    key={day.calendar_date}
                                    data-element-id={generateId('tongshu', 'month_row', rowIndex)}
                                    sx={{
                                        bgcolor: isSelected ? 'action.selected' : 'inherit',
                                        cursor: 'pointer',
                                        '&:hover': { bgcolor: 'action.hover' }
                                    }}
                                    onClick={() => onDateClick && onDateClick(d)}
                                >
                                    <TableCell>{format(d, 'dd.MM')}</TableCell>
                                    <TableCell>{format(d, 'EEEE', { locale: ru })}</TableCell>
                                    <TableCell sx={{ fontWeight: isSelected ? 'bold' : 'normal' }}>
                                        {renderPillar(day.day_pillar, stemColors, branchColors)}
                                    </TableCell>
                                    <TableCell>{day.solar_term_char}</TableCell>
                                    <TableCell>
                                        <Tooltip title={`${day.day_officer_char} — ${day.day_officer_name_ru}`}>
                                            <Chip
                                                label={`${day.day_officer_char} (${day.day_officer_name_ru})`}
                                                color={getOfficerColor(day.day_officer_category)}
                                                size="small"
                                            />
                                        </Tooltip>
                                    </TableCell>
                                    <TableCell>
                                        <Tooltip title={`${day.constellation_char} — ${day.constellation_name_ru} (${day.constellation_direction})`}>
                                            <Chip
                                                label={`${day.constellation_char} (${day.constellation_name_ru})`}
                                                color={getConstellationColor(day.constellation_nature)}
                                                size="small"
                                            />
                                        </Tooltip>
                                    </TableCell>
                                    <TableCell>
                                        <Tooltip title={day.belt_stars?.join(', ') || ''}>
                                            <Chip
                                                label={day.belt_type === 'yellow' ? 'Ж' : day.belt_type === 'black' ? 'Ч' : 'Н'}
                                                color={getBeltColor(day.belt_type)}
                                                size="small"
                                            />
                                        </Tooltip>
                                    </TableCell>
                                    <TableCell>{day.moon_phase_name}</TableCell>
                                    <TableCell>
                                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                            {(day.symbolic_stars || []).slice(0, 3).map((star, i) => (
                                                <Chip key={i} label={star.name} size="small" sx={{ fontSize: '0.7rem' }} />
                                            ))}
                                            {(day.symbolic_stars || []).length > 3 && (
                                                <Chip label={`+${day.symbolic_stars.length - 3}`} size="small" variant="outlined" sx={{ fontSize: '0.7rem' }} />
                                            )}
                                        </Box>
                                    </TableCell>
                                </TableRow>
                            );
                        })}
                    </TableBody>
                </Table>
            </TableContainer>
        </>
    );
}

// ---------------------------------------------------------------------------
// Year View
// ---------------------------------------------------------------------------
function DailyYearView({ data, selectedDate }) {
    if (!Array.isArray(data) || data.length === 0) return null;

    // Group by month
    const byMonth = {};
    data.forEach(day => {
        const d = parseISO(day.calendar_date);
        const key = d.getMonth();
        if (!byMonth[key]) byMonth[key] = [];
        byMonth[key].push(day);
    });

    return (
        <Box>
            <Typography variant="h5" component="h2" gutterBottom>
                {selectedDate.getFullYear()} год
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
                {data.length} дней
            </Typography>

            {Object.entries(byMonth).map(([monthIdx, days]) => (
                <Paper key={monthIdx} sx={{ mb: 2, p: 2 }}>
                    <Typography variant="h6" gutterBottom>
                        {format(new Date(selectedDate.getFullYear(), parseInt(monthIdx), 1), 'LLLL', { locale: ru })}
                    </Typography>
                    <Grid container spacing={1}>
                        {days.map(day => {
                            const d = parseISO(day.calendar_date);
                            const isSelected = isSameDay(d, selectedDate);
                            return (
                                <Grid item key={day.calendar_date}>
                                    <Tooltip title={`${day.day_pillar} | ${day.day_officer_char} | ${day.constellation_char}`}>
                                        <Chip
                                            label={format(d, 'dd')}
                                            color={getBeltColor(day.belt_type)}
                                            variant={isSelected ? 'filled' : 'outlined'}
                                            sx={{ minWidth: 48 }}
                                            data-element-id={generateId('tongshu', 'day_chip', day.calendar_date)}
                                        />
                                    </Tooltip>
                                </Grid>
                            );
                        })}
                    </Grid>
                </Paper>
            ))}
        </Box>
    );
}

export default TongShuPage;
