<script setup>
import { ref, computed, onMounted } from 'vue'

const API_URL = '/api/services/'

const services = ref([])
const search = ref('')
const loading = ref(false)
const error = ref('')

const filteredServices = computed(() =>
  services.value.filter(service => {
    const query = search.value.toLowerCase()

    return (
      service.name.toLowerCase().includes(query) ||
      String(service.category).includes(query)
    )
  })
)

async function loadServices() {
  loading.value = true
  error.value = ''

  try {
    const response = await fetch(API_URL, {
      credentials: 'same-origin'
    })

    if (!response.ok) {
      throw new Error(`Помилка сервера: ${response.status}`)
    }

    const data = await response.json()
    services.value = Array.isArray(data) ? data : data.results || []
  } catch (err) {
    error.value = 'Не вдалося завантажити послуги'
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(loadServices)
</script>

<template>
  <section class="content-card">
    <div class="section-header">
      <h2>Послуги сервісного центру</h2>
    </div>

    <input
      v-model="search"
      class="search-input"
      placeholder="Пошук послуги або категорії"
    />

    <p v-if="loading">Завантаження послуг...</p>
    <p v-if="error" style="color: red">{{ error }}</p>

    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>№</th>
            <th>Назва послуги</th>
            <th>Категорія</th>
            <th>Вартість</th>
            <th>Тривалість</th>
          </tr>
        </thead>

        <tbody>
          <tr
            v-for="service in filteredServices"
            :key="service.service_id"
          >
            <td>{{ service.service_id }}</td>
            <td>{{ service.name }}</td>
            <td>Категорія №{{ service.category }}</td>
            <td>{{ service.price }} грн</td>
            <td>{{ service.duration_minutes }} хв</td>
          </tr>

          <tr v-if="!loading && filteredServices.length === 0">
            <td colspan="5">Послуг не знайдено</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
