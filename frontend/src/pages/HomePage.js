import React from 'react';
import { Typography, Box, Card, CardContent, Grid, Button } from '@mui/material';
import { Link } from 'react-router-dom';
import { generateId } from '../hooks/useElementId';

function HomePage() {
    return (
        <Box data-element-id={generateId('home', 'page')}>
            <Typography variant="h4" component="h1" gutterBottom data-element-id={generateId('home', 'title')}>
                Платформа китайской метафизики
            </Typography>

            <Typography variant="body1" paragraph>
                Добро пожаловать в единую платформу для работы с инструментами китайской метафизики.
                Здесь вы можете просматривать календарь Тун Шу, расклады Ци Мэнь и управлять клиентами в CRM-системе.
            </Typography>

            <Grid container spacing={3} sx={{ mt: 3 }}>
                <Grid item xs={12} md={4}>
                    <Card data-element-id={generateId('home', 'card', 'tongshu')}>
                        <CardContent>
                            <Typography variant="h5" component="div" gutterBottom>
                                Тун Шу
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Календарь Тун Шу с возможностью просмотра по дням, неделям, месяцам и годам.
                                Информация о благоприятных и неблагоприятных днях, элементах и фазах.
                            </Typography>
                            <Button
                                component={Link}
                                to="/tongshu"
                                variant="contained"
                                color="primary"
                                sx={{ mt: 2 }}
                                data-element-id={generateId('home', 'btn', 'tongshu')}
                            >
                                Открыть календарь
                            </Button>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={4}>
                    <Card data-element-id={generateId('home', 'card', 'qimen')}>
                        <CardContent>
                            <Typography variant="h5" component="div" gutterBottom>
                                Ци Мэнь
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Расклады Ци Мэнь по различным методологиям (Чжи Рэн и Чай Бу).
                                Просмотр и анализ структур, дворцов, звезд и врат.
                            </Typography>
                            <Button
                                component={Link}
                                to="/qimen"
                                variant="contained"
                                color="primary"
                                sx={{ mt: 2 }}
                                data-element-id={generateId('home', 'btn', 'qimen')}
                            >
                                Открыть Ци Мэнь
                            </Button>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={4}>
                    <Card data-element-id={generateId('home', 'card', 'crm')}>
                        <CardContent>
                            <Typography variant="h5" component="div" gutterBottom>
                                CRM-система
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Управление клиентами, сессиями и расчетами.
                                Сохранение истории работы, заметок и рекомендаций.
                            </Typography>
                            <Button
                                component={Link}
                                to="/crm"
                                variant="contained"
                                color="primary"
                                sx={{ mt: 2 }}
                                data-element-id={generateId('home', 'btn', 'crm')}
                            >
                                Открыть CRM
                            </Button>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </Box>
    );
}

export default HomePage;