<template>
  <div class="admin-dashboard">
    <h1>Admin Dashboard</h1>

    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab"
        @click="activeTab = tab"
        :class="['tab-btn', { active: activeTab === tab }]"
      >
        {{ tab }}
      </button>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>

    <!-- Users Tab -->
    <template v-if="activeTab === 'Users'">
      <div class="tab-content">
        <h2>Manage Users</h2>

        <button @click="showUserForm = !showUserForm" class="btn btn-primary" style="margin-bottom: 1.5rem;">
          {{ showUserForm ? 'Cancel' : '+ Add User' }}
        </button>

        <div v-if="showUserForm" class="form-section">
          <h3>Create New User</h3>
          <form @submit.prevent="createUser">
            <div class="form-grid">
              <div class="form-group">
                <label for="new-email">Email</label>
                <input
                  id="new-email"
                  v-model="newUser.email"
                  type="email"
                  placeholder="user@booksy.com"
                  required
                />
              </div>

              <div class="form-group">
                <label for="new-password">Password</label>
                <input
                  id="new-password"
                  v-model="newUser.password"
                  type="password"
                  placeholder="Min 6 characters"
                  minlength="6"
                  required
                />
              </div>

              <div class="form-group">
                <label for="new-role">Role</label>
                <select id="new-role" v-model="newUser.role">
                  <option value="user">User</option>
                  <option value="admin">Admin</option>
                </select>
              </div>

              <div class="form-group">
                <label>&nbsp;</label>
                <button type="submit" class="btn btn-primary" :disabled="creatingUser">
                  {{ creatingUser ? 'Creating...' : 'Create User' }}
                </button>
              </div>
            </div>
          </form>
        </div>

        <div class="users-section">
          <h3>All Users</h3>
          <div v-if="loadingUsers" class="loading">
            <div class="spinner"></div>
          </div>
          <table v-else-if="users.length > 0" class="users-table">
            <thead>
              <tr>
                <th>Email</th>
                <th>Role</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td>{{ user.email }}</td>
                <td><span :class="['badge', user.role === 'admin' ? 'badge-admin' : '']">{{ user.role }}</span></td>
                <td>{{ formatDate(user.created_at) }}</td>
              </tr>
            </tbody>
          </table>
          <div v-else class="empty">No users found</div>
        </div>
      </div>
    </template>

    <!-- Hardware Tab -->
    <template v-if="activeTab === 'Hardware'">
        <div class="tab-content">
        <h2>Manage Hardware</h2>

        <button @click="showAddForm = !showAddForm" class="btn btn-primary" style="margin-bottom: 1.5rem;">
          {{ showAddForm ? 'Cancel' : '+ Add Hardware' }}
        </button>

        <div v-if="showAddForm" class="form-section">
          <h3>Add New Hardware</h3>
          <form @submit.prevent="addHardware">
            <div class="form-grid">
              <div class="form-group">
                <label for="hw-name">Name</label>
                <input
                  id="hw-name"
                  v-model="newHardware.name"
                  type="text"
                  placeholder="e.g., iPhone 13 Pro Max"
                  required
                />
              </div>

              <div class="form-group">
                <label for="hw-brand">Brand</label>
                <input
                  id="hw-brand"
                  v-model="newHardware.brand"
                  type="text"
                  placeholder="e.g., Apple"
                  required
                />
              </div>

              <div class="form-group">
                <label for="hw-date">Purchase Date (DD-MM-YYYY)</label>
                <input
                  id="hw-date"
                  v-model="newHardware.purchase_date"
                  type="text"
                  :placeholder="todayDateFormat"
                  pattern="\d{2}-\d{2}-\d{4}"
                  @change="validatePurchaseDate"
                  required
                />
              </div>

              <div class="form-group">
                <label for="hw-status">Status</label>
                <select id="hw-status" v-model="newHardware.status">
                  <option value="Available">Available</option>
                  <option value="In Use">In Use</option>
                  <option value="Repair">Repair</option>
                </select>
              </div>

              <div class="form-group" style="grid-column: 1 / -1;">
                <label for="hw-notes">Notes (Optional)</label>
                <textarea
                  id="hw-notes"
                  v-model="newHardware.notes"
                  placeholder="Any special notes..."
                  rows="3"
                ></textarea>
              </div>

              <div class="form-group" style="grid-column: 1 / -1;">
                <button type="submit" class="btn btn-primary" :disabled="addingHardware">
                  {{ addingHardware ? 'Adding...' : 'Add Hardware' }}
                </button>
              </div>
            </div>
          </form>
        </div>

