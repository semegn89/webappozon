import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Plus, Filter, Ticket, Clock, CheckCircle, XCircle } from 'lucide-react'
import { ticketsApi } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'

const Tickets: React.FC = () => {
  const navigate = useNavigate()
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [priorityFilter, setPriorityFilter] = useState<string>('')

  const { data, isLoading, error } = useQuery({
    queryKey: ['tickets', { status: statusFilter, priority: priorityFilter }],
    queryFn: () => ticketsApi.getTickets({
      status: statusFilter || undefined,
      priority: priorityFilter || undefined,
      page: 1,
      page_size: 50
    })
  })

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'open':
        return <Ticket size={16} color="#1976d2" />
      case 'in_progress':
        return <Clock size={16} color="#f57c00" />
      case 'resolved':
        return <CheckCircle size={16} color="#388e3c" />
      case 'closed':
        return <XCircle size={16} color="#7b1fa2" />
      default:
        return <Ticket size={16} />
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'open':
        return 'Открыт'
      case 'in_progress':
        return 'В работе'
      case 'resolved':
        return 'Решен'
      case 'closed':
        return 'Закрыт'
      default:
        return status
    }
  }

  const getPriorityText = (priority: string) => {
    switch (priority) {
      case 'low':
        return 'Низкий'
      case 'normal':
        return 'Обычный'
      case 'high':
        return 'Высокий'
      default:
        return priority
    }
  }

  if (isLoading) return <LoadingSpinner message="Загрузка тикетов..." />
  if (error) return <div className="error">Ошибка загрузки тикетов</div>

  const tickets = data?.items || []

  return (
    <div className="container">
      {/* Заголовок */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1>Мои тикеты</h1>
            <p>Управление запросами в службу поддержки</p>
          </div>
          <button 
            className="btn"
            onClick={() => navigate('/tickets/create')}
          >
            <Plus size={16} />
            Создать тикет
          </button>
        </div>
      </div>

      {/* Фильтры */}
      <div className="card">
        <h3>Фильтры</h3>
        <div className="filters">
          <button
            className={`filter-chip ${statusFilter === '' ? 'active' : ''}`}
            onClick={() => setStatusFilter('')}
          >
            Все статусы
          </button>
          <button
            className={`filter-chip ${statusFilter === 'open' ? 'active' : ''}`}
            onClick={() => setStatusFilter('open')}
          >
            Открытые
          </button>
          <button
            className={`filter-chip ${statusFilter === 'in_progress' ? 'active' : ''}`}
            onClick={() => setStatusFilter('in_progress')}
          >
            В работе
          </button>
          <button
            className={`filter-chip ${statusFilter === 'resolved' ? 'active' : ''}`}
            onClick={() => setStatusFilter('resolved')}
          >
            Решенные
          </button>
          <button
            className={`filter-chip ${statusFilter === 'closed' ? 'active' : ''}`}
            onClick={() => setStatusFilter('closed')}
          >
            Закрытые
          </button>
        </div>
        
        <div className="filters" style={{ marginTop: '8px' }}>
          <button
            className={`filter-chip ${priorityFilter === '' ? 'active' : ''}`}
            onClick={() => setPriorityFilter('')}
          >
            Все приоритеты
          </button>
          <button
            className={`filter-chip ${priorityFilter === 'high' ? 'active' : ''}`}
            onClick={() => setPriorityFilter('high')}
          >
            Высокий
          </button>
          <button
            className={`filter-chip ${priorityFilter === 'normal' ? 'active' : ''}`}
            onClick={() => setPriorityFilter('normal')}
          >
            Обычный
          </button>
          <button
            className={`filter-chip ${priorityFilter === 'low' ? 'active' : ''}`}
            onClick={() => setPriorityFilter('low')}
          >
            Низкий
          </button>
        </div>
      </div>

      {/* Список тикетов */}
      {tickets.length === 0 ? (
        <div className="empty-state">
          <Ticket size={48} className="empty-state-icon" />
          <h3 className="empty-state-title">Тикеты не найдены</h3>
          <p className="empty-state-description">
            У вас пока нет тикетов поддержки. Создайте первый тикет, если нужна помощь.
          </p>
          <button 
            className="btn"
            onClick={() => navigate('/tickets/create')}
            style={{ marginTop: '16px' }}
          >
            <Plus size={16} />
            Создать тикет
          </button>
        </div>
      ) : (
        <div className="list">
          {tickets.map((ticket) => (
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
                  {ticket.description && (
                    <div className="list-item-meta" style={{ marginTop: '4px' }}>
                      {ticket.description.length > 100 
                        ? `${ticket.description.substring(0, 100)}...` 
                        : ticket.description
                      }
                    </div>
                  )}
                </div>
                
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '4px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    {getStatusIcon(ticket.status)}
                    <span className={`status-badge status-${ticket.status.replace('_', '-')}`}>
                      {getStatusText(ticket.status)}
                    </span>
                  </div>
                  
                  <span className={`status-badge priority-${ticket.priority}`}>
                    {getPriorityText(ticket.priority)}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Статистика */}
      {tickets.length > 0 && (
        <div className="card">
          <h3>Статистика</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '16px' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: '600', color: '#1976d2' }}>
                {tickets.filter(t => t.status === 'open').length}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--tg-theme-hint-color)' }}>Открытые</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: '600', color: '#f57c00' }}>
                {tickets.filter(t => t.status === 'in_progress').length}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--tg-theme-hint-color)' }}>В работе</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: '600', color: '#388e3c' }}>
                {tickets.filter(t => t.status === 'resolved').length}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--tg-theme-hint-color)' }}>Решенные</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: '600', color: '#7b1fa2' }}>
                {tickets.filter(t => t.status === 'closed').length}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--tg-theme-hint-color)' }}>Закрытые</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Tickets
