"use client";
import { useEffect, useState, useRef } from "react";
// 1. Import new icons and chart components
import { 
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid 
} from 'recharts';
import { 
  ArrowLeft, Calendar, DollarSign, TrendingUp, ChevronDown, Search // Import new icons
} from "lucide-react";

type Prediction = {
  symbol: string;
  current_price: number;
  predicted_prices: number[];
  confidence: number;
  confidence_level: string;
  prediction_date: string;
  days_ahead: number;
};

// This is the corrected list that maps symbols to your dataset names
const COIN_LIST = [
  { symbol: "BTC", name: "Bitcoin" },
  { symbol: "ETH", name: "Ethereum" },
  { symbol: "ADA", name: "Cardano" },
  { symbol: "DOT", name: "Polkadot" },
  { symbol: "LINK", name: "ChainLink" },
  { symbol: "LTC", name: "Litecoin" },
  { symbol: "XRP", name: "XRP" },
  { symbol: "DOGE", name: "Dogecoin" },
  { symbol: "SOL", name: "Solana" },
  { symbol: "BNB", name: "BinanceCoin" },
  { symbol: "USDT", name: "Tether" },
  { symbol: "USDC", name: "USDCoin" },
  { symbol: "WBTC", name: "WrappedBitcoin" },
  { symbol: "UNI", name: "Uniswap" },
  { symbol: "AAVE", name: "Aave" },
  { symbol: "ATOM", name: "Cosmos" },
  { symbol: "CRO", name: "CryptocomCoin" },
  { symbol: "EOS", name: "EOS" },
  { symbol: "IOTA", name: "Iota" },
  { symbol: "XMR", name: "Monero" },
  { symbol: "NEM", name: "NEM" },
  { symbol: "XLM", name: "Stellar" },
  { symbol: "TRX", name: "Tron" },
];

