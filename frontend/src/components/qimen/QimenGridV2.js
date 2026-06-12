import React, { useState, useEffect } from 'react';
import { Box, Paper, Typography, Grid } from '@mui/material';
import { alpha } from '@mui/material/styles';
import qimenService from '../../services/qimenService';
import { generateId } from '../../hooks/useElementId';

// Порядок Ло Шу
const GRID_ORDER = [
    [4, 9, 2],
    [3, 5, 7],
    [8, 1, 6],
];

const PALACE_COLORS = {
    1: '#1976d2',
    2: '#8d6e63',
    3: '#2e7d32',
    4: '#2e7d32',
    5: '#f9a825',
    6: '#78909c',
    7: '#b0bec5',
    8: '#795548',
    9: '#c62828',
};

const STEM_NAMES = {
    '甲': 'Цзя', '乙': 'И', '丙': 'Бин', '丁': 'Дин',
    '戊': 'У', '己': 'Цзи', '庚': 'Гэн', '辛': 'Синь',
    '壬': 'Жэнь', '癸': 'Гуй',
};

const BORDER_TOP = [
    { char: '申', animal: 'Обезьяна', time: '15:00', color: '#ff8f00' },
    { char: '酉', animal: 'Петух', time: '17:00', color: '#78909c' },
    { char: '戌', animal: 'Собака', time: '19:00', color: '#8d6e63' },
];

const BORDER_RIGHT = [
    { char: '巳', animal: 'Змея', time: '09:00', color: '#c62828' },
    { char: '午', animal: 'Лошадь', time: '11:00', color: '#c62828' },
    { char: '未', animal: 'Коза', time: '13:00', color: '#ef6c00' },
];

const BORDER_BOTTOM = [
    { char: '丑', animal: 'Бык', time: '01:00', color: '#8d6e63' },
    { char: '子', animal: 'Крыса', time: '23:00', color: '#1976d2' },
    { char: '亥', animal: 'Свинья', time: '21:00', color: '#78909c' },
];

const BORDER_LEFT = [
    { char: '辰', animal: 'Дракон', time: '07:00', color: '#2e7d32' },
    { char: '卯', animal: 'Кролик', time: '05:00', color: '#2e7d32' },
    { char: '寅', animal: 'Тигр', time: '03:00', color: '#2e7d32' },
];

const BorderSegment = ({ char, animal, time, color }) => (
    <Box
        sx={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            border: `1px solid ${alpha(color, 0.5)}`,
            backgroundColor: alpha(color, 0.08),
            py: 0.5,
            px: 0.5,
            minWidth: 0,
        }}
    >
        <Typography variant="caption" sx={{ fontWeight: 'bold', color, fontSize: '0.75rem' }}>
            {char}
        </Typography>
        <Typography variant="caption" sx={{ fontSize: '0.65rem', color: 'text.secondary' }}>
            {animal}
        </Typography>
        <Typography variant="caption" sx={{ fontSize: '0.6rem', color: 'text.secondary' }}>
            {time}
        </Typography>
    </Box>
);

