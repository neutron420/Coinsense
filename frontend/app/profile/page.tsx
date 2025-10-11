"use client";
import { useEffect, useState } from "react";
import Link from "next/link";

type User = {
  id: number;
  username: string;
  email: string;
  created_at?: string;
};

export default function ProfilePage() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("coinsense_token") : null;
    if (!token) {
      window.location.href = "/login";
      return;
    }
    async function load() {
      try {
        const res = await fetch(process.env.NEXT_PUBLIC_API_URL + "/api/auth/me", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.detail || "Failed to load profile");
        }
        setUser(data);
      } catch (err: any) {
        setError(err.message || "Something went wrong");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  async function handleLogout() {
    localStorage.removeItem("coinsense_token");
    window.location.href = "/";
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="h-10 w-10 rounded-full border-2 border-black/20 dark:border-white/20 border-t-transparent animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center px-6">
        <div className="max-w-md w-full text-center">
          <h1 className="text-xl font-semibold">Could not load profile</h1>
          <p className="text-sm text-black/70 dark:text-white/70 mt-2">{error}</p>
          <div className="mt-6 flex items-center justify-center gap-3">
            <Link href="/login" className="rounded-full bg-foreground text-background px-5 h-10 inline-flex items-center">Sign in</Link>
            <Link href="/" className="rounded-full border border-black/[.08] dark:border-white/[.14] px-5 h-10 inline-flex items-center">Go home</Link>
          </div>
        </div>
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="min-h-screen px-6 py-10">
      <div className="mx-auto w-full max-w-3xl">
        <div className="flex items-center gap-3 mb-4">
          <button onClick={() => history.back()} className="h-9 px-3 rounded-md border border-black/[.12] dark:border-white/[.16] inline-flex items-center hover:bg-black/[.04] dark:hover:bg-white/[.06]">← Back</button>
        </div>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">Your profile</h1>
            <p className="text-sm text-black/70 dark:text-white/70">Signed in as <span className="font-medium">{user.username}</span></p>
          </div>
          <button onClick={handleLogout} className="rounded-full border border-black/[.08] dark:border-white/[.14] px-4 h-9 inline-flex items-center hover:bg-black/[.04] dark:hover:bg-white/[.06]">Logout</button>
        </div>

        <div className="mt-8 grid gap-4">
          <div className="p-5 rounded-lg border border-black/[.08] dark:border-white/[.12]">
            <div className="text-sm text-black/60 dark:text-white/60">Username</div>
            <div className="mt-1 font-medium">{user.username}</div>
          </div>
          <div className="p-5 rounded-lg border border-black/[.08] dark:border-white/[.12]">
            <div className="text-sm text-black/60 dark:text-white/60">Email</div>
            <div className="mt-1 font-medium">{user.email}</div>
          </div>
          {user.created_at && (
            <div className="p-5 rounded-lg border border-black/[.08] dark:border-white/[.12]">
              <div className="text-sm text-black/60 dark:text-white/60">Joined</div>
              <div className="mt-1 font-medium">{new Date(user.created_at).toLocaleString()}</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}