<div class="hardware-section">
  <h3>All Hardware</h3>

  <div v-if="loadingHardware" class="loading">
    <div class="spinner"></div>
  </div>

  <template v-else>
    <div v-if="allHardware.length > 0" class="hardware-list">
      <div v-for="hw in allHardware" :key="hw.id" class="hw-card card">
        <div class="hw-info">
          <div class="hw-main">
            <h4 class="hw-name">{{ hw.name }}</h4>
            <p class="hw-meta">{{ hw.brand }} • {{ hw.purchase_date }}</p>
            <p v-if="hw.notes" class="hw-notes">{{ hw.notes }}</p>
          </div>
        </div>

        <div class="hw-actions">
          <button
            v-if="hw.status === 'Repair'"
            @click="toggleRepair(hw.id)"
            class="btn btn-small"
            :disabled="togglingRepair[hw.id]"
            style="background: #d1d5db; color: #4b5563; border: 1px solid #9ca3af;"
          >
            {{ togglingRepair[hw.id] ? 'Finishing...' : 'Finish Repair' }}
          </button>
          <button
            v-else-if="hw.status === 'In Use'"
            class="btn btn-small"
            disabled
            style="background: #f3f4f6; color: #9ca3af; border: 1px solid #e5e7eb; cursor: not-allowed;"
          >
            Start Repair
          </button>
          <button
            v-else
            @click="toggleRepair(hw.id)"
            class="btn btn-small"
            :disabled="togglingRepair[hw.id]"
            style="background: #218cac; color: #fff; border: 1px solid #1a7a96;"
          >
            {{ togglingRepair[hw.id] ? 'Starting...' : 'Start Repair' }}
          </button>
          <button
            @click="deleteHardware(hw.id)"
            class="btn btn-danger btn-small"
            :disabled="deleting[hw.id]"
          >
            {{ deleting[hw.id] ? 'Deleting...' : 'Delete' }}
          </button>
        </div>
      </div>
    </div>

    <div v-else class="empty">
      No hardware found
    </div>
  </template>
</div>
</div>
</template>
</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminAPI, dashboardAPI } from '../api'

// State
const activeTab = ref('Users')
const tabs = ['Users', 'Hardware']
const error = ref('')
const success = ref('')
const showAddForm = ref(false)
const showUserForm = ref(false)

// Users
const users = ref([])
const loadingUsers = ref(false)
const creatingUser = ref(false)
const newUser = ref({
  email: '',
  password: '',
  role: 'user'
})

// Hardware
const allHardware = ref([])
const loadingHardware = ref(false)
const addingHardware = ref(false)
const deleting = ref({})
const togglingRepair = ref({})
const newHardware = ref({
  name: '',
  brand: '',
  purchase_date: '',
  status: 'Available',
  notes: ''
})

// Helper to get today's date in DD-MM-YYYY format
const getTodayDateFormat = () => {
  const today = new Date()
  const day = String(today.getDate()).padStart(2, '0')
  const month = String(today.getMonth() + 1).padStart(2, '0')
  const year = today.getFullYear()
  return `${day}-${month}-${year}`
}

const todayDateFormat = getTodayDateFormat()

// Validate purchase date is not in the future
const validatePurchaseDate = () => {
  if (!newHardware.value.purchase_date) return
  
  const [day, month, year] = newHardware.value.purchase_date.split('-').map(Number)
  const inputDate = new Date(year, month - 1, day)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  if (inputDate > today) {
    error.value = 'Purchase date cannot be in the future'
    newHardware.value.purchase_date = ''
  }
}

// Load users
const loadUsers = async () => {
  loadingUsers.value = true
  error.value = ''

  try {
    const response = await adminAPI.listUsers()
    users.value = response.data
  } catch (err) {
    error.value = 'Failed to load users'
    console.error(err)
  } finally {
    loadingUsers.value = false
  }
}

// Create user
const createUser = async () => {
  creatingUser.value = true
  error.value = ''
  success.value = ''

  try {
    await adminAPI.createUser(newUser.value)
    success.value = `User ${newUser.value.email} created successfully!`
    newUser.value = { email: '', password: '', role: 'user' }
    await loadUsers()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to create user'
  } finally {
    creatingUser.value = false
  }
}

