import api from './api';
import { getCached, setCached } from './cacheUtils';

const CACHE_TTL = 60 * 60 * 1000; // 1 hour

const refsService = {
    // 12 Officers
    fetchOfficers: async () => {
        const cacheKey = 'refs_officers';
        const cached = getCached(cacheKey, CACHE_TTL);
        if (cached) return cached;
        const response = await api.get('/api/refs/officers');
        setCached(cacheKey, response.data);
        return response.data;
    },
    updateOfficer: async (id, data) => {
        const response = await api.put(`/api/refs/officers/${id}`, data);
        return response.data;
    },

    // 28 Constellations
    fetchConstellations: async () => {
        const cacheKey = 'refs_constellations';
        const cached = getCached(cacheKey, CACHE_TTL);
        if (cached) return cached;
        const response = await api.get('/api/refs/constellations');
        setCached(cacheKey, response.data);
        return response.data;
    },
    updateConstellation: async (id, data) => {
        const response = await api.put(`/api/refs/constellations/${id}`, data);
        return response.data;
    },

    // Belt Stars
    fetchBeltStars: async () => {
        const cacheKey = 'refs_belt_stars';
        const cached = getCached(cacheKey, CACHE_TTL);
        if (cached) return cached;
        const response = await api.get('/api/refs/belt-stars');
        setCached(cacheKey, response.data);
        return response.data;
    },
    updateBeltStar: async (id, data) => {
        const response = await api.put(`/api/refs/belt-stars/${id}`, data);
        return response.data;
    },

    // 10 Heavenly Stems
    fetchHeavenlyStems: async () => {
        const cacheKey = 'refs_heavenly_stems';
        const cached = getCached(cacheKey, CACHE_TTL);
        if (cached) return cached;
        const response = await api.get('/api/refs/heavenly-stems');
        setCached(cacheKey, response.data);
        return response.data;
    },
    updateHeavenlyStem: async (id, data) => {
        const response = await api.put(`/api/refs/heavenly-stems/${id}`, data);
        return response.data;
    },

    // 12 Earthly Branches
    fetchEarthlyBranches: async () => {
        const cacheKey = 'refs_earthly_branches';
        const cached = getCached(cacheKey, CACHE_TTL);
        if (cached) return cached;
        const response = await api.get('/api/refs/earthly-branches');
        setCached(cacheKey, response.data);
        return response.data;
    },
    updateEarthlyBranch: async (id, data) => {
        const response = await api.put(`/api/refs/earthly-branches/${id}`, data);
        return response.data;
    },

    // Black Rabbit Stars
    fetchBlackRabbitStars: async () => {
        const cacheKey = 'refs_black_rabbit_stars';
        const cached = getCached(cacheKey, CACHE_TTL);
        if (cached) return cached;
        const response = await api.get('/api/refs/black-rabbit-stars');
        setCached(cacheKey, response.data);
        return response.data;
    },
    updateBlackRabbitStar: async (starName, data) => {
        const response = await api.put(`/api/refs/black-rabbit-stars/${encodeURIComponent(starName)}`, data);
        return response.data;
    },

    // 5 Elements
    fetchElements: async () => {
        const cacheKey = 'refs_elements';
        const cached = getCached(cacheKey, CACHE_TTL);
        if (cached) return cached;
        const response = await api.get('/api/refs/elements');
        setCached(cacheKey, response.data);
        return response.data;
    },
    updateElement: async (id, data) => {
        const response = await api.put(`/api/refs/elements/${id}`, data);
        return response.data;
    },

    // Shen Sha (Symbolic Stars) Config
    fetchShenShaConfig: async () => {
        const cacheKey = 'refs_shensha_config';
        const cached = getCached(cacheKey, CACHE_TTL);
        if (cached) return cached;
        const response = await api.get('/api/refs/shensha-config');
        setCached(cacheKey, response.data);
        return response.data;
    },
    updateShenShaConfig: async (id, data) => {
        const response = await api.put(`/api/refs/shensha-config/${id}`, data);
        return response.data;
    },
};

export default refsService;
