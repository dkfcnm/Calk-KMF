import React from 'react';
import { generateId } from '../../../hooks/useElementId';
import {
    Box,
    Grid,
    Paper,
    Chip,
    Tooltip,
    Typography
} from '@mui/material';
import {
    format,
    parseISO,
    startOfMonth,
    endOfMonth,
    getDay,
    isSameDay,
    isBefore,
    startOfDay
} from 'date-fns';

// Day names starting from Monday
const WEEK_DAYS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

const NAYIN_ELEMENT_CHAR = {
    'Дерево': '木',
    'Огонь': '火',
    'Земля': '土',
    'Металл': '金',
    'Вода': '水',
};

const getOfficerColor = (category) => {
    switch (category) {
        case 'auspicious': return 'success';
        case 'inauspicious': return 'error';
        default: return 'warning';
    }
};

const getConstellationColor = (nature) => {
    switch (nature) {
        case 'auspicious': return 'success';
        case 'inauspicious': return 'error';
        default: return 'warning';
    }
};

const getBeltColor = (beltType) => {
    switch (beltType) {
        case 'yellow': return 'success';
        case 'black': return 'error';
        default: return 'default';
    }
};

/**
 * CalendarGrid — ячеистая сетка календаря Тун Шу 7×N
 * 
 * Props:
 *  - data: массив дней из API
 *  - selectedDate: Date — выбранная дата
 *  - currentDate: Date — сегодня (для подсветки)
 *  - onDateClick: (date: Date) => void
 */
