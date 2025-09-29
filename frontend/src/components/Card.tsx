import type { HTMLAttributes } from 'react'

export function Card({ className = '', ...props }: HTMLAttributes<HTMLDivElement>) {
	return <div className={`rounded-lg border border-zinc-800 bg-zinc-900/70 ${className}`} {...props} />
}

export function CardHeader({ className = '', ...props }: HTMLAttributes<HTMLDivElement>) {
	return <div className={`px-5 pt-4 ${className}`} {...props} />
}

export function CardBody({ className = '', ...props }: HTMLAttributes<HTMLDivElement>) {
	return <div className={`px-5 pb-5 ${className}`} {...props} />
}


