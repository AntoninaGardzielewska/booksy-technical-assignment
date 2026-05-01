<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <div>
        <h1 class="page-title">Hardware Catalog</h1>
        <p class="page-subtitle">Search for equipment, compare availability, and rent instantly.</p>
      </div>
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="🔍 Search hardware..."
          class="search-input"
          @keyup.enter="handleSemanticSearch"
        />
        <button @click="handleSemanticSearch" class="btn btn-primary btn-small">Search</button>
      </div>

      <div class="filters-group">
        <div class="filters-row">
          <select v-model="statusFilter" @change="loadHardware" class="filter-select filter-compact">
            <option value="">All Statuses</option>
            <option value="Available">Available</option>
            <option value="In Use">In Use</option>
            <option value="Repair">Repair</option>
          </select>

          <select v-model="brandFilter" @change="loadHardware" class="filter-select filter-compact">
            <option value="">All Brands</option>
            <option v-for="brand in uniqueBrands" :key="brand" :value="brand">
              {{ brand }}
            </option>
          </select>

          <select v-model="sortBy" @change="loadHardware" class="filter-select filter-compact">
            <option value="name">Sort by Name</option>
            <option value="brand">Sort by Brand</option>
            <option value="purchase_date">Sort by Date</option>
            <option value="status">Sort by Status</option>
          </select>
        </div>
      </div>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>

    <div class="hardware-list">
      <div
        v-for="hw in hardware"
        :key="hw.id"
        class="hardware-card card"
      >
        <div class="hardware-info">
          <div class="hardware-main">
            <h3 class="hardware-name">{{ hw.name }}</h3>
            <p class="hardware-meta">{{ hw.brand }} • {{ hw.purchase_date }}</p>
          </div>
          <div class="hardware-status">
            <span :class="['badge', `badge-${hw.status.toLowerCase().replace(' ', '-')}`]">
              {{ hw.status }}
            </span>
          </div>
          <div v-if="hw.notes" class="hardware-notes">{{ hw.notes }}</div>
        </div>

        <div class="card-actions">
          <template v-if="hw.status === 'Available'">
            <button
              @click="rentHardware(hw.id)"
              class="btn btn-primary btn-small"
              :disabled="renting[hw.id]"
            >
              {{ renting[hw.id] ? 'Renting...' : 'Rent' }}
            </button>
          </template>
          <template v-else>
            <button class="btn btn-small" disabled style="opacity: 0.5;">{{ hw.status }}</button>
          </template>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Loading hardware...</p>
    </div>

    <div v-if="!loading && hardware.length === 0" class="empty">
      <p>No hardware found</p>
    </div>

    <div class="pagination" v-if="totalItems > limit">
      <button
        @click="skip -= limit"
        :disabled="skip === 0"
        class="btn btn-small"
      >
        ← Previous
      </button>
      <span class="page-info">
        Showing {{ skip + 1 }} - {{ Math.min(skip + limit, totalItems) }} of {{ totalItems }}
      </span>
      <button
        @click="skip += limit"
        :disabled="skip + limit >= totalItems"
        class="btn btn-small"
      >
        Next →
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { dashboardAPI, searchAPI } from '../api'

const hardware = ref([])
const loading = ref(false)
const error = ref('')
const success = ref('')
const renting = ref({})

const statusFilter = ref('')
const brandFilter = ref('')
const sortBy = ref('name')
const searchQuery = ref('')
const skip = ref(0)
const limit = ref(20)
const totalItems = ref(0)

const uniqueBrands = computed(() => {
  const brands = new Set(hardware.value.map(hw => hw.brand))
  return Array.from(brands).sort()
})

