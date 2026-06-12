import api from './api';
import { getCached, setCached } from './cacheUtils';

const CACHE_TTL = 30 * 60 * 1000; // 30 minutes

/**
 * Сервис для взаимодействия с API календаря Тун Шу
 */
const tongShuService = {
    /**
     * Получает данные календаря Тун Шу на конкретный день
     * @param {string} targetDate - Дата в формате YYYY-MM-DD
     * @returns {Promise<Object>} - Данные календаря на день
     */
    fetchDayData: async (targetDate) => {
        const response = await api.get('/api/tongshu/calendar/day', {
            params: { target_date: targetDate }
        });
        return response.data;
    },

    /**
     * Получает данные календаря Тун Шу на неделю, начиная с указанной даты
     * @param {string} startDate - Начальная дата недели в формате YYYY-MM-DD
     * @returns {Promise<Object>} - Данные календаря на неделю
     */
    fetchWeekData: async (startDate) => {
        const response = await api.get('/api/tongshu/calendar/week', {
            params: { start_date: startDate }
        });
        return response.data;
    },

    /**
     * Получает данные календаря Тун Шу на месяц
     * @param {number} year - Год
     * @param {number} month - Месяц (1-12)
     * @returns {Promise<Object>} - Данные календаря на месяц
     */
    fetchMonthData: async (year, month) => {
        const response = await api.get('/api/tongshu/calendar/month', {
            params: { year, month }
        });
        return response.data;
    },

    /**
     * Получает данные календаря Тун Шу на год
     * @param {number} year - Год
     * @returns {Promise<Object>} - Данные календаря на год
     */
    fetchYearData: async (year) => {
        const response = await api.get('/api/tongshu/calendar/year', {
            params: { year }
        });
        return response.data;
    },

    /**
     * Получает почасовые данные календаря Тун Шу для конкретной даты
     * @param {string} dateStr - Дата в формате YYYY-MM-DD
     * @returns {Promise<Object>} - Почасовые данные календаря
     */
    fetchHoursData: async (dateStr) => {
        const response = await api.get(`/api/tongshu/hours/${dateStr}`);
        return response.data;
    },

    /**
     * Получает данные о благоприятных и неблагоприятных активностях на дату
     * @param {string} targetDate - Дата в формате YYYY-MM-DD
     * @returns {Promise<Object>} - Список активностей с их благоприятностью
     */
    fetchActivitiesData: async (targetDate) => {
        const response = await api.get(`/api/tongshu/activities/${targetDate}`);
        return response.data;
    },

    // ------------------------------------------------------------------
    // New methods using t_tung_shu_daily (SQLite-compatible)
    // ------------------------------------------------------------------

    /**
     * Получает данные Тун Шу на конкретный день из агрегатной таблицы
     * @param {string} targetDate - Дата в формате YYYY-MM-DD
     * @returns {Promise<Object>} - Данные дня
     */
    fetchDailyDayData: async (targetDate) => {
        const cacheKey = `tongshu_daily_day_${targetDate}`;
        const cached = getCached(cacheKey, CACHE_TTL);
        if (cached) return cached;
        const response = await api.get('/api/tongshu/daily/day', {
            params: { target_date: targetDate }
        });
        setCached(cacheKey, response.data);
        return response.data;
    },

    /**
     * Получает данные Тун Шу на месяц из агрегатной таблицы
     * @param {number} year - Год
     * @param {number} month - Месяц (1-12)
     * @returns {Promise<Array>} - Данные за месяц
     */
    fetchDailyMonthData: async (year, month) => {
        const cacheKey = `tongshu_daily_month_${year}_${month}`;
        const cached = getCached(cacheKey, CACHE_TTL);
        if (cached) return cached;
        const response = await api.get('/api/tongshu/daily/month', {
            params: { year, month }
        });
        setCached(cacheKey, response.data);
        return response.data;
    },

    /**
     * Получает данные Тун Шу на неделю из агрегатной таблицы
     * @param {string} startDate - Начальная дата в формате YYYY-MM-DD
     * @returns {Promise<Array>} - Данные за неделю
     */
    fetchDailyWeekData: async (startDate) => {
        const cacheKey = `tongshu_daily_week_${startDate}`;
        const cached = getCached(cacheKey, CACHE_TTL);
        if (cached) return cached;
        const response = await api.get('/api/tongshu/daily/week', {
            params: { start_date: startDate }
        });
        setCached(cacheKey, response.data);
        return response.data;
    },

    /**
     * Получает данные Тун Шу на год из агрегатной таблицы
     * @param {number} year - Год
     * @returns {Promise<Array>} - Данные за год
     */
    fetchDailyYearData: async (year) => {
        const cacheKey = `tongshu_daily_year_${year}`;
        const cached = getCached(cacheKey, CACHE_TTL);
        if (cached) return cached;
        const response = await api.get('/api/tongshu/daily/year', {
            params: { year }
        });
        setCached(cacheKey, response.data);
        return response.data;
    },

    /**
     * Получает персонализированные данные Тун Шу на день
     * @param {string} targetDate - Дата в формате YYYY-MM-DD
     * @param {number} profileId - ID профиля
     * @returns {Promise<Object>} - Персонализированные данные дня
     */
    fetchPersonalizedDayData: async (targetDate, profileId) => {
        const response = await api.get('/api/tongshu/personalized/day', {
            params: { target_date: targetDate, profile_id: profileId }
        });
        return response.data;
    }
};

export default tongShuService;
