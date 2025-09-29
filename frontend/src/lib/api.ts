import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
	baseURL: API_BASE_URL,
})

api.interceptors.request.use((config) => {
	const token = localStorage.getItem('token')
	if (token) {
		config.headers = config.headers ?? {}
		config.headers.Authorization = `Bearer ${token}`
	}
	return config
})

api.interceptors.response.use(
	(response) => response,
	(error) => {
		if (error?.response?.status === 401) {
			localStorage.removeItem('token')
			window.dispatchEvent(new Event('auth:logout'))
		}
		return Promise.reject(error)
	}
)

export function setToken(token: string) {
	localStorage.setItem('token', token)
}

export function clearToken() {
	localStorage.removeItem('token')
}

export function getToken(): string | null {
	return localStorage.getItem('token')
}


