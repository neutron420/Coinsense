"use client";
import { useEffect, useState } from "react";

export default function SentimentPage() {
  const [text, setText] = useState("");
  const [query, setQuery] = useState("cryptocurrency");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [market, setMarket] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("coinsense_token");
    if (!token) window.location.href = "/login";
  }, []);

  async function analyzeText() {
    setError(null);
    setLoading(true);
    setResult(null);
    const token = localStorage.getItem("coinsense_token");
    try {
      const res = await fetch(process.env.NEXT_PUBLIC_API_URL + "/api/sentiment/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ text }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Analysis failed");
      setResult(data);
    } catch (e: any) {
      setError(e.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  async function analyzeMarket() {
    setError(null);
    setLoading(true);
    setMarket(null);
    const token = localStorage.getItem("coinsense_token");
    try {
      const res = await fetch(process.env.NEXT_PUBLIC_API_URL + "/api/sentiment/market-sentiment", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ query, max_articles: 10 }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Market analysis failed");
      setMarket(data);
    } catch (e: any) {
      setError(e.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen px-6 py-10">
      <div className="mx-auto w-full max-w-5xl">
        <div className="flex items-center gap-3 mb-4">
          <button onClick={() => history.back()} className="h-9 px-3 rounded-md border border-black/[.12] dark:border-white/[.16] inline-flex items-center hover:bg-black/[.04] dark:hover:bg-white/[.06]">← Back</button>
        </div>
        <h1 className="text-2xl font-semibold tracking-tight">Sentiment</h1>

        <div className="mt-6 grid md:grid-cols-2 gap-6">
          <div className="p-6 rounded-xl border border-black/[.08] dark:border-white/[.12]">
            <h2 className="font-semibold">Analyze text</h2>
            <textarea
              className="mt-3 w-full h-32 p-3 rounded-md border border-black/[.12] dark:border-white/[.16] bg-transparent"
              placeholder="Paste news or social text here..."
              value={text}
              onChange={(e) => setText(e.target.value)}
            />
            <button onClick={analyzeText} disabled={loading || !text.trim()} className="mt-3 h-11 px-5 rounded-md bg-foreground text-background font-medium disabled:opacity-60">Analyze</button>
            {result && (
              <div className="mt-4 text-sm">
                <div><span className="text-black/60 dark:text-white/60">Label:</span> <span className="font-medium">{result.label}</span></div>
                <div><span className="text-black/60 dark:text-white/60">Score:</span> {result.score.toFixed(3)} (conf {result.confidence.toFixed(3)})</div>
                <div className="text-black/60 dark:text-white/60">{new Date(result.analysis_date).toLocaleString()}</div>
              </div>
            )}
          </div>
          <div className="p-6 rounded-xl border border-black/[.08] dark:border-white/[.12]">
            <h2 className="font-semibold">Market sentiment</h2>
            <input
              className="mt-3 w-full h-11 px-3 rounded-md border border-black/[.12] dark:border-white/[.16] bg-transparent"
              placeholder="Query (e.g., bitcoin, ethereum)"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <button onClick={analyzeMarket} disabled={loading || !query.trim()} className="mt-3 h-11 px-5 rounded-md bg-foreground text-background font-medium disabled:opacity-60">Analyze market</button>
            {market && (
              <div className="mt-4 text-sm">
                <div><span className="text-black/60 dark:text-white/60">Overall:</span> <span className="font-medium">{market.overall_sentiment}</span> (conf {market.confidence.toFixed(3)})</div>
                <div className="mt-2 grid grid-cols-3 gap-2">
                  <div className="p-2 rounded border border-emerald-500/30">Pos: {market.positive_count}</div>
                  <div className="p-2 rounded border border-red-500/30">Neg: {market.negative_count}</div>
                  <div className="p-2 rounded border border-gray-500/30">Neu: {market.neutral_count}</div>
                </div>
              </div>
            )}
          </div>
        </div>
        {error && <div className="mt-4 text-sm text-red-600 dark:text-red-400">{error}</div>}
      </div>
    </div>
  );
}


