import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { Search, Filter, Package, FileText } from 'lucide-react'
import { modelsApi } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'

const Models: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const navigate = useNavigate()
  
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '')
  const [selectedBrand, setSelectedBrand] = useState(searchParams.get('brand') || '')
  const [selectedCategory, setSelectedCategory] = useState(searchParams.get('category') || '')
  const [showFilters, setShowFilters] = useState(false)

  const page = parseInt(searchParams.get('page') || '1')

  // Параметры запроса
  const queryParams = {
    page,
    page_size: 20,
    q: searchQuery || undefined,
    brand: selectedBrand || undefined,
    category: selectedCategory || undefined,
    is_active: true
  }

  const { data, isLoading, error } = useQuery({
    queryKey: ['models', queryParams],
    queryFn: () => modelsApi.getModels(queryParams)
  })

  const handleSearch = () => {
    const params = new URLSearchParams()
    if (searchQuery) params.set('q', searchQuery)
    if (selectedBrand) params.set('brand', selectedBrand)
    if (selectedCategory) params.set('category', selectedCategory)
    params.set('page', '1')
    setSearchParams(params)
  }

  const clearFilters = () => {
    setSearchQuery('')
    setSelectedBrand('')
    setSelectedCategory('')
    setSearchParams({})
  }

  if (isLoading) return <LoadingSpinner message="Загрузка моделей..." />
  if (error) return <div className="error">Ошибка загрузки моделей</div>

  // Универсальная распаковка ответа API
  // Поддерживаем форматы:
  // 1) { items: [...], pages: N }
  // 2) { models: [...] }
  // 3) [...] (чистый массив)
  const raw = data as any

  const models: any[] =
    (raw?.items ?? raw?.models ?? (Array.isArray(raw) ? raw : [])) as any[]

  const totalPages: number =
    (typeof raw?.pages === 'number' && raw.pages > 0) ? raw.pages : 1

  return (
    <div className="container">
      {/* Заголовок */}
      <div className="card">
        <h1>Каталог моделей</h1>
        <p>Найдите нужную модель и скачайте инструкции</p>
      </div>

      {/* Поиск */}
      <div className="card">
        <div className="search">
          <input
            type="text"
            className="search-input"
            placeholder="Поиск по названию, коду, бренду..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <Search className="search-icon" size={20} />
        </div>
        
        <div style={{ display: 'flex', gap: '8px', marginTop: '12px' }}>
          <button className="btn btn-small" onClick={handleSearch}>
            Найти
          </button>
          <button 
            className="btn btn-small btn-secondary" 
            onClick={() => setShowFilters(!showFilters)}
          >
            <Filter size={16} />
            Фильтры
          </button>
          {(searchQuery || selectedBrand || selectedCategory) && (
            <button className="btn btn-small btn-secondary" onClick={clearFilters}>
              Очистить
            </button>
          )}
        </div>

        {/* Фильтры */}
        {showFilters && (
          <div style={{ marginTop: '16px', padding: '16px', backgroundColor: 'var(--tg-theme-secondary-bg-color)', borderRadius: '8px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div className="form-group">
                <label className="form-label">Бренд</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="Введите бренд"
                  value={selectedBrand}
                  onChange={(e) => setSelectedBrand(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Категория</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="Введите категорию"
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Результаты */}
      {models.length === 0 ? (
        <div className="empty-state">
          <Package size={48} className="empty-state-icon" />
          <h3 className="empty-state-title">Модели не найдены</h3>
          <p className="empty-state-description">
            Попробуйте изменить параметры поиска или очистить фильтры
          </p>
        </div>
      ) : (
        <>
          <div className="card">
            <p>Найдено моделей: {data?.total || 0}</p>
          </div>

          <div className="models-grid">
            {models.map((model: any) => (
              <div 
                key={model.id} 
                className="model-card"
                onClick={() => navigate(`/models/${model.id}`)}
              >
                <div className="model-card-header">
                  <div className="model-icon">
                    <Package size={24} color="#3b82f6" />
                  </div>
                  <div className="model-status">
                    <span className={`status-badge ${model.is_active ? 'status-active' : 'status-blocked'}`}>
                      {model.is_active ? 'Активна' : 'Неактивна'}
                    </span>
                  </div>
                </div>
                
                <div className="model-card-content">
                  <h3 className="model-title">{model.name}</h3>
                  <p className="model-category">
                    {model.brand && `${model.brand} • `}
                    {model.category}
                  </p>
                  <p className="model-code">Код: {model.code}</p>
                  
                  {model.description && (
                    <p className="model-description">
                      {model.description.length > 80 
                        ? `${model.description.substring(0, 80)}...` 
                        : model.description
                      }
                    </p>
                  )}
                </div>
                
                <div className="model-card-footer">
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
                  <div className="model-date">
                    {new Date(model.created_at).toLocaleDateString('ru-RU')}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Пагинация */}
          {totalPages > 1 && (
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'center', gap: '8px' }}>
                <button 
                  className="btn btn-small btn-secondary"
                  disabled={page === 1}
                  onClick={() => {
                    const params = new URLSearchParams(searchParams)
                    params.set('page', (page - 1).toString())
                    setSearchParams(params)
                  }}
                >
                  Назад
                </button>
                
                <span style={{ display: 'flex', alignItems: 'center', padding: '0 16px' }}>
                  Страница {page} из {totalPages}
                </span>
                
                <button 
                  className="btn btn-small btn-secondary"
                  disabled={page === totalPages}
                  onClick={() => {
                    const params = new URLSearchParams(searchParams)
                    params.set('page', (page + 1).toString())
                    setSearchParams(params)
                  }}
                >
                  Вперед
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default Models
