import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Package, Ticket, FileText, Search } from 'lucide-react'
import { modelsApi, ticketsApi } from '../services/api'
import { useAuth } from '../contexts/AuthContext'

const Home: React.FC = () => {
  const navigate = useNavigate()
  const { user } = useAuth()

  // Получаем последние модели
  const { data: recentModels } = useQuery({
    queryKey: ['models', 'recent'],
    queryFn: () => modelsApi.getModels({ page: 1, page_size: 6 }),
    select: (data) => data.items
  })

  // Получаем статистику тикетов пользователя
  const { data: userTickets } = useQuery({
    queryKey: ['tickets', 'user'],
    queryFn: () => ticketsApi.getTickets({ page: 1, page_size: 5 }),
    select: (data) => data.items
  })

  const quickActions = [
    {
      title: 'Каталог моделей',
      description: 'Просмотр и поиск моделей',
      icon: Package,
      action: () => navigate('/models'),
      color: '#2481cc'
    },
    {
      title: 'Мои тикеты',
      description: 'Управление тикетами поддержки',
      icon: Ticket,
      action: () => navigate('/tickets'),
      color: '#f57c00'
    },
    {
      title: 'Создать тикет',
      description: 'Новый запрос в поддержку',
      icon: FileText,
      action: () => navigate('/tickets/create'),
      color: '#388e3c'
    }
  ]

  return (
    <div className="container">
      {/* Приветствие */}
      <div className="card">
        <h1>Добро пожаловать, {user?.first_name || 'Пользователь'}!</h1>
        <p>Выберите действие или найдите нужную модель в каталоге.</p>
      </div>

      {/* Быстрые действия */}
      <div className="card">
        <h2>Быстрые действия</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', marginTop: '16px' }}>
          {quickActions.map((action, index) => {
            const Icon = action.icon
            return (
              <button
                key={index}
                className="btn btn-secondary"
                onClick={action.action}
                style={{ 
                  display: 'flex', 
                  flexDirection: 'column', 
                  alignItems: 'center', 
                  gap: '8px',
                  padding: '16px',
                  textAlign: 'center'
                }}
              >
                <Icon size={24} color={action.color} />
                <div>
                  <div style={{ fontWeight: '600', marginBottom: '4px' }}>{action.title}</div>
                  <div style={{ fontSize: '12px', opacity: 0.8 }}>{action.description}</div>
                </div>
              </button>
            )
          })}
        </div>
      </div>

      {/* Последние модели */}
      {recentModels && recentModels.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h2>Последние модели</h2>
            <button 
              className="btn btn-small"
              onClick={() => navigate('/models')}
            >
              Все модели
            </button>
          </div>
          <div className="list">
            {recentModels.map((model: any) => (
              <div 
                key={model.id} 
                className="list-item"
                onClick={() => navigate(`/models/${model.id}`)}
              >
                <div className="list-item-header">
                  <div>
                    <div className="list-item-title">{model.name}</div>
                    <div className="list-item-subtitle">
                      {model.brand && `${model.brand} • `}
                      {model.code}
                      {model.year_range && ` • ${model.year_range}`}
                    </div>
                  </div>
                  {model.has_files && (
                    <FileText size={16} color="#2481cc" />
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Мои тикеты */}
      {userTickets && userTickets.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h2>Мои тикеты</h2>
            <button 
              className="btn btn-small"
              onClick={() => navigate('/tickets')}
            >
              Все тикеты
            </button>
          </div>
          <div className="list">
            {userTickets.map((ticket: any) => (
              <div 
                key={ticket.id} 
                className="list-item"
                onClick={() => navigate(`/tickets/${ticket.id}`)}
              >
                <div className="list-item-header">
                  <div>
                    <div className="list-item-title">{ticket.subject}</div>
                    <div className="list-item-subtitle">
                      #{ticket.id} • {new Date(ticket.created_at).toLocaleDateString('ru-RU')}
                    </div>
                  </div>
                  <span className={`status-badge status-${ticket.status.replace('_', '-')}`}>
                    {ticket.status === 'open' && 'Открыт'}
                    {ticket.status === 'in_progress' && 'В работе'}
                    {ticket.status === 'resolved' && 'Решен'}
                    {ticket.status === 'closed' && 'Закрыт'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Поиск */}
      <div className="card">
        <h2>Поиск</h2>
        <div className="search">
          <input
            type="text"
            className="search-input"
            placeholder="Поиск моделей..."
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                const query = (e.target as HTMLInputElement).value
                if (query.trim()) {
                  navigate(`/models?q=${encodeURIComponent(query.trim())}`)
                }
              }
            }}
          />
          <Search className="search-icon" size={20} />
        </div>
      </div>
    </div>
  )
}

export default Home
