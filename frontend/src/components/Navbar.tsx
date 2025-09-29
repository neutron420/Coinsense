import { Link } from 'react-router-dom'
import Button from './Button'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
	const { user, logout } = useAuth()
	return (
		<nav className="sticky top-0 z-10 w-full border-b border-zinc-800 bg-zinc-950/80 backdrop-blur">
			<div className="mx-auto max-w-6xl px-4 py-3 flex items-center gap-3 text-sm">
				<Link to="/" className="font-semibold text-zinc-200">CoinSense</Link>
				<div className="flex-1" />
				<Link to="/dashboard" className="text-zinc-300 hover:text-white">Dashboard</Link>
				<Link to="/chat" className="text-zinc-300 hover:text-white">Chat</Link>
				<Link to="/predict" className="text-zinc-300 hover:text-white">Predict</Link>
				<Link to="/sentiment" className="text-zinc-300 hover:text-white">Sentiment</Link>
				<div className="flex-1" />
				{user ? (
					<Button variant="secondary" onClick={logout}>Logout</Button>
				) : (
					<>
						<Link to="/login" className="text-zinc-300 hover:text-white">Login</Link>
						<Link to="/register" className="text-zinc-300 hover:text-white">Register</Link>
					</>
				)}
			</div>
		</nav>
	)
}


