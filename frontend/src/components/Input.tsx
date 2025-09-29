import type { InputHTMLAttributes } from 'react'
import { forwardRef } from 'react'

type Props = InputHTMLAttributes<HTMLInputElement> & { label?: string }

export default forwardRef<HTMLInputElement, Props>(function Input({ label, className = '', ...props }, ref) {
	return (
		<label className="grid gap-1 text-sm">
			{label && <span className="text-zinc-300">{label}</span>}
			<input ref={ref} className={`rounded-md bg-zinc-900/60 border border-zinc-800 px-3 py-2 text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-emerald-600 ${className}`} {...props} />
		</label>
	)
})


