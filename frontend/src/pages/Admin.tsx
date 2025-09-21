import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { modelsApi, adminApi } from '../services/api'

export default function Admin() {
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({ name: '', description: '', category: '', brand: '', code: '' })
  const queryClient = useQueryClient()

  const { data: modelsData, isLoading } = useQuery({
    queryKey: ['models'],
    queryFn: modelsApi.getModels,
  })

  const { data: stats } = useQuery({
    queryKey: ['stats'],
    queryFn: adminApi.getStats,
  })

  const createMutation = useMutation({
    mutationFn: modelsApi.createModel,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['models'] })
      queryClient.invalidateQueries({ queryKey: ['stats'] })
      setShowForm(false)
      setFormData({ name: '', description: '', category: '', brand: '', code: '' })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: modelsApi.deleteModel,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['models'] })
      queryClient.invalidateQueries({ queryKey: ['stats'] })
    },
  })

  const models = modelsData?.models || []

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.name.trim()) return
    createMutation.mutate(formData)
  }

  const handleDelete = (id: number) => {
    if (confirm('Удалить модель?')) {
      deleteMutation.mutate(id)
    }
  }

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1>Админ-панель</h1>
        <button 
          onClick={() => setShowForm(!showForm)}
          style={{ padding: '0.75rem 1.5rem', background: '#2563eb', color: 'white', border: 'none', borderRadius: '6px' }}
        >
          {showForm ? 'Отмена' : 'Создать модель'}
        </button>
      </div>

      {/* Статистика */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        <div style={{ background: 'white', padding: '1.5rem', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
          <h3 style={{ margin: '0 0 0.5rem 0', color: '#1f2937' }}>Модели</h3>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: 0, color: '#2563eb' }}>{stats?.models_count || 0}</p>
        </div>
        <div style={{ background: 'white', padding: '1.5rem', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
          <h3 style={{ margin: '0 0 0.5rem 0', color: '#1f2937' }}>Тикеты</h3>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: 0, color: '#f59e0b' }}>{stats?.tickets_count || 0}</p>
        </div>
        <div style={{ background: 'white', padding: '1.5rem', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
          <h3 style={{ margin: '0 0 0.5rem 0', color: '#1f2937' }}>Файлы</h3>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: 0, color: '#10b981' }}>{stats?.files_count || 0}</p>
        </div>
      </div>

      {/* Форма создания */}
      {showForm && (
        <div style={{ background: 'white', padding: '2rem', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', marginBottom: '2rem' }}>
          <h2 style={{ margin: '0 0 1.5rem 0' }}>Создать модель</h2>
          <form onSubmit={handleSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
              <input
                type="text"
                placeholder="Название"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                style={{ padding: '0.75rem', border: '1px solid #d1d5db', borderRadius: '6px' }}
                required
              />
              <input
                type="text"
                placeholder="Код"
                value={formData.code}
                onChange={(e) => setFormData(prev => ({ ...prev, code: e.target.value }))}
                style={{ padding: '0.75rem', border: '1px solid #d1d5db', borderRadius: '6px' }}
              />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
              <input
                type="text"
                placeholder="Бренд"
                value={formData.brand}
                onChange={(e) => setFormData(prev => ({ ...prev, brand: e.target.value }))}
                style={{ padding: '0.75rem', border: '1px solid #d1d5db', borderRadius: '6px' }}
              />
              <input
                type="text"
                placeholder="Категория"
                value={formData.category}
                onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                style={{ padding: '0.75rem', border: '1px solid #d1d5db', borderRadius: '6px' }}
              />
            </div>
            <textarea
              placeholder="Описание"
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              style={{ width: '100%', padding: '0.75rem', border: '1px solid #d1d5db', borderRadius: '6px', marginBottom: '1rem', minHeight: '100px' }}
            />
            <button 
              type="submit" 
              disabled={createMutation.isPending}
              style={{ padding: '0.75rem 1.5rem', background: '#10b981', color: 'white', border: 'none', borderRadius: '6px' }}
            >
              {createMutation.isPending ? 'Создание...' : 'Создать'}
            </button>
          </form>
        </div>
      )}

      {/* Список моделей */}
      <div style={{ background: 'white', padding: '2rem', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <h2 style={{ margin: '0 0 1.5rem 0' }}>Модели ({models.length})</h2>
        
        {isLoading ? (
          <div>Загрузка...</div>
        ) : (
          <div style={{ display: 'grid', gap: '1rem' }}>
            {models.map((model: any) => (
              <div key={model.id} style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                padding: '1rem',
                border: '1px solid #e5e7eb',
                borderRadius: '6px'
              }}>
                <div>
                  <h3 style={{ margin: '0 0 0.25rem 0' }}>{model.name}</h3>
                  <p style={{ margin: 0, color: '#6b7280', fontSize: '0.875rem' }}>
                    ID: {model.id} • {model.brand} • {model.category} • {model.code}
                  </p>
                </div>
                <button
                  onClick={() => handleDelete(model.id)}
                  disabled={deleteMutation.isPending}
                  style={{ padding: '0.5rem 1rem', background: '#dc2626', color: 'white', border: 'none', borderRadius: '4px' }}
                >
                  Удалить
                </button>
              </div>
            ))}
          </div>
        )}

        {models.length === 0 && !isLoading && (
          <div style={{ textAlign: 'center', padding: '2rem', color: '#6b7280' }}>
            <p>Модели не найдены</p>
          </div>
        )}
      </div>
    </div>
  )
}
