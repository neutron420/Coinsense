import type { HTMLAttributes } from 'react'

export default function Page({ className = '', ...props }: HTMLAttributes<HTMLDivElement>) {
	return (
		<div className={`min-h-screen bg-zinc-950 text-zinc-100`}>
			<div className={`mx-auto max-w-6xl px-4 ${className}`} {...props} />
		</div>
	)
}


