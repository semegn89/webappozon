import React from 'react'

interface LoadingSpinnerProps {
  message?: string
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ message = 'Загрузка...' }) => {
  return (
    <div className="loading">
      <div className="spinner"></div>
      <span style={{ marginLeft: '12px' }}>{message}</span>
    </div>
  )
}

export default LoadingSpinner
