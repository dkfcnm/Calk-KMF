import React from 'react';
import { render, screen } from '@testing-library/react';
import QimenGridV2 from './QimenGridV2';
import qimenService from '../../services/qimenService';

jest.mock('../../services/qimenService');

const mockPalaces = {
    '1': { palace_no: 1, heaven_stem: '戊', earth_stem: '癸', star: '蓬', gate: '休', spirit: '符', is_main_star: 0, is_main_gate: 0, is_fou_tou_heaven: 0, is_fou_tou_earth: 0 },
    '2': { palace_no: 2, heaven_stem: '己', earth_stem: '乙', star: '芮', gate: '死', spirit: '蛇', is_main_star: 0, is_main_gate: 0, is_fou_tou_heaven: 0, is_fou_tou_earth: 0 },
    '3': { palace_no: 3, heaven_stem: '庚', earth_stem: '丙', star: '冲', gate: '伤', spirit: '阴', is_main_star: 0, is_main_gate: 0, is_fou_tou_heaven: 0, is_fou_tou_earth: 0 },
    '4': { palace_no: 4, heaven_stem: '辛', earth_stem: '丁', star: '辅', gate: '杜', spirit: '合', is_main_star: 0, is_main_gate: 0, is_fou_tou_heaven: 0, is_fou_tou_earth: 0 },
    '5': { palace_no: 5, heaven_stem: '壬', earth_stem: '戊', star: '禽', gate: '', spirit: '陈', is_main_star: 0, is_main_gate: 0, is_fou_tou_heaven: 0, is_fou_tou_earth: 0 },
    '6': { palace_no: 6, heaven_stem: '癸', earth_stem: '己', star: '心', gate: '开', spirit: '雀', is_main_star: 0, is_main_gate: 0, is_fou_tou_heaven: 0, is_fou_tou_earth: 0 },
    '7': { palace_no: 7, heaven_stem: '丁', earth_stem: '庚', star: '柱', gate: '惊', spirit: '地', is_main_star: 0, is_main_gate: 0, is_fou_tou_heaven: 0, is_fou_tou_earth: 0 },
    '8': { palace_no: 8, heaven_stem: '丙', earth_stem: '辛', star: '任', gate: '生', spirit: '天', is_main_star: 0, is_main_gate: 0, is_fou_tou_heaven: 0, is_fou_tou_earth: 0 },
    '9': { palace_no: 9, heaven_stem: '乙', earth_stem: '壬', star: '英', gate: '景', spirit: '符', is_main_star: 0, is_main_gate: 0, is_fou_tou_heaven: 0, is_fou_tou_earth: 0 },
};

const mockChart = {
    chart_id: 'test',
    date_time: '2026-06-01 12:00',
    chart_num: 8,
    yin_yang: 'Yang',
    method: 'zhirun',
    level: 'hour',
    palaces: mockPalaces,
};

describe('QimenGridV2', () => {
    beforeEach(() => {
        jest.clearAllMocks();
        qimenService.fetchStars.mockResolvedValue([]);
        qimenService.fetchGates.mockResolvedValue([]);
        qimenService.fetchSpirits.mockResolvedValue([]);
    });

    it('renders without crashing', async () => {
        render(<QimenGridV2 chart={mockChart} levelLabel="Часа" />);
        expect(await screen.findByText('Расклад Часа')).toBeTruthy();
    });

    it('renders 9 palace cells', async () => {
        render(<QimenGridV2 chart={mockChart} levelLabel="Часа" />);
        const palaces = await screen.findAllByTestId(/qimen-palace-/);
        expect(palaces.length).toBe(9);
    });

    it('renders directional border segments', async () => {
        render(<QimenGridV2 chart={mockChart} levelLabel="Часа" />);
        expect(await screen.findByText('Дракон')).toBeTruthy();
        expect(await screen.findByText('Крыса')).toBeTruthy();
        expect(await screen.findByText('Змея')).toBeTruthy();
        expect(await screen.findByText('Обезьяна')).toBeTruthy();
    });

    it('shows loading state when chart is missing', () => {
        render(<QimenGridV2 chart={null} />);
        expect(screen.getByText(/Расклад не загружен/)).toBeTruthy();
    });
});