function CalendarGrid({ data, selectedDate, currentDate, onDateClick, stemColors, branchColors }) {
    if (!data || data.length === 0) return null;

    const monthStart = startOfMonth(selectedDate);
    const monthEnd = endOfMonth(selectedDate);

    // Build map dateString -> dayData for O(1) lookup
    const dayMap = {};
    data.forEach(day => {
        dayMap[day.calendar_date] = day;
    });

    // getDay returns 0 for Sunday, 1 for Monday... we want Monday = 0
    const firstDayOfWeek = getDay(monthStart); // 0=Sun, 1=Mon...
    const mondayOffset = firstDayOfWeek === 0 ? 6 : firstDayOfWeek - 1;

    // Build grid cells
    const cells = [];

    // Empty cells before first day
    for (let i = 0; i < mondayOffset; i++) {
        cells.push({ type: 'empty', key: `empty-${i}` });
    }

    // Day cells
    const totalDays = monthEnd.getDate();
    for (let dayNum = 1; dayNum <= totalDays; dayNum++) {
        const dateStr = format(
            new Date(monthStart.getFullYear(), monthStart.getMonth(), dayNum),
            'yyyy-MM-dd'
        );
        cells.push({
            type: 'day',
            dayNum,
            dateStr,
            data: dayMap[dateStr] || null
        });
    }

    // Fill remaining cells to complete the last week
    const remaining = (7 - (cells.length % 7)) % 7;
    for (let i = 0; i < remaining; i++) {
        cells.push({ type: 'empty', key: `empty-end-${i}` });
    }

    const today = startOfDay(currentDate || new Date());

    return (
        <Box>
            {/* Day of week headers */}
            <Grid container columns={7} sx={{ mb: 1 }}>
                {WEEK_DAYS.map((name, idx) => (
                    <Grid item xs={1} key={idx}>
                        <Box
                            sx={{
                                textAlign: 'center',
                                fontWeight: 'bold',
                                py: 1,
                                bgcolor: 'grey.100',
                                borderRadius: 1,
                                mx: 0.5
                            }}
                            data-element-id={generateId('tongshu', 'weekday_header', idx)}
                        >
                            <Typography variant="subtitle2">{name}</Typography>
                        </Box>
                    </Grid>
                ))}
            </Grid>

            {/* Calendar cells */}
            <Grid container columns={7} spacing={0.5}>
                {cells.map((cell, idx) => {
                    if (cell.type === 'empty') {
                        return (
                            <Grid item xs={1} key={cell.key}>
                                <Box sx={{ minHeight: 160, mx: 0.5 }} data-element-id={generateId('tongshu', 'cell', `empty_${idx}`)} />
                            </Grid>
                        );
                    }

                    const dayDate = parseISO(cell.dateStr);
                    const isSelected = isSameDay(dayDate, selectedDate);
                    const isToday = isSameDay(dayDate, today);
                    const isPast = isBefore(dayDate, today);
                    const day = cell.data;

                    // Pillars in order: day, month, year (configurable in future)
                    const pillarOrder = ['day', 'month', 'year'];

                    return (
                        <Grid item xs={1} key={cell.dateStr}>
                            <Paper
                                elevation={isSelected ? 4 : 1}
                                onClick={() => onDateClick(dayDate)}
                                data-element-id={generateId('tongshu', 'day_cell', cell.dayNum)}
                                sx={{
                                    minHeight: 160,
                                    p: 0.5,
                                    cursor: 'pointer',
                                    position: 'relative',
                                    border: isToday
                                        ? '2px solid #1976d2'
                                        : isSelected
                                            ? '2px solid #9c27b0'
                                            : '1px solid transparent',
                                    borderRadius: 1.5,
                                    opacity: isPast && !isToday ? 0.4 : 1,
                                    bgcolor: isPast && !isToday ? 'grey.200' : 'background.paper',
                                    transition: 'all 0.2s',
                                    '&:hover': {
                                        bgcolor: 'action.hover',
                                        transform: 'translateY(-2px)',
                                        boxShadow: 3
                                    },
                                    display: 'flex',
                                    flexDirection: 'column',
                                    gap: 0.25,
                                    overflow: 'hidden'
                                }}
                            >
                                {/* Top row: 3 pillars + day numbers */}
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                    {/* Pillars block */}
                                    <Box sx={{ display: 'flex', gap: 0.5, flex: 1, justifyContent: 'center' }}>
                                        {pillarOrder.map((pkey) => {
                                            const pillar = day?.[`${pkey}_pillar`] || '';
                                            const period = day?.[`${pkey}_period`];
                                            const elemNum = day?.[`${pkey}_element_num`];
                                            const stem = pillar?.[0] || '';
                                            const branch = pillar?.[1] || '';
                                            return (
                                                <Box key={pkey} sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', minWidth: 28 }}>
                                                    {/* Period number */}
                                                    <Typography variant="caption" sx={{ fontSize: '0.6rem', lineHeight: 1, color: 'text.secondary' }}>
                                                        {period ?? ''}
                                                    </Typography>
                                                    {/* Stem */}
                                                    <Typography
                                                        component="span"
                                                        sx={{
                                                            fontWeight: 700,
                                                            fontSize: '0.95rem',
                                                            lineHeight: 1.1,
                                                            color: stemColors?.[stem] || 'text.primary',
                                                        }}
                                                    >
                                                        {stem}
                                                    </Typography>
                                                    {/* Branch */}
                                                    <Typography
                                                        component="span"
                                                        sx={{
                                                            fontWeight: 700,
                                                            fontSize: '0.95rem',
                                                            lineHeight: 1.1,
                                                            color: branchColors?.[branch] || 'text.primary',
                                                        }}
                                                    >
                                                        {branch}
                                                    </Typography>
                                                    {/* Element number */}
                                                    <Typography variant="caption" sx={{ fontSize: '0.6rem', lineHeight: 1, color: 'text.secondary' }}>
                                                        {elemNum ?? ''}
                                                    </Typography>
                                                </Box>
                                            );
                                        })}
                                    </Box>

                                    {/* Day numbers block */}
                                    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', minWidth: 36 }}>
                                        <Typography
                                            variant="h6"
                                            sx={{
                                                fontWeight: isToday ? 800 : 600,
                                                color: isToday ? 'primary.main' : 'text.primary',
                                                lineHeight: 1.1,
                                                fontSize: '1.1rem'
                                            }}
                                            data-element-id={generateId('tongshu', 'day_number', cell.dayNum)}
                                        >
                                            {cell.dayNum}
                                        </Typography>
                                        {day?.lunar_day && (
                                            <Tooltip title={day.moon_phase_name || ''}>
                                                <Typography variant="caption" sx={{ fontSize: '0.6rem', lineHeight: 1, color: 'text.secondary' }}>
                                                    {day.lunar_day}
                                                    {day.moon_phase_pct ? ` / ${Math.round(day.moon_phase_pct)}%` : ''}
                                                </Typography>
                                            </Tooltip>
                                        )}
                                    </Box>
                                </Box>

                                {day && (
                                    <>
                                        {/* Hexagram family + production chain row */}
                                        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 0.5, minHeight: 14 }}>
                                            {day.hexagram_family_same && (
                                                <Tooltip title="Все три столпа — одна семья гексаграмм">
                                                    <Typography variant="caption" sx={{ fontSize: '0.65rem', color: 'warning.main', fontWeight: 700 }}>
                                                        Семья гексаграмм !
                                                    </Typography>
                                                </Tooltip>
                                            )}
                                            {day.production_chain && (
                                                <Tooltip title="Цепочка порождения">
                                                    <Typography variant="caption" sx={{ fontSize: '0.65rem', color: 'success.main', fontWeight: 700 }}>
                                                        !
                                                    </Typography>
                                                </Tooltip>
                                            )}
                                        </Box>

                                        {/* Na Yin elements */}
                                        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, alignItems: 'center' }}>
                                            {['year', 'month', 'day'].map((pkey) => {
                                                const elem = day?.[`${pkey}_nayin_element`];
                                                if (!elem) return null;
                                                return (
                                                    <Typography
                                                        key={pkey}
                                                        component="span"
                                                        sx={{
                                                            fontSize: '0.85rem',
                                                            fontWeight: 600,
                                                            color: stemColors?.[elem] || 'text.secondary',
                                                            lineHeight: 1.2
                                                        }}
                                                        title={elem}
                                                    >
                                                        {NAYIN_ELEMENT_CHAR[elem] || elem}
                                                    </Typography>
                                                );
                                            })}
                                        </Box>

                                        {/* Officer + Constellation row */}
                                        <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap' }}>
                                            <Tooltip title={`${day.day_officer_char} — ${day.day_officer_name_ru}`}>
                                                <Chip
                                                    label={day.day_officer_char}
                                                    color={getOfficerColor(day.day_officer_category)}
                                                    size="small"
                                                    data-element-id={generateId('tongshu', 'officer_chip', cell.dayNum)}
                                                    sx={{
                                                        height: 18,
                                                        fontSize: '0.65rem',
                                                        '& .MuiChip-label': { px: 0.5 }
                                                    }}
                                                />
                                            </Tooltip>
                                            <Tooltip title={`${day.constellation_char} — ${day.constellation_name_ru} (${day.constellation_direction})`}>
                                                <Chip
                                                    label={day.constellation_char}
                                                    color={getConstellationColor(day.constellation_nature)}
                                                    size="small"
                                                    data-element-id={generateId('tongshu', 'constellation_chip', cell.dayNum)}
                                                    sx={{
                                                        height: 18,
                                                        fontSize: '0.65rem',
                                                        '& .MuiChip-label': { px: 0.5 }
                                                    }}
                                                />
                                            </Tooltip>
                                        </Box>

                                        {/* Belt + Moon row */}
                                        <Box sx={{ display: 'flex', gap: 0.5, mt: 'auto', justifyContent: 'space-between', alignItems: 'center' }}>
                                            <Chip
                                                label={day.belt_type === 'yellow' ? 'Ж' : day.belt_type === 'black' ? 'Ч' : 'Н'}
                                                color={getBeltColor(day.belt_type)}
                                                size="small"
                                                data-element-id={generateId('tongshu', 'belt_chip', cell.dayNum)}
                                                sx={{
                                                    height: 16,
                                                    fontSize: '0.6rem',
                                                    minWidth: 20
                                                }}
                                            />
                                            <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.6rem' }} data-element-id={generateId('tongshu', 'moon_phase', cell.dayNum)}>
                                                {day.moon_phase_name}
                                            </Typography>
                                        </Box>
                                    </>
                                )}
                            </Paper>
                        </Grid>
                    );
                })}
            </Grid>
        </Box>
    );
}

export default React.memo(CalendarGrid);
