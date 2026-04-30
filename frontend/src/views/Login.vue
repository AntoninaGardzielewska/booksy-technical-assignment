<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="login-title">📦 HardwareHub</h1>
      <p class="login-subtitle">Hardware Rental Management System</p>

      <form @submit.prevent="handleLogin">
        <div v-if="error" class="alert alert-error">{{ error }}</div>

        <div class="form-group">
          <label for="email">Email Address</label>
          <input
            id="email"
            v-model="email"
            type="email"
            placeholder="user@booksy.com"
            required
            @focus="error = ''"
          />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="••••••••"
            required
            @focus="error = ''"
          />
        </div>

        <button type="submit" class="btn btn-primary" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Sign In</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const authStore = useAuthStore()
const router = useRouter()

const handleLogin = async () => {
  error.value = ''
  loading.value = true

  try {
    await authStore.login(email.value, password.value)
    router.push('/dashboard')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #218cac 0%, #1a6a8a 100%);
  padding: 1rem;
}

.login-card {
  background: white;
  border-radius: 12px;
  padding: 3rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 400px;
}

.login-title {
  text-align: center;
  font-size: 2rem;
  margin-bottom: 0.5rem;
  color: #218cac;
}

.login-subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 2rem;
}

form {
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
}

.demo-credentials {
  text-align: center;
  padding-top: 1.5rem;
  border-top: 1px solid #e0e0e0;
  font-size: 0.875rem;
  color: #666;
}

.demo-credentials p {
  margin: 0.25rem 0;
}

@media (max-width: 480px) {
  .login-card {
    padding: 2rem;
  }

  .login-title {
    font-size: 1.5rem;
  }
}
</style>