const PalaceCell = ({ palace, isSelected, onClick, refs }) => {
    if (!palace) {
        return (
            <Paper sx={{ height: '100%', minHeight: 180, opacity: 0.3 }} />
        );
    }

    const {
        palace_no,
        heaven_stem,
        earth_stem,
        star,
        gate,
        spirit,
        is_main_star,
        is_main_gate,
        is_fou_tou_heaven,
        is_fou_tou_earth,
    } = palace;

    const bgColor = PALACE_COLORS[palace_no] || '#90a4ae';
    const alphaBg = alpha(bgColor, 0.12);

    const starName = refs.starsMap[star]?.name_ru || '';
    const gateName = refs.gatesMap[gate]?.name_ru || '';
    const spiritName = refs.spiritsMap[spirit]?.name_ru || '';
    const heavenName = STEM_NAMES[heaven_stem] || '';
    const earthName = STEM_NAMES[earth_stem] || '';

    return (
        <Paper
            onClick={onClick}
            data-testid={`qimen-palace-${palace_no}`}
            data-element-id={generateId('qimen', 'palace', palace_no)}
            sx={{
                p: 1,
                height: '100%',
                minHeight: 180,
                cursor: 'pointer',
                backgroundColor: isSelected ? alpha(bgColor, 0.35) : alphaBg,
                border: isSelected ? `2px solid ${bgColor}` : `1px solid ${alpha(bgColor, 0.5)}`,
                position: 'relative',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                transition: 'all 0.2s ease',
            }}
        >
            {/* Номер дворца — справа сверху */}
            <Typography
                variant="caption"
                sx={{
                    position: 'absolute',
                    top: 4,
                    right: 6,
                    fontWeight: 'bold',
                    color: bgColor,
                }}
            >
                {palace_no}
            </Typography>

            {/* Индикаторы главной звезды/врат — слева сверху */}
            <Box sx={{ position: 'absolute', top: 4, left: 4, display: 'flex', gap: 0.5 }}>
                {is_main_star === 1 && (
                    <Typography variant="caption" sx={{ fontWeight: 'bold', color: 'success.dark', fontSize: '0.65rem' }}>
                        值使
                    </Typography>
                )}
                {is_main_gate === 1 && (
                    <Typography variant="caption" sx={{ fontWeight: 'bold', color: 'error.dark', fontSize: '0.65rem' }}>
                        值符
                    </Typography>
                )}
            </Box>

            {/* Небесный ствол — крупно */}
            <Box sx={{ textAlign: 'center', mt: 2 }}>
                <Typography variant="h4" sx={{ fontWeight: 700, lineHeight: 1.1, color: 'text.primary' }}>
                    {heaven_stem}
                </Typography>
            </Box>

            {/* Детали */}
            <Box sx={{ mt: 0.5, display: 'flex', flexDirection: 'column', gap: 0.3, alignItems: 'center' }}>
                <Typography variant="body2" sx={{ fontSize: '0.8rem', color: 'text.primary' }}>
                    {heaven_stem} {heavenName}
                    {is_fou_tou_heaven === 1 && <span style={{ color: '#e65100', marginLeft: 4 }}>伏</span>}
                </Typography>
                <Typography variant="body2" sx={{ fontSize: '0.8rem', color: 'text.primary' }}>
                    {earth_stem} {earthName}
                    {is_fou_tou_earth === 1 && <span style={{ color: '#e65100', marginLeft: 4 }}>伏</span>}
                </Typography>
                <Typography variant="body2" sx={{ fontSize: '0.8rem', color: 'text.secondary' }}>
                    {star} {starName}
                </Typography>
                <Typography variant="body2" sx={{ fontSize: '0.8rem', color: 'text.secondary' }}>
                    {spirit} {spiritName}
                </Typography>
                <Typography variant="body2" sx={{ fontSize: '0.8rem', color: 'text.secondary' }}>
                    {gate} {gateName}
                </Typography>
            </Box>
        </Paper>
    );
};

const CenterCell = ({ chart, palace, isSelected, onClick, refs, levelLabel }) => {
    const bgColor = PALACE_COLORS[5];
    const alphaBg = alpha(bgColor, 0.12);
    const methodName = chart.method === 'zhirun' ? 'Джи Жэнь' : 'Чай Бу';

    return (
        <Paper
            onClick={onClick}
            data-testid="qimen-palace-5"
            data-element-id={generateId('qimen', 'palace', 5)}
            sx={{
                p: 1,
                height: '100%',
                minHeight: 180,
                cursor: 'pointer',
                backgroundColor: isSelected ? alpha(bgColor, 0.35) : alphaBg,
                border: isSelected ? `2px solid ${bgColor}` : `1px solid ${alpha(bgColor, 0.5)}`,
                position: 'relative',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                textAlign: 'center',
            }}
        >
            <Typography variant="subtitle1" sx={{ fontWeight: 'bold', color: 'text.primary' }}>
                {chart.yin_yang === 'Yang' ? 'Ян' : chart.yin_yang === 'Yin' ? 'Инь' : chart.yin_yang} {chart.chart_num}
            </Typography>
            <Typography variant="body2" sx={{ color: 'text.secondary', mt: 0.5 }}>
                Расклад {levelLabel}
            </Typography>
            <Typography variant="caption" sx={{ color: 'text.secondary', mt: 0.5 }}>
                Система: {methodName}
            </Typography>

            {palace && palace.heaven_stem && (
                <Box sx={{ mt: 1, opacity: 0.8 }}>
                    <Typography variant="caption" display="block">
                        {palace.heaven_stem} {STEM_NAMES[palace.heaven_stem] || ''}
                    </Typography>
                    <Typography variant="caption" display="block">
                        {palace.earth_stem} {STEM_NAMES[palace.earth_stem] || ''}
                    </Typography>
                    {palace.star && (
                        <Typography variant="caption" display="block">
                            {palace.star} {refs.starsMap[palace.star]?.name_ru || ''}
                        </Typography>
                    )}
                </Box>
            )}

            <Typography
                variant="caption"
                sx={{ position: 'absolute', top: 4, right: 6, fontWeight: 'bold', color: bgColor }}
            >
                5
            </Typography>
        </Paper>
    );
};

