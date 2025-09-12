import React, { createContext, useContext, useEffect, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useTelegram } from './TelegramContext'
import { api } from '../services/api'

interface User {
  id: number
  telegram_user_id: number
  username?: string
  first_name?: string
  last_name?: string
  language_code: string
  role: 'user' | 'admin'
  is_blocked: boolean
  full_name: string
  is_admin: boolean
}

interface AuthContextType {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: () => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false,
  login: async () => {},
  logout: () => {},
})

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: React.ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const { initData, isReady } = useTelegram()
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'))
  const queryClient = useQueryClient()

  // Мутация для аутентификации
  const loginMutation = useMutation({
    mutationFn: async (initData: string) => {
      const response = await api.post('/auth/verify', { init_data: initData })
      return response.data
    },
    onSuccess: (data) => {
      setToken(data.token.access_token)
      localStorage.setItem('token', data.token.access_token)
      queryClient.setQueryData(['user'], data.user)
    },
    onError: (error) => {
      console.error('Authentication failed:', error)
      setToken(null)
      localStorage.removeItem('token')
    }
  })

  // Запрос информации о пользователе
  const { data: user, isLoading: userLoading } = useQuery({
    queryKey: ['user'],
    queryFn: async () => {
      const response = await api.get('/auth/me')
      return response.data
    },
    enabled: !!token,
    retry: false
  })

  // Автоматическая аутентификация при готовности
  useEffect(() => {
    if (isReady && initData && !token) {
      login()
    }
  }, [isReady, initData, token])

  const login = async () => {
    if (initData) {
      await loginMutation.mutateAsync(initData)
    }
  }

  const logout = () => {
    setToken(null)
    localStorage.removeItem('token')
    queryClient.clear()
  }

  const isAuthenticated = !!token && !!user
  const isLoading = loginMutation.isPending || userLoading

  return (
    <AuthContext.Provider value={{
      user: user || null,
      token,
      isAuthenticated,
      isLoading,
      login,
      logout
    }}>
      {children}
    </AuthContext.Provider>
  )
}
