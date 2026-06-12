import React, { useState, useEffect } from 'react';
import {
    Box,
    Card,
    CardHeader,
    CardContent,
    Divider,
    Typography,
    Chip,
    List,
    ListItem,
    ListItemText,
    Alert,
    CircularProgress
} from '@mui/material';
import qimenService from '../../services/qimenService';

/**
 * Компонент для отображения расширенной информации о выбранном дворце
 * 
 * @param {object} props.palace - данные о выбранном дворце
 * @param {object} props.chart - полные данные расклада (для столпов и сезона)
 */
const PalaceExtendedInfo = ({ palace, chart }) => {
    const [stemCombo, setStemCombo] = useState(null);
    const [allCombos, setAllCombos] = useState([]);
    const [combosLoading, setCombosLoading] = useState(false);

    // Предзагружаем все комбинации стволов при монтировании
    useEffect(() => {
        let cancelled = false;
        const load = async () => {
            setCombosLoading(true);
            try {
                const combos = await qimenService.fetchStemCombos();
                if (!cancelled) setAllCombos(combos || []);
            } catch (err) {
                console.error('Failed to preload stem combos', err);
            } finally {
                if (!cancelled) setCombosLoading(false);
            }
        };
        load();
        return () => { cancelled = true; };
    }, []);

    // Ищем комбинацию локально при изменении дворца
    useEffect(() => {
        if (!palace || !palace.heaven_stem || !palace.earth_stem) {
            setStemCombo(null);
            return;
        }
        const combo = allCombos.find(
            (c) => c.stem_top === palace.heaven_stem && c.stem_bottom === palace.earth_stem
        );
        setStemCombo(combo || null);
    }, [palace, allCombos]);

    if (!palace) {
        return (
            <Card sx={{ mt: 2 }}>
                <CardContent>
                    <Typography variant="body1" align="center" color="text.secondary">
                        Выберите дворец для просмотра подробной информации
                    </Typography>
                </CardContent>
            </Card>
        );
    }

    const {
        palace_no,
        earth_stem,
        heaven_stem,
        star,
        gate,
        spirit,
        is_main_star,
        is_main_gate,
        is_fou_tou_heaven,
        is_fou_tou_earth
    } = palace;

    // Таблица соответствий для описаний звезд
    const starDescriptions = {
        "天蓬": "Небесное мужество (Тянь Пэн)",
        "天芮": "Небесная мягкость (Тянь Жуй)",
        "天冲": "Небесный прорыв (Тянь Чун)",
        "天辅": "Небесная поддержка (Тянь Фу)",
        "天禽": "Небесная птица (Тянь Цинь)",
        "天心": "Небесное сердце (Тянь Синь)",
        "天柱": "Небесная колонна (Тянь Чжу)",
        "天任": "Небесная ответственность (Тянь Жэнь)",
        "天英": "Небесный герой (Тянь Ин)",
        // Сокращённые формы из templates
        "蓬": "Небесное мужество (Тянь Пэн)",
        "芮": "Небесная мягкость (Тянь Жуй)",
        "冲": "Небесный прорыв (Тянь Чун)",
        "辅": "Небесная поддержка (Тянь Фу)",
        "禽": "Небесная птица (Тянь Цинь)",
        "心": "Небесное сердце (Тянь Синь)",
        "柱": "Небесная колонна (Тянь Чжу)",
        "任": "Небесная ответственность (Тянь Жэнь)",
        "英": "Небесный герой (Тянь Ин)"
    };

    // Таблица соответствий для описаний ворот
    const gateDescriptions = {
        "休门": "Ворота отдыха (Сю Мэнь)",
        "生门": "Ворота рождения (Шэн Мэнь)",
        "伤门": "Ворота ранения (Шан Мэнь)",
        "杜门": "Ворота преграды (Ду Мэнь)",
        "景门": "Ворота пейзажа (Цзин Мэнь)",
        "死门": "Ворота смерти (Сы Мэнь)",
        "惊门": "Ворота испуга (Цзин Мэнь)",
        "开门": "Ворота открытия (Кай Мэнь)",
        "神门": "Ворота духа (Шэнь Мэнь)",
        // Сокращённые формы
        "休": "Ворота отдыха (Сю Мэнь)",
        "生": "Ворота рождения (Шэн Мэнь)",
        "伤": "Ворота ранения (Шан Мэнь)",
        "杜": "Ворота преграды (Ду Мэнь)",
        "景": "Ворота пейзажа (Цзин Мэнь)",
        "死": "Ворота смерти (Сы Мэнь)",
        "惊": "Ворота испуга (Цзин Мэнь)",
        "开": "Ворота открытия (Кай Мэнь)"
    };

    // Таблица соответствий для описаний духов
    const spiritDescriptions = {
        "值符": "Дух власти (Чжи Фу)",
        "腾蛇": "Взлетающая змея (Тэн Шэ)",
        "太阴": "Великая Инь (Тай Инь)",
        "六合": "Шесть гармоний (Лю Хэ)",
        "白虎": "Белый тигр (Бай Ху)",
        "玄武": "Черный воин (Сюань У)",
        "九地": "Девять земель (Цзю Ди)",
        "九天": "Девять небес (Цзю Тянь)",
        // Сокращённые формы
        "符": "Дух власти (Чжи Фу)",
        "蛇": "Взлетающая змея (Тэн Шэ)",
        "阴": "Великая Инь (Тай Инь)",
        "合": "Шесть гармоний (Лю Хэ)",
        "陈": "Гоу Чэн (в некоторых школах)",
        "雀": "Чжу Цюэ (в некоторых школах)",
        "地": "Девять земель (Цзю Ди)",
        "天": "Девять небес (Цзю Тянь)"
    };

    // Определение элементальных свойств
    const getElementForStem = (stem) => {
        const elements = {
            "甲": "Дерево", "乙": "Дерево",
            "丙": "Огонь", "丁": "Огонь",
            "戊": "Земля", "己": "Земля",
            "庚": "Металл", "辛": "Металл",
            "壬": "Вода", "癸": "Вода"
        };
        return elements[stem] || "Неизвестно";
    };

    // Сезонная сила элемента
    const getSeasonalStrength = (element, monthBranch) => {
        // Карта сезонов по ветвям
        const seasonMap = {
            "寅": "Весна", "卯": "Весна", "辰": "Весна",
            "巳": "Лето", "午": "Лето", "未": "Лето",
            "申": "Осень", "酉": "Осень", "戌": "Осень",
            "亥": "Зима", "子": "Зима", "丑": "Зима"
        };

        const season = seasonMap[monthBranch] || "Неизвестно";

        const strengthRules = {
            "Весна": { "Дерево": "сильный", "Огонь": "средний", "Земля": "слабый", "Металл": "слабый", "Вода": "средний" },
            "Лето": { "Дерево": "средний", "Огонь": "сильный", "Земля": "средний", "Металл": "слабый", "Вода": "слабый" },
            "Осень": { "Дерево": "слабый", "Огонь": "слабый", "Земля": "средний", "Металл": "сильный", "Вода": "средний" },
            "Зима": { "Дерево": "средний", "Огонь": "слабый", "Земля": "слабый", "Металл": "средний", "Вода": "сильный" }
        };

        const seasonStrength = strengthRules[season] || {};
        return {
            season,
            strength: seasonStrength[element] || "средний"
        };
    };

    // Получаем элементы для стволов
    const earthElement = getElementForStem(earth_stem);
    const heavenElement = getElementForStem(heaven_stem);

    // Определяем сезон из месячного столпа расклада
    let monthBranch = "";
    if (chart && chart.month_pillar) {
        monthBranch = chart.month_pillar.slice(1); // второй иероглиф = ветвь
    }
    const heavenSeason = monthBranch ? getSeasonalStrength(heavenElement, monthBranch) : null;
    const earthSeason = monthBranch ? getSeasonalStrength(earthElement, monthBranch) : null;

    // Цвет для благоприятности комбинации
    const getFavorabilityColor = (fav) => {
        if (fav > 0) return 'success';
        if (fav < 0) return 'error';
        return 'warning';
    };

    const getFavorabilityLabel = (fav) => {
        if (fav > 0) return 'Благоприятная';
        if (fav < 0) return 'Неблагоприятная';
        return 'Нейтральная';
    };

    return (
        <Card sx={{ mt: 3 }} elevation={4}>
            <CardHeader
                title={`Дворец ${palace_no}`}
                subheader={`Небесный: ${heaven_stem} (${heavenElement}) | Земной: ${earth_stem} (${earthElement})`}
            />
            <CardContent>
                {/* Особые отметки */}
                <Box sx={{ mb: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {is_main_star === 1 && (
                        <Chip size="small" color="success" label="Главная звезда (值使)" />
                    )}
                    {is_main_gate === 1 && (
                        <Chip size="small" color="success" label="Главные врата (值符)" />
                    )}
                    {is_fou_tou_heaven === 1 && (
                        <Chip size="small" color="warning" label="伏吟 Небесный" />
                    )}
                    {is_fou_tou_earth === 1 && (
                        <Chip size="small" color="warning" label="伏吟 Земной" />
                    )}
                </Box>

                {/* Комбинация стволов (100 комбинаций) */}
                {combosLoading ? (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                        <CircularProgress size={16} />
                        <Typography variant="body2" color="text.secondary">
                            Загрузка комбинации...
                        </Typography>
                    </Box>
                ) : stemCombo ? (
                    <Box sx={{ mb: 2 }}>
                        <Alert severity={getFavorabilityColor(stemCombo.favorability)} sx={{ mb: 1 }}>
                            <Typography variant="subtitle2">
                                Комбинация {stemCombo.combo_char}: {stemCombo.name_ru}
                            </Typography>
                            <Typography variant="caption">
                                {getFavorabilityLabel(stemCombo.favorability)} ({stemCombo.favorability > 0 ? '+' : ''}{stemCombo.favorability})
                            </Typography>
                        </Alert>
                        <Typography variant="body2" color="text.secondary">
                            {stemCombo.description_ru}
                        </Typography>
                    </Box>
                ) : null}

                <Divider sx={{ my: 2 }} />

                {/* Звезда */}
                <Typography variant="h6" gutterBottom>
                    Звезда: {star}
                    {is_main_star === 1 && (
                        <Chip size="small" color="success" label="Главная" sx={{ ml: 1 }} />
                    )}
                </Typography>
                <Typography variant="body1" paragraph>
                    {starDescriptions[star] || "Описание отсутствует"}
                </Typography>

                <Divider sx={{ my: 2 }} />

                {/* Ворота */}
                <Typography variant="h6" gutterBottom>
                    Ворота: {gate}
                    {is_main_gate === 1 && (
                        <Chip size="small" color="success" label="Главные" sx={{ ml: 1 }} />
                    )}
                </Typography>
                <Typography variant="body1" paragraph>
                    {gateDescriptions[gate] || "Описание отсутствует"}
                </Typography>

                <Divider sx={{ my: 2 }} />

                {/* Дух */}
                <Typography variant="h6" gutterBottom>
                    Дух: {spirit}
                </Typography>
                <Typography variant="body1" paragraph>
                    {spiritDescriptions[spirit] || "Описание отсутствует"}
                </Typography>

                <Divider sx={{ my: 2 }} />

                {/* Взаимодействие элементов */}
                <Typography variant="h6" gutterBottom>
                    Взаимодействие элементов
                </Typography>
                <List dense>
                    <ListItem>
                        <ListItemText
                            primary={`Земной ствол (${earth_stem}): ${earthElement}`}
                            secondary="Влияет на физический уровень событий и материальные проявления"
                        />
                    </ListItem>
                    <ListItem>
                        <ListItemText
                            primary={`Небесный ствол (${heaven_stem}): ${heavenElement}`}
                            secondary="Влияет на энергетический и духовный уровень событий"
                        />
                    </ListItem>
                    <ListItem>
                        <ListItemText
                            primary={`Взаимодействие ${heavenElement} и ${earthElement}`}
                            secondary={getElementInteraction(heavenElement, earthElement)}
                        />
                    </ListItem>
                </List>

                {/* Сезонная сила */}
                {heavenSeason && earthSeason && (
                    <>
                        <Divider sx={{ my: 2 }} />
                        <Typography variant="h6" gutterBottom>
                            Сезонная сила ({heavenSeason.season})
                        </Typography>
                        <List dense>
                            <ListItem>
                                <ListItemText
                                    primary={`Небесный ствол (${heaven_stem}, ${heavenElement})`}
                                    secondary={`Сила: ${heavenSeason.strength}`}
                                />
                            </ListItem>
                            <ListItem>
                                <ListItemText
                                    primary={`Земной ствол (${earth_stem}, ${earthElement})`}
                                    secondary={`Сила: ${earthSeason.strength}`}
                                />
                            </ListItem>
                        </List>
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                            Сезонная сила определяется по месячной ветви расклада. 
                            Сильный элемент усиливает свои проявления, слабый — ослабляет.
                        </Typography>
                    </>
                )}
            </CardContent>
        </Card>
    );
};

/**
 * Функция для определения описания взаимодействия элементов
 */
function getElementInteraction(element1, element2) {
    if (element1 === element2) {
        return "Элементы одинаковы, что усиливает их проявление и создает гармонию.";
    }

    const interactions = {
        "Дерево-Огонь": "Дерево питает Огонь, способствуя его росту - благоприятное взаимодействие.",
        "Огонь-Земля": "Огонь создает Землю (пепел), укрепляя её - благоприятное взаимодействие.",
        "Земля-Металл": "Земля содержит и порождает Металл - благоприятное взаимодействие.",
        "Металл-Вода": "Металл собирает и очищает Воду - благоприятное взаимодействие.",
        "Вода-Дерево": "Вода питает Дерево, помогая ему расти - благоприятное взаимодействие.",

        "Дерево-Земля": "Дерево забирает силы у Земли - явление истощения.",
        "Огонь-Металл": "Огонь плавит Металл - явление разрушения.",
        "Земля-Вода": "Земля поглощает Воду - явление контроля.",
        "Металл-Дерево": "Металл рубит Дерево - явление противостояния.",
        "Вода-Огонь": "Вода тушит Огонь - явление сдерживания."
    };

    const key1 = `${element1}-${element2}`;
    const key2 = `${element2}-${element1}`;

    return interactions[key1] || interactions[key2] || "Нейтральное взаимодействие.";
}

export default PalaceExtendedInfo;
