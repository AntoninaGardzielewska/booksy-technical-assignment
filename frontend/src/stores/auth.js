import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '../api'

export const useAuthStore = defineStore('auth', () => {
    const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
    const token = ref(localStorage.getItem('access_token') || '')

    const isAuthenticated = computed(() => !!token.value && !!user.value)
    const isAdmin = computed(() => user.value?.role === 'admin')

    const setAuth = (userData, accessToken) => {
        user.value = userData
        token.value = accessToken
        localStorage.setItem('user', JSON.stringify(userData))
        localStorage.setItem('access_token', accessToken)
    }

    const login = async (email, password) => {
        const response = await authAPI.login(email, password)
        setAuth(response.data.user, response.data.access_token)
        return response.data.user
    }

    const logout = () => {
        user.value = null
        token.value = ''
        authAPI.logout()
    }

    return {
        user,
        token,
        isAuthenticated,
        isAdmin,
        login,
        logout,
        setAuth
    }
})
