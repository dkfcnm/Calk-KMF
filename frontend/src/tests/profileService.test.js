import api from '../services/api';
import profileService from '../services/profileService';

jest.mock('../services/api', () => ({
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
}));

describe('profileService', () => {
    afterEach(() => {
        jest.resetAllMocks();
    });

    it('listProfiles calls correct endpoint', async () => {
        api.get.mockResolvedValueOnce({ data: { items: [], total: 0 } });

        await profileService.listProfiles();
        expect(api.get).toHaveBeenCalledWith('/api/profiles', { params: { skip: '0', limit: '100' } });
    });

    it('calculateChart calls POST endpoint', async () => {
        api.post.mockResolvedValueOnce({ data: { id: 1, day_master: '甲' } });

        await profileService.calculateChart(1);
        expect(api.post).toHaveBeenCalledWith('/api/profiles/1/calculate-chart');
    });

    it('searchCities calls cities endpoint with encoded query', async () => {
        api.get.mockResolvedValueOnce({ data: { cities: [{ city_name_ru: 'Москва' }] } });

        await profileService.searchCities('Моск');
        expect(api.get).toHaveBeenCalledWith('/api/profiles/cities/search', { params: { q: 'Моск', limit: '10' } });
    });
});
