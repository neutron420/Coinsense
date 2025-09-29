import type { ButtonHTMLAttributes } from 'react'

type Props = ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'secondary' | 'ghost' }

export default function Button({ variant = 'primary', className = '', ...props }: Props) {
	const base = 'inline-flex items-center justify-center px-4 py-2 rounded-md transition-colors disabled:opacity-60 disabled:cursor-not-allowed'
	const styles = {
		primary: 'bg-emerald-600 hover:bg-emerald-500 text-white',
		secondary: 'bg-zinc-700 hover:bg-zinc-600 text-white',
		ghost: 'bg-transparent hover:bg-zinc-800 text-zinc-200 border border-zinc-700',
	}[variant]
	return <button className={`${base} ${styles} ${className}`} {...props} />
}


