import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, waitFor, act } from '@testing-library/react';
import ProfilesPage from '../pages/ProfilesPage';
import profileService from '../services/profileService';

// Mock the profileService module
jest.mock('../services/profileService', () => ({
    listProfiles: jest.fn(),
    getProfile: jest.fn(),
    createProfile: jest.fn(),
    updateProfile: jest.fn(),
    deleteProfile: jest.fn(),
    calculateChart: jest.fn(),
    searchCities: jest.fn(),
}));

describe('ProfilesPage', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    it('renders profiles list with birth chart chips', async () => {
        profileService.listProfiles.mockResolvedValueOnce({
            items: [
                {
                    id: 1,
                    name: 'Test User',
                    birth_date: '2026-05-15',
                    birth_time: '12:00:00',
                    birth_city: 'Moscow',
                    birth_chart: {
                        year_pillar: '丙午',
                        month_pillar: '癸巳',
                        day_pillar: '己丑',
                        hour_pillar: '壬申',
                        day_master: '己',
                    },
                },
            ],
            total: 1,
        });

        await act(async () => {
            render(<ProfilesPage />);
        });

        await waitFor(() => {
            expect(screen.getByText('Test User')).toBeInTheDocument();
        });

        expect(screen.getByText('丙午 癸巳 己丑 壬申')).toBeInTheDocument();
        expect(screen.getByText(/Дневной господин: 己/)).toBeInTheDocument();
    });

    it('renders empty state when no profiles', async () => {
        profileService.listProfiles.mockResolvedValueOnce({ items: [], total: 0 });

        await act(async () => {
            render(<ProfilesPage />);
        });

        await waitFor(() => {
            expect(screen.getByText(/Профили не созданы/)).toBeInTheDocument();
        });
    });

    it('renders add profile button', async () => {
        profileService.listProfiles.mockResolvedValueOnce({ items: [], total: 0 });

        await act(async () => {
            render(<ProfilesPage />);
        });

        await waitFor(() => {
            expect(screen.getByText('Добавить профиль')).toBeInTheDocument();
        });
    });
});
