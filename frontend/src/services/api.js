import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Единый axios instance для всего приложения.
 * Настроен с baseURL, interceptors для обработки ошибок и таймаутом.
 */
const api = axios.create({
    baseURL: API_URL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor
api.interceptors.request.use(
    (config) => {
        // Можно добавить токен авторизации здесь в будущем
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor
api.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        if (error.response) {
            // Сервер вернул ошибку (4xx, 5xx)
            console.error(
                `API Error [${error.response.status}]:`,
                error.response.data?.detail || error.message
            );
        } else if (error.request) {
            // Запрос был отправлен, но ответа не получено
            console.error('API Error: No response received from server');
        } else {
            // Ошибка при настройке запроса
            console.error('API Error:', error.message);
        }
        return Promise.reject(error);
    }
);

export default api;
