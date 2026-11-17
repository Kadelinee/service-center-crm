
<script setup>
import { ref, computed, onMounted } from 'vue'

const API_URL = '/api/clients/'

function getCsrfToken() {
  const cookie = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))

  return cookie ? decodeURIComponent(cookie.split('=')[1]) : ''
}

const clients = ref([])
const search = ref('')
const showForm = ref(false)
const editingId = ref(null)
const error = ref('')
const loading = ref(false)

const form = ref({
  name: '',
  phone: '',
  email: ''
})


const filteredClients = computed(() =>
  clients.value.filter(client =>
    client.full_name.toLowerCase().includes(search.value.toLowerCase()) ||
    client.phone.includes(search.value)
  )
)


async function loadClients() {
  loading.value = true
  error.value = ''
  try {
    const response = await fetch(API_URL)
    if (!response.ok) throw new Error('Помилка завантаження')
    clients.value = await response.json()
  } catch (err) {
    error.value = 'Не вдалося завантажити клієнтів'
  } finally {
    loading.value = false
  }
}

onMounted(loadClients)

function openAddForm() {
  editingId.value = null
  form.value = { name: '', phone: '', email: '' }
  error.value = ''
  showForm.value = true
}


function editClient(client) {
  editingId.value = client.client_id
  form.value = {
    name: client.full_name,
    phone: client.phone,
    email: client.email || ''
  }

  error.value = ''
  showForm.value = true
}


async function saveClient() {
  const name = form.value.name.trim()
  const phone = form.value.phone.trim()
  const email = form.value.email.trim()

  if (!name || !phone) {
    error.value = 'Заповніть ПІБ та телефон'
    return
  }

  if (!/^\+?[0-9]{10,13}$/.test(phone)) {
    error.value = 'Введіть коректний номер телефону'
    return
  }

  if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    error.value = 'Введіть коректний email'
    return
  }

  const isEditing = editingId.value !== null

  const url = isEditing
    ? `${API_URL}${editingId.value}/`
    : API_URL

  try {
    error.value = ''

    const response = await fetch(url, {
      method: isEditing ? 'PATCH' : 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify({
        full_name: name,
        phone,
        email
      })
    })

    if (!response.ok) {
      const data = await response.json().catch(() => ({}))
      const message = Object.entries(data)
        .map(([field, messages]) =>
          `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`
        )
        .join('; ')

      throw new Error(message || `Помилка сервера: ${response.status}`)
    }

    closeForm()
    await loadClients()
  } catch (err) {
    error.value = err.message || 'Не вдалося зберегти клієнта'
  }
}


async function deleteClient(id) {
  if (!confirm('Видалити цього клієнта?')) return

  error.value = ''

  try {
    const response = await fetch(`${API_URL}${id}/`, {
      method: 'DELETE',
      credentials: 'same-origin',
      headers: {
        'X-CSRFToken': getCsrfToken()
      }
    })

    if (!response.ok) {
      const data = await response.json().catch(() => ({}))

      throw new Error(
        data.detail || `Помилка видалення: ${response.status}`
      )
    }

    await loadClients()
  } catch (err) {
    error.value = err.message || 'Не вдалося видалити клієнта'
  }
}


function closeForm() {
  showForm.value = false
  editingId.value = null
  error.value = ''
}
</script>

<template>
  <section class="content-card">
    <div class="section-header">
      <h2>Клієнти</h2>
      <button class="primary-btn" @click="openAddForm">
        + Додати клієнта
      </button>
    </div>

    <input
      v-model="search"
      class="search-input"
      placeholder="Пошук за ім'ям або телефоном"
    />

    <p v-if="loading">Завантаження клієнтів...</p>

    <p v-if="error && !showForm" class="form-error">
      {{ error }}
    </p>

    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>№</th>
            <th>ПІБ</th>
            <th>Телефон</th>
            <th>Email</th>
            <th>Дії</th>
          </tr>
        </thead>

        <tbody>
<tr v-for="client in filteredClients" :key="client.client_id">
    <td>{{ client.client_id }}</td>
    <td>{{ client.full_name }}</td>
    <td>{{ client.phone }}</td>
    <td>{{ client.email }}</td>
            <td class="actions-cell">
              <button class="edit-btn" @click="editClient(client)">
                Редагувати
              </button>

              <button class="delete-btn"
        @click="deleteClient(client.client_id)">
                Видалити
              </button>
            </td>
          </tr>

          <tr v-if="!loading && filteredClients.length === 0">
            <td colspan="5">Клієнтів не знайдено</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showForm" class="modal-overlay">
      <form class="modal" @submit.prevent="saveClient">
        <h2>{{ editingId !== null ? 'Редагувати клієнта' : 'Новий клієнт' }}</h2>

        <label>ПІБ</label>
        <input v-model="form.name" placeholder="Введіть ПІБ" />

        <label>Телефон</label>
        <input v-model="form.phone" placeholder="+380..." />

        <label>Email</label>
        <input v-model="form.email" type="email" placeholder="example@gmail.com" />

        <p v-if="error" class="form-error">{{ error }}</p>

        <div class="form-actions">
          <button type="button" class="cancel-btn" @click="closeForm">
            Скасувати
          </button>

          <button type="submit" class="primary-btn">
            Зберегти
          </button>
        </div>
      </form>
    </div>
  </section>
</template>