"use client";
import { useState } from "react";
import Link from "next/link";

export default function RegisterPage() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setLoading(true);
    try {
      const res = await fetch(process.env.NEXT_PUBLIC_API_URL + "/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Registration failed");
      }
      setSuccess("Account created. You can now sign in.");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-6 py-12">
      <div className="w-full max-w-md">
        <h1 className="text-2xl font-semibold tracking-tight">Create your CoinSense account</h1>
        <p className="text-sm text-black/70 dark:text-white/70 mt-1">
          Already have an account? <Link href="/login" className="underline underline-offset-4">Sign in</Link>
        </p>
        <form onSubmit={handleSubmit} className="mt-6 grid gap-4">
          <div className="grid gap-2">
            <label className="text-sm font-medium">Username</label>
            <input
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="h-11 px-3 rounded-md border border-black/[.12] dark:border-white/[.16] bg-transparent"
              placeholder="yourname"
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium">Email</label>
            <input
              required
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="h-11 px-3 rounded-md border border-black/[.12] dark:border-white/[.16] bg-transparent"
              placeholder="you@example.com"
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium">Password</label>
            <input
              required
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="h-11 px-3 rounded-md border border-black/[.12] dark:border-white/[.16] bg-transparent"
              placeholder="••••••••"
            />
          </div>
          {error && <div className="text-sm text-red-600 dark:text-red-400">{error}</div>}
          {success && <div className="text-sm text-emerald-700 dark:text-emerald-400">{success}</div>}
          <button
            type="submit"
            disabled={loading}
            className="h-11 rounded-md bg-foreground text-background font-medium hover:opacity-90 disabled:opacity-60"
          >
            {loading ? "Creating..." : "Create account"}
          </button>
        </form>
      </div>
    </div>
  );
}


