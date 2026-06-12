import api from './api';

class ProfileService {
    async listProfiles(skip = 0, limit = 100, search = '') {
        const params = { skip: String(skip), limit: String(limit) };
        if (search) params.search = search;
        const res = await api.get('/api/profiles', { params });
        return res.data;
    }

    async getProfile(id) {
        const res = await api.get(`/api/profiles/${id}`);
        return res.data;
    }

    async createProfile(data) {
        const res = await api.post('/api/profiles', data);
        return res.data;
    }

    async updateProfile(id, data) {
        const res = await api.put(`/api/profiles/${id}`, data);
        return res.data;
    }

    async deleteProfile(id) {
        const res = await api.delete(`/api/profiles/${id}`);
        return res.data;
    }

    async calculateChart(id) {
        const res = await api.post(`/api/profiles/${id}/calculate-chart`);
        return res.data;
    }

    async searchCities(query, limit = 10) {
        const params = { q: query, limit: String(limit) };
        const res = await api.get('/api/profiles/cities/search', { params });
        return res.data;
    }
}

export default new ProfileService();
