"use client";
import { useEffect, useState } from "react";

type Prediction = {
  symbol: string;
  current_price: number;
  predicted_price: number;
  confidence: number;
  confidence_level: string;
  prediction_date: string;
  days_ahead: number;
};

const SYMBOLS = [
  "BTC","ETH","ADA","DOT","LINK","LTC","XRP","DOGE","SOL","MATIC","BNB","USDT","USDC","WBTC","UNI","AAVE","ATOM","CRO","EOS","IOTA","XMR","NEM","XLM","TRX"
];

export default function PredictPage() {
  const [symbol, setSymbol] = useState("BTC");
  const [days, setDays] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pred, setPred] = useState<Prediction | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("coinsense_token");
    if (!token) window.location.href = "/login";
  }, []);

  async function runPrediction() {
    setError(null);
    setLoading(true);
    setPred(null);
    const token = localStorage.getItem("coinsense_token");
    try {
      const res = await fetch(process.env.NEXT_PUBLIC_API_URL + "/api/predict/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ symbol, days_ahead: days }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Prediction failed");
      setPred(data);
    } catch (e: any) {
      setError(e.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen px-6 py-10">
      <div className="mx-auto w-full max-w-4xl">
        <div className="flex items-center gap-3 mb-4">
          <button onClick={() => history.back()} className="h-9 px-3 rounded-md border border-black/[.12] dark:border-white/[.16] inline-flex items-center hover:bg-black/[.04] dark:hover:bg-white/[.06]">← Back</button>
        </div>
        <h1 className="text-2xl font-semibold tracking-tight">Price Prediction</h1>
        <div className="mt-6 grid sm:grid-cols-3 gap-4">
          <div className="grid gap-2">
            <label className="text-sm">Symbol</label>
            <select value={symbol} onChange={(e) => setSymbol(e.target.value)} className="h-11 px-3 rounded-md border border-black/[.12] dark:border-white/[.16] bg-transparent">
              {SYMBOLS.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
          <div className="grid gap-2">
            <label className="text-sm">Days ahead (1-7)</label>
            <input type="number" min={1} max={7} value={days} onChange={(e) => setDays(parseInt(e.target.value) || 1)} className="h-11 px-3 rounded-md border border-black/[.12] dark:border-white/[.16] bg-transparent" />
          </div>
          <div className="flex items-end">
            <button onClick={runPrediction} disabled={loading} className="w-full h-11 rounded-md bg-foreground text-background font-medium disabled:opacity-60">{loading ? "Predicting..." : "Predict"}</button>
          </div>
        </div>

        {error && <div className="mt-4 text-sm text-red-600 dark:text-red-400">{error}</div>}

        {pred && (
          <div className="mt-6 p-6 rounded-xl border border-black/[.08] dark:border-white/[.12]">
            <div className="grid sm:grid-cols-2 gap-4">
              <div>
                <div className="text-sm text-black/60 dark:text-white/60">Symbol</div>
                <div className="font-medium">{pred.symbol}</div>
              </div>
              <div>
                <div className="text-sm text-black/60 dark:text-white/60">Prediction date</div>
                <div className="font-medium">{new Date(pred.prediction_date).toLocaleString()}</div>
              </div>
              <div>
                <div className="text-sm text-black/60 dark:text-white/60">Current price</div>
                <div className="font-medium">{pred.current_price.toFixed(2)}</div>
              </div>
              <div>
                <div className="text-sm text-black/60 dark:text-white/60">Predicted price ({pred.days_ahead}d)</div>
                <div className="font-medium">{pred.predicted_price.toFixed(2)}</div>
              </div>
            </div>
            <div className="mt-6">
              <div className="text-sm text-black/60 dark:text-white/60">Confidence ({pred.confidence_level})</div>
              <div className="h-3 mt-2 w-full rounded-full bg-black/10 dark:bg-white/10">
                <div className="h-3 rounded-full bg-emerald-500" style={{ width: `${Math.min(100, Math.max(0, pred.confidence * 100))}%` }} />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}


