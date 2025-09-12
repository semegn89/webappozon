import React from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Home, Package, Ticket, Settings, User } from 'lucide-react'

const Navigation: React.FC = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const { user } = useAuth()

  const navItems = [
    { path: '/', icon: Home, label: 'Главная' },
    { path: '/models', icon: Package, label: 'Модели' },
    { path: '/tickets', icon: Ticket, label: 'Тикеты' },
  ]

  // Добавляем админ-панель для админов
  if (user?.is_admin) {
    navItems.push({ path: '/admin', icon: Settings, label: 'Админ' })
  }

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/'
    }
    return location.pathname.startsWith(path)
  }

  return (
    <nav className="nav">
      {navItems.map((item) => {
        const Icon = item.icon
        return (
          <button
            key={item.path}
            className={`nav-item ${isActive(item.path) ? 'active' : ''}`}
            onClick={() => navigate(item.path)}
          >
            <Icon size={16} />
            <span>{item.label}</span>
          </button>
        )
      })}
    </nav>
  )
}

export default Navigation
