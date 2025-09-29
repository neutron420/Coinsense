import type { FormEvent } from 'react'
import { useState } from 'react'
import { api } from '../lib/api'

type Prediction = { symbol: string; predicted_price?: number; confidence?: number; [k: string]: unknown }

export default function Predict() {
	const [symbol, setSymbol] = useState('bitcoin')
	const [result, setResult] = useState<Prediction | null>(null)
	const [loading, setLoading] = useState(false)
	const [error, setError] = useState<string | null>(null)

	async function onSubmit(e: FormEvent) {
		e.preventDefault()
		setError(null)
		setLoading(true)
		try {
			const { data } = await api.post('/api/predict/predict', { symbol })
			setResult(data)
		} catch (err: unknown) {
			const message = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Prediction failed'
			setError(message)
		} finally {
			setLoading(false)
		}
	}

	return (
		<div className="container" style={{ maxWidth: 720, margin: '0 auto', paddingTop: 32 }}>
			<div className="card">
				<div className="card-header">
					<h2>Predict</h2>
				</div>
				<div className="card-body">
					<form onSubmit={onSubmit} className="grid" style={{ gridTemplateColumns: '1fr auto', gap: 8 }}>
                    <input
                        value={symbol}
                        onChange={(e) => setSymbol(e.currentTarget.value)}
                        placeholder="e.g. bitcoin"
                        className="form-control"
                    />
						<button type="submit" disabled={loading} className="btn btn-primary">
							{loading ? 'Predicting…' : 'Predict'}
						</button>
					</form>
						{error && <div style={{ color: 'crimson', marginTop: 12 }}>{error}</div>}
						{result && (
							<div style={{ marginTop: 16 }}>
								<pre>{JSON.stringify(result, null, 2)}</pre>
							</div>
						)}
                </div>
            </div>
        </div>
    )
}
