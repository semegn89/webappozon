import React, { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { 
  Users, Package, Ticket, BarChart3, Plus, 
  TrendingUp, Eye, Download, MessageSquare, Calendar,
  CheckCircle, Search, Edit, Trash2, Upload, Lock
} from 'lucide-react'
import { adminApi, modelsApi, ticketsApi } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import ModelForm from '../components/ModelForm'

const Admin: React.FC = () => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<'dashboard' | 'models' | 'tickets'>('dashboard')
  const [isModelFormOpen, setIsModelFormOpen] = useState(false)
  const [editingModel, setEditingModel] = useState<any>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [password, setPassword] = useState('')

  // Получаем статистику
  const { data: statsData, isLoading: statsLoading } = useQuery({
    queryKey: ['admin-stats'],
    queryFn: adminApi.getAdminStats
  })

  // Получаем модели
  const { data: modelsData } = useQuery({
    queryKey: ['admin-models'],
    queryFn: () => modelsApi.getModels({ page: 1, page_size: 10 }),
    enabled: activeTab === 'models'
  })

  // Получаем тикеты
  const { data: ticketsData } = useQuery({
    queryKey: ['admin-tickets'],
    queryFn: () => ticketsApi.getTickets({ page: 1, page_size: 10 }),
    enabled: activeTab === 'tickets'
  })


  // Мутация для удаления модели
  const deleteModelMutation = useMutation({
    mutationFn: modelsApi.deleteModel,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-models'] })
      queryClient.invalidateQueries({ queryKey: ['models'] })
    }
  })

  const tabs = [
    { id: 'dashboard', label: 'Дашборд', icon: BarChart3, color: '#3b82f6' },
    { id: 'models', label: 'Модели', icon: Package, color: '#10b981' },
    { id: 'tickets', label: 'Тикеты', icon: Ticket, color: '#f59e0b' }
  ]

  // Функции для работы с моделями
  const handleCreateModel = () => {
    setEditingModel(null)
    setIsModelFormOpen(true)
  }

  const handleEditModel = (model: any) => {
    setEditingModel(model)
    setIsModelFormOpen(true)
  }

  const handleDeleteModel = async (modelId: number) => {
    if (window.confirm('Вы уверены, что хотите удалить эту модель?')) {
      await deleteModelMutation.mutateAsync(modelId)
    }
  }

  const handleModelFormSuccess = () => {
    queryClient.invalidateQueries({ queryKey: ['admin-models'] })
    queryClient.invalidateQueries({ queryKey: ['models'] })
    setActiveTab('models') // переключаем на вкладку моделей
  }

  // Проверка аутентификации
  useEffect(() => {
    const adminAuth = localStorage.getItem('admin_auth')
    if (adminAuth === 'true') {
      setIsAuthenticated(true)
    }
  }, [])

  const handleLogin = () => {
    // Простая защита паролем
    if (password === 'admin123') {
      setIsAuthenticated(true)
      localStorage.setItem('admin_auth', 'true')
    } else {
      alert('Неверный пароль!')
    }
  }

  const handleLogout = () => {
    setIsAuthenticated(false)
    localStorage.removeItem('admin_auth')
  }

  // Если не аутентифицирован, показываем форму входа
  if (!isAuthenticated) {
    return (
      <div className="admin-login">
        <div className="login-card">
          <div className="login-header">
            <Lock size={48} color="#3b82f6" />
            <h1>Админ Панель</h1>
            <p>Введите пароль для доступа</p>
          </div>
          <div className="login-form">
            <input
              type="password"
              placeholder="Пароль"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
              className="login-input"
            />
            <button onClick={handleLogin} className="login-btn">
              Войти
            </button>
          </div>
          <button onClick={() => navigate('/')} className="back-btn">
            ← Вернуться в приложение
          </button>
        </div>
      </div>
    )
  }

  if (statsLoading) return <LoadingSpinner message="Загрузка админ-панели..." />

  // Статистические карточки
  const StatCard = ({ title, value, icon: Icon, color, trend }: any) => (
    <div className="admin-stat-card">
      <div className="stat-card-content">
        <div className="stat-card-info">
          <p className="stat-card-title">{title}</p>
          <p className="stat-card-value">{value}</p>
          {trend && (
            <div className="stat-card-trend">
              <TrendingUp className="trend-icon" />
              <span className="trend-text">{trend}</span>
            </div>
          )}
        </div>
        <div className="stat-card-icon" style={{ backgroundColor: color }}>
          <Icon size={24} color="white" />
        </div>
      </div>
    </div>
  )

  // Карточка модели
  const ModelCard = ({ model }: any) => (
    <div className="admin-card model-card">
      <div className="model-card-header">
        <div className="model-card-info">
          <div className="model-icon">
            <Package size={20} color="#3b82f6" />
          </div>
          <div>
            <h3 className="model-title">{model.name}</h3>
            <p className="model-category">{model.category} {model.brand && `• ${model.brand}`}</p>
          </div>
        </div>
        <div className="model-actions">
          <button 
            className="action-btn edit-btn"
            onClick={() => handleEditModel(model)}
            title="Редактировать"
          >
            <Edit size={16} />
          </button>
          <button 
            className="action-btn delete-btn"
            onClick={() => handleDeleteModel(model.id)}
            title="Удалить"
            disabled={deleteModelMutation.isPending}
          >
            <Trash2 size={16} />
          </button>
        </div>
      </div>
      <p className="model-description">{model.description || 'Описание не указано'}</p>
      <div className="model-footer">
        <div className="model-stats">
          <div className="model-stat">
            <Eye size={16} />
            <span>0 просмотров</span>
          </div>
          <div className="model-stat">
            <Download size={16} />
            <span>0 загрузок</span>
          </div>
        </div>
        <span className={`status-badge ${model.is_active ? 'status-active' : 'status-blocked'}`}>
          {model.is_active ? 'Активна' : 'Неактивна'}
        </span>
      </div>
    </div>
  )

  // Карточка тикета
  const TicketCard = ({ ticket }: any) => (
    <div className="admin-card ticket-card">
      <div className="ticket-card-header">
        <div className="ticket-card-info">
          <div className={`ticket-icon ${ticket.status}`}>
            <Ticket size={20} />
          </div>
          <div>
            <h3 className="ticket-title">{ticket.subject}</h3>
            <p className="ticket-priority">Приоритет: {ticket.priority}</p>
          </div>
        </div>
        <div className="ticket-actions">
          <button className="action-btn message-btn">
            <MessageSquare size={16} />
          </button>
          <button className="action-btn check-btn">
            <CheckCircle size={16} />
          </button>
        </div>
      </div>
      <p className="ticket-description">{ticket.description}</p>
      <div className="ticket-footer">
        <div className="ticket-date">
          <Calendar size={16} />
          <span>{new Date(ticket.created_at).toLocaleDateString()}</span>
        </div>
        <span className={`status-badge status-${ticket.status}`}>
          {ticket.status === 'open' && 'Открыт'}
          {ticket.status === 'in_progress' && 'В работе'}
          {ticket.status === 'resolved' && 'Решен'}
          {ticket.status === 'closed' && 'Закрыт'}
        </span>
      </div>
    </div>
  )


  return (
    <div className="admin-container">
      {/* Header */}
      <div className="admin-header">
        <div className="admin-header-content">
          <h1 className="admin-title">Админ Кабинет</h1>
          <p className="admin-subtitle">Управление системой и контентом</p>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button 
              className="back-btn"
              onClick={() => navigate('/')}
            >
              ← Вернуться в приложение
            </button>
            <button 
              className="logout-btn"
              onClick={handleLogout}
            >
              Выйти
            </button>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="admin-tabs">
        {tabs.map((tab) => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              className={`admin-tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id as any)}
            >
              <Icon size={20} color={activeTab === tab.id ? 'white' : tab.color} />
              <span>{tab.label}</span>
            </button>
          )
        })}
      </div>

      {/* Content */}
      <div className="admin-content">
        {activeTab === 'dashboard' && (
          <div className="dashboard-content">
            {/* Stats */}
            <div className="stats-grid">
              <StatCard
                title="Всего моделей"
                value={statsData?.total_models || 0}
                icon={Package}
                color="#3b82f6"
                trend="+12%"
              />
              <StatCard
                title="Активных тикетов"
                value={statsData?.active_tickets || 0}
                icon={Ticket}
                color="#f59e0b"
                trend="+5%"
              />
              <StatCard
                title="Всего файлов"
                value={statsData?.total_files || 0}
                icon={FileText}
                color="#8b5cf6"
                trend="+8%"
              />
              <StatCard
                title="Загрузок"
                value={statsData?.total_downloads || 0}
                icon={Download}
                color="#10b981"
                trend="+15%"
              />
            </div>

            {/* Quick Actions */}
            <div className="quick-actions-section">
              <h2 className="section-title">Быстрые действия</h2>
              <div className="quick-actions-grid">
                <button className="quick-action-btn" onClick={handleCreateModel}>
                  <Plus size={24} color="white" />
                  <div>
                    <h3>Добавить модель</h3>
                    <p>Создать новую модель</p>
                  </div>
                </button>
                <button className="quick-action-btn">
                  <Upload size={24} color="white" />
                  <div>
                    <h3>Загрузить файл</h3>
                    <p>Добавить инструкцию</p>
                  </div>
                </button>
                <button className="quick-action-btn">
                  <BarChart3 size={24} color="white" />
                  <div>
                    <h3>Аналитика</h3>
                    <p>Посмотреть статистику</p>
                  </div>
                </button>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="recent-activity-section">
              <h2 className="section-title">Последние активности</h2>
              <div className="activity-list">
                <div className="activity-item">
                  <div className="activity-icon">
                    <Package size={16} color="#3b82f6" />
                  </div>
                  <div className="activity-content">
                    <p className="activity-text">Добавлена новая модель "Sample Model"</p>
                    <p className="activity-time">2 часа назад</p>
                  </div>
                </div>
                <div className="activity-item">
                  <div className="activity-icon">
                    <Ticket size={16} color="#f59e0b" />
                  </div>
                  <div className="activity-content">
                    <p className="activity-text">Создан новый тикет поддержки</p>
                    <p className="activity-time">4 часа назад</p>
                  </div>
                </div>
                <div className="activity-item">
                  <div className="activity-icon">
                    <Users size={16} color="#8b5cf6" />
                  </div>
                  <div className="activity-content">
                    <p className="activity-text">Новый пользователь зарегистрирован</p>
                    <p className="activity-time">6 часов назад</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'models' && (
          <div className="models-content">
            <div className="content-header">
              <h2 className="section-title">Управление моделями</h2>
              <button className="admin-button" onClick={handleCreateModel}>
                <Plus size={20} />
                Добавить модель
              </button>
            </div>
            <div className="models-grid">
              {(() => {
                // Универсальная распаковка ответа API для моделей
                const adminModelsRaw = modelsData as any
                const adminModels: any[] =
                  (adminModelsRaw?.items ?? adminModelsRaw?.models ?? (Array.isArray(adminModelsRaw) ? adminModelsRaw : [])) as any[]
                
                return adminModels.length > 0 ? (
                  adminModels.map((model: any) => (
                    <ModelCard key={model.id} model={model} />
                  ))
                ) : (
                  <div className="empty-state">
                    <Package size={48} color="#9ca3af" />
                    <h3>Модели не найдены</h3>
                    <p>Добавьте первую модель</p>
                  </div>
                )
              })()}
            </div>
          </div>
        )}

        {activeTab === 'tickets' && (
          <div className="tickets-content">
            <div className="content-header">
              <h2 className="section-title">Управление тикетами</h2>
              <div className="ticket-filters">
                <button className="filter-btn active">Все</button>
                <button className="filter-btn">Открытые</button>
                <button className="filter-btn">В работе</button>
                <button className="filter-btn">Закрытые</button>
              </div>
            </div>
            <div className="tickets-list">
              {ticketsData?.items?.map((ticket: any) => (
                <TicketCard key={ticket.id} ticket={ticket} />
              )) || (
                <div className="empty-state">
                  <Ticket size={48} color="#9ca3af" />
                  <h3>Тикеты не найдены</h3>
                  <p>Пока нет тикетов поддержки</p>
                </div>
              )}
            </div>
          </div>
        )}

      </div>

      {/* Модальное окно для создания/редактирования модели */}
      <ModelForm
        isOpen={isModelFormOpen}
        onClose={() => setIsModelFormOpen(false)}
        onSuccess={handleModelFormSuccess}
        model={editingModel}
      />
    </div>
  )
}

export default Admin