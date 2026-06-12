import React, { useState, useEffect } from 'react';
import { Box, Paper, Typography, Divider } from '@mui/material';
import qimenService from '../../services/qimenService';

const SEASON_MAP = {
    '寅': 'Весна', '卯': 'Весна', '辰': 'Весна',
    '巳': 'Лето', '午': 'Лето', '未': 'Лето',
    '申': 'Осень', '酉': 'Осень', '戌': 'Осень',
    '亥': 'Зима', '子': 'Зима', '丑': 'Зима',
};

const BRANCH_ANIMALS = {
    '子': 'Крыса', '丑': 'Бык', '寅': 'Тигр', '卯': 'Кролик',
    '辰': 'Дракон', '巳': 'Змея', '午': 'Лошадь', '未': 'Коза',
    '申': 'Обезьяна', '酉': 'Петух', '戌': 'Собака', '亥': 'Свинья',
};

const DECADE_INSTRUMENT_MAP = {
    '甲': '戊', '己': '戊',
    '乙': '己', '庚': '己',
    '丙': '庚', '辛': '庚',
    '丁': '辛', '壬': '辛',
    '戊': '壬', '癸': '壬',
};

const QimenSummaryPanel = ({ chart }) => {
    const [trigrams, setTrigrams] = useState([]);

    useEffect(() => {
        let cancelled = false;
        qimenService.fetchTrigrams()
            .then((data) => {
                if (!cancelled) setTrigrams(data || []);
            })
            .catch(() => {});
        return () => { cancelled = true; };
    }, []);

    if (!chart) return null;

    const methodName = chart.method === 'zhirun' ? 'Джи Жэнь' : 'Чай Бу';

    const monthBranch = chart.month_pillar ? chart.month_pillar.slice(1) : '';
    const season = SEASON_MAP[monthBranch] || '—';

    const hourBranch = chart.hour_pillar ? chart.hour_pillar.slice(1) : '';
    const hourAnimal = BRANCH_ANIMALS[hourBranch] || '';
    const hourDisplay = hourBranch ? `${hourBranch} (${hourAnimal})` : '—';

    const dayStem = chart.day_pillar ? chart.day_pillar[0] : '';
    const instrument = DECADE_INSTRUMENT_MAP[dayStem] || '—';

    let mainStar = null;
    let mainGate = null;
    if (chart.palaces) {
        Object.values(chart.palaces).forEach((p) => {
            if (p.is_main_star === 1) mainStar = p;
            if (p.is_main_gate === 1) mainGate = p;
        });
    }

    return (
        <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
                Сводка
            </Typography>

            <Box sx={{ mb: 1 }}>
                <Typography variant="body2" color="text.secondary">
                    Сезон
                </Typography>
                <Typography variant="body1">{season}</Typography>
            </Box>

            <Divider sx={{ my: 1 }} />

            <Box sx={{ mb: 1 }}>
                <Typography variant="body2" color="text.secondary">
                    Час
                </Typography>
                <Typography variant="body1">{hourDisplay}</Typography>
            </Box>

            <Divider sx={{ my: 1 }} />

            <Box sx={{ mb: 1 }}>
                <Typography variant="body2" color="text.secondary">
                    Инструмент декады
                </Typography>
                <Typography variant="body1">{instrument}</Typography>
            </Box>

            <Divider sx={{ my: 1 }} />

            <Box sx={{ mb: 1 }}>
                <Typography variant="body2" color="text.secondary">
                    Главная звезда
                </Typography>
                <Typography variant="body1">
                    {mainStar ? `${mainStar.star} (Дворец ${mainStar.palace_no})` : '—'}
                </Typography>
            </Box>

            <Divider sx={{ my: 1 }} />

            <Box sx={{ mb: 1 }}>
                <Typography variant="body2" color="text.secondary">
                    Главные врата
                </Typography>
                <Typography variant="body1">
                    {mainGate ? `${mainGate.gate} (Дворец ${mainGate.palace_no})` : '—'}
                </Typography>
            </Box>

            <Divider sx={{ my: 1 }} />

            <Box sx={{ mb: 1 }}>
                <Typography variant="body2" color="text.secondary">
                    Система
                </Typography>
                <Typography variant="body1">В системе {methodName}</Typography>
            </Box>

            <Divider sx={{ my: 1 }} />

            <Typography variant="subtitle2" gutterBottom>
                Триграммы Ба Гуа
            </Typography>

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                {trigrams.map((t) => (
                    <Box key={t.trigram_id} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="body2" fontWeight="bold" sx={{ minWidth: 24 }}>
                            {t.trigram_char}
                        </Typography>
                        <Typography variant="caption">{t.trigram_name_ru}</Typography>
                        <Typography variant="caption" color="text.secondary">
                            ({Array.isArray(t.palace_nos) ? t.palace_nos.join(', ') : t.palace_nos})
                        </Typography>
                    </Box>
                ))}
            </Box>
        </Paper>
    );
};

export default QimenSummaryPanel;
