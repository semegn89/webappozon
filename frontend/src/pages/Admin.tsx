import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Settings, Users, Package, Ticket, BarChart3, Plus } from 'lucide-react'
import { adminApi, modelsApi, ticketsApi } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'

const Admin: React.FC = () => {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<'dashboard' | 'models' | 'tickets' | 'users'>('dashboard')

  // Получаем статистику
  const { data: stats, isLoading: statsLoading } = useQuery({
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

  // Получаем пользователей
  const { data: usersData } = useQuery({
    queryKey: ['admin-users'],
    queryFn: () => adminApi.getUsers({ page: 1, page_size: 10 }),
    enabled: activeTab === 'users'
  })

  const tabs = [
    { id: 'dashboard', label: 'Дашборд', icon: BarChart3 },
    { id: 'models', label: 'Модели', icon: Package },
    { id: 'tickets', label: 'Тикеты', icon: Ticket },
    { id: 'users', label: 'Пользователи', icon: Users }
  ]

  if (statsLoading) return <LoadingSpinner message="Загрузка админ-панели..." />

  return (
    <div className="container">
      {/* Заголовок */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
          <Settings size={24} color="#2481cc" />
          <h1>Админ-панель</h1>
        </div>
        <p>Управление моделями, тикетами и пользователями</p>
      </div>

      {/* Вкладки */}
      <div className="card">
        <div style={{ display: 'flex', gap: '8px', marginBottom: '16px', overflowX: 'auto' }}>
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                className={`btn btn-small ${activeTab === tab.id ? '' : 'btn-secondary'}`}
                onClick={() => setActiveTab(tab.id as any)}
              >
                <Icon size={16} />
                {tab.label}
              </button>
            )
          })}
        </div>

        {/* Дашборд */}
        {activeTab === 'dashboard' && stats && (
          <div>
            <h3>Общая статистика</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '16px', marginBottom: '24px' }}>
              <div style={{ textAlign: 'center', padding: '16px', backgroundColor: 'var(--tg-theme-secondary-bg-color)', borderRadius: '8px' }}>
                <div style={{ fontSize: '24px', fontWeight: '600', color: '#2481cc' }}>
                  {stats.users.total}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--tg-theme-hint-color)' }}>Пользователи</div>
              </div>
              <div style={{ textAlign: 'center', padding: '16px', backgroundColor: 'var(--tg-theme-secondary-bg-color)', borderRadius: '8px' }}>
                <div style={{ fontSize: '24px', fontWeight: '600', color: '#388e3c' }}>
                  {stats.models.total}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--tg-theme-hint-color)' }}>Модели</div>
              </div>
              <div style={{ textAlign: 'center', padding: '16px', backgroundColor: 'var(--tg-theme-secondary-bg-color)', borderRadius: '8px' }}>
                <div style={{ fontSize: '24px', fontWeight: '600', color: '#f57c00' }}>
                  {stats.tickets.total}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--tg-theme-hint-color)' }}>Тикеты</div>
              </div>
              <div style={{ textAlign: 'center', padding: '16px', backgroundColor: 'var(--tg-theme-secondary-bg-color)', borderRadius: '8px' }}>
                <div style={{ fontSize: '24px', fontWeight: '600', color: '#7b1fa2' }}>
                  {stats.files.total}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--tg-theme-hint-color)' }}>Файлы</div>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              <div>
                <h4>Статистика тикетов</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Открытые:</span>
                    <span style={{ fontWeight: '600', color: '#1976d2' }}>{stats.tickets.open}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Высокий приоритет:</span>
                    <span style={{ fontWeight: '600', color: '#d32f2f' }}>{stats.tickets.high_priority}</span>
                  </div>
                </div>
              </div>
              
              <div>
                <h4>Статистика пользователей</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Админы:</span>
                    <span style={{ fontWeight: '600', color: '#2481cc' }}>{stats.users.admins}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Заблокированы:</span>
                    <span style={{ fontWeight: '600', color: '#d32f2f' }}>{stats.users.blocked}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Модели */}
        {activeTab === 'models' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3>Модели</h3>
              <button className="btn btn-small">
                <Plus size={16} />
                Добавить
              </button>
            </div>
            
            {modelsData?.items && modelsData.items.length > 0 ? (
              <div className="list">
                {modelsData.items.map((model: any) => (
                  <div key={model.id} className="list-item">
                    <div className="list-item-header">
                      <div>
                        <div className="list-item-title">{model.name}</div>
                        <div className="list-item-subtitle">
                          {model.brand && `${model.brand} • `}
                          {model.code}
                        </div>
                      </div>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button className="btn btn-small btn-secondary">
                          Редактировать
                        </button>
                        <button className="btn btn-small btn-danger">
                          Удалить
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <Package size={48} className="empty-state-icon" />
                <h3 className="empty-state-title">Модели не найдены</h3>
                <p className="empty-state-description">
                  Добавьте первую модель в каталог
                </p>
              </div>
            )}
          </div>
        )}

        {/* Тикеты */}
        {activeTab === 'tickets' && (
          <div>
            <h3>Тикеты</h3>
            
            {ticketsData?.items && ticketsData.items.length > 0 ? (
              <div className="list">
                {ticketsData.items.map((ticket: any) => (
                  <div key={ticket.id} className="list-item">
                    <div className="list-item-header">
                      <div>
                        <div className="list-item-title">{ticket.subject}</div>
                        <div className="list-item-subtitle">
                          #{ticket.id} • {new Date(ticket.created_at).toLocaleDateString('ru-RU')}
                        </div>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span className={`status-badge status-${ticket.status.replace('_', '-')}`}>
                          {ticket.status === 'open' && 'Открыт'}
                          {ticket.status === 'in_progress' && 'В работе'}
                          {ticket.status === 'resolved' && 'Решен'}
                          {ticket.status === 'closed' && 'Закрыт'}
                        </span>
                        <button 
                          className="btn btn-small btn-secondary"
                          onClick={() => navigate(`/tickets/${ticket.id}`)}
                        >
                          Открыть
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <Ticket size={48} className="empty-state-icon" />
                <h3 className="empty-state-title">Тикеты не найдены</h3>
                <p className="empty-state-description">
                  Пока нет тикетов поддержки
                </p>
              </div>
            )}
          </div>
        )}

        {/* Пользователи */}
        {activeTab === 'users' && (
          <div>
            <h3>Пользователи</h3>
            
            {usersData?.items && usersData.items.length > 0 ? (
              <div className="list">
                {usersData.items.map((user: any) => (
                  <div key={user.id} className="list-item">
                    <div className="list-item-header">
                      <div>
                        <div className="list-item-title">{user.full_name}</div>
                        <div className="list-item-subtitle">
                          @{user.username || 'без username'} • {user.telegram_user_id}
                        </div>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span className={`status-badge ${user.role === 'admin' ? 'priority-high' : 'priority-normal'}`}>
                          {user.role === 'admin' ? 'Админ' : 'Пользователь'}
                        </span>
                        {user.is_blocked && (
                          <span className="status-badge priority-high">
                            Заблокирован
                          </span>
                        )}
                        <button className="btn btn-small btn-secondary">
                          Редактировать
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <Users size={48} className="empty-state-icon" />
                <h3 className="empty-state-title">Пользователи не найдены</h3>
                <p className="empty-state-description">
                  Пока нет зарегистрированных пользователей
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default Admin
