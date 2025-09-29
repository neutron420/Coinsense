import type { FormEvent } from 'react'
import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { Link, useNavigate } from 'react-router-dom'
import Page from '../layouts/Page'
import Navbar from '../components/Navbar'
import { Card, CardBody, CardHeader } from '../components/Card'
import Input from '../components/Input'
import Button from '../components/Button'

export default function Register() {
	const { register } = useAuth()
	const navigate = useNavigate()
	const [username, setUsername] = useState('')
	const [email, setEmail] = useState('')
	const [password, setPassword] = useState('')
	const [error, setError] = useState<string | null>(null)
	const [loading, setLoading] = useState(false)

	async function onSubmit(e: FormEvent) {
		e.preventDefault()
		setError(null)
		setLoading(true)
		try {
			await register(username, email, password)
			navigate('/dashboard')
		} catch (err: unknown) {
			const message = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Registration failed'
			setError(message)
		} finally {
			setLoading(false)
		}
	}

	return (
		<Page>
			<Navbar />
			<div className="container" style={{ maxWidth: 560 }}>
				<Card>
					<CardHeader><h2>Create account</h2></CardHeader>
					<CardBody>
						<form onSubmit={onSubmit} className="grid gap-3">
							<Input label="Username" value={username} onChange={(e) => setUsername(e.target.value)} required />
							<Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
							<Input label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
							<Button type="submit" disabled={loading}>{loading ? 'Creating account...' : 'Create account'}</Button>
							{error && <div style={{ color: 'crimson' }}>{error}</div>}
						</form>
						<p style={{ marginTop: 12 }}>Already have an account? <Link to="/login">Login</Link></p>
					</CardBody>
				</Card>
			</div>
		</Page>
	)
}


