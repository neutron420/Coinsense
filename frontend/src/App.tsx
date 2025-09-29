import './App.css'
import { BrowserRouter, Navigate, Route, Routes, Link } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Chat from './pages/Chat'
import Predict from './pages/Predict'
import Sentiment from './pages/Sentiment'

function PrivateRoute({ children }: { children: React.ReactElement }) {
  const { user, loading } = useAuth()
  if (loading) return <div style={{ padding: 24 }}>Loading...</div>
  return user ? children : <Navigate to="/login" replace />
}

function Layout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth()
  return (
    <div>
      <nav style={{ display: 'flex', gap: 12, padding: 12, borderBottom: '1px solid #ddd' }}>
        <Link to="/">Home</Link>
        {user && (
          <>
            <Link to="/dashboard">Dashboard</Link>
            <Link to="/chat">Chat</Link>
            <Link to="/predict">Predict</Link>
            <Link to="/sentiment">Sentiment</Link>
            <button onClick={logout}>Logout</button>
          </>
        )}
        {!user && (
          <>
            <Link to="/login">Login</Link>
            <Link to="/register">Register</Link>
          </>
        )}
      </nav>
      {children}
    </div>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
            <Route path="/chat" element={<PrivateRoute><Chat /></PrivateRoute>} />
            <Route path="/predict" element={<PrivateRoute><Predict /></PrivateRoute>} />
            <Route path="/sentiment" element={<PrivateRoute><Sentiment /></PrivateRoute>} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </AuthProvider>
  )
}
