import apiClient from './client'

export const authAPI = {
    login: (email, password) =>
        apiClient.post('/auth/login', { email, password }),

    logout: () => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
    }
}

export const adminAPI = {
    createUser: (userData) =>
        apiClient.post('/admin/users', userData),

    listUsers: () =>
        apiClient.get('/admin/users'),

    addHardware: (hardwareData) =>
        apiClient.post('/admin/hardware', hardwareData),

    deleteHardware: (hardwareId) =>
        apiClient.delete(`/admin/hardware/${hardwareId}`),

    toggleRepairStatus: (hardwareId) =>
        apiClient.patch(`/admin/hardware/${hardwareId}/toggle-repair`)
}

export const dashboardAPI = {
    listHardware: (params) =>
        apiClient.get('/dashboard/hardware', { params }),

    rentHardware: (hardwareId) =>
        apiClient.post(`/dashboard/hardware/${hardwareId}/rent`),

    returnHardware: (hardwareId) =>
        apiClient.post(`/dashboard/hardware/${hardwareId}/return`),

    getUserRentals: () =>
        apiClient.get('/dashboard/user-rentals')
}

export const searchAPI = {
    semanticSearch: (query) =>
        apiClient.post('/search/semantic', { query })
}
