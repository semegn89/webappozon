import React, { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Send, Clock, CheckCircle, XCircle, User, Package } from 'lucide-react'
import { ticketsApi } from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import LoadingSpinner from '../components/LoadingSpinner'

const TicketDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()
  const queryClient = useQueryClient()
  
  const [newMessage, setNewMessage] = useState('')

  const { data: ticket, isLoading, error } = useQuery({
    queryKey: ['ticket', id],
    queryFn: () => ticketsApi.getTicket(Number(id)),
    enabled: !!id
  })

  const { data: messages, isLoading: messagesLoading } = useQuery({
    queryKey: ['ticket-messages', id],
    queryFn: () => ticketsApi.getTicketMessages(Number(id)),
    enabled: !!id
  })

  // Мутация для отправки сообщения
  const sendMessageMutation = useMutation({
    mutationFn: (data: { body: string }) => ticketsApi.createTicketMessage(Number(id), data),
    onSuccess: () => {
      setNewMessage('')
      queryClient.invalidateQueries({ queryKey: ['ticket-messages', id] })
    }
  })

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault()
    if (!newMessage.trim()) return
    
    sendMessageMutation.mutate({ body: newMessage.trim() })
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'open':
        return <Clock size={16} color="#1976d2" />
      case 'in_progress':
        return <Clock size={16} color="#f57c00" />
      case 'resolved':
        return <CheckCircle size={16} color="#388e3c" />
      case 'closed':
        return <XCircle size={16} color="#7b1fa2" />
      default:
        return <Clock size={16} />
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

  if (isLoading) return <LoadingSpinner message="Загрузка тикета..." />
  if (error || !ticket) return <div className="error">Тикет не найден</div>

  return (
    <div className="container">
      {/* Заголовок */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
          <button 
            className="btn btn-small btn-secondary"
            onClick={() => navigate('/tickets')}
          >
            <ArrowLeft size={16} />
            Назад
          </button>
          <h1>{ticket.subject}</h1>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
          {getStatusIcon(ticket.status)}
          <span className={`status-badge status-${ticket.status.replace('_', '-')}`}>
            {getStatusText(ticket.status)}
          </span>
          <span className={`status-badge priority-${ticket.priority}`}>
            {getPriorityText(ticket.priority)}
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          <div>
            <h4>Номер тикета</h4>
            <p>#{ticket.id}</p>
          </div>
          <div>
            <h4>Дата создания</h4>
            <p>{new Date(ticket.created_at).toLocaleDateString('ru-RU')}</p>
          </div>
          {ticket.closed_at && (
            <div>
              <h4>Дата закрытия</h4>
              <p>{new Date(ticket.closed_at).toLocaleDateString('ru-RU')}</p>
            </div>
          )}
        </div>
      </div>

      {/* Информация о модели */}
      {ticket.model && (
        <div className="card">
          <h3>Связанная модель</h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px', backgroundColor: 'var(--tg-theme-secondary-bg-color)', borderRadius: '8px' }}>
            <Package size={20} color="#2481cc" />
            <div>
              <div style={{ fontWeight: '600' }}>{ticket.model.name}</div>
              <div style={{ fontSize: '14px', color: 'var(--tg-theme-hint-color)' }}>
                {ticket.model.brand && `${ticket.model.brand} • `}
                {ticket.model.code}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Описание */}
      <div className="card">
        <h3>Описание проблемы</h3>
        <p style={{ whiteSpace: 'pre-wrap' }}>{ticket.description}</p>
      </div>

      {/* Переписка */}
      <div className="card">
        <h3>Переписка</h3>
        
        {messagesLoading ? (
          <LoadingSpinner message="Загрузка сообщений..." />
        ) : !messages || messages.length === 0 ? (
          <div className="empty-state">
            <p>Сообщений пока нет</p>
          </div>
        ) : (
          <div style={{ marginBottom: '16px' }}>
            {messages.map((message: any) => (
              <div 
                key={message.id} 
                style={{ 
                  marginBottom: '16px', 
                  padding: '12px', 
                  backgroundColor: message.author_id === user?.id ? 'var(--tg-theme-button-color)' : 'var(--tg-theme-secondary-bg-color)',
                  color: message.author_id === user?.id ? 'white' : 'var(--tg-theme-text-color)',
                  borderRadius: '8px',
                  marginLeft: message.author_id === user?.id ? '20%' : '0',
                  marginRight: message.author_id === user?.id ? '0' : '20%'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <User size={14} />
                    <span style={{ fontSize: '12px', fontWeight: '500' }}>
                      {message.author.full_name}
                    </span>
                    {message.is_internal_note && (
                      <span style={{ fontSize: '10px', opacity: 0.8, fontStyle: 'italic' }}>
                        (внутренняя заметка)
                      </span>
                    )}
                  </div>
                  <span style={{ fontSize: '12px', opacity: 0.8 }}>
                    {new Date(message.created_at).toLocaleString('ru-RU')}
                  </span>
                </div>
                <div style={{ whiteSpace: 'pre-wrap' }}>{message.body}</div>
              </div>
            ))}
          </div>
        )}

        {/* Форма отправки сообщения */}
        {ticket.is_open && (
          <form onSubmit={handleSendMessage}>
            <div className="form-group">
              <textarea
                className="form-input form-textarea"
                placeholder="Введите ваше сообщение..."
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                rows={3}
              />
            </div>
            <button
              type="submit"
              className="btn"
              disabled={sendMessageMutation.isPending || !newMessage.trim()}
            >
              {sendMessageMutation.isPending ? (
                <LoadingSpinner message="Отправка..." />
              ) : (
                <>
                  <Send size={16} />
                  Отправить
                </>
              )}
            </button>
          </form>
        )}

        {!ticket.is_open && (
          <div style={{ padding: '16px', backgroundColor: 'var(--tg-theme-secondary-bg-color)', borderRadius: '8px', textAlign: 'center' }}>
            <p>Тикет закрыт. Новые сообщения отправлять нельзя.</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default TicketDetail