// Load hardware
const loadHardware = async () => {
  loadingHardware.value = true
  error.value = ''

  try {
    const response = await dashboardAPI.listHardware({ skip: 0, limit: 20 })
    allHardware.value = response.data.items
  } catch (err) {
    error.value = 'Failed to load hardware'
    console.error(err)
  } finally {
    loadingHardware.value = false
  }
}

// Add hardware
const addHardware = async () => {
  addingHardware.value = true
  error.value = ''
  success.value = ''

  try {
    await adminAPI.addHardware(newHardware.value)
    success.value = `Hardware "${newHardware.value.name}" added successfully!`
    newHardware.value = {
      name: '',
      brand: '',
      purchase_date: '',
      status: 'Available',
      notes: ''
    }
    await loadHardware()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to add hardware'
  } finally {
    addingHardware.value = false
  }
}

// Delete hardware
const deleteHardware = async (hardwareId) => {
  if (!confirm('Are you sure you want to delete this hardware?')) {
    return
  }

  deleting.value[hardwareId] = true
  error.value = ''
  success.value = ''

  try {
    await adminAPI.deleteHardware(hardwareId)
    success.value = 'Hardware deleted successfully!'
    await loadHardware()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to delete hardware'
  } finally {
    deleting.value[hardwareId] = false
  }
}

// Toggle repair
const toggleRepair = async (hardwareId) => {
  togglingRepair.value[hardwareId] = true
  error.value = ''
  success.value = ''

  try {
    await adminAPI.toggleRepairStatus(hardwareId)
    success.value = 'Repair status updated!'
    await loadHardware()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to update repair status'
  } finally {
    togglingRepair.value[hardwareId] = false
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

onMounted(() => {
  loadUsers()
  loadHardware()
})
</script>

<style scoped>
.admin-dashboard {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

h1 {
  color: #1b1d21;
  font-size: 1.75rem;
  margin-bottom: 1.5rem;
}

h2 {
  color: #1b1d21;
  font-size: 1.25rem;
  margin-bottom: 1.5rem;
}

h3 {
  color: #1b1d21;
  margin-bottom: 1rem;
}

.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  border-bottom: 1px solid #e0e0e0;
}

.tab-btn {
  background: none;
  border: none;
  padding: 1rem 1.5rem;
  font-size: 1rem;
  font-weight: 500;
  color: #666;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: #1b1d21;
}

.tab-btn.active {
  color: #218cac;
  border-bottom-color: #218cac;
}

.tab-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.form-section {
  background: white;
  border: 1px solid #f0f0f0;
  border-radius: 10px;
  padding: 1.5rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.users-section,
.hardware-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid #f0f0f0;
}

.users-table thead {
  background: #f0f0f0;
}

.users-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #1b1d21;
  font-size: 0.9rem;
}

.users-table td {
  padding: 1rem;
  border-top: 1px solid #f0f0f0;
  color: #333;
}

.hardware-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.hw-card {
  padding: 1.25rem !important;
  display: grid !important;
  grid-template-columns: 1fr auto;
  gap: 1.5rem;
  align-items: start;
}

.hw-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.hw-main {
  flex: 1;
}

.hw-name {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1b1d21;
}

.hw-meta {
  margin: 0.25rem 0 0 0;
  font-size: 0.85rem;
  color: #999;
}

.hw-status {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.hw-notes {
  font-size: 0.85rem;
  color: #666;
  margin-top: 0.5rem;
}

.hw-actions {
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

.alert {
  border-radius: 10px;
  margin-bottom: 1.5rem;
}

.badge {
  padding: 0.3rem 0.6rem;
  font-size: 0.7rem;
  white-space: nowrap;
}

.text-success {
  color: #22c55e;
}

.text-danger {
  color: #ef4444;
}

.status-indicator {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-available {
  background: #d4f0d1;
  border: 1px solid #22c55e;
}

.status-inactive {
  background: #e5e5e5;
  border: 1px solid #999;
}

textarea::placeholder {
  color: #a0aec0;
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .hw-card {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .hw-info {
    flex-direction: column;
    gap: 0.75rem;
  }

  .hw-actions {
    justify-content: flex-end;
  }

  .users-table {
    font-size: 0.9rem;
  }

  .users-table th,
  .users-table td {
    padding: 0.75rem;
  }
}
</style>