"use client";
import Link from "next/link";
import Image from "next/image";
import { useEffect, useState } from "react";
import { usePathname } from "next/navigation"; // Import to track active page
import { Menu, X } from "lucide-react"; // Import icons for mobile menu

export default function Navbar() {
  const [signedIn, setSignedIn] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const pathname = usePathname(); // Get current path

  // This effect checks for the auth token
  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("coinsense_token") : null;
    setSignedIn(!!token);
  }, [pathname]); // Re-check on route change

  // Handle logout
  const handleLogout = () => {
    localStorage.removeItem("coinsense_token");
    setSignedIn(false);
    setIsMobileMenuOpen(false);
    window.location.href = "/"; // Redirect to home
  };

  // Define nav links for easier reuse in mobile/desktop
  const navLinks = [
    { href: "/dashboard", label: "Dashboard" },
    { href: "/predict", label: "Predict" },
    { href: "/sentiment", label: "Sentiment" },
    { href: "/chat", label: "Chat" },
  ];

  return (
    // Added `relative` for mobile menu positioning
    <header className="relative sticky top-0 z-40 backdrop-blur supports-[backdrop-filter]:bg-background/70 border-b border-black/[.08] dark:border-white/[.12]">
      <div className="mx-auto w-full max-w-6xl px-6 py-4 flex items-center justify-between">
        
        {/* Logo */}
        <div className="flex items-center gap-2">
          <Image src="/globe.svg" alt="CoinSense logo" width={24} height={24} />
          <Link href="/" className="text-lg font-semibold tracking-tight">
            CoinSense
          </Link>
        </div>

        {/* Desktop Navigation */}
        <nav className="hidden sm:flex items-center gap-2">
          {navLinks.map((link) => {
            const isActive = pathname.startsWith(link.href);
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-zinc-800 text-white" // Active link style
                    : "text-zinc-400 hover:text-white hover:bg-zinc-800/50" // Inactive link style
                }`}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>

        {/* Auth Buttons (Desktop) */}
        <div className="hidden sm:flex items-center gap-3 text-sm font-medium">
          {signedIn ? (
            <>
              <Link
                href="/profile"
                className="rounded-full border border-black/[.08] dark:border-white/[.14] px-4 h-9 inline-flex items-center hover:bg-black/[.04] dark:hover:bg-white/[.06] transition-colors"
              >
                Profile
              </Link>
              <button
                onClick={handleLogout}
                className="rounded-full bg-foreground text-background px-5 h-9 inline-flex items-center hover:opacity-80 transition-opacity"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link
                href="/login"
                className="rounded-full border border-black/[.08] dark:border-white/[.14] px-4 h-9 inline-flex items-center hover:bg-black/[.04] dark:hover:bg-white/[.06] transition-colors"
              >
                Sign in
              </Link>
              <Link
                href="/register"
                className="rounded-full bg-foreground text-background px-5 h-9 inline-flex items-center hover:opacity-80 transition-opacity"
              >
                Create account
              </Link>
            </>
          )}
        </div>

        {/* Mobile Menu Button */}
        <div className="sm:hidden">
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="p-2 rounded-lg text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-100 transition-colors"
            aria-label="Toggle menu"
          >
            {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {isMobileMenuOpen && (
        <div
          className="sm:hidden absolute top-full left-0 right-0 bg-zinc-950 border-b border-zinc-800 shadow-xl"
          onClick={() => setIsMobileMenuOpen(false)} // Click outside to close (on the container)
        >
          <div className="flex flex-col px-4 pt-2 pb-6 space-y-2">
            {/* Mobile Nav Links */}
            {navLinks.map((link) => {
              const isActive = pathname.startsWith(link.href);
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`block px-3 py-3 rounded-lg text-base font-medium ${
                    isActive
                      ? "bg-emerald-600 text-white"
                      : "text-zinc-300 hover:bg-zinc-800 hover:text-white"
                  }`}
                >
                  {link.label}
                </Link>
              );
            })}
            
            {/* Mobile Auth Links */}
            <div className="border-t border-zinc-800 pt-4 space-y-3">
              {signedIn ? (
                <>
                  <Link
                    href="/profile"
                    className="block w-full text-left px-4 py-3 rounded-lg text-zinc-300 hover:bg-zinc-800 hover:text-white"
                  >
                    Profile
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="block w-full text-left px-4 py-3 rounded-lg text-red-400 hover:bg-red-500/20"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link
                    href="/login"
                    className="block w-full text-center px-5 py-3 rounded-lg border border-zinc-700 text-zinc-300 hover:bg-zinc-800"
                  >
                    Sign in
                  </Link>
                  <Link
                    href="/register"
                    className="block w-full text-center px-5 py-3 rounded-lg bg-emerald-600 text-white hover:opacity-80"
                  >
                    Create account
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </header>
  );
}