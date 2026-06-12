import api from './api';

const fengShuiService = {
    fetchFlyingStarsChart: async (date, hour = null) => {
        const params = { target_date: date };
        if (hour !== null) params.hour = hour;
        const response = await api.get('/api/fengshui/chart', { params });
        return response.data;
    },
    fetchCurrentFlyingStars: async () => {
        const response = await api.get('/api/fengshui/current');
        return response.data;
    },
    fetchFengShuiDirections: async (date, hour = null) => {
        const params = { target_date: date };
        if (hour !== null) params.hour = hour;
        const response = await api.get('/api/fengshui/directions', { params });
        return response.data;
    },
};

export default fengShuiService;
