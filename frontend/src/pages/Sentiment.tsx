import type { FormEvent } from 'react'
import { useState } from 'react'
import { api } from '../lib/api'
import Page from '../layouts/Page'
import Navbar from '../components/Navbar'
import { Card, CardBody, CardHeader } from '../components/Card'
import Textarea from '../components/Textarea'
import Button from '../components/Button'

export default function Sentiment() {
	const [text, setText] = useState('')
	const [result, setResult] = useState<unknown>(null)
	const [loading, setLoading] = useState(false)
	const [error, setError] = useState<string | null>(null)

	async function onSubmit(e: FormEvent) {
		e.preventDefault()
		setError(null)
		setLoading(true)
		try {
			const { data } = await api.post('/api/sentiment/analyze', { text })
			setResult(data)
		} catch (err: unknown) {
			const message = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Sentiment analysis failed'
			setError(message)
		} finally {
			setLoading(false)
		}
	}

return (
	<Page>
		<Navbar />
		<div className="container" style={{ maxWidth: 720 }}>
			<Card>
				<CardHeader><h2>Sentiment</h2></CardHeader>
				<CardBody>
					<form onSubmit={onSubmit} className="grid gap-3">
						<Textarea rows={5} value={text} onChange={(e) => setText(e.target.value)} placeholder="Paste news text or your input..." />
						<Button type="submit" disabled={loading}>{loading ? 'Analyzing…' : 'Analyze'}</Button>
					</form>
					{error && <div style={{ color: 'crimson', marginTop: 12 }}>{error}</div>}
					{result != null && (
						<div style={{ marginTop: 16 }}>
							<pre>{JSON.stringify(result, null, 2)}</pre>
						</div>
					)}
				</CardBody>
			</Card>
		</div>
	</Page>
)
}


