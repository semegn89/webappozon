import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Models from './pages/Models'
import Admin from './pages/Admin'
import TicketDetail from './pages/TicketDetail'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5000,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div style={{ minHeight: '100vh', background: '#f5f5f5' }}>
          <nav style={{ background: '#2563eb', color: 'white', padding: '1rem' }}>
            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
              <h1 style={{ margin: 0, fontSize: '1.5rem' }}>Simple App</h1>
              <Link to="/" style={{ color: 'white', textDecoration: 'none' }}>Модели</Link>
              <Link to="/admin" style={{ color: 'white', textDecoration: 'none' }}>Админ</Link>
            </div>
          </nav>
          
          <main style={{ padding: '2rem' }}>
            <Routes>
              <Route path="/" element={<Models />} />
              <Route path="/admin" element={<Admin />} />
              <Route path="/tickets/:id" element={<TicketDetail />} />
            </Routes>
          </main>
        </div>
      </Router>
    </QueryClientProvider>
  )
}

export default App
