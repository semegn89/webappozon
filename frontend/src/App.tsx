import { Routes, Route } from 'react-router-dom'
import { TelegramProvider } from './contexts/TelegramContext'
import { AuthProvider } from './contexts/AuthContext'
import Layout from './components/Layout'
import Home from './pages/Home'
import Models from './pages/Models'
import ModelDetail from './pages/ModelDetail'
import Tickets from './pages/Tickets'
import TicketDetail from './pages/TicketDetail'
import CreateTicket from './pages/CreateTicket'
import Admin from './pages/Admin'
import NotFound from './pages/NotFound'

function App() {
  return (
    <TelegramProvider>
      <AuthProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/models" element={<Models />} />
            <Route path="/models/:id" element={<ModelDetail />} />
            <Route path="/tickets" element={<Tickets />} />
            <Route path="/tickets/:id" element={<TicketDetail />} />
            <Route path="/tickets/create" element={<CreateTicket />} />
            <Route path="/admin" element={<Admin />} />
            <Route path="/admin/tickets/:id" element={<TicketDetail />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Layout>
      </AuthProvider>
    </TelegramProvider>
  )
}

export default App