const QimenGridV2 = ({ chart, selectedPalace, onPalaceClick, levelLabel = '' }) => {
    const [refs, setRefs] = useState({ starsMap: {}, gatesMap: {}, spiritsMap: {} });

    useEffect(() => {
        let cancelled = false;
        const load = async () => {
            try {
                const [stars, gates, spirits] = await Promise.all([
                    qimenService.fetchStars(),
                    qimenService.fetchGates(),
                    qimenService.fetchSpirits(),
                ]);
                if (cancelled) return;
                const toMap = (arr, keyField) => {
                    const map = {};
                    (arr || []).forEach((item) => {
                        map[item[keyField]] = item;
                    });
                    return map;
                };
                setRefs({
                    starsMap: toMap(stars, 'star_char'),
                    gatesMap: toMap(gates, 'gate_char'),
                    spiritsMap: toMap(spirits, 'spirit_char'),
                });
            } catch (err) {
                console.error('Failed to load QM references', err);
            }
        };
        load();
        return () => {
            cancelled = true;
        };
    }, []);

    if (!chart || !chart.palaces) {
        return (
            <Box sx={{ p: 3, textAlign: 'center' }}>
                <Typography variant="body1" color="text.secondary">
                    Расклад не загружен или не содержит данных
                </Typography>
            </Box>
        );
    }

    return (
        <Box sx={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            {/* Верхняя граница */}
            <Box sx={{ display: 'flex', width: '100%', maxWidth: 800, mb: 0.5 }}>
                {BORDER_TOP.map((b, i) => (
                    <BorderSegment key={i} {...b} />
                ))}
            </Box>

            {/* Середина: левая граница + сетка + правая граница */}
            <Box sx={{ display: 'flex', width: '100%', maxWidth: 800 }}>
                {/* Левая граница */}
                <Box sx={{ display: 'flex', flexDirection: 'column', mr: 0.5, width: 60 }}>
                    {BORDER_LEFT.map((b, i) => (
                        <BorderSegment key={i} {...b} />
                    ))}
                </Box>

                {/* Сетка */}
                <Box sx={{ flex: 1 }}>
                    {GRID_ORDER.map((row, rowIdx) => (
                        <Grid container spacing={1} key={rowIdx} sx={{ mb: 1 }}>
                            {row.map((palaceNo) => {
                                const palace = chart.palaces[palaceNo] || null;
                                const isSelected = selectedPalace === palaceNo;
                                const handleClick = () => onPalaceClick && onPalaceClick(palaceNo);
                                return (
                                    <Grid item xs={4} key={palaceNo}>
                                        {palaceNo === 5 ? (
                                            <CenterCell
                                                chart={chart}
                                                palace={palace}
                                                isSelected={isSelected}
                                                onClick={handleClick}
                                                refs={refs}
                                                levelLabel={levelLabel}
                                            />
                                        ) : (
                                            <PalaceCell
                                                palace={palace}
                                                isSelected={isSelected}
                                                onClick={handleClick}
                                                refs={refs}
                                            />
                                        )}
                                    </Grid>
                                );
                            })}
                        </Grid>
                    ))}
                </Box>

                {/* Правая граница */}
                <Box sx={{ display: 'flex', flexDirection: 'column', ml: 0.5, width: 60 }}>
                    {BORDER_RIGHT.map((b, i) => (
                        <BorderSegment key={i} {...b} />
                    ))}
                </Box>
            </Box>

            {/* Нижняя граница */}
            <Box sx={{ display: 'flex', width: '100%', maxWidth: 800, mt: 0.5 }}>
                {BORDER_BOTTOM.map((b, i) => (
                    <BorderSegment key={i} {...b} />
                ))}
            </Box>
        </Box>
    );
};

export default React.memo(QimenGridV2);
