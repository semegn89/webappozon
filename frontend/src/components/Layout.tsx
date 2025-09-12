import React from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useTelegram } from '../contexts/TelegramContext'
import Navigation from './Navigation'
import LoadingSpinner from './LoadingSpinner'

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth()
  const { isReady } = useTelegram()

  // Показываем загрузку пока не готовы
  if (!isReady || isLoading) {
    return <LoadingSpinner />
  }

  // Показываем ошибку если не аутентифицированы
  if (!isAuthenticated) {
    return (
      <div className="container">
        <div className="error">
          <h2>Ошибка аутентификации</h2>
          <p>Не удалось войти в систему. Попробуйте перезагрузить страницу.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      <Navigation />
      <main className="main">
        {children}
      </main>
    </div>
  )
}

export default Layout
