import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, fireEvent } from '@testing-library/react';
import CalendarGrid from '../components/tongshu/MonthlyCalendar/CalendarGrid';

const mockData = [
    {
        calendar_date: '2026-05-24',
        year_pillar: '丙午',
        month_pillar: '癸巳',
        day_pillar: '戊戌',
        year_stem: '丙',
        year_branch: '午',
        month_stem: '癸',
        month_branch: '巳',
        day_stem: '戊',
        day_branch: '戌',
        year_period: 3,
        month_period: 6,
        day_period: 6,
        year_element_num: 9,
        month_element_num: 8,
        day_element_num: 9,
        year_nayin_element: 'Вода',
        month_nayin_element: 'Вода',
        day_nayin_element: 'Дерево',
        hexagram_family_same: false,
        production_chain: false,
        lunar_day: 8,
        moon_phase_name: 'Растущая (более половины)',
        moon_phase_pct: 55.5,
        day_officer_char: '除',
        day_officer_name_ru: 'Удаление',
        day_officer_category: 'auspicious',
        constellation_char: '翼',
        constellation_name_ru: 'Крылья',
        constellation_direction: 'Юг',
        constellation_nature: 'auspicious',
        belt_type: 'yellow',
        belt_stars: ['Золотой замок'],
    }
];

const stemColors = { '丙': '#d32f2f', '癸': '#1976d2', '戊': '#388e3c' };
const branchColors = { '午': '#d32f2f', '巳': '#d32f2f', '戌': '#ed6c02' };

describe('CalendarGrid', () => {
    const selectedDate = new Date(2026, 4, 24); // May 24, 2026
    const currentDate = new Date(2026, 4, 24);
    const onDateClick = jest.fn();

    it('renders weekday headers', () => {
        render(
            <CalendarGrid
                data={mockData}
                selectedDate={selectedDate}
                currentDate={currentDate}
                onDateClick={onDateClick}
                stemColors={stemColors}
                branchColors={branchColors}
            />
        );
        expect(screen.getByText('Пн')).toBeInTheDocument();
        expect(screen.getByText('Вс')).toBeInTheDocument();
    });

    it('renders day number and lunar day', () => {
        render(
            <CalendarGrid
                data={mockData}
                selectedDate={selectedDate}
                currentDate={currentDate}
                onDateClick={onDateClick}
                stemColors={stemColors}
                branchColors={branchColors}
            />
        );
        expect(screen.getByText('24')).toBeInTheDocument();
        // Lunar day 8 with percentage: "8 / 56%"
        expect(screen.getByText(/8\s*\/\s*56%/)).toBeInTheDocument();
    });

    it('renders three pillars with stems and branches', () => {
        render(
            <CalendarGrid
                data={mockData}
                selectedDate={selectedDate}
                currentDate={currentDate}
                onDateClick={onDateClick}
                stemColors={stemColors}
                branchColors={branchColors}
            />
        );
        // Day pillar characters should be present
        expect(screen.getByText('戊')).toBeInTheDocument();
        expect(screen.getByText('戌')).toBeInTheDocument();
    });

    it('renders officer and constellation chips', () => {
        render(
            <CalendarGrid
                data={mockData}
                selectedDate={selectedDate}
                currentDate={currentDate}
                onDateClick={onDateClick}
                stemColors={stemColors}
                branchColors={branchColors}
            />
        );
        expect(screen.getByText('除')).toBeInTheDocument();
        expect(screen.getByText('翼')).toBeInTheDocument();
    });

    it('calls onDateClick when day cell is clicked', () => {
        render(
            <CalendarGrid
                data={mockData}
                selectedDate={selectedDate}
                currentDate={currentDate}
                onDateClick={onDateClick}
                stemColors={stemColors}
                branchColors={branchColors}
            />
        );
        const dayCell = screen.getByText('24').closest('.MuiPaper-root');
        if (dayCell) {
            fireEvent.click(dayCell);
            expect(onDateClick).toHaveBeenCalled();
        }
    });

    it('renders Na Yin elements as Chinese characters', () => {
        render(
            <CalendarGrid
                data={mockData}
                selectedDate={selectedDate}
                currentDate={currentDate}
                onDateClick={onDateClick}
                stemColors={stemColors}
                branchColors={branchColors}
            />
        );
        // Water = 水, Wood = 木 — may appear multiple times in the grid,
        // so we check that at least one instance is present.
        const waterElements = screen.queryAllByText('水');
        const woodElements = screen.queryAllByText('木');
        expect(waterElements.length).toBeGreaterThanOrEqual(1);
        expect(woodElements.length).toBeGreaterThanOrEqual(1);
    });
});
