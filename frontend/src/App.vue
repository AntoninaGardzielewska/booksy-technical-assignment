```vue
<template>
  <div id="app" class="app-container">
    <nav v-if="authStore.isAuthenticated" class="navbar">
      <div class="navbar-content">
        <router-link to="/dashboard" class="logo">
          HardwareHub
        </router-link>

        <div class="nav-center">
          <router-link to="/dashboard">Explore</router-link>
          <router-link to="/rentals">My Rentals</router-link>
          <router-link v-if="authStore.isAdmin" to="/admin">
            Admin
          </router-link>
        </div>

        <div class="nav-right">
          <button class="user-pill" @click="logout">
            {{ authStore.user?.email }}
          </button>
        </div>
      </div>
    </nav>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useAuthStore } from "./stores/auth"
import { useRouter } from "vue-router"

const authStore = useAuthStore()
const router = useRouter()

const logout = () => {
  authStore.logout()
  router.push("/login")
}
</script>