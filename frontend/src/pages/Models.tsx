import { useQuery } from '@tanstack/react-query'
import { modelsApi } from '../services/api'

export default function Models() {
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['models'],
    queryFn: modelsApi.getModels,
  })

  const models = data?.models || []

  if (isLoading) return <div>Загрузка...</div>

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1>Каталог моделей ({models.length})</h1>
        <button onClick={() => refetch()} style={{ padding: '0.5rem 1rem', background: '#2563eb', color: 'white', border: 'none', borderRadius: '4px' }}>
          Обновить
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1rem' }}>
        {models.map((model: any) => (
          <div key={model.id} style={{ 
            background: 'white', 
            padding: '1.5rem', 
            borderRadius: '8px', 
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)' 
          }}>
            <h3 style={{ margin: '0 0 0.5rem 0', color: '#1f2937' }}>{model.name}</h3>
            <p style={{ color: '#6b7280', fontSize: '0.875rem', margin: '0 0 1rem 0' }}>
              {model.brand} • {model.category} • {model.code}
            </p>
            <p style={{ color: '#4b5563', margin: '0 0 1rem 0' }}>{model.description}</p>
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              paddingTop: '1rem',
              borderTop: '1px solid #e5e7eb'
            }}>
              <span style={{ 
                background: model.is_active ? '#dcfce7' : '#fef2f2',
                color: model.is_active ? '#166534' : '#dc2626',
                padding: '0.25rem 0.5rem',
                borderRadius: '4px',
                fontSize: '0.75rem',
                fontWeight: '500'
              }}>
                {model.is_active ? 'Активна' : 'Неактивна'}
              </span>
              <span style={{ fontSize: '0.75rem', color: '#9ca3af' }}>
                {new Date(model.created_at).toLocaleDateString('ru-RU')}
              </span>
            </div>
          </div>
        ))}
      </div>

      {models.length === 0 && (
        <div style={{ textAlign: 'center', padding: '4rem', color: '#6b7280' }}>
          <h3>Модели не найдены</h3>
          <p>Создайте первую модель в админ-панели</p>
        </div>
      )}
    </div>
  )
}
