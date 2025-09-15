import React from 'react'
import { useLocation } from 'react-router-dom'
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
  const location = useLocation()

  // Проверяем, находимся ли мы в админ-панели
  const isAdminPage = location.pathname.startsWith('/admin')

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
      {/* Скрываем Navigation в админ-панели */}
      {!isAdminPage && <Navigation />}
      <main className="main">
        {children}
      </main>
    </div>
  )
}

export default Layout
