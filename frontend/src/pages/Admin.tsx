import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { 
  Settings, Users, Package, Ticket, BarChart3, Plus, 
  TrendingUp, Eye, Download, MessageSquare, Calendar,
  CheckCircle, Filter, Search, Edit, Trash2, Upload
} from 'lucide-react'
import { adminApi, modelsApi, ticketsApi } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'

const Admin: React.FC = () => {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<'dashboard' | 'models' | 'tickets' | 'users'>('dashboard')

  // Получаем статистику
  const { isLoading: statsLoading } = useQuery({
    queryKey: ['admin-stats'],
    queryFn: adminApi.getAdminStats
  })

  // Получаем модели
  const { data: modelsData } = useQuery({
    queryKey: ['admin-models'],
    queryFn: () => modelsApi.getModels({ page: 1, page_size: 10 }),
    enabled: activeTab === 'models'
  })

  // Получаем тикеты
  const { data: ticketsData } = useQuery({
    queryKey: ['admin-tickets'],
    queryFn: () => ticketsApi.getTickets({ page: 1, page_size: 10 }),
    enabled: activeTab === 'tickets'
  })

  // Получаем пользователей
  const { data: usersData } = useQuery({
    queryKey: ['admin-users'],
    queryFn: () => adminApi.getUsers({ page: 1, page_size: 10 }),
    enabled: activeTab === 'users'
  })

  const tabs = [
    { id: 'dashboard', label: 'Дашборд', icon: BarChart3, color: 'from-blue-500 to-blue-600' },
    { id: 'models', label: 'Модели', icon: Package, color: 'from-green-500 to-green-600' },
    { id: 'tickets', label: 'Тикеты', icon: Ticket, color: 'from-orange-500 to-orange-600' },
    { id: 'users', label: 'Пользователи', icon: Users, color: 'from-purple-500 to-purple-600' }
  ]

  if (statsLoading) return <LoadingSpinner message="Загрузка админ-панели..." />

  // Статистические карточки
  const StatCard = ({ title, value, icon: Icon, color, trend }: any) => (
    <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-600 text-sm font-medium">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
          {trend && (
            <div className="flex items-center mt-2">
              <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
              <span className="text-green-600 text-sm font-medium">{trend}</span>
            </div>
          )}
        </div>
        <div className={`p-3 rounded-xl bg-gradient-to-r ${color}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </div>
  )

  // Карточка модели
  const ModelCard = ({ model }: any) => (
    <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-100 rounded-lg">
            <Package className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{model.name}</h3>
            <p className="text-gray-600 text-sm">{model.category}</p>
          </div>
        </div>
        <div className="flex space-x-2">
          <button className="p-2 text-gray-400 hover:text-blue-600 transition-colors">
            <Edit className="w-4 h-4" />
          </button>
          <button className="p-2 text-gray-400 hover:text-red-600 transition-colors">
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>
      <p className="text-gray-600 text-sm mb-4">{model.description}</p>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4 text-sm text-gray-500">
          <div className="flex items-center">
            <Eye className="w-4 h-4 mr-1" />
            <span>0 просмотров</span>
          </div>
          <div className="flex items-center">
            <Download className="w-4 h-4 mr-1" />
            <span>0 загрузок</span>
          </div>
        </div>
        <span className="px-3 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
          Активна
        </span>
      </div>
    </div>
  )

  // Карточка тикета
  const TicketCard = ({ ticket }: any) => (
    <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-lg ${
            ticket.status === 'open' ? 'bg-orange-100' : 
            ticket.status === 'closed' ? 'bg-green-100' : 'bg-blue-100'
          }`}>
            <Ticket className={`w-5 h-5 ${
              ticket.status === 'open' ? 'text-orange-600' : 
              ticket.status === 'closed' ? 'text-green-600' : 'text-blue-600'
            }`} />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{ticket.subject}</h3>
            <p className="text-gray-600 text-sm">Приоритет: {ticket.priority}</p>
          </div>
        </div>
        <div className="flex space-x-2">
          <button className="p-2 text-gray-400 hover:text-blue-600 transition-colors">
            <MessageSquare className="w-4 h-4" />
          </button>
          <button className="p-2 text-gray-400 hover:text-green-600 transition-colors">
            <CheckCircle className="w-4 h-4" />
          </button>
        </div>
      </div>
      <p className="text-gray-600 text-sm mb-4">{ticket.description}</p>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4 text-sm text-gray-500">
          <div className="flex items-center">
            <Calendar className="w-4 h-4 mr-1" />
            <span>{new Date(ticket.created_at).toLocaleDateString()}</span>
          </div>
        </div>
        <span className={`px-3 py-1 text-xs font-medium rounded-full ${
          ticket.status === 'open' ? 'bg-orange-100 text-orange-800' : 
          ticket.status === 'closed' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'
        }`}>
          {ticket.status === 'open' ? 'Открыт' : 
           ticket.status === 'closed' ? 'Закрыт' : 'В работе'}
        </span>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="container mx-auto px-4 py-8">
        {/* Красивый заголовок */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8 border border-gray-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-4 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl">
                <Settings className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
                  Админ Кабинет
                </h1>
                <p className="text-gray-600 mt-2 text-lg">Управление системой и контентом</p>
              </div>
            </div>
            <button
              onClick={() => navigate('/')}
              className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
            >
              ← Вернуться в приложение
            </button>
          </div>
        </div>

        {/* Вкладки */}
        <div className="bg-white rounded-2xl shadow-lg p-2 mb-8 border border-gray-100">
          <div className="flex space-x-2">
            {tabs.map((tab) => {
              const Icon = tab.icon
              const isActive = activeTab === tab.id
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center space-x-3 px-6 py-4 rounded-xl font-medium transition-all duration-300 ${
                    isActive
                      ? `bg-gradient-to-r ${tab.color} text-white shadow-lg transform scale-105`
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span>{tab.label}</span>
                </button>
              )
            })}
          </div>
        </div>

        {/* Контент */}
        <div className="space-y-8">
          {activeTab === 'dashboard' && (
            <>
              {/* Статистика */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                  title="Всего моделей"
                  value={modelsData?.models?.length || 0}
                  icon={Package}
                  color="from-blue-500 to-blue-600"
                  trend="+12%"
                />
                <StatCard
                  title="Активных тикетов"
                  value={ticketsData?.tickets?.filter((t: any) => t.status === 'open').length || 0}
                  icon={Ticket}
                  color="from-orange-500 to-orange-600"
                  trend="+5%"
                />
                <StatCard
                  title="Пользователей"
                  value={usersData?.users?.length || 0}
                  icon={Users}
                  color="from-green-500 to-green-600"
                  trend="+8%"
                />
                <StatCard
                  title="Загрузок"
                  value="1,234"
                  icon={Download}
                  color="from-purple-500 to-purple-600"
                  trend="+15%"
                />
              </div>

              {/* Быстрые действия */}
              <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Быстрые действия</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <button className="p-6 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl hover:from-blue-600 hover:to-blue-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1">
                    <div className="flex items-center space-x-4">
                      <Plus className="w-8 h-8" />
                      <div className="text-left">
                        <h3 className="font-semibold text-lg">Добавить модель</h3>
                        <p className="text-blue-100 text-sm">Создать новую модель</p>
                      </div>
                    </div>
                  </button>
                  <button className="p-6 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-xl hover:from-green-600 hover:to-green-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1">
                    <div className="flex items-center space-x-4">
                      <Upload className="w-8 h-8" />
                      <div className="text-left">
                        <h3 className="font-semibold text-lg">Загрузить файл</h3>
                        <p className="text-green-100 text-sm">Добавить инструкцию</p>
                      </div>
                    </div>
                  </button>
                  <button className="p-6 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-xl hover:from-purple-600 hover:to-purple-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1">
                    <div className="flex items-center space-x-4">
                      <BarChart3 className="w-8 h-8" />
                      <div className="text-left">
                        <h3 className="font-semibold text-lg">Аналитика</h3>
                        <p className="text-purple-100 text-sm">Посмотреть статистику</p>
                      </div>
                    </div>
                  </button>
                </div>
              </div>

              {/* Последние активности */}
              <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Последние активности</h2>
                <div className="space-y-4">
                  <div className="flex items-center space-x-4 p-4 bg-gray-50 rounded-xl">
                    <div className="p-2 bg-blue-100 rounded-lg">
                      <Package className="w-5 h-5 text-blue-600" />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">Добавлена новая модель "Sample Model"</p>
                      <p className="text-gray-600 text-sm">2 часа назад</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4 p-4 bg-gray-50 rounded-xl">
                    <div className="p-2 bg-orange-100 rounded-lg">
                      <Ticket className="w-5 h-5 text-orange-600" />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">Создан новый тикет поддержки</p>
                      <p className="text-gray-600 text-sm">4 часа назад</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4 p-4 bg-gray-50 rounded-xl">
                    <div className="p-2 bg-green-100 rounded-lg">
                      <Users className="w-5 h-5 text-green-600" />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">Новый пользователь зарегистрирован</p>
                      <p className="text-gray-600 text-sm">6 часов назад</p>
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}

          {activeTab === 'models' && (
            <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Управление моделями</h2>
                <button className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all duration-300 shadow-lg hover:shadow-xl">
                  <Plus className="w-5 h-5 mr-2 inline" />
                  Добавить модель
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {modelsData?.models?.map((model: any) => (
                  <ModelCard key={model.id} model={model} />
                ))}
              </div>
            </div>
          )}

          {activeTab === 'tickets' && (
            <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Управление тикетами</h2>
                <div className="flex space-x-3">
                  <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
                    <Filter className="w-4 h-4 mr-2 inline" />
                    Фильтр
                  </button>
                  <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
                    <Search className="w-4 h-4 mr-2 inline" />
                    Поиск
                  </button>
                </div>
              </div>
              <div className="space-y-4">
                {ticketsData?.tickets?.map((ticket: any) => (
                  <TicketCard key={ticket.id} ticket={ticket} />
                ))}
              </div>
            </div>
          )}

          {activeTab === 'users' && (
            <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Управление пользователями</h2>
                <button className="px-6 py-3 bg-gradient-to-r from-green-600 to-blue-600 text-white rounded-xl hover:from-green-700 hover:to-blue-700 transition-all duration-300 shadow-lg hover:shadow-xl">
                  <Users className="w-5 h-5 mr-2 inline" />
                  Добавить пользователя
                </button>
              </div>
              <div className="text-center py-12">
                <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Пользователи</h3>
                <p className="text-gray-600">Здесь будет список пользователей</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Admin