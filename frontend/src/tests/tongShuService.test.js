import tongShuService from '../services/tongShuService';

// Mock the api module
jest.mock('../services/api', () => ({
    get: jest.fn(),
}));

import api from '../services/api';

describe('tongShuService', () => {
    beforeEach(() => {
        api.get.mockClear();
    });

    it('fetchPersonalizedDayData calls correct endpoint', async () => {
        const mockResponse = {
            date: '2026-05-31',
            hidden_stems: { year: [{ stem: '丙', percentage: 70.0 }] },
            personalized_ten_gods: { year: 'dr', month: 'iw', day: 'ho', hour: 'dw' },
            profile: { id: 3, name: 'Test', day_master: '己' },
        };

        api.get.mockResolvedValueOnce({ data: mockResponse });

        const result = await tongShuService.fetchPersonalizedDayData('2026-05-31', 3);

        expect(api.get).toHaveBeenCalledWith(
            '/api/tongshu/personalized/day',
            { params: { target_date: '2026-05-31', profile_id: 3 } }
        );
        expect(result.profile.day_master).toBe('己');
        expect(result.personalized_ten_gods.year).toBe('dr');
    });

    it('fetchDailyDayData calls correct endpoint', async () => {
        api.get.mockResolvedValueOnce({ data: { calendar_date: '2026-05-31', day_pillar: '庚寅' } });

        await tongShuService.fetchDailyDayData('2026-05-31');
        expect(api.get).toHaveBeenCalledWith(
            '/api/tongshu/daily/day',
            { params: { target_date: '2026-05-31' } }
        );
    });
});
