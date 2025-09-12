import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Package, Ticket, FileText, Search, Star } from 'lucide-react'
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
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      iconBg: '#667eea'
    },
    {
      title: 'Мои тикеты',
      description: 'Управление тикетами поддержки',
      icon: Ticket,
      action: () => navigate('/tickets'),
      gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      iconBg: '#f093fb'
    },
    {
      title: 'Создать тикет',
      description: 'Новый запрос в поддержку',
      icon: FileText,
      action: () => navigate('/tickets/create'),
      gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      iconBg: '#4facfe'
    }
  ]

  const stats = [
    {
      title: 'Всего моделей',
      value: recentModels?.length || 0,
      icon: Package,
      color: '#667eea',
      change: '+12%'
    },
    {
      title: 'Активные тикеты',
      value: userTickets?.filter((t: any) => t.status === 'open').length || 0,
      icon: Ticket,
      color: '#f093fb',
      change: '+5%'
    },
    {
      title: 'Решено сегодня',
      value: userTickets?.filter((t: any) => t.status === 'resolved').length || 0,
      icon: Star,
      color: '#4facfe',
      change: '+8%'
    }
  ]

  return (
    <div className="home-container">
      {/* Hero Section */}
      <div className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">
            Добро пожаловать, <span className="gradient-text">{user?.first_name || 'Пользователь'}</span>! ✨
          </h1>
          <p className="hero-subtitle">
            Добро пожаловать в ваш персональный кабинет. Здесь вы можете найти модели, 
            управлять тикетами поддержки и получить всю необходимую помощь.
          </p>
        </div>
        <div className="hero-stats">
          {stats.map((stat, index) => {
            const Icon = stat.icon
            return (
              <div key={index} className="stat-item animate-fadeInUp" style={{ animationDelay: `${index * 0.1}s` }}>
                <div className="stat-icon" style={{ backgroundColor: stat.color }}>
                  <Icon size={20} color="white" />
                </div>
                <div className="stat-content">
                  <div className="stat-value">{stat.value}</div>
                  <div className="stat-title">{stat.title}</div>
                  <div className="stat-change">{stat.change}</div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="section">
        <h2 className="section-title">Быстрые действия</h2>
        <div className="actions-grid">
          {quickActions.map((action, index) => {
            const Icon = action.icon
            return (
              <div
                key={index}
                className="action-card animate-fadeInUp"
                style={{ animationDelay: `${index * 0.1}s` }}
                onClick={action.action}
              >
                <div className="action-icon" style={{ background: action.gradient }}>
                  <Icon size={28} color="white" />
                </div>
                <div className="action-content">
                  <h3 className="action-title">{action.title}</h3>
                  <p className="action-description">{action.description}</p>
                </div>
                <div className="action-arrow">→</div>
              </div>
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
      <div className="search-section">
        <div className="search-container">
          <h2 className="search-title">Найти модель</h2>
          <p className="search-subtitle">
            Введите название модели, код или бренд для быстрого поиска
          </p>
          <div className="search-input-container">
            <input
              type="text"
              className="search-input"
              placeholder="Например: iPhone 15, Samsung Galaxy..."
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  const query = (e.target as HTMLInputElement).value
                  if (query.trim()) {
                    navigate(`/models?q=${encodeURIComponent(query.trim())}`)
                  }
                }
              }}
            />
            <button 
              className="search-button"
              onClick={(e) => {
                const input = (e.target as HTMLElement).parentElement?.querySelector('input') as HTMLInputElement
                if (input?.value.trim()) {
                  navigate(`/models?q=${encodeURIComponent(input.value.trim())}`)
                }
              }}
            >
              <Search size={20} color="white" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home