const loadHardware = async () => {
  loading.value = true
  error.value = ''

  try {
    const params = {
      skip: skip.value,
      limit: limit.value,
      sort_by: sortBy.value
    }

    if (statusFilter.value) {
      params.status_filter = statusFilter.value
    }

    if (brandFilter.value) {
      params.brand_filter = brandFilter.value
    }

    const response = await dashboardAPI.listHardware(params)
    hardware.value = response.data.items
    totalItems.value = response.data.total
  } catch (err) {
    error.value = 'Failed to load hardware'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const rentHardware = async (hardwareId) => {
  renting.value[hardwareId] = true
  error.value = ''
  success.value = ''

  try {
    await dashboardAPI.rentHardware(hardwareId)
    success.value = 'Hardware rented successfully!'
    await loadHardware()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to rent hardware'
  } finally {
    renting.value[hardwareId] = false
  }
}

const handleSemanticSearch = async () => {
  // If search is cleared, return to normal hardware listing
  if (!searchQuery.value.trim()) {
    skip.value = 0
    await loadHardware()
    return
  }

  loading.value = true
  error.value = ''

  try {
    const response = await searchAPI.semanticSearch(searchQuery.value)
    let results = response.data.results

    // Apply filters to search results
    if (statusFilter.value) {
      results = results.filter(hw => hw.status === statusFilter.value)
    }
    if (brandFilter.value) {
      results = results.filter(hw => hw.brand === brandFilter.value)
    }

    // Apply sorting
    if (sortBy.value) {
      results.sort((a, b) => {
        if (sortBy.value === 'name') {
          return a.name.localeCompare(b.name)
        } else if (sortBy.value === 'brand') {
          return a.brand.localeCompare(b.brand)
        } else if (sortBy.value === 'purchase_date') {
          return new Date(a.purchase_date) - new Date(b.purchase_date)
        } else if (sortBy.value === 'status') {
          return a.status.localeCompare(b.status)
        }
      })
    }

    hardware.value = results
    totalItems.value = results.length
    success.value = `Found ${results.length} matching items`
  } catch (err) {
    error.value = 'Search failed'
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadHardware()
})
</script>

<style scoped>
.dashboard {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.dashboard-header {
  background: white;
  border-radius: 10px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  border: 1px solid #f0f0f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.page-title {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 700;
  color: #1b1d21;
}

.page-subtitle {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
}

.search-box {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.search-input {
  flex: 1;
  min-width: 0;
  padding: 0.65rem 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 0.9rem;
  background: white;
}

.search-input:focus {
  outline: none;
  border-color: #218cac;
  box-shadow: 0 0 0 3px rgba(33, 140, 172, 0.1);
}

.filters-group {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.filters-row {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  flex-wrap: wrap;
}

.filter-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 0.85rem;
  background: #f0f0f0;
  color: #1b1d21;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 60px;
  flex: 0 1 auto;
}

.filter-select:hover {
  border-color: #218cac;
  background: white;
}

.filter-select:focus {
  outline: none;
  border-color: #218cac;
  box-shadow: 0 0 0 3px rgba(33, 140, 172, 0.1);
}

.filter-compact {
  flex: 0 0 auto;
}

.hardware-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.hardware-card {
  padding: 1.25rem !important;
  display: grid !important;
  grid-template-columns: 1fr auto;
  gap: 1.5rem;
  align-items: start;
}

.hardware-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.hardware-main {
  flex: 1;
}

.hardware-name {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1b1d21;
}

.hardware-meta {
  margin: 0.25rem 0 0 0;
  font-size: 0.85rem;
  color: #999;
}

.hardware-status {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.hardware-notes {
  font-size: 0.85rem;
  color: #666;
  margin-top: 0.5rem;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
}

.badge {
  padding: 0.3rem 0.6rem;
  font-size: 0.7rem;
  white-space: nowrap;
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

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1.5rem;
}

.page-info {
  color: #999;
  font-size: 0.85rem;
}

.alert {
  border-radius: 10px;
}

@media (max-width: 768px) {
  .dashboard-header {
    padding: 1rem;
  }

  .page-title {
    font-size: 1.4rem;
  }

  .search-box {
    flex-direction: column;
  }

  .filters-group {
    flex-direction: column;
  }

  .filters-row {
    flex-direction: column;
  }

  .filter-select {
    width: 100%;
  }

  .hardware-card {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .hardware-info {
    flex-direction: column;
    gap: 0.75rem;
  }

  .card-actions {
    justify-content: flex-end;
  }
}
</style>
