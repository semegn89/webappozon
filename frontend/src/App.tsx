import { Routes, Route } from 'react-router-dom'
import { TelegramProvider } from './contexts/TelegramContext'
import { AuthProvider } from './contexts/AuthContext'
import Layout from './components/Layout'
import Home from './pages/Home'
import Models from './pages/Models'
import ModelDetail from './pages/ModelDetail'
import Tickets from './pages/Tickets'
import TicketDetail from './pages/TicketDetail'
import CreateTicket from './pages/CreateTicket'
import Admin from './pages/Admin'
import NotFound from './pages/NotFound'

// Компонент для страницы аналитики
const Analytics = () => (
  <div className="admin-container">
    <div className="admin-header">
      <div className="admin-header-content">
        <h1 className="admin-title">Аналитика</h1>
        <p className="admin-subtitle">Статистика и отчеты</p>
      </div>
    </div>
    <div className="admin-content">
      <div className="analytics-content">
        <h2>Аналитика системы</h2>
        <p>Здесь будет отображаться подробная аналитика по моделям, тикетам и пользователям.</p>
        <div className="analytics-placeholder">
          <div className="placeholder-card">
            <h3>График активности</h3>
            <p>График активности пользователей за последние 30 дней</p>
          </div>
          <div className="placeholder-card">
            <h3>Популярные модели</h3>
            <p>Топ-10 самых популярных моделей</p>
          </div>
          <div className="placeholder-card">
            <h3>Статистика тикетов</h3>
            <p>Распределение тикетов по статусам и приоритетам</p>
          </div>
        </div>
      </div>
    </div>
  </div>
)

function App() {
  return (
    <TelegramProvider>
      <AuthProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/models" element={<Models />} />
            <Route path="/models/:id" element={<ModelDetail />} />
            <Route path="/tickets" element={<Tickets />} />
            <Route path="/tickets/:id" element={<TicketDetail />} />
            <Route path="/tickets/create" element={<CreateTicket />} />
            <Route path="/admin" element={<Admin />} />
            <Route path="/admin/analytics" element={<Analytics />} />
            <Route path="/admin/tickets/:id" element={<TicketDetail />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Layout>
      </AuthProvider>
    </TelegramProvider>
  )
}

export default App