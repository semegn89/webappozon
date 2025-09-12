import React, { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import { ArrowLeft, Send, Package } from 'lucide-react'
import { ticketsApi, modelsApi } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'

const CreateTicket: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const modelId = searchParams.get('model_id')

  const [formData, setFormData] = useState({
    subject: '',
    description: '',
    priority: 'normal' as 'low' | 'normal' | 'high',
    model_id: modelId ? parseInt(modelId) : undefined
  })

  // Получаем информацию о модели если указана
  const { data: model } = useQuery({
    queryKey: ['model', modelId],
    queryFn: () => modelsApi.getModel(Number(modelId)),
    enabled: !!modelId
  })

  // Мутация для создания тикета
  const createTicketMutation = useMutation({
    mutationFn: ticketsApi.createTicket,
    onSuccess: (data) => {
      navigate(`/tickets/${data.id}`)
    },
    onError: (error) => {
      console.error('Failed to create ticket:', error)
    }
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.subject.trim() || !formData.description.trim()) {
      return
    }
    createTicketMutation.mutate(formData)
  }

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

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
          <h1>Создать тикет</h1>
        </div>
        <p>Опишите вашу проблему или вопрос, и мы поможем вам</p>
      </div>

      {/* Информация о модели */}
      {model && (
        <div className="card">
          <h3>Связанная модель</h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px', backgroundColor: 'var(--tg-theme-secondary-bg-color)', borderRadius: '8px' }}>
            <Package size={20} color="#2481cc" />
            <div>
              <div style={{ fontWeight: '600' }}>{model.name}</div>
              <div style={{ fontSize: '14px', color: 'var(--tg-theme-hint-color)' }}>
                {model.brand && `${model.brand} • `}
                {model.code}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Форма создания тикета */}
      <form onSubmit={handleSubmit}>
        <div className="card">
          <h3>Информация о тикете</h3>
          
          <div className="form-group">
            <label className="form-label">Тема *</label>
            <input
              type="text"
              className="form-input"
              placeholder="Краткое описание проблемы"
              value={formData.subject}
              onChange={(e) => handleInputChange('subject', e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Приоритет</label>
            <select
              className="form-select"
              value={formData.priority}
              onChange={(e) => handleInputChange('priority', e.target.value)}
            >
              <option value="low">Низкий</option>
              <option value="normal">Обычный</option>
              <option value="high">Высокий</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Описание *</label>
            <textarea
              className="form-input form-textarea"
              placeholder="Подробно опишите вашу проблему или вопрос..."
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              required
            />
          </div>

          <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
            <button
              type="submit"
              className="btn"
              disabled={createTicketMutation.isPending || !formData.subject.trim() || !formData.description.trim()}
            >
              {createTicketMutation.isPending ? (
                <LoadingSpinner message="Создание..." />
              ) : (
                <>
                  <Send size={16} />
                  Создать тикет
                </>
              )}
            </button>
            
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => navigate('/tickets')}
            >
              Отмена
            </button>
          </div>
        </div>
      </form>

      {/* Подсказки */}
      <div className="card">
        <h3>Советы для быстрого решения</h3>
        <ul style={{ paddingLeft: '20px', lineHeight: '1.6' }}>
          <li>Укажите точную модель и серийный номер устройства</li>
          <li>Опишите шаги, которые привели к проблеме</li>
          <li>Приложите скриншоты или фотографии, если это поможет</li>
          <li>Укажите версию программного обеспечения, если применимо</li>
          <li>Выберите правильный приоритет - высокий только для критических проблем</li>
        </ul>
      </div>
    </div>
  )
}

export default CreateTicket
