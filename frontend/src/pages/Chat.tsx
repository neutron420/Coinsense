import type { FormEvent } from 'react'
import { useEffect, useRef, useState } from 'react'
import { api } from '../lib/api'
import Page from '../layouts/Page'
import Navbar from '../components/Navbar'
import { Card, CardBody, CardHeader } from '../components/Card'
import Textarea from '../components/Textarea'
import Button from '../components/Button'

type Message = { role: 'user' | 'assistant'; text: string }

export default function Chat() {
	const [messages, setMessages] = useState<Message[]>([])
	const [input, setInput] = useState('')
	const [loading, setLoading] = useState(false)
	const endRef = useRef<HTMLDivElement | null>(null)

	useEffect(() => {
		endRef.current?.scrollIntoView({ behavior: 'smooth' })
	}, [messages])

	async function onSubmit(e: FormEvent) {
		e.preventDefault()
		if (!input.trim()) return
		const userMsg: Message = { role: 'user', text: input }
		setMessages((prev) => [...prev, userMsg])
		setInput('')
		setLoading(true)
		try {
			const { data } = await api.post('/api/chat/message', { message: userMsg.text })
			const botMsg: Message = { role: 'assistant', text: data?.response ?? JSON.stringify(data) }
			setMessages((prev) => [...prev, botMsg])
		} catch (err: unknown) {
			const message = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Error'
			setMessages((prev) => [...prev, { role: 'assistant', text: message }])
		} finally {
			setLoading(false)
		}
	}

	return (
		<Page>
			<Navbar />
			<div className="container" style={{ maxWidth: 900 }}>
				<Card>
					<CardHeader><h2>Chat</h2></CardHeader>
					<CardBody>
						<div style={{ minHeight: 360 }}>
							{messages.map((m, idx) => (
								<div key={idx} style={{ margin: '8px 0', color: m.role === 'user' ? '#e5e5e5' : '#86efac' }}>
									<strong>{m.role === 'user' ? 'You' : 'Bot'}:</strong> {m.text}
								</div>
							))}
							<div ref={endRef} />
						</div>
						<form onSubmit={onSubmit} className="grid" style={{ gridTemplateColumns: '1fr auto', gap: 8, marginTop: 12 }}>
							<Textarea value={input} onChange={(e) => setInput(e.target.value)} placeholder="Type your message..." rows={3} />
							<Button type="submit" disabled={loading}>{loading ? 'Sending…' : 'Send'}</Button>
						</form>
					</CardBody>
				</Card>
			</div>
		</Page>
	)
}


