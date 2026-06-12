import api from './api';

/**
 * Сервис для взаимодействия с API CRM-системы
 */
const crmService = {
    /**
     * Получение списка клиентов с возможностью поиска
     * @param {string} search - строка поиска (имя, email, телефон)
     * @param {number} limit - максимальное количество результатов
     * @param {number} offset - смещение для пагинации
     * @returns {Promise<Array>} - список клиентов
     */
    fetchClients: async (search = '', limit = 100, offset = 0) => {
        const response = await api.get('/api/crm/clients/', {
            params: { search, limit, offset }
        });
        return response.data;
    },

    /**
     * Получение детальной информации о клиенте по ID
     * @param {number} clientId - ID клиента
     * @returns {Promise<Object>} - данные клиента
     */
    fetchClientById: async (clientId) => {
        const response = await api.get(`/api/crm/clients/${clientId}`);
        return response.data;
    },

    /**
     * Создание нового клиента
     * @param {Object} clientData - данные клиента
     * @returns {Promise<Object>} - созданный клиент
     */
    createClient: async (clientData) => {
        const response = await api.post('/api/crm/clients/', clientData);
        return response.data;
    },

    /**
     * Обновление данных клиента
     * @param {number} clientId - ID клиента
     * @param {Object} clientData - данные для обновления
     * @returns {Promise<Object>} - обновленный клиент
     */
    updateClient: async (clientId, clientData) => {
        const response = await api.put(`/api/crm/clients/${clientId}`, clientData);
        return response.data;
    },

    /**
     * Удаление клиента
     * @param {number} clientId - ID клиента
     * @returns {Promise<Object>} - результат операции
     */
    deleteClient: async (clientId) => {
        const response = await api.delete(`/api/crm/clients/${clientId}`);
        return response.data;
    },

    /**
     * Создание новой сессии для клиента
     * @param {Object} sessionData - данные сессии
     * @returns {Promise<Object>} - созданная сессия
     */
    createSession: async (sessionData) => {
        const response = await api.post('/api/crm/sessions/', sessionData);
        return response.data;
    },

    /**
     * Получение списка сессий клиента
     * @param {number} clientId - ID клиента
     * @returns {Promise<Array>} - список сессий
     */
    fetchClientSessions: async (clientId) => {
        const response = await api.get(`/api/crm/clients/${clientId}/sessions`);
        return response.data;
    },

    /**
     * Связывание расчета с клиентом
     * @param {Object} linkData - данные связи
     * @returns {Promise<Object>} - связь расчета с клиентом
     */
    linkCalculation: async (linkData) => {
        const response = await api.post('/api/crm/calculations/link', linkData);
        return response.data;
    },

    /**
     * Получение списка расчетов, связанных с клиентом
     * @param {number} clientId - ID клиента
     * @returns {Promise<Array>} - список связанных расчетов
     */
    fetchClientCalculations: async (clientId) => {
        const response = await api.get(`/api/crm/clients/${clientId}/calculations`);
        return response.data;
    },

    /**
     * Создание заметки для клиента
     * @param {Object} noteData - данные заметки
     * @returns {Promise<Object>} - созданная заметка
     */
    createNote: async (noteData) => {
        const response = await api.post('/api/crm/notes/', noteData);
        return response.data;
    },

    /**
     * Получение списка заметок клиента
     * @param {number} clientId - ID клиента
     * @returns {Promise<Array>} - список заметок
     */
    fetchClientNotes: async (clientId) => {
        const response = await api.get(`/api/crm/clients/${clientId}/notes`);
        return response.data;
    }
};

export default crmService;
