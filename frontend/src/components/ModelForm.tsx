import React, { useState, useEffect } from 'react'
import { X, Save, Package } from 'lucide-react'
import { modelsApi } from '../services/api'

interface ModelFormProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  model?: any // Модель для редактирования, undefined для создания
}

const ModelForm: React.FC<ModelFormProps> = ({ isOpen, onClose, onSuccess, model }) => {
  const [formData, setFormData] = useState({
    name: '',
    code: '',
    brand: '',
    category: 'general',
    year_from: '',
    year_to: '',
    description: '',
    image_url: '',
    is_active: true
  })
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  // Заполняем форму данными модели при редактировании
  useEffect(() => {
    if (model) {
      setFormData({
        name: model.name || '',
        code: model.code || '',
        brand: model.brand || '',
        category: model.category || 'general',
        year_from: model.year_from || '',
        year_to: model.year_to || '',
        description: model.description || '',
        image_url: model.image_url || '',
        is_active: model.is_active !== undefined ? model.is_active : true
      })
    } else {
      // Сброс формы для создания новой модели
      setFormData({
        name: '',
        code: '',
        brand: '',
        category: 'general',
        year_from: '',
        year_to: '',
        description: '',
        image_url: '',
        is_active: true
      })
    }
    setError('')
  }, [model, isOpen])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      const data = {
        ...formData,
        year_from: formData.year_from ? parseInt(formData.year_from) : null,
        year_to: formData.year_to ? parseInt(formData.year_to) : null
      }

      if (model) {
        // Редактирование существующей модели
        await modelsApi.updateModel(model.id, data)
      } else {
        // Создание новой модели
        await modelsApi.createModel(data)
      }

      onSuccess()
      onClose()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Произошла ошибка при сохранении модели')
    } finally {
      setIsLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    }))
  }

  if (!isOpen) return null

  return (
    <div className="modal-overlay">
      <div className="modal-content model-form">
        <div className="modal-header">
          <div className="modal-title">
            <Package size={24} color="#3b82f6" />
            <h2>{model ? 'Редактировать модель' : 'Создать модель'}</h2>
          </div>
          <button className="modal-close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="model-form-content">
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="name">Название модели *</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                placeholder="Например: iPhone 15 Pro"
              />
            </div>
            <div className="form-group">
              <label htmlFor="code">Код модели</label>
              <input
                type="text"
                id="code"
                name="code"
                value={formData.code}
                onChange={handleChange}
                placeholder="Например: A3102"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="brand">Бренд</label>
              <input
                type="text"
                id="brand"
                name="brand"
                value={formData.brand}
                onChange={handleChange}
                placeholder="Например: Apple"
              />
            </div>
            <div className="form-group">
              <label htmlFor="category">Категория</label>
              <select
                id="category"
                name="category"
                value={formData.category}
                onChange={handleChange}
              >
                <option value="general">Общее</option>
                <option value="smartphone">Смартфон</option>
                <option value="tablet">Планшет</option>
                <option value="laptop">Ноутбук</option>
                <option value="accessory">Аксессуар</option>
                <option value="other">Другое</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="year_from">Год выпуска (от)</label>
              <input
                type="number"
                id="year_from"
                name="year_from"
                value={formData.year_from}
                onChange={handleChange}
                placeholder="2023"
                min="1990"
                max="2030"
              />
            </div>
            <div className="form-group">
              <label htmlFor="year_to">Год выпуска (до)</label>
              <input
                type="number"
                id="year_to"
                name="year_to"
                value={formData.year_to}
                onChange={handleChange}
                placeholder="2024"
                min="1990"
                max="2030"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="image_url">URL изображения</label>
            <input
              type="url"
              id="image_url"
              name="image_url"
              value={formData.image_url}
              onChange={handleChange}
              placeholder="https://example.com/image.jpg"
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Описание</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows={4}
              placeholder="Подробное описание модели..."
            />
          </div>

          <div className="form-group checkbox-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="is_active"
                checked={formData.is_active}
                onChange={handleChange}
              />
              <span className="checkbox-text">Модель активна</span>
            </label>
          </div>

          <div className="modal-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Отмена
            </button>
            <button type="submit" className="btn btn-primary" disabled={isLoading}>
              {isLoading ? (
                <>
                  <div className="spinner" />
                  Сохранение...
                </>
              ) : (
                <>
                  <Save size={16} />
                  {model ? 'Сохранить' : 'Создать'}
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ModelForm
