"use client";
import { useEffect, useState } from "react";
import Link from "next/link";

export default function DashboardPage() {
  const [signedIn, setSignedIn] = useState(false);
  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("coinsense_token") : null;
    if (!token) {
      window.location.href = "/login";
    } else {
      setSignedIn(true);
    }
  }, []);

  return (
    <div className="min-h-screen px-6 py-10">
      <div className="mx-auto w-full max-w-6xl">
        <div className="flex items-center gap-3 mb-4">
          <Link href="/" className="h-9 px-3 rounded-md border border-black/[.12] dark:border-white/[.16] inline-flex items-center hover:bg-black/[.04] dark:hover:bg-white/[.06]">← Back</Link>
        </div>
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-sm text-black/70 dark:text-white/70 mt-2">Welcome back. Choose a tool to get insights.</p>
        <div className="mt-6 grid md:grid-cols-2 xl:grid-cols-4 gap-6">
          <Link href="/chat" className="p-6 rounded-xl border border-black/[.08] dark:border-white/[.12] hover:bg-black/[.03] dark:hover:bg-white/[.04] transition">
            <div className="text-2xl">💬</div>
            <h2 className="font-semibold mt-2">AI Chat</h2>
            <p className="text-sm text-black/70 dark:text-white/70 mt-1">Chat with your crypto assistant.</p>
          </Link>
          <Link href="/predict" className="p-6 rounded-xl border border-black/[.08] dark:border-white/[.12] hover:bg-black/[.03] dark:hover:bg-white/[.04] transition">
            <div className="text-2xl">📈</div>
            <h2 className="font-semibold mt-2">Price Prediction</h2>
            <p className="text-sm text-black/70 dark:text-white/70 mt-1">Forecast next 1-7 days with LSTM.</p>
          </Link>
          <Link href="/sentiment" className="p-6 rounded-xl border border-black/[.08] dark:border-white/[.12] hover:bg-black/[.03] dark:hover:bg-white/[.04] transition">
            <div className="text-2xl">📰</div>
            <h2 className="font-semibold mt-2">Sentiment</h2>
            <p className="text-sm text-black/70 dark:text-white/70 mt-1">Analyze text and market mood.</p>
          </Link>
          
        </div>
        <div className="mt-8 grid sm:grid-cols-2 gap-6">
          <div className="p-6 rounded-xl border border-black/[.08] dark:border-white/[.12]">
            <h2 className="font-semibold">Forecasts</h2>
            <div className="mt-3 h-40 rounded-lg bg-gradient-to-tr from-emerald-400/20 to-emerald-600/20 border border-emerald-500/30 animate-pulse" />
          </div>
          <div className="p-6 rounded-xl border border-black/[.08] dark:border-white/[.12]">
            <h2 className="font-semibold">Sentiment</h2>
            <div className="mt-3 h-40 rounded-lg bg-gradient-to-tr from-indigo-400/20 to-indigo-600/20 border border-indigo-500/30 animate-pulse" />
          </div>
        </div>
      </div>
    </div>
  );
}