export default function PredictPage() {
  const [selectedCoinName, setSelectedCoinName] = useState("Bitcoin");
  const [days, setDays] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pred, setPred] = useState<Prediction | null>(null);
  const [chartData, setChartData] = useState<any[]>([]);

  // --- States for new custom dropdown ---
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const dropdownRef = useRef<HTMLDivElement | null>(null);

  // Get the symbol for the selected name
  const selectedCoinSymbol = COIN_LIST.find(c => c.name === selectedCoinName)?.symbol || "BTC";

  // Filtered list for the dropdown
  const filteredCoins = COIN_LIST.filter(
    (coin) =>
      coin.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      coin.symbol.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [dropdownRef]);


  useEffect(() => {
    const token = localStorage.getItem("coinsense_token");
    if (!token) window.location.href = "/login";
  }, []);

  async function runPrediction() {
    setError(null);
    setLoading(true);
    setPred(null);
    setChartData([]); 
    const token = localStorage.getItem("coinsense_token");

    try {
      const res = await fetch(process.env.NEXT_PUBLIC_API_URL + "/api/predict/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ symbol: selectedCoinName, days_ahead: days }),
      });
      const data: Prediction = await res.json();
      if (!res.ok) throw new Error((data as any).detail || "Prediction failed");
      
      setPred(data);

      const newChartData = data.predicted_prices.map((price, index) => ({
        day: `Day ${index + 1}`,
        price: price,
      }));
      
      setChartData([
        { day: 'Current', price: data.current_price },
        ...newChartData
      ]);

    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  const lastPredictedPrice = pred ? pred.predicted_prices[pred.predicted_prices.length - 1] : 0;

  return (
    <div className="min-h-screen bg-black text-gray-200 px-6 py-10">
      <div className="mx-auto w-full max-w-4xl">
        
        <div className="flex items-center gap-3 mb-6">
          <button 
            onClick={() => history.back()} 
            className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back</span>
          </button>
        </div>
        <h1 className="text-4xl font-bold tracking-tight text-white mb-2">Price Prediction</h1>
        <p className="text-gray-400 mb-8">Select a coin and a time frame to forecast its price using our LSTM model.</p>

        {/* Control Panel */}
        <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl flex flex-col sm:flex-row items-center gap-4">
          
          {/* --- NEW CUSTOM DROPDOWN --- */}
          <div className="w-full sm:w-1/3">
            <label className="text-sm font-medium text-gray-400 mb-2 block">Cryptocurrency</label>
            <div className="relative" ref={dropdownRef}>
              <button
                onClick={() => setDropdownOpen(!dropdownOpen)}
                className="w-full h-12 pl-10 pr-10 flex items-center justify-between rounded-lg border border-zinc-700 bg-zinc-800 text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <span className="truncate">{selectedCoinSymbol} - {selectedCoinName}</span>
                <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${dropdownOpen ? 'rotate-180' : ''}`} />
              </button>

              {dropdownOpen && (
                <div className="absolute z-10 top-full mt-2 w-full bg-zinc-800 border border-zinc-700 rounded-lg shadow-lg max-h-60 flex flex-col">
                  <div className="p-2">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                      <input
                        type="text"
                        placeholder="Search coin..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full h-9 pl-9 pr-3 rounded border border-zinc-700 bg-zinc-900 text-white text-sm focus:outline-none"
                      />
                    </div>
                  </div>
                  <div className="overflow-y-auto flex-1">
                    {filteredCoins.length > 0 ? (
                      filteredCoins.map((coin) => (
                        <button
                          key={coin.name}
                          onClick={() => {
                            setSelectedCoinName(coin.name);
                            setDropdownOpen(false);
                            setSearchTerm("");
                          }}
                          className="w-full text-left px-3 py-2.5 text-sm text-gray-200 hover:bg-emerald-500 hover:text-white flex items-center gap-2"
                        >
                          <span className="font-bold w-12">{coin.symbol}</span>
                          <span className="text-gray-400">{coin.name}</span>
                        </button>
                      ))
                    ) : (
                      <div className="px-3 py-2.5 text-sm text-gray-500 text-center">
                        No results
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
          {/* --- END CUSTOM DROPDOWN --- */}

          <div className="w-full sm:w-1/3">
            <label className="text-sm font-medium text-gray-400 mb-2 block">Days Ahead</label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
              <input 
                type="number" 
                min={1} 
                max={7} 
                value={days} 
                onChange={(e) => {
                  const val = parseInt(e.target.value);
                  if (e.target.value === "") {
                      setDays(1);
                  } else if (val >= 1 && val <= 7) {
                      setDays(val);
                  }
                }} 
                className="w-full h-12 pl-10 pr-4 rounded-lg border border-zinc-700 bg-zinc-800 text-white focus:outline-none focus:ring-2 focus:ring-emerald-500" 
              />
            </div>
          </div>

          <div className="w-full sm:w-1/3 sm:mt-auto">
             <button 
               onClick={runPrediction} 
               disabled={loading} 
               className="w-full h-12 rounded-lg bg-emerald-500 text-white font-medium disabled:opacity-50 flex items-center justify-center gap-2 transition-colors hover:bg-emerald-400"
             >
               {loading ? "Predicting..." : <><TrendingUp className="w-5 h-5" /><span>Predict</span></>}
             </button>
          </div>
        </div>

        {error && <div className="mt-4 p-4 rounded-lg bg-red-900/50 border border-red-700 text-red-300">{error}</div>}

        {/* --- Results Card --- */}
        {pred && (
          <div className="mt-8 p-6 bg-black border border-zinc-800 rounded-xl">
            
            <h2 className="text-2xl font-semibold mb-4 text-white">
              {COIN_LIST.find(c => c.name === pred.symbol)?.symbol} Forecast
            </h2>
            
            <div className="h-80 w-full mb-8">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 5, right: 20, left: -20, bottom: 5 }}>
                  <CartesianGrid stroke="#888888" strokeDasharray="3 3" strokeOpacity={0.2} />
                  <XAxis dataKey="day" stroke="#a0a0a0" />
                  <YAxis 
                    domain={['dataMin - 100', 'dataMax + 100']} 
                    stroke="#a0a0a0" 
                    allowDataOverflow={true}
                    tickFormatter={(val) => `$${Math.round(val)}`}
                  />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#18181b', border: '1px solid #3f3f46', borderRadius: '8px' }}
                    labelStyle={{ color: 'white' }}
                    formatter={(value: number) => [value.toFixed(2), 'Price']}
                  />
                  <Line type="monotone" dataKey="price" stroke="#22c55e" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 8 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="text-center mb-8">
              <div className="text-lg text-gray-400">Predicted Price ({pred.days_ahead}d)</div>
              <div className="text-5xl font-bold text-emerald-400 mt-1">
                ${lastPredictedPrice.toFixed(2)}
              </div>
            </div>

            <div className="max-w-md mx-auto space-y-3">
              <div className="flex justify-between items-center p-3 bg-zinc-900 rounded-lg">
                <span className="text-gray-400">Current Price</span>
                <span className="font-medium text-white">${pred.current_price.toFixed(2)}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-zinc-900 rounded-lg">
                <span className="text-gray-400">Symbol</span>
                <span className="font-medium text-white">{COIN_LIST.find(c => c.name === pred.symbol)?.symbol || pred.symbol}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-zinc-900 rounded-lg">
                <span className="text-gray-400">Prediction Date</span>
                <span className="font-medium text-white">{new Date(pred.prediction_date).toLocaleString()}</span>
              </div>
            </div>

            <div className="mt-8">
              <div className="text-sm text-gray-400 mb-1">Confidence ({pred.confidence_level})</div>
              <div className="h-3 w-full rounded-full bg-zinc-800 overflow-hidden">
                <div 
                  className="h-3 rounded-full bg-emerald-500" 
                  style={{ width: `${Math.min(100, Math.max(0, pred.confidence * 100))}%` }} 
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}