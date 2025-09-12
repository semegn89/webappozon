import React from 'react'
import { useNavigate } from 'react-router-dom'
import { Home, ArrowLeft } from 'lucide-react'

const NotFound: React.FC = () => {
  const navigate = useNavigate()

  return (
    <div className="container">
      <div className="empty-state">
        <h1 style={{ fontSize: '72px', marginBottom: '16px' }}>404</h1>
        <h2 className="empty-state-title">Страница не найдена</h2>
        <p className="empty-state-description">
          Запрашиваемая страница не существует или была перемещена.
        </p>
        
        <div style={{ display: 'flex', gap: '12px', marginTop: '24px', justifyContent: 'center' }}>
          <button 
            className="btn"
            onClick={() => navigate('/')}
          >
            <Home size={16} />
            На главную
          </button>
          
          <button 
            className="btn btn-secondary"
            onClick={() => navigate(-1)}
          >
            <ArrowLeft size={16} />
            Назад
          </button>
        </div>
      </div>
    </div>
  )
}

export default NotFound
