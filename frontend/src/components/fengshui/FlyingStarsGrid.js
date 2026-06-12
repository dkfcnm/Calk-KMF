import React from 'react';
import { Paper, Typography, Box, Chip, Tooltip } from '@mui/material';
import { generateId } from '../../hooks/useElementId';

// Цвета звезд Летящих Звезд
const STAR_COLORS = {
    1: '#2196f3', // Вода - синий
    2: '#8d6e63', // Земля - коричневый
    3: '#4caf50', // Дерево - зеленый
    4: '#4caf50', // Дерево - зеленый
    5: '#8d6e63', // Земля - коричневый
    6: '#ffc107', // Металл - желтый/золотой
    7: '#ffc107', // Металл - желтый/золотой
    8: '#8d6e63', // Земля - коричневый
    9: '#f44336', // Огонь - красный
};

// Элементы звезд
const STAR_ELEMENTS = {
    1: 'Вода',
    2: 'Земля',
    3: 'Дерево',
    4: 'Дерево',
    5: 'Земля',
    6: 'Металл',
    7: 'Металл',
    8: 'Земля',
    9: 'Огонь',
};

// Порядок отображения дворцов в сетке 3x3
// Сетка: NW N NE
//        W  C  E
//        SW S SE
const GRID_LAYOUT = [
    ['NW', 'N', 'NE'],
    ['W', 'C', 'E'],
    ['SW', 'S', 'SE'],
];

function FlyingStarsGrid({ chartData, showLabels = true, compact = false }) {
    if (!chartData || !chartData.palaces) {
        return (
            <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography color="text.secondary">
                    Данные Летящих Звезд недоступны
                </Typography>
            </Paper>
        );
    }

    const { palaces, period, date_time } = chartData;

    return (
        <Paper sx={{ p: 2 }} data-element-id={generateId('fengshui', 'grid', 'flying-stars')}>
            {showLabels && (
                <Typography variant="h6" gutterBottom>
                    Летящие Звёзды (Период {period})
                </Typography>
            )}
            <Box
                sx={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(3, 1fr)',
                    gap: 1,
                    maxWidth: 360,
                    mx: 'auto',
                }}
            >
                {GRID_LAYOUT.map((row, rowIndex) =>
                    row.map((direction, colIndex) => {
                        const palaceData = palaces[direction];
                        if (!palaceData) return null;

                        const { palace, year_star, month_star, day_star, hour_star, direction_ru } = palaceData;
                        const isCenter = direction === 'C';

                        return (
                            <Tooltip
                                key={direction}
                                title={
                                    <Box>
                                        <Typography variant="subtitle2">{direction_ru} (Дворец {palace})</Typography>
                                        <Typography variant="body2">Год: {year_star} ({STAR_ELEMENTS[year_star]})</Typography>
                                        <Typography variant="body2">Месяц: {month_star} ({STAR_ELEMENTS[month_star]})</Typography>
                                        <Typography variant="body2">День: {day_star} ({STAR_ELEMENTS[day_star]})</Typography>
                                        {!compact && <Typography variant="body2">Час: {hour_star} ({STAR_ELEMENTS[hour_star]})</Typography>}
                                    </Box>
                                }
                                arrow
                            >
                                <Box
                                    sx={{
                                        border: isCenter ? '2px solid #f44336' : '1px solid #e0e0e0',
                                        borderRadius: 1,
                                        p: 1.5,
                                        textAlign: 'center',
                                        bgcolor: isCenter ? 'rgba(244, 67, 54, 0.08)' : 'background.paper',
                                        minHeight: 80,
                                        display: 'flex',
                                        flexDirection: 'column',
                                        justifyContent: 'center',
                                        alignItems: 'center',
                                        cursor: 'pointer',
                                        '&:hover': {
                                            bgcolor: 'action.hover',
                                        },
                                    }}
                                    data-element-id={generateId('fengshui', 'palace', direction)}
                                >
                                    <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>
                                        {direction}
                                    </Typography>
                                    <Typography variant="body2" sx={{ fontWeight: 'bold', fontSize: '0.75rem' }}>
                                        {direction_ru}
                                    </Typography>
                                    <Box sx={{ mt: 0.5, display: 'flex', gap: 0.5, flexWrap: 'wrap', justifyContent: 'center' }}>
                                        <Chip
                                            label={year_star}
                                            size="small"
                                            sx={{
                                                bgcolor: STAR_COLORS[year_star],
                                                color: '#fff',
                                                fontSize: '0.65rem',
                                                height: 20,
                                                minWidth: 20,
                                            }}
                                            title={`Год: ${STAR_ELEMENTS[year_star]}`}
                                        />
                                        <Chip
                                            label={month_star}
                                            size="small"
                                            sx={{
                                                bgcolor: STAR_COLORS[month_star],
                                                color: '#fff',
                                                fontSize: '0.65rem',
                                                height: 20,
                                                minWidth: 20,
                                                opacity: 0.85,
                                            }}
                                            title={`Месяц: ${STAR_ELEMENTS[month_star]}`}
                                        />
                                        <Chip
                                            label={day_star}
                                            size="small"
                                            sx={{
                                                bgcolor: STAR_COLORS[day_star],
                                                color: '#fff',
                                                fontSize: '0.65rem',
                                                height: 20,
                                                minWidth: 20,
                                                opacity: 0.7,
                                            }}
                                            title={`День: ${STAR_ELEMENTS[day_star]}`}
                                        />
                                        {!compact && (
                                            <Chip
                                                label={hour_star}
                                                size="small"
                                                sx={{
                                                    bgcolor: STAR_COLORS[hour_star],
                                                    color: '#fff',
                                                    fontSize: '0.65rem',
                                                    height: 20,
                                                    minWidth: 20,
                                                    opacity: 0.55,
                                                }}
                                                title={`Час: ${STAR_ELEMENTS[hour_star]}`}
                                            />
                                        )}
                                    </Box>
                                </Box>
                            </Tooltip>
                        );
                    })
                )}
            </Box>
            <Box sx={{ mt: 1, display: 'flex', justifyContent: 'center', gap: 2, flexWrap: 'wrap' }}>
                <Typography variant="caption" color="text.secondary">
                    {compact ? 'Год ● Месяц ● День' : 'Год ● Месяц ● День ● Час'}
                </Typography>
            </Box>
        </Paper>
    );
}

export default React.memo(FlyingStarsGrid);
