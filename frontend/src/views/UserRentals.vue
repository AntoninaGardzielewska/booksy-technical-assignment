<template>
  <div class="rentals">
    <h1>My Rentals</h1>

    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>

    <div class="rental-filters">
      <label>
        <input v-model="showActive" type="checkbox" />
        <span>Show Active Only</span>
      </label>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Loading rentals...</p>
    </div>

    <div v-else-if="filteredRentals.length === 0" class="empty">
      <p>No rentals found</p>
    </div>

    <div v-else class="rentals-list">
      <div
        v-for="rental in filteredRentals"
        :key="rental.id"
        class="rental-item card"
      >
        <div class="rental-info">
          <div class="rental-main">
            <h3 class="rental-name">{{ rental.hardware.name }}</h3>
            <p class="rental-meta">{{ rental.hardware.brand }} • {{ formatDate(rental.rented_at) }}</p>
            <p v-if="rental.hardware.notes" class="rental-notes">{{ rental.hardware.notes }}</p>
          </div>

        </div>

        <div class="rental-actions">
          <button
            v-if="!rental.returned_at"
            @click="returnHardware(rental.hardware.id)"
            class="btn btn-primary btn-small"
            :disabled="returning[rental.hardware.id]"
          >
            {{ returning[rental.hardware.id] ? 'Returning...' : 'Return' }}
          </button>
          <button v-else class="btn btn-small" disabled style="opacity: 0.5;">Returned</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { dashboardAPI } from '../api'

const rentals = ref([])
const loading = ref(false)
const error = ref('')
const success = ref('')
const returning = ref({})
const showActive = ref(false)

const filteredRentals = computed(() => {
  if (!showActive.value) {
    return rentals.value
  }
  return rentals.value.filter(r => !r.returned_at)
})

const loadRentals = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await dashboardAPI.getUserRentals()
    rentals.value = response.data
  } catch (err) {
    error.value = 'Failed to load rentals'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const returnHardware = async (hardwareId) => {
  returning.value[hardwareId] = true
  error.value = ''
  success.value = ''

  try {
    await dashboardAPI.returnHardware(hardwareId)
    success.value = 'Hardware returned successfully!'
    await loadRentals()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to return hardware'
  } finally {
    returning.value[hardwareId] = false
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const calculateDuration = (rental) => {
  const startDate = new Date(rental.rented_at)
  const endDate = rental.returned_at ? new Date(rental.returned_at) : new Date()
  const diffTime = Math.abs(endDate - startDate)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return `${diffDays} day${diffDays !== 1 ? 's' : ''}`
}

onMounted(() => {
  loadRentals()
})
</script>

<style scoped>
.rentals {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

h1 {
  margin-bottom: 1.5rem;
  color: #1b1d21;
  font-size: 1.75rem;
}

.rental-filters {
  margin-bottom: 1.5rem;
  display: flex;
  gap: 1rem;
}

.rental-filters label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-weight: 500;
  color: #333;
}

.rental-filters input {
  width: auto;
  margin: 0;
  cursor: pointer;
}

.rentals-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.rental-item {
  padding: 1.25rem !important;
  display: grid !important;
  grid-template-columns: 1fr auto;
  gap: 1.5rem;
  align-items: start;
}

.rental-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.rental-main {
  flex: 1;
}

.rental-name {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1b1d21;
}

.rental-meta {
  margin: 0.25rem 0 0 0;
  font-size: 0.85rem;
  color: #999;
}

.rental-status {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.rental-notes {
  font-size: 0.85rem;
  color: #666;
  margin-top: 0.5rem;
}

.rental-actions {
  display: flex;
  gap: 0.5rem;
}

.loading,
.empty {
  text-align: center;
  padding: 2rem;
  background: white;
  border-radius: 10px;
  border: 1px solid #f0f0f0;
  color: #999;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.alert {
  border-radius: 10px;
  margin-bottom: 1.5rem;
}

@media (max-width: 768px) {
  h1 {
    font-size: 1.4rem;
  }

  .rental-item {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .rental-info {
    flex-direction: column;
    gap: 0.75rem;
  }

  .rental-actions {
    justify-content: flex-end;
  }
}
</style>
