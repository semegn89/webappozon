import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ticketsApi } from '../services/api'

export default function TicketDetail() {
  const { id } = useParams<{ id: string }>()
  const [newMessage, setNewMessage] = useState('')
  const queryClient = useQueryClient()

  const { data: ticket } = useQuery({
    queryKey: ['ticket', id],
    queryFn: () => ticketsApi.getTicket(Number(id)),
    enabled: !!id,
  })

  const { data: messages } = useQuery({
    queryKey: ['messages', id],
    queryFn: () => ticketsApi.getMessages(Number(id)),
    enabled: !!id,
  })

  const sendMutation = useMutation({
    mutationFn: (message: string) => ticketsApi.sendMessage(Number(id), { body: message }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['messages', id] })
      setNewMessage('')
    },
  })

  if (!ticket) return <div>Загрузка...</div>

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ background: 'white', padding: '2rem', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', marginBottom: '2rem' }}>
        <h1 style={{ margin: '0 0 1rem 0' }}>{ticket.subject}</h1>
        <p style={{ color: '#6b7280', margin: '0 0 1rem 0' }}>
          Статус: {ticket.status} • Приоритет: {ticket.priority}
        </p>
        <p style={{ margin: 0 }}>{ticket.description}</p>
      </div>

      <div style={{ background: 'white', padding: '2rem', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <h2 style={{ margin: '0 0 1.5rem 0' }}>Сообщения</h2>
        
        <div style={{ marginBottom: '2rem', maxHeight: '400px', overflowY: 'auto' }}>
          {messages?.map((message: any) => (
            <div key={message.id} style={{ 
              marginBottom: '1rem', 
              padding: '1rem', 
              background: '#f9fafb', 
              borderRadius: '6px',
              borderLeft: '4px solid #2563eb'
            }}>
              <div style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '0.5rem' }}>
                Пользователь {message.user_id} • {new Date(message.created_at).toLocaleString('ru-RU')}
              </div>
              <div>{message.message}</div>
            </div>
          ))}
        </div>

        <form onSubmit={(e) => { e.preventDefault(); if (newMessage.trim()) sendMutation.mutate(newMessage.trim()) }}>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <textarea
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Введите сообщение..."
              style={{ flex: 1, padding: '0.75rem', border: '1px solid #d1d5db', borderRadius: '6px', minHeight: '80px' }}
            />
            <button
              type="submit"
              disabled={sendMutation.isPending || !newMessage.trim()}
              style={{ padding: '0.75rem 1.5rem', background: '#2563eb', color: 'white', border: 'none', borderRadius: '6px', alignSelf: 'flex-end' }}
            >
              {sendMutation.isPending ? 'Отправка...' : 'Отправить'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
