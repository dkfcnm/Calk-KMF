import React from 'react';
import {
    Box,
    Grid,
    Typography,
    Card,
    CardContent,
    Divider
} from '@mui/material';
import PalaceDetail from './PalaceDetail';

/**
 * Компонент отображения сетки расклада Ци Мэнь (9 дворцов)
 * 
 * @param {object} props.chart - данные расклада
 * @param {number} props.selectedPalace - номер выбранного дворца
 * @param {function} props.onPalaceClick - обработчик клика по дворцу
 */
const QimenGrid = ({ chart, selectedPalace = null, onPalaceClick, levelLabel = '' }) => {
    if (!chart || !chart.palaces) {
        return (
            <Box sx={{ p: 3, textAlign: 'center' }}>
                <Typography variant="body1" color="text.secondary">
                    Расклад не загружен или не содержит данных
                </Typography>
            </Box>
        );
    }

    // Порядок расположения дворцов на сетке (порядок Ло Шу)
    // 4 9 2
    // 3 5 7
    // 8 1 6
    const gridOrder = [
        [4, 9, 2],
        [3, 5, 7],
        [8, 1, 6]
    ];

    // Расчет времени и даты для отображения
    const dateTime = new Date(chart.date_time);
    const formattedDateTime = new Intl.DateTimeFormat('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(dateTime);

    // Название метода для отображения
    const methodName = chart.method === 'zhirun' ? 'Джи Жэнь' : 'Чай Бу';
    const levelDisplay = levelLabel ? ` (${levelLabel})` : '';

    // Показываем дополнительные столпы если есть
    const extraPillars = [];
    if (chart.year_pillar) extraPillars.push(`Год: ${chart.year_pillar}`);
    if (chart.month_pillar) extraPillars.push(`Мес: ${chart.month_pillar}`);
    if (chart.day_pillar) extraPillars.push(`День: ${chart.day_pillar}`);
    if (chart.hour_pillar) extraPillars.push(`Час: ${chart.hour_pillar}`);

    return (
        <Box>
            <Card elevation={3} sx={{ mb: 3 }}>
                <CardContent>
                    <Grid container spacing={2}>
                        <Grid item xs={12} md={6}>
                            <Typography variant="h6" gutterBottom>
                                Информация о раскладе
                            </Typography>
                            <Typography variant="body1">
                                <strong>Дата:</strong> {formattedDateTime}
                            </Typography>
                            <Typography variant="body1">
                                <strong>Методология:</strong> {methodName}{levelDisplay}
                            </Typography>
                            {extraPillars.length > 0 && (
                                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                                    {extraPillars.join(' | ')}
                                </Typography>
                            )}
                        </Grid>
                        <Grid item xs={12} md={6}>
                            <Typography variant="h6" gutterBottom>
                                Параметры расклада
                            </Typography>
                            <Typography variant="body1">
                                <strong>Номер структуры (Ju):</strong> {chart.chart_num}
                            </Typography>
                            <Typography variant="body1">
                                <strong>Инь/Ян:</strong> {chart.yin_yang === 'Yang' ? 'Ян Дунь' : chart.yin_yang === 'Yin' ? 'Инь Дунь' : chart.yin_yang}
                            </Typography>
                        </Grid>
                    </Grid>
                </CardContent>
            </Card>

            <Divider sx={{ mb: 3 }} />

            {/* Сетка дворцов */}
            <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom align="center">
                    Сетка расклада {methodName}{levelDisplay}
                </Typography>

                {gridOrder.map((row, rowIdx) => (
                    <Grid container spacing={2} key={`row-${rowIdx}`} sx={{ mb: 2 }}>
                        {row.map((palaceNo) => (
                            <Grid item xs={4} key={`palace-${palaceNo}`}>
                                <PalaceDetail
                                    data={chart.palaces[palaceNo]}
                                    isSelected={selectedPalace === palaceNo}
                                    onClick={() => onPalaceClick && onPalaceClick(palaceNo)}
                                />
                            </Grid>
                        ))}
                    </Grid>
                ))}
            </Box>
        </Box>
    );
};

export default QimenGrid;