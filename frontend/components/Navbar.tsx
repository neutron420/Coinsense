"use client";
import Link from "next/link";
import Image from "next/image";
import { useEffect, useState } from "react";

export default function Navbar() {
  const [signedIn, setSignedIn] = useState(false);
  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("coinsense_token") : null;
    setSignedIn(!!token);
  }, []);

  return (
    <header className="sticky top-0 z-40 backdrop-blur supports-[backdrop-filter]:bg-background/70 border-b border-black/[.08] dark:border-white/[.12]">
      <div className="mx-auto w-full max-w-6xl px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Image src="/globe.svg" alt="CoinSense logo" width={24} height={24} />
          <Link href="/" className="text-lg font-semibold tracking-tight">CoinSense</Link>
        </div>
        <nav className="hidden sm:flex items-center gap-6 text-sm">
          <Link href="/dashboard" className="hover:underline underline-offset-4">Dashboard</Link>
          <Link href="/predict" className="hover:underline underline-offset-4">Predict</Link>
          <Link href="/sentiment" className="hover:underline underline-offset-4">Sentiment</Link>
          <Link href="/chat" className="hover:underline underline-offset-4">Chat</Link>
        </nav>
        <div className="flex items-center gap-3">
          {signedIn ? (
            <>
              <Link href="/profile" className="rounded-full border border-black/[.08] dark:border-white/[.14] px-4 h-9 inline-flex items-center hover:bg-black/[.04] dark:hover:bg-white/[.06]">Profile</Link>
              <button
                onClick={() => { localStorage.removeItem("coinsense_token"); window.location.href = "/"; }}
                className="rounded-full bg-foreground text-background px-5 h-9 inline-flex items-center font-medium hover:opacity-90"
              >Logout</button>
            </>
          ) : (
            <>
              <Link href="/login" className="rounded-full border border-black/[.08] dark:border-white/[.14] px-4 h-9 inline-flex items-center hover:bg-black/[.04] dark:hover:bg-white/[.06]">Sign in</Link>
              <Link href="/register" className="rounded-full bg-foreground text-background px-5 h-9 inline-flex items-center font-medium hover:opacity-90">Create account</Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}


