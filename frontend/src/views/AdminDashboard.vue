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

        <div class="form-section">
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
                <th>Status</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td>{{ user.email }}</td>
                <td><span :class="['badge', user.role === 'admin' ? 'badge-admin' : '']">{{ user.role }}</span></td>
                <td><span :class="user.is_active ? 'text-success' : 'text-danger'">{{ user.is_active ? 'Active' : 'Inactive' }}</span></td>
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

        <div class="form-section">
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
                  placeholder="15-03-2022"
                  pattern="\d{2}-\d{2}-\d{4}"
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
    <div v-if="allHardware.length > 0" class="hardware-grid">

      <div v-for="hw in allHardware" :key="hw.id" class="hw-card">

        <div class="hw-header">
          <h4>{{ hw.name }}</h4>
          <span class="badge" :class="'badge-' + hw.status.toLowerCase().replace(' ', '-')">
            {{ hw.status }}
          </span>
        </div>

        <p class="hw-brand">{{ hw.brand }}</p>
        <p class="hw-date">Purchased: {{ hw.purchase_date }}</p>

        <div class="hw-actions">
          <button @click="toggleRepair(hw.id)" class="btn btn-warning btn-small">
            Toggle Repair
          </button>
          <button @click="deleteHardware(hw.id)" class="btn btn-danger btn-small">
            Delete
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