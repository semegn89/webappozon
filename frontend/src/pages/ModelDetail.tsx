import React, { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, Download, Eye, FileText, Package } from 'lucide-react'
import { modelsApi, ticketsApi } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'

const ModelDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<'info' | 'files'>('info')

  const { data: model, isLoading, error } = useQuery({
    queryKey: ['model', id],
    queryFn: () => modelsApi.getModel(Number(id)),
    enabled: !!id
  })

  const { data: files } = useQuery({
    queryKey: ['model-files', id],
    queryFn: () => ticketsApi.getModelFiles(Number(id)),
    enabled: !!id
  })

  const handleDownload = async (file: any) => {
    try {
      const link = document.createElement('a')
      link.href = file.url
      link.download = file.filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } catch (error) {
      console.error('Download failed:', error)
    }
  }

  const handleView = async (file: any) => {
    try {
      window.open(file.url, '_blank')
    } catch (error) {
      console.error('View failed:', error)
    }
  }

  const getFileIcon = (mimeType: string): string => {
    if (mimeType.includes('pdf')) return '📄'
    if (mimeType.includes('word') || mimeType.includes('docx')) return '📝'
    if (mimeType.includes('excel') || mimeType.includes('xlsx')) return '📊'
    if (mimeType.includes('image')) return '🖼️'
    if (mimeType.includes('zip')) return '📦'
    return '📎'
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  if (isLoading) return <LoadingSpinner message="Загрузка модели..." />
  if (error || !model) return <div className="error">Модель не найдена</div>

  return (
    <div className="container">
      {/* Заголовок */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
          <button 
            className="btn btn-small btn-secondary"
            onClick={() => navigate('/models')}
          >
            <ArrowLeft size={16} />
            Назад
          </button>
          <h1>{model.name}</h1>
        </div>
        
        <div className="card-subtitle">
          {model.brand && `${model.brand} • `}
          {model.code}
          {model.year_range && ` • ${model.year_range}`}
        </div>
      </div>

      {/* Вкладки */}
      <div className="card">
        <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
          <button
            className={`btn btn-small ${activeTab === 'info' ? '' : 'btn-secondary'}`}
            onClick={() => setActiveTab('info')}
          >
            <Package size={16} />
            Информация
          </button>
          <button
            className={`btn btn-small ${activeTab === 'files' ? '' : 'btn-secondary'}`}
            onClick={() => setActiveTab('files')}
          >
            <FileText size={16} />
            Файлы ({files?.length || 0})
          </button>
        </div>

        {/* Информация о модели */}
        {activeTab === 'info' && (
          <div>
            {model.description && (
              <div style={{ marginBottom: '16px' }}>
                <h3>Описание</h3>
                <p>{model.description}</p>
              </div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              {model.brand && (
                <div>
                  <h4>Бренд</h4>
                  <p>{model.brand}</p>
                </div>
              )}
              
              {model.category && (
                <div>
                  <h4>Категория</h4>
                  <p>{model.category}</p>
                </div>
              )}
              
              {model.year_range && (
                <div>
                  <h4>Годы выпуска</h4>
                  <p>{model.year_range}</p>
                </div>
              )}
              
              <div>
                <h4>Код модели</h4>
                <p>{model.code}</p>
              </div>
              
              <div>
                <h4>Дата добавления</h4>
                <p>{new Date(model.created_at).toLocaleDateString('ru-RU')}</p>
              </div>
            </div>

            {/* Кнопка создания тикета */}
            <div style={{ marginTop: '24px', padding: '16px', backgroundColor: 'var(--tg-theme-secondary-bg-color)', borderRadius: '8px' }}>
              <h3>Нужна помощь?</h3>
              <p style={{ marginBottom: '12px' }}>Создайте тикет поддержки для этой модели</p>
              <button 
                className="btn"
                onClick={() => navigate(`/tickets/create?model_id=${model.id}`)}
              >
                Создать тикет
              </button>
            </div>
          </div>
        )}

        {/* Файлы */}
        {activeTab === 'files' && (
          <div>
            {!files || files.length === 0 ? (
              <div className="empty-state">
                <FileText size={48} className="empty-state-icon" />
                <h3 className="empty-state-title">Файлы не найдены</h3>
                <p className="empty-state-description">
                  Для этой модели пока нет доступных файлов
                </p>
              </div>
            ) : (
              <div className="list">
                {files.map((file: any) => (
                  <div key={file.id} className="list-item">
                    <div className="list-item-header">
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <span style={{ fontSize: '24px' }}>{getFileIcon(file.mime_type)}</span>
                        <div>
                          <div className="list-item-title">{file.filename}</div>
                          <div className="list-item-subtitle">
                            {file.mime_type.split('/')[1]?.toUpperCase() || 'FILE'} • {formatFileSize(file.file_size)}
                            {file.comment && ` • ${file.comment}`}
                          </div>
                          <div className="list-item-meta">
                            {new Date(file.created_at).toLocaleDateString('ru-RU')}
                          </div>
                        </div>
                      </div>
                      
                      <div style={{ display: 'flex', gap: '8px' }}>
                        {(file.mime_type.includes('pdf') || file.mime_type.includes('image')) && (
                        <button
                          className="btn btn-small btn-secondary"
                          onClick={() => handleView(file)}
                        >
                          <Eye size={14} />
                          Просмотр
                        </button>
                        )}
                        <button
                          className="btn btn-small"
                          onClick={() => handleDownload(file)}
                        >
                          <Download size={14} />
                          Скачать
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default ModelDetail
