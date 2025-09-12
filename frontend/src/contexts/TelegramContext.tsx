import React, { createContext, useContext, useEffect, useState } from 'react'
import { WebApp } from '@twa-dev/sdk'

interface TelegramContextType {
  webApp: WebApp | null
  user: any | null
  initData: string | null
  isReady: boolean
}

const TelegramContext = createContext<TelegramContextType>({
  webApp: null,
  user: null,
  initData: null,
  isReady: false,
})

export const useTelegram = () => {
  const context = useContext(TelegramContext)
  if (!context) {
    throw new Error('useTelegram must be used within a TelegramProvider')
  }
  return context
}

interface TelegramProviderProps {
  children: React.ReactNode
}

export const TelegramProvider: React.FC<TelegramProviderProps> = ({ children }) => {
  const [webApp, setWebApp] = useState<WebApp | null>(null)
  const [user, setUser] = useState<any | null>(null)
  const [initData, setInitData] = useState<string | null>(null)
  const [isReady, setIsReady] = useState(false)

  useEffect(() => {
    // Инициализация Telegram WebApp
    const tg = window.Telegram?.WebApp
    
    if (tg) {
      setWebApp(tg)
      setUser(tg.initDataUnsafe?.user || null)
      setInitData(tg.initData || null)
      
      // Настройка WebApp
      tg.ready()
      tg.expand()
      
      // Отключаем закрытие по свайпу
      tg.enableClosingConfirmation()
      
      setIsReady(true)
      
      console.log('Telegram WebApp initialized:', {
        user: tg.initDataUnsafe?.user,
        initData: tg.initData
      })
    } else {
      // Для разработки - создаем мок данные
      const mockUser = {
        id: 123456789,
        first_name: 'Test',
        last_name: 'User',
        username: 'testuser',
        language_code: 'ru'
      }
      
      const mockInitData = 'user=%7B%22id%22%3A123456789%2C%22first_name%22%3A%22Test%22%2C%22last_name%22%3A%22User%22%2C%22username%22%3A%22testuser%22%2C%22language_code%22%3A%22ru%22%7D&chat_instance=-123456789&chat_type=sender&auth_date=1234567890&hash=mock_hash'
      
      setUser(mockUser)
      setInitData(mockInitData)
      setIsReady(true)
      
      console.log('Using mock Telegram data for development')
    }
  }, [])

  return (
    <TelegramContext.Provider value={{ webApp, user, initData, isReady }}>
      {children}
    </TelegramContext.Provider>
  )
}
