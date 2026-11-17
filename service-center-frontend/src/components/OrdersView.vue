<script setup>
import { ref, computed, onMounted } from 'vue'


const orders = ref([])
const loading = ref(false)
const loadError = ref('')


async function loadOrders() {
  loading.value = true
  loadError.value = ''

  try {
    const [ordersResponse, clientsResponse, linksResponse] =
      await Promise.all([
        fetch('/api/orders/', { credentials: 'same-origin' }),
        fetch('/api/clients/', { credentials: 'same-origin' }),
        fetch('/api/order-services/', { credentials: 'same-origin' })
      ])

    if (
      !ordersResponse.ok ||
      !clientsResponse.ok ||
      !linksResponse.ok
    ) {
      throw new Error('Не вдалося отримати дані з Django API')
    }

    const ordersData = await ordersResponse.json()
    const clientsData = await clientsResponse.json()
    const linksData = await linksResponse.json()

    const orderList = Array.isArray(ordersData)
      ? ordersData
      : ordersData.results || []

    const clientList = Array.isArray(clientsData)
      ? clientsData
      : clientsData.results || []

    const linkList = Array.isArray(linksData)
      ? linksData
      : linksData.results || []

    const clientNames = Object.fromEntries(
      clientList.map(client => [
        client.client_id,
        client.full_name
      ])
    )

    const servicesByOrder = {}

    linkList.forEach(link => {
      if (!servicesByOrder[link.order]) {
        servicesByOrder[link.order] = []
      }

      servicesByOrder[link.order].push(link.service_name)
    })

    orders.value = orderList.map(order => ({
      id: order.order_id,
      client: clientNames[order.client] ||
        `Клієнт №${order.client}`,
      service: servicesByOrder[order.order_id]?.join(', ') ||
        'Не вказано',
      status: order.status,
      price: order.total_price
    }))
  } catch (err) {
    loadError.value = err.message
    console.error(err)
  } finally {
    loading.value = false
  }
}


onMounted(loadOrders)


const clients = ref([])
const services = ref([])

async function loadFormOptions() {
  try {
    const [clientsResponse, servicesResponse] = await Promise.all([
      fetch('/api/clients/', { credentials: 'same-origin' }),
      fetch('/api/services/', { credentials: 'same-origin' })
    ])

    if (!clientsResponse.ok || !servicesResponse.ok) {
      throw new Error('Не вдалося завантажити дані форми')
    }

    const clientsData = await clientsResponse.json()
    const servicesData = await servicesResponse.json()

    clients.value = Array.isArray(clientsData)
      ? clientsData
      : clientsData.results || []

    services.value = Array.isArray(servicesData)
      ? servicesData
      : servicesData.results || []
  } catch (err) {
    error.value = err.message
  }
}

onMounted(loadFormOptions)

const statusNames = {
  new: 'Нове',
  confirmed: 'Підтверджено',
  in_progress: 'В роботі',
  completed: 'Виконано',
  cancelled: 'Скасовано'
}

const filterStatus = ref('all')
const showForm = ref(false)
const error = ref('')
const saving = ref(false)

const newOrder = ref({
  client: '',
  service: ''
})

const filteredOrders = computed(() =>
  filterStatus.value === 'all'
    ? orders.value
    : orders.value.filter(o => o.status === filterStatus.value)
)

function getCsrfToken() {
  const cookie = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))

  return cookie ? decodeURIComponent(cookie.split('=')[1]) : ''
}


async function changeStatus(order, event) {
  const newStatus = event.target.value
  const oldStatus = order.status

  order.status = newStatus
  loadError.value = ''

  try {
    const response = await fetch(`/api/orders/${order.id}/`, {
      method: 'PATCH',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify({
        status: newStatus
      })
    })

    if (!response.ok) {
      const data = await response.json().catch(() => ({}))
      throw new Error(
        JSON.stringify(data) || `Помилка сервера: ${response.status}`
      )
    }

    await loadOrders()
  } catch (err) {
    order.status = oldStatus
    loadError.value = `Не вдалося змінити статус: ${err.message}`
    event.target.value = oldStatus
  }
}



async function addOrder() {
  if (saving.value) return

  if (!newOrder.value.client || !newOrder.value.service) {
    error.value = 'Оберіть клієнта та послугу'
    return
  }

  saving.value = true
  error.value = ''

  try {
    const response = await fetch('/api/orders/', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify({
        client: Number(newOrder.value.client),
        service_id: Number(newOrder.value.service),
        quantity: 1,
        status: 'new'
      })
    })

    if (!response.ok) {
      const data = await response.json().catch(() => ({}))

      const message = Object.entries(data)
        .map(([field, messages]) =>
          `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`
        )
        .join('; ')

      throw new Error(
        message || `Помилка створення: ${response.status}`
      )
    }

    await loadOrders()
    closeForm()
  } catch (err) {
    error.value = err.message || 'Не вдалося створити замовлення'
  } finally {
    saving.value = false
  }
}


function closeForm() {
  showForm.value = false
  error.value = ''
  newOrder.value = { client: '', service: '' }
}
</script>

<template>
  <section class="content-card">
    <div class="section-header">
      <h2>Замовлення</h2>

      <div class="order-controls">
        <select v-model="filterStatus" class="filter-select">
          <option value="all">Усі статуси</option>
          <option
            v-for="(label, value) in statusNames"
            :key="value"
            :value="value"
          >
            {{ label }}
          </option>
        </select>

        <button class="primary-btn" @click="showForm = true">
          + Нове замовлення
        </button>
      </div>
    </div>

<p v-if="loading">Завантаження замовлень...</p>
<p v-if="loadError" class="form-error">{{ loadError }}</p>

    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>№</th>
            <th>Клієнт</th>
            <th>Послуга</th>
            <th>Статус</th>
            <th>Вартість</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="order in filteredOrders" :key="order.id">
            <td>{{ order.id }}</td>
            <td>{{ order.client }}</td>
            <td>{{ order.service }}</td>
            <td>
              <select
                :value="order.status"
                class="status-select"
                @change="changeStatus(order, $event)"
              >
                <option
                  v-for="(label, value) in statusNames"
                  :key="value"
                  :value="value"
                >
                  {{ label }}
                </option>
              </select>
            </td>
            <td>{{ order.price }} грн</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showForm" class="modal-overlay">
      <form class="modal" @submit.prevent="addOrder">
        <h2>Нове замовлення</h2>
 
<label>Клієнт</label>
<select v-model.number="newOrder.client" class="form-select">
  <option value="">Оберіть клієнта</option>
  <option
    v-for="client in clients"
    :key="client.client_id"
    :value="client.client_id"
  >
    {{ client.full_name }}
  </option>
</select>


        
<label>Послуга</label>
<select v-model.number="newOrder.service" class="form-select">
  <option value="">Оберіть послугу</option>
  <option
    v-for="service in services"
    :key="service.service_id"
    :value="service.service_id"
  >
    {{ service.name }} — {{ service.price }} грн
  </option>
</select>


        <p v-if="error" class="form-error">{{ error }}</p>

        <div class="form-actions">
          <button type="button" class="cancel-btn" @click="closeForm">
            Скасувати
          </button>

          
<button
  type="submit"
  class="primary-btn"
  :disabled="saving"
>
  {{ saving ? 'Збереження...' : 'Створити' }}
</button>

        </div>
      </form>
    </div>
  </section>
</template>
