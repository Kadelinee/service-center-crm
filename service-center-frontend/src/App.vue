<script setup>
import { ref, computed, onMounted, watch } from 'vue'

import ClientsView from './components/ClientsView.vue'
import OrdersView from './components/OrdersView.vue'
import ServicesView from './components/ServicesView.vue'

const activePage = ref('dashboard')

const menu = [
  { id: 'dashboard', title: 'Головна' },
  { id: 'clients', title: 'Клієнти' },
  { id: 'orders', title: 'Замовлення' },
  { id: 'services', title: 'Послуги' }
]

const clients = ref([])
const orders = ref([])
const loading = ref(false)
const error = ref('')

const statusNames = {
  new: 'Нове',
  confirmed: 'Підтверджено',
  in_progress: 'В роботі',
  completed: 'Виконано',
  cancelled: 'Скасовано'
}

const completedCount = computed(() =>
  orders.value.filter(order => order.status === 'completed').length
)

const recentOrders = computed(() =>
  [...orders.value]
    .sort((a, b) => b.id - a.id)
    .slice(0, 5)
)

function extractList(data) {
  return Array.isArray(data) ? data : data.results || []
}

async function loadDashboard() {
  loading.value = true
  error.value = ''

  try {
    const [clientsResponse, ordersResponse, linksResponse] =
      await Promise.all([
        fetch('/api/clients/', { credentials: 'same-origin' }),
        fetch('/api/orders/', { credentials: 'same-origin' }),
        fetch('/api/order-services/', {
          credentials: 'same-origin'
        })
      ])

    if (
      !clientsResponse.ok ||
      !ordersResponse.ok ||
      !linksResponse.ok
    ) {
      throw new Error('Не вдалося завантажити дані з Django API')
    }

    const clientsData = await clientsResponse.json()
    const ordersData = await ordersResponse.json()
    const linksData = await linksResponse.json()

    clients.value = extractList(clientsData)

    const orderList = extractList(ordersData)
    const linkList = extractList(linksData)

    const clientNames = Object.fromEntries(
      clients.value.map(client => [
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
    error.value = err.message
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(loadDashboard)

watch(activePage, page => {
  if (page === 'dashboard') {
    loadDashboard()
  }
})
</script>

<template>
  <div class="app-layout">
    <aside class="sidebar">
      <h2>ServiceCenter CRM</h2>
      <p>Сервісний центр техніки</p>

      <nav>
        <button
          v-for="item in menu"
          :key="item.id"
          :class="{ active: activePage === item.id }"
          @click="activePage = item.id"
        >
          {{ item.title }}
        </button>
      </nav>
    </aside>

    <main class="main-content">
      <header class="page-header">
        <h1>
          {{
            activePage === 'dashboard' ? 'Панель керування' :
            activePage === 'clients' ? 'Управління клієнтами' :
            activePage === 'orders' ? 'Управління замовленнями' :
            'Каталог послуг'
          }}
        </h1>
        <span>Адміністратор</span>
      </header>

      <template v-if="activePage === 'dashboard'">
        <p v-if="loading">Завантаження статистики...</p>
        <p v-if="error" class="form-error">{{ error }}</p>

        <section class="stats">
          <div class="stat-card">
            <h3>Клієнти</h3>
            <strong>{{ clients.length }}</strong>
          </div>

          <div class="stat-card">
            <h3>Замовлення</h3>
            <strong>{{ orders.length }}</strong>
          </div>

          <div class="stat-card">
            <h3>Виконано</h3>
            <strong>{{ completedCount }}</strong>
          </div>
        </section>

        <section class="content-card">
          <h2>Останні замовлення</h2>

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
                <tr
                  v-for="order in recentOrders"
                  :key="order.id"
                >
                  <td>{{ order.id }}</td>
                  <td>{{ order.client }}</td>
                  <td>{{ order.service }}</td>
                  <td>
                    <span class="status">
                      {{ statusNames[order.status] || order.status }}
                    </span>
                  </td>
                  <td>{{ order.price }} грн</td>
                </tr>

                <tr v-if="!loading && recentOrders.length === 0">
                  <td colspan="5">Замовлень не знайдено</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </template>

      <ClientsView v-if="activePage === 'clients'" />
      <OrdersView v-if="activePage === 'orders'" />
      <ServicesView v-if="activePage === 'services'" />
    </main>
  </div>
</template>
