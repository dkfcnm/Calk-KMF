import api from './api';
import { fetchCached } from './cacheUtils';

const CACHE_TTL = 60 * 60 * 1000; // 1 hour

const CACHE_KEYS = {
    stars: 'qimen_ref_stars',
    gates: 'qimen_ref_gates',
    spirits: 'qimen_ref_spirits',
    stemCombos: 'qimen_ref_stem_combos',
    trigrams: 'qimen_ref_trigrams',
};

/**
 * Сервис для взаимодействия с API Ци Мэнь
 */
const qimenService = {
    /**
     * Получить список раскладов Ци Мэнь для указанной методологии
     */
    fetchChartsList: async (
        method = 'zhirun',
        startDate = new Date(),
        endDate = new Date(),
        limit = 100,
        offset = 0
    ) => {
        const startDateStr = startDate.toISOString().split('T')[0];
        const endDateStr = endDate.toISOString().split('T')[0];

        const response = await api.get(`/api/qimen/charts/${method}`, {
            params: {
                start_date: startDateStr,
                end_date: endDateStr,
                limit,
                offset
            }
        });

        return response.data;
    },

    /**
     * Получить детальные данные расклада по ID
     */
    fetchChartById: async (chartId) => {
        const response = await api.get(`/api/qimen/chart/${chartId}`);
        return response.data;
    },

    /**
     * Рассчитать новый расклад Ци Мэнь на указанную дату
     */
    calculateChart: async (method, dateTime) => {
        const dateTimeStr = dateTime.toISOString().slice(0, 16).replace('T', ' ');

        const response = await api.get(`/api/qimen/calculate/${method}`, {
            params: { datetime_str: dateTimeStr }
        });

        return response.data;
    },

    /**
     * Получить текущий расклад Ци Мэнь
     */
    fetchCurrentChart: async (method) => {
        const response = await api.get(`/api/qimen/current/${method}`);
        return response.data;
    },

    /**
     * Получить данные конкретного дворца расклада
     */
    fetchPalaceData: async (chartId, palaceNo) => {
        const response = await api.get(`/api/qimen/palace/${chartId}/${palaceNo}`);
        return response.data;
    },

    // ------------------------------------------------------------------
    // Level endpoints
    // ------------------------------------------------------------------

    fetchAllLevels: async (method, targetDate) => {
        const dateStr = targetDate.toISOString().split('T')[0];
        const response = await api.get(`/api/qimen/levels/${method}`, {
            params: { target_date: dateStr }
        });
        return response.data;
    },

    fetchHourlyCharts: async (method, targetDate) => {
        const dateStr = targetDate.toISOString().split('T')[0];
        const response = await api.get(`/api/qimen/hourly/${method}`, {
            params: { target_date: dateStr }
        });
        return response.data;
    },

    fetchDailyChart: async (method, targetDate) => {
        const dateStr = targetDate.toISOString().split('T')[0];
        const response = await api.get(`/api/qimen/daily/${method}`, {
            params: { target_date: dateStr }
        });
        return response.data;
    },

    fetchMonthlyChart: async (method, year, month) => {
        const response = await api.get(`/api/qimen/monthly/${method}`, {
            params: { year, month }
        });
        return response.data;
    },

    fetchYearlyChart: async (method, year) => {
        const response = await api.get(`/api/qimen/yearly/${method}`, {
            params: { year }
        });
        return response.data;
    },

    // ------------------------------------------------------------------
    // Reference endpoints (with localStorage cache + TTL)
    // ------------------------------------------------------------------

    fetchStars: async () => fetchCached(CACHE_KEYS.stars, async () => {
        const response = await api.get('/api/qimen/references/stars');
        return response.data;
    }),

    fetchGates: async () => fetchCached(CACHE_KEYS.gates, async () => {
        const response = await api.get('/api/qimen/references/gates');
        return response.data;
    }),

    fetchSpirits: async () => fetchCached(CACHE_KEYS.spirits, async () => {
        const response = await api.get('/api/qimen/references/spirits');
        return response.data;
    }),

    fetchStemCombos: async () => fetchCached(CACHE_KEYS.stemCombos, async () => {
        const response = await api.get('/api/qimen/references/stem_combos');
        return response.data;
    }),

    fetchStemCombo: async (stemTop, stemBottom) => {
        const response = await api.get(`/api/qimen/references/stem_combo/${stemTop}/${stemBottom}`);
        return response.data;
    },

    fetchTrigrams: async () => fetchCached(CACHE_KEYS.trigrams, async () => {
        const response = await api.get('/api/qimen/references/trigrams');
        return response.data;
    }),

    /**
     * Предзагрузить все справочники Ци Мэнь
     */
    preloadAllReferences: async () => {
        await Promise.all([
            qimenService.fetchStars(),
            qimenService.fetchGates(),
            qimenService.fetchSpirits(),
            qimenService.fetchStemCombos(),
            qimenService.fetchTrigrams(),
        ]);
    },
};

export default qimenService;
