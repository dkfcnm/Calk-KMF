import React from 'react';
import {
    Box,
    Paper,
    Typography,
    Chip
} from '@mui/material';

/**
 * Компонент отображения дворца в раскладе Ци Мэнь
 * 
 * @param {object} props.data - данные о дворце
 * @param {boolean} props.isSelected - выбран ли дворец
 * @param {function} props.onClick - обработчик клика по дворцу
 */
const PalaceDetail = ({ data, isSelected = false, onClick }) => {
    if (!data) return null;

    const {
        palace_no,
        earth_stem,
        is_fou_tou_earth,
        heaven_stem,
        is_fou_tou_heaven,
        star,
        is_main_star,
        gate,
        is_main_gate,
        spirit
    } = data;

    return (
        <Paper
            elevation={isSelected ? 8 : 2}
            sx={{
                p: 1.5,
                borderRadius: 1,
                height: '100%',
                cursor: 'pointer',
                backgroundColor: isSelected ? 'primary.light' : 'background.paper',
                transition: 'all 0.3s ease',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                '&:hover': {
                    backgroundColor: isSelected ? 'primary.light' : 'action.hover',
                    elevation: isSelected ? 10 : 5,
                }
            }}
            onClick={onClick}
        >
            <Typography variant="subtitle1" align="center" gutterBottom>
                Дворец {palace_no}
            </Typography>

            {/* Земная ветвь дворца */}
            <Box mb={1}>
                <Typography variant="body2" align="center" color="text.secondary">
                    Земная ветвь:
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Typography variant="body1" fontWeight={600}>
                        {earth_stem}
                    </Typography>
                    {is_fou_tou_earth === 1 && (
                        <Chip
                            label="伏吟"
                            size="small"
                            color="warning"
                            sx={{ ml: 0.5, height: 16, fontSize: '0.6rem' }}
                        />
                    )}
                </Box>
            </Box>

            {/* Небесный ствол дворца */}
            <Box mb={1}>
                <Typography variant="body2" align="center" color="text.secondary">
                    Небесный ствол:
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Typography variant="body1" fontWeight={600}>
                        {heaven_stem}
                    </Typography>
                    {is_fou_tou_heaven === 1 && (
                        <Chip
                            label="伏吟"
                            size="small"
                            color="warning"
                            sx={{ ml: 0.5, height: 16, fontSize: '0.6rem' }}
                        />
                    )}
                </Box>
            </Box>

            {/* Звезда дворца */}
            <Box mb={1}>
                <Typography variant="body2" align="center" color="text.secondary">
                    Звезда:
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Typography variant="body1" fontWeight={600}>
                        {star}
                    </Typography>
                    {is_main_star === 1 && (
                        <Chip
                            label="值使"
                            size="small"
                            color="success"
                            sx={{ ml: 0.5, height: 16, fontSize: '0.6rem' }}
                        />
                    )}
                </Box>
            </Box>

            {/* Ворота дворца */}
            <Box mb={1}>
                <Typography variant="body2" align="center" color="text.secondary">
                    Ворота:
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Typography variant="body1" fontWeight={600}>
                        {gate}
                    </Typography>
                    {is_main_gate === 1 && (
                        <Chip
                            label="值符"
                            size="small"
                            color="success"
                            sx={{ ml: 0.5, height: 16, fontSize: '0.6rem' }}
                        />
                    )}
                </Box>
            </Box>

            {/* Дух дворца */}
            <Box>
                <Typography variant="body2" align="center" color="text.secondary">
                    Дух:
                </Typography>
                <Typography variant="body1" fontWeight={500} align="center">
                    {spirit}
                </Typography>
            </Box>
        </Paper>
    );
};

export default React.memo(PalaceDetail);