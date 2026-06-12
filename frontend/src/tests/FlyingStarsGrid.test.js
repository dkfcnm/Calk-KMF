import React from 'react';
import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import FlyingStarsGrid from '../components/fengshui/FlyingStarsGrid';

describe('FlyingStarsGrid', () => {
    const mockChartData = {
        date_time: '2026-05-31T00:00:00',
        period: 9,
        palaces: {
            N: { palace: 1, year_star: 6, month_star: 1, day_star: 5, hour_star: 4, direction_ru: 'Север' },
            NE: { palace: 8, year_star: 4, month_star: 8, day_star: 3, hour_star: 2, direction_ru: 'Северо-восток' },
            E: { palace: 3, year_star: 8, month_star: 3, day_star: 7, hour_star: 6, direction_ru: 'Восток' },
            SE: { palace: 4, year_star: 9, month_star: 4, day_star: 8, hour_star: 7, direction_ru: 'Юго-восток' },
            S: { palace: 9, year_star: 5, month_star: 9, day_star: 4, hour_star: 3, direction_ru: 'Юг' },
            SW: { palace: 2, year_star: 7, month_star: 2, day_star: 6, hour_star: 5, direction_ru: 'Юго-запад' },
            W: { palace: 7, year_star: 3, month_star: 7, day_star: 2, hour_star: 1, direction_ru: 'Запад' },
            NW: { palace: 6, year_star: 2, month_star: 6, day_star: 1, hour_star: 9, direction_ru: 'Северо-запад' },
            C: { palace: 5, year_star: 1, month_star: 5, day_star: 9, hour_star: 8, direction_ru: 'Центр' },
        },
    };

    it('renders the grid with 9 palaces', () => {
        render(<FlyingStarsGrid chartData={mockChartData} />);
        expect(screen.getByText('Летящие Звёзды (Период 9)')).toBeInTheDocument();
        expect(screen.getByText('Север')).toBeInTheDocument();
        expect(screen.getByText('Центр')).toBeInTheDocument();
        expect(screen.getByText('Юг')).toBeInTheDocument();
    });

    it('renders star chips for each palace', () => {
        render(<FlyingStarsGrid chartData={mockChartData} />);
        // Проверяем наличие звезд в сетке (всего 9 дворцов x 4 звезды = 36 чипов)
        const chips = screen.getAllByText(/^[1-9]$/);
        expect(chips.length).toBeGreaterThanOrEqual(36);
    });

    it('shows fallback when no data', () => {
        render(<FlyingStarsGrid chartData={null} />);
        expect(screen.getByText('Данные Летящих Звезд недоступны')).toBeInTheDocument();
    });

    it('compact mode hides hour star and changes legend', () => {
        render(<FlyingStarsGrid chartData={mockChartData} compact />);
        // В compact mode легенда должна быть без "Час"
        expect(screen.getByText('Год ● Месяц ● День')).toBeInTheDocument();
        // hour_star chips не должны отображаться (в mockChartData hour_star=4 для N, 
        // но compact скрывает все hour_star chips)
        const chips = screen.getAllByText(/^[1-9]$/);
        // Без compact: 36 chips (9 x 4), с compact: 27 chips (9 x 3)
        expect(chips.length).toBe(27);
    });
});
