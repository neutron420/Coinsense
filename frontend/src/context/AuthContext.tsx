import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { api, setToken, clearToken, getToken } from '../lib/api'

type User = {
	id: number
	username: string
	email: string
	created_at?: string
}

type AuthContextValue = {
	user: User | null
	loading: boolean
	login: (emailOrUsername: string, password: string) => Promise<void>
	register: (username: string, email: string, password: string) => Promise<void>
	logout: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
	const [user, setUser] = useState<User | null>(null)
	const [loading, setLoading] = useState<boolean>(true)

	const fetchMe = useCallback(async () => {
		try {
			const { data } = await api.get('/api/user/me')
			setUser(data)
		} catch (_) {
			setUser(null)
		}
	}, [])

	useEffect(() => {
		const token = getToken()
		if (!token) {
			setLoading(false)
			return
		}
		fetchMe().finally(() => setLoading(false))

		const onLogout = () => setUser(null)
		window.addEventListener('auth:logout', onLogout)
		return () => window.removeEventListener('auth:logout', onLogout)
	}, [fetchMe])

	const login = useCallback(async (emailOrUsername: string, password: string) => {
		const { data } = await api.post('/api/auth/login', { username: emailOrUsername, password })
		setToken(data.access_token ?? data.token)
		await fetchMe()
	}, [fetchMe])

	const register = useCallback(async (username: string, email: string, password: string) => {
		await api.post('/api/auth/register', { username, email, password })
		await login(username, password)
	}, [login])

	const logout = useCallback(() => {
		clearToken()
		setUser(null)
	}, [])

	const value = useMemo<AuthContextValue>(() => ({ user, loading, login, register, logout }), [user, loading, login, register, logout])

	return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
	const ctx = useContext(AuthContext)
	if (!ctx) throw new Error('useAuth must be used within AuthProvider')
	return ctx
}


