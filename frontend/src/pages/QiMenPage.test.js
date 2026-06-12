import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import QiMenPage from './QiMenPage';
import qimenService from '../services/qimenService';

// Mock the service
jest.mock('../services/qimenService');

// Mock MUI DatePicker to avoid complex date handling in tests
jest.mock('@mui/x-date-pickers/DatePicker', () => ({
    DatePicker: ({ value, onChange, renderInput }) => renderInput({ inputProps: {}, InputProps: {} })
}));

jest.mock('@mui/x-date-pickers/AdapterDateFns', () => ({
    AdapterDateFns: () => null
}));

jest.mock('@mui/x-date-pickers/LocalizationProvider', () => ({
    LocalizationProvider: ({ children }) => children
}));

const mockPalaces = {
    '1': { palace_no: 1, heaven_stem: '戊', earth_stem: '戊', star: '蓬', gate: '休', spirit: '符', is_main_star: 0, is_main_gate: 0 },
    '2': { palace_no: 2, heaven_stem: '己', earth_stem: '己', star: '芮', gate: '死', spirit: '蛇', is_main_star: 0, is_main_gate: 0 },
    '3': { palace_no: 3, heaven_stem: '庚', earth_stem: '庚', star: '冲', gate: '伤', spirit: '阴', is_main_star: 0, is_main_gate: 0 },
    '4': { palace_no: 4, heaven_stem: '辛', earth_stem: '辛', star: '辅', gate: '杜', spirit: '合', is_main_star: 0, is_main_gate: 0 },
    '5': { palace_no: 5, heaven_stem: '壬', earth_stem: '壬', star: '禽', gate: '', spirit: '陈', is_main_star: 0, is_main_gate: 0 },
    '6': { palace_no: 6, heaven_stem: '癸', earth_stem: '癸', star: '心', gate: '开', spirit: '雀', is_main_star: 0, is_main_gate: 0 },
    '7': { palace_no: 7, heaven_stem: '丁', earth_stem: '丁', star: '柱', gate: '惊', spirit: '地', is_main_star: 0, is_main_gate: 0 },
    '8': { palace_no: 8, heaven_stem: '丙', earth_stem: '丙', star: '任', gate: '生', spirit: '天', is_main_star: 0, is_main_gate: 0 },
    '9': { palace_no: 9, heaven_stem: '乙', earth_stem: '乙', star: '英', gate: '景', spirit: '符', is_main_star: 0, is_main_gate: 0 },
};

const mockAllLevelsData = {
    year: {
        chart_id: 'zhirun_year_2026',
        date_time: '2026',
        chart_num: 1,
        yin_yang: 'Yang',
        year_pillar: '丙午',
        method: 'zhirun',
        level: 'year',
        palaces: mockPalaces
    },
    month: {
        chart_id: 'zhirun_month_2026_6',
        date_time: '2026-06',
        chart_num: 4,
        yin_yang: 'Yin',
        year_pillar: '丙午',
        month_pillar: '癸巳',
        method: 'zhirun',
        level: 'month',
        palaces: mockPalaces
    },
    day: {
        chart_id: 'zhirun_day_2026-06-01',
        date_time: '2026-06-01',
        chart_num: 4,
        yin_yang: 'Yang',
        year_pillar: '丙午',
        month_pillar: '癸巳',
        day_pillar: '丙午',
        method: 'zhirun',
        level: 'day',
        palaces: mockPalaces
    },
    hours: Array.from({ length: 12 }, (_, i) => ({
        chart_id: `zhirun_2026-06-01_${String(i * 2).padStart(2, '0')}:00`,
        date_time: `2026-06-01 ${String(i * 2).padStart(2, '0')}:00`,
        chart_num: 8,
        yin_yang: 'Yang',
        hour_pillar: '戊子',
        method: 'zhirun',
        level: 'hour',
        palaces: mockPalaces
    }))
};

describe('QiMenPage', () => {
    beforeEach(() => {
        jest.clearAllMocks();
        qimenService.fetchAllLevels.mockResolvedValue(mockAllLevelsData);
        qimenService.fetchStemCombo.mockResolvedValue({
            combo_char: '戊戊',
            favorability: -1,
            name_ru: 'Фу Инь',
            description_ru: 'Препятствия'
        });
        qimenService.fetchStars.mockResolvedValue([]);
        qimenService.fetchGates.mockResolvedValue([]);
        qimenService.fetchSpirits.mockResolvedValue([]);
        qimenService.fetchTrigrams.mockResolvedValue([]);
        qimenService.fetchStemCombos.mockResolvedValue([]);
    });

    it('renders the page title and level tabs', async () => {
        render(<QiMenPage />);
        
        const title = await screen.findByText('Расклады Ци Мэнь');
        expect(title).toBeTruthy();
        
        expect(await screen.findByRole('tab', { name: 'Час' })).toBeTruthy();
        expect(screen.getByRole('tab', { name: 'День' })).toBeTruthy();
        expect(screen.getByRole('tab', { name: 'Месяц' })).toBeTruthy();
        expect(screen.getByRole('tab', { name: 'Год' })).toBeTruthy();
    });

    it('loads and displays hour level by default', async () => {
        render(<QiMenPage />);
        
        await waitFor(() => {
            expect(qimenService.fetchAllLevels).toHaveBeenCalled();
        });

        // Should show the grid with palace cards
        const palaces = await screen.findAllByTestId(/qimen-palace-/);
        expect(palaces.length).toBeGreaterThanOrEqual(9);
    });

    it('switches to day level when day tab is clicked', async () => {
        render(<QiMenPage />);

        const dayTab = await screen.findByText('День');
        fireEvent.click(dayTab);

        // After clicking day tab, should still have the grid
        const palaces = await screen.findAllByTestId(/qimen-palace-/);
        expect(palaces.length).toBeGreaterThanOrEqual(9);
    });

    it('shows hour selector when hour tab is active', async () => {
        render(<QiMenPage />);
        
        const selector = await screen.findByLabelText('Двухчасовой интервал');
        expect(selector).toBeTruthy();
    });

    it('shows palace detail when a palace is clicked', async () => {
        render(<QiMenPage />);

        const palaceCard = await screen.findByTestId('qimen-palace-1');
        expect(palaceCard).toBeTruthy();

        fireEvent.click(palaceCard);

        // Should show palace extended info - look for the palace header
        await screen.findByText(/Дворец 1/);
    });

    it('handles missing data gracefully', async () => {
        qimenService.fetchAllLevels.mockResolvedValue({
            year: null,
            month: null,
            day: null,
            hours: []
        });

        render(<QiMenPage />);
        
        const noDataMessage = await screen.findByText(/Нет данных/);
        expect(noDataMessage).toBeTruthy();
    });
});
