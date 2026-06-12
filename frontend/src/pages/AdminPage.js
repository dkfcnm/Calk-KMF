import React from 'react';
import {
    Typography,
    Box,
    Paper,
    Switch,
    FormControlLabel,
    Divider,
    Alert,
    ToggleButtonGroup,
    ToggleButton,
} from '@mui/material';
import {
    Settings as SettingsIcon,
    LightMode as LightModeIcon,
    DarkMode as DarkModeIcon,
    ViewCompact as CompactIcon,
    ViewComfy as ComfortableIcon,
    Language as LanguageIcon,
} from '@mui/icons-material';
import { useElementIdMarker } from '../contexts/ElementIdMarkerContext';
import { useDebugMode } from '../contexts/DebugModeContext';
import { useDisplaySettings } from '../contexts/DisplaySettingsContext';

function AdminPage() {
    const { markerEnabled, toggleMarker } = useElementIdMarker();
    const { debugMode, toggleDebugMode } = useDebugMode();
    const { settings, setTheme, setDensity, setLanguage } = useDisplaySettings();

    return (
        <Box>
            <Typography variant="h4" component="h1" gutterBottom>
                Администратор
            </Typography>

            <Paper sx={{ p: 3, mb: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    <SettingsIcon color="primary" />
                    <Typography variant="h6">Визуальные настройки</Typography>
                </Box>

                <Alert severity="info" sx={{ mb: 2 }}>
                    Здесь вы можете управлять отображением вспомогательных элементов интерфейса.
                </Alert>

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <FormControlLabel
                        control={
                            <Switch
                                checked={markerEnabled}
                                onChange={toggleMarker}
                                color="primary"
                            />
                        }
                        label={
                            <Box>
                                <Typography variant="body1">
                                    Показывать ID элементов (¡)
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                    В правом верхнем углу каждого элемента отображается знак ¡. При нажатии на него открывается ID элемента для копирования.
                                </Typography>
                            </Box>
                        }
                    />

                    <Divider />

                    <FormControlLabel
                        control={
                            <Switch
                                checked={debugMode}
                                onChange={toggleDebugMode}
                                color="secondary"
                            />
                        }
                        label={
                            <Box>
                                <Typography variant="body1">
                                    Режим отладки UI (Debug Mode)
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                    Показывает визуальные badge с ID на элементах, обёрнутых в ElementIdBadge. Горячая клавиша: Ctrl+Shift+D.
                                </Typography>
                            </Box>
                        }
                    />
                </Box>
            </Paper>

            <Paper sx={{ p: 3, mb: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    <LightModeIcon color="primary" />
                    <Typography variant="h6">Тема оформления</Typography>
                </Box>

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <Box>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                            Выберите цветовую схему интерфейса:
                        </Typography>
                        <ToggleButtonGroup
                            value={settings.theme}
                            exclusive
                            onChange={(e, val) => val && setTheme(val)}
                            size="small"
                        >
                            <ToggleButton value="light">
                                <LightModeIcon fontSize="small" sx={{ mr: 0.5 }} />
                                Светлая
                            </ToggleButton>
                            <ToggleButton value="dark">
                                <DarkModeIcon fontSize="small" sx={{ mr: 0.5 }} />
                                Тёмная
                            </ToggleButton>
                        </ToggleButtonGroup>
                    </Box>

                    <Divider />

                    <Box>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                            Плотность элементов:
                        </Typography>
                        <ToggleButtonGroup
                            value={settings.density}
                            exclusive
                            onChange={(e, val) => val && setDensity(val)}
                            size="small"
                        >
                            <ToggleButton value="comfortable">
                                <ComfortableIcon fontSize="small" sx={{ mr: 0.5 }} />
                                Удобная
                            </ToggleButton>
                            <ToggleButton value="compact">
                                <CompactIcon fontSize="small" sx={{ mr: 0.5 }} />
                                Компактная
                            </ToggleButton>
                        </ToggleButtonGroup>
                    </Box>

                    <Divider />

                    <Box>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                            Язык интерфейса:
                        </Typography>
                        <ToggleButtonGroup
                            value={settings.language}
                            exclusive
                            onChange={(e, val) => val && setLanguage(val)}
                            size="small"
                        >
                            <ToggleButton value="ru">
                                <LanguageIcon fontSize="small" sx={{ mr: 0.5 }} />
                                Русский
                            </ToggleButton>
                            <ToggleButton value="en">
                                <LanguageIcon fontSize="small" sx={{ mr: 0.5 }} />
                                English
                            </ToggleButton>
                        </ToggleButtonGroup>
                        <Alert severity="warning" sx={{ mt: 1 }}>
                            Перевод на английский находится в разработке. Текущий интерфейс отображается на русском языке.
                        </Alert>
                    </Box>
                </Box>
            </Paper>

            <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                    Справка
                </Typography>
                <Typography variant="body2" color="text.secondary" component="div">
                    <Box component="ul" sx={{ pl: 2, mt: 1 }}>
                        <li><strong>ID элементов (¡)</strong> — вспомогательная система для точной коммуникации с AI-агентом. Каждый значимый элемент интерфейса получает уникальный ID.</li>
                        <li><strong>Режим отладки</strong> — технический режим для разработчиков. Показывает дополнительную информацию о компонентах.</li>
                        <li><strong>Тема оформления</strong> — переключение между светлой и тёмной цветовой схемой.</li>
                        <li><strong>Плотность</strong> — компактный режим уменьшает отступы между элементами для отображения большего объёма информации.</li>
                    </Box>
                </Typography>
            </Paper>
        </Box>
    );
}

export default AdminPage;
