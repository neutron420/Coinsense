import type { FormEvent } from 'react'
import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { Link, useNavigate } from 'react-router-dom'

export default function Login() {
	const { login } = useAuth()
	const navigate = useNavigate()
	const [username, setUsername] = useState('')
	const [password, setPassword] = useState('')
	const [error, setError] = useState<string | null>(null)
	const [loading, setLoading] = useState(false)

	async function onSubmit(e: FormEvent) {
		e.preventDefault()
		setError(null)
		setLoading(true)
		try {
			await login(username, password)
			navigate('/dashboard')
		} catch (err: unknown) {
			const message = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Login failed'
			setError(message)
		} finally {
			setLoading(false)
		}
	}

	return (
		<div style={{ maxWidth: 420, margin: '48px auto', padding: 24 }}>
			<h2>Login</h2>
			<form onSubmit={onSubmit}>
				<div style={{ display: 'grid', gap: 12 }}>
					<label>
						Username or Email
						<input value={username} onChange={(e) => setUsername(e.target.value)} required />
					</label>
					<label>
						Password
						<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
					</label>
					<button type="submit" disabled={loading}>{loading ? 'Signing in...' : 'Sign in'}</button>
					{error && <div style={{ color: 'crimson' }}>{error}</div>}
				</div>
			</form>
			<p style={{ marginTop: 16 }}>No account? <Link to="/register">Register</Link></p>
		</div>
	)
}


