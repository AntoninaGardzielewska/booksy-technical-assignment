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
        <div class="rental-header">
          <h3>{{ rental.hardware.name }}</h3>
          <span :class="['badge', rental.returned_at ? 'badge-available' : 'badge-in-use']">
            {{ rental.returned_at ? 'Returned' : 'Active' }}
          </span>
        </div>

        <div class="rental-details">
          <div class="detail-row">
            <span class="detail-label">Brand:</span>
            <span class="detail-value">{{ rental.hardware.brand }}</span>
          </div>

          <div class="detail-row">
            <span class="detail-label">Rented On:</span>
            <span class="detail-value">{{ formatDate(rental.rented_at) }}</span>
          </div>

          <div v-if="rental.returned_at" class="detail-row">
            <span class="detail-label">Returned On:</span>
            <span class="detail-value">{{ formatDate(rental.returned_at) }}</span>
          </div>

          <div class="detail-row">
            <span class="detail-label">Duration:</span>
            <span class="detail-value">{{ calculateDuration(rental) }}</span>
          </div>

          <div v-if="rental.hardware.notes" class="detail-row">
            <span class="detail-label">Notes:</span>
            <span class="detail-value">{{ rental.hardware.notes }}</span>
          </div>
        </div>

        <div class="rental-actions">
          <button
            v-if="!rental.returned_at"
            @click="returnHardware(rental.hardware.id)"
            class="btn btn-success btn-small"
            :disabled="returning[rental.hardware.id]"
          >
            {{ returning[rental.hardware.id] ? 'Returning...' : 'Return Hardware' }}
          </button>
          <span v-else class="btn btn-secondary btn-small" disabled>Already Returned</span>
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
}

.rental-filters input {
  width: auto;
  margin: 0;
  cursor: pointer;
}

.rentals-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
}

.rental-item {
  display: flex;
  flex-direction: column;
}

.rental-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 1rem;
}

.rental-header h3 {
  margin: 0;
  flex: 1;
  color: #00B4D8;
}

.rental-details {
  flex: 1;
  margin-bottom: 1rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.75rem;
  font-size: 0.95rem;
}

.detail-label {
  font-weight: 600;
  color: #333;
  min-width: 120px;
}

.detail-value {
  color: #666;
  text-align: right;
  flex: 1;
}

.rental-actions {
  padding-top: 1rem;
  border-top: 1px solid #e0e0e0;
}

.rental-actions button {
  width: 100%;
}

.loading,
.empty {
  text-align: center;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  color: #666;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.alert {
  margin-bottom: 1.5rem;
}

@media (max-width: 768px) {
  .rentals-list {
    grid-template-columns: 1fr;
  }

  .detail-row {
    flex-direction: column;
  }

  .detail-value {
    text-align: left;
  }
}
</style>
