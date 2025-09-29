import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Page from '../layouts/Page'
import Navbar from '../components/Navbar'
import { Card, CardBody, CardHeader } from '../components/Card'

export default function Dashboard() {
	const { user } = useAuth()
	return (
		<Page>
			<Navbar />
			<div className="container">
				<h2 className="text-zinc-100" style={{ margin: '24px 0' }}>Welcome{user ? `, ${user.username}` : ''}</h2>
				<div className="grid" style={{ gap: 16, gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))' }}>
					<Card>
						<CardHeader><strong>Chat</strong></CardHeader>
						<CardBody>
							<p className="text-zinc-300">Ask crypto questions grounded in your knowledge base.</p>
							<p style={{ marginTop: 12 }}><Link to="/chat">Open Chat →</Link></p>
						</CardBody>
					</Card>
					<Card>
						<CardHeader><strong>Predict</strong></CardHeader>
						<CardBody>
							<p className="text-zinc-300">Run LSTM price predictions for supported coins.</p>
							<p style={{ marginTop: 12 }}><Link to="/predict">Open Predict →</Link></p>
						</CardBody>
					</Card>
					<Card>
						<CardHeader><strong>Sentiment</strong></CardHeader>
						<CardBody>
							<p className="text-zinc-300">Analyze sentiment of text or news snippets.</p>
							<p style={{ marginTop: 12 }}><Link to="/sentiment">Open Sentiment →</Link></p>
						</CardBody>
					</Card>
				</div>
			</div>
		</Page>
	)
}


