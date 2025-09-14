import React, { useState, useEffect } from 'react'
import { X, Save, Package, Upload, Download, Trash2, File } from 'lucide-react'
import { modelsApi, ticketsApi } from '../services/api'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

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
    category: '',
    description: '',
    image_url: '',
    is_active: true
  })
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [uploadComment, setUploadComment] = useState('')

  // Загружаем файлы модели (только если модель существует)
  const { data: modelFiles = [], refetch: refetchFiles } = useQuery({
    queryKey: ['model-files', model?.id],
    queryFn: () => ticketsApi.getModelFiles(model.id),
    enabled: !!model?.id
  })

  // Мутация для загрузки файла
  const uploadFileMutation = useMutation({
    mutationFn: ({ file, comment }: { file: File, comment?: string }) => 
      ticketsApi.uploadModelFile(model.id, file, comment),
    onSuccess: () => {
      refetchFiles()
      setUploadComment('')
    }
  })

  // Мутация для удаления файла
  const deleteFileMutation = useMutation({
    mutationFn: (fileId: number) => ticketsApi.deleteModelFile(model.id, fileId),
    onSuccess: () => {
      refetchFiles()
    }
  })

  // Заполняем форму данными модели при редактировании
  useEffect(() => {
    if (model) {
      setFormData({
        name: model.name || '',
        code: model.code || '',
        brand: model.brand || '',
        category: model.category || '',
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
        category: '',
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
        ...formData
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

  const handleFileUpload = () => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = '.pdf,.png,.jpg,.jpeg,.gif,.doc,.docx,.xlsx,.txt'
    input.multiple = true
    input.onchange = (e) => {
      const files = (e.target as HTMLInputElement).files
      if (files && files.length > 0) {
        Array.from(files).forEach(file => {
          uploadFileMutation.mutate({ 
            file, 
            comment: uploadComment || undefined 
          })
        })
      }
    }
    input.click()
  }

  const handleDeleteFile = (fileId: number, filename: string) => {
    if (window.confirm(`Удалить файл "${filename}"?`)) {
      deleteFileMutation.mutate(fileId)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
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
              <input
                type="text"
                id="category"
                name="category"
                value={formData.category}
                onChange={handleChange}
                placeholder="Например: Фотоаппараты, Серверное оборудование, Игровые приставки"
                maxLength={100}
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

          {/* Секция файлов модели (только для редактирования) */}
          {model && (
            <div className="model-files-section">
              <h3>Файлы модели</h3>
              <p className="files-description">Файлы, относящиеся к этой модели</p>
              
              {/* Загрузка файлов */}
              <div className="file-upload-section">
                <div className="upload-comment">
                  <input
                    type="text"
                    placeholder="Комментарий к файлу (опционально)"
                    value={uploadComment}
                    onChange={(e) => setUploadComment(e.target.value)}
                    className="form-input"
                  />
                </div>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handleFileUpload}
                  disabled={uploadFileMutation.isPending}
                >
                  <Upload size={16} />
                  {uploadFileMutation.isPending ? 'Загрузка...' : 'Загрузить файлы'}
                </button>
              </div>

              {/* Список файлов */}
              {modelFiles.length > 0 && (
                <div className="files-list">
                  <h4>Прикрепленные файлы:</h4>
                  {modelFiles.map((file: any) => (
                    <div key={file.id} className="file-item">
                      <div className="file-info">
                        <File size={16} />
                        <div className="file-details">
                          <span className="file-name">{file.filename}</span>
                          <span className="file-meta">
                            {formatFileSize(file.file_size)} • {new Date(file.created_at).toLocaleDateString('ru-RU')}
                          </span>
                          {file.comment && (
                            <span className="file-comment">{file.comment}</span>
                          )}
                        </div>
                      </div>
                      <div className="file-actions">
                        <a
                          href={file.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="btn btn-sm btn-secondary"
                        >
                          <Download size={14} />
                        </a>
                        <button
                          type="button"
                          className="btn btn-sm btn-danger"
                          onClick={() => handleDeleteFile(file.id, file.filename)}
                          disabled={deleteFileMutation.isPending}
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

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
