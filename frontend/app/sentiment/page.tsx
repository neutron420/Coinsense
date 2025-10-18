"use client";
import { useEffect, useState, useRef } from "react";
import { ArrowLeft, CheckCircle, ChevronDown, MinusCircle, Search, ThumbsDown, ThumbsUp, XCircle, Link as LinkIcon, LucideIcon } from "lucide-react";

// Types
type SentimentResult = {
  overall_sentiment: string;
  confidence: number;
  positive_count: number;
  negative_count: number;
  neutral_count: number;
  total_articles: number;
  sentiment_score: number; // The score between -1 and 1
  analysis_date: string;
  articles_analyzed: AnalyzedArticle[]; // Updated this type
  error?: string;
};

type AnalyzedArticle = {
  title: string;
  sentiment: string;
  confidence: number;
  source: string;
  url?: string; // Add optional URL for clickable links
};

type CustomAnalysisResult = {
  label: string;
  score: number; // FinBERT often returns 'score', map confidence if needed
  confidence?: number; // Add optional confidence if backend sends it
  text?: string; // Text analyzed
};

// --- List of Coins for Dropdown ---
// Make sure these names match what your backend expects for crypto-sentiment/{name}
const COIN_LIST = [
    { symbol: "MARKET", name: "Market (Overall)" }, // Option for overall market
    { symbol: "BTC", name: "Bitcoin" },
    { symbol: "ETH", name: "Ethereum" },
    { symbol: "ADA", name: "Cardano" },
    { symbol: "SOL", name: "Solana" },
    { symbol: "XRP", name: "XRP" },
    { symbol: "DOGE", name: "Dogecoin" },
    { symbol: "DOT", name: "Polkadot" },
    { symbol: "LINK", name: "ChainLink" },
    { symbol: "LTC", name: "Litecoin" },
    { symbol: "BNB", name: "BinanceCoin" },
    // Add other coins supported by your /crypto-sentiment/{name} endpoint
];


export default function SentimentPage() {
  const [activeTab, setActiveTab] = useState<"market" | "custom">("market");
  const [marketSentiment, setMarketSentiment] = useState<SentimentResult | null>(null);
  const [customText, setCustomText] = useState("");
  const [customResult, setCustomResult] = useState<CustomAnalysisResult | null>(null);
  const [loadingMarket, setLoadingMarket] = useState(false);
  const [loadingCustom, setLoadingCustom] = useState(false);
  const [errorMarket, setErrorMarket] = useState<string | null>(null);
  const [errorCustom, setErrorCustom] = useState<string | null>(null);

  // --- State for Coin Dropdown ---
  const [selectedCoinName, setSelectedCoinName] = useState("Market (Overall)"); // Default to market
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const dropdownRef = useRef<HTMLDivElement | null>(null);

  // Helper to find symbol based on selected name
  const getSelectedCoinSymbol = () => COIN_LIST.find(c => c.name === selectedCoinName)?.symbol || "MARKET";

  // Filtered coins for dropdown
  const filteredCoins = COIN_LIST.filter(
    (coin) =>
      coin.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      coin.symbol.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Close dropdown on outside click
   useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // --- Fetch Market Sentiment ---
  const fetchMarketSentiment = async (coinNameToFetch: string) => {
    setLoadingMarket(true);
    setErrorMarket(null);
    setMarketSentiment(null); // Clear previous results
    const token = localStorage.getItem("coinsense_token");
    if (!token) {
        console.error("No token found, redirecting to login.");
        window.location.href = "/login"; // Redirect if no token
        return;
    }

    let url = process.env.NEXT_PUBLIC_API_URL + "/api/sentiment/";
    let method = "POST"; // Default method
    let bodyPayload: BodyInit | null | undefined = undefined;
    const headers: HeadersInit = {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
    };

    if (coinNameToFetch === "Market (Overall)") {
        url += "market-sentiment";
        bodyPayload = JSON.stringify({ query: "cryptocurrency", max_articles: 20 });
        method = "POST"; // Market sentiment uses POST
    } else {
        const coin = COIN_LIST.find(c => c.name === coinNameToFetch);
        if (coin && coin.symbol !== "MARKET") {
             url += `crypto-sentiment/${encodeURIComponent(coin.name)}`;
             method = "GET"; // Specific crypto sentiment uses GET
             delete headers['Content-Type']; // Remove header for GET
             bodyPayload = undefined; // No body for GET
        } else {
             setErrorMarket("Invalid coin selected for fetching sentiment.");
             setLoadingMarket(false);
             return;
        }
    }

    console.log(`Fetching sentiment from: ${url} Method: ${method} for: ${coinNameToFetch}`);

    try {
      const res = await fetch(url, {
        method: method,
        headers: headers,
        body: bodyPayload
      });

       if (res.status === 401) {
          console.error("API returned 401 Unauthorized.");
          localStorage.removeItem("coinsense_token");
          window.location.href = "/login";
          throw new Error("Unauthorized");
        }

      if (res.status === 405) { // Handle method not allowed specifically
          console.error(`API Error: Method ${method} not allowed for ${url}`);
          throw new Error(`Method ${method} not allowed. Backend configuration error?`);
      }

      if (!res.ok) {
           // Try to parse error JSON, fallback to status text
           let errorDetail = `Request failed with status ${res.status}`;
           try {
               const errorData = await res.json();
               errorDetail = errorData.detail || errorDetail;
           } catch (parseError) {
                // Keep the original status text if JSON parsing fails
           }
           console.error("API Error Response:", errorDetail);
           throw new Error(errorDetail);
      }

      const data: SentimentResult = await res.json();

        // Ensure articles_analyzed is an array before mapping
        const articlesWithLinks = Array.isArray(data.articles_analyzed)
            ? data.articles_analyzed.map(article => ({
                  ...article,
                  url: article.url || undefined // Ensure URL is optional or undefined
              }))
            : []; // Default to empty array if not present or not an array

      setMarketSentiment({...data, articles_analyzed: articlesWithLinks});

    } catch (e: any) {
        if (e.message === "Unauthorized") return; // Already handled redirect
        console.error("Fetch Market Sentiment Error:", e);
        setErrorMarket(e.message || "Something went wrong while fetching sentiment.");
    } finally {
      setLoadingMarket(false);
    }
  };

  // Effect to fetch sentiment on initial load and when selection changes
  useEffect(() => {
    // Ensure this runs only client-side where localStorage is available
    if (typeof window !== 'undefined') {
        const token = localStorage.getItem("coinsense_token");
        if (token) {
             console.log(`Selected coin changed to: ${selectedCoinName}. Fetching sentiment...`)
             fetchMarketSentiment(selectedCoinName);
        } else if (!window.location.pathname.startsWith('/login')) { // Prevent redirect loop if already on login
            console.log("No token found on load/change, redirecting.");
            window.location.href = "/login";
        }
    }
  }, [selectedCoinName]); // Dependency array includes selectedCoinName


  // --- Analyze Custom Text ---
  const analyzeCustomText = async () => {
    const textToAnalyze = customText.trim();
    if (!textToAnalyze) return;
    setLoadingCustom(true);
    setErrorCustom(null);
    setCustomResult(null);
    const token = localStorage.getItem("coinsense_token");
     if (!token) {
         console.error("No token found, redirecting to login.");
        window.location.href = "/login";
        return;
    }

    try {
      const res = await fetch(process.env.NEXT_PUBLIC_API_URL + "/api/sentiment/analyze", {
        method: "POST", // This endpoint uses POST
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ text: textToAnalyze }), // Backend expects {"text": "..."}
      });

       if (res.status === 401) {
            console.error("API returned 401 Unauthorized.");
            localStorage.removeItem("coinsense_token");
            window.location.href = "/login";
            throw new Error("Unauthorized");
        }

        if (!res.ok) {
             let errorDetail = `Analysis failed (${res.status})`;
             try {
                const errorData = await res.json();
                errorDetail = errorData.detail || errorDetail;
             } catch (parseError) {}
             console.error("API Error Response:", errorDetail);
             throw new Error(errorDetail);
        }

      const rawData = await res.json();
      // Adjust based on the actual response structure of /api/sentiment/analyze
      const resultData: CustomAnalysisResult = {
          label: rawData.label || rawData.sentiment || 'neutral', // Adapt to backend field names
          score: rawData.score || 0,
          confidence: rawData.confidence || rawData.score || 0,
          text: textToAnalyze
      };
      setCustomResult(resultData);

    } catch (e: any) {
        if (e.message === "Unauthorized") return;
        console.error("Analyze Custom Text Error:", e);
        setErrorCustom(e.message || "Something went wrong during analysis.");
    } finally {
      setLoadingCustom(false);
    }
  };

  // --- Helper to get sentiment style ---
  const getSentimentStyle = (sentiment: string | undefined): { color: string; Icon: LucideIcon; bgColor: string; name: string } => {
    switch (sentiment?.toLowerCase()) {
      case 'positive': return { color: 'text-emerald-400', Icon: ThumbsUp, bgColor: 'bg-emerald-900/50', name: 'Positive' };
      case 'negative': return { color: 'text-red-400', Icon: ThumbsDown, bgColor: 'bg-red-900/50', name: 'Negative' };
      default: return { color: 'text-gray-400', Icon: MinusCircle, bgColor: 'bg-zinc-800/50', name: 'Neutral' };
    }
  };

    // --- Helper for Sentiment Score Gauge ---
    const getScoreGaugeStyle = (score: number | undefined) => {
        if (score === undefined || score === null || isNaN(score)) { // Added NaN check
            return { width: '50%', colorClass: 'bg-gray-600', positionPercent: 50 };
        }
        const positionPercent = Math.max(0, Math.min(100, (score + 1) / 2 * 100));
        let colorClass = 'bg-gray-500';
        if (score > 0.15) colorClass = 'bg-emerald-500'; // Increased positive threshold slightly
        else if (score < -0.15) colorClass = 'bg-red-500'; // Increased negative threshold slightly
        return { width: `${positionPercent}%`, colorClass, positionPercent };
    };


  return (
    <div className="min-h-screen bg-black text-gray-200 px-4 sm:px-6 py-10">
      <div className="mx-auto w-full max-w-4xl">
        <div className="flex items-center gap-3 mb-6">
          <button
            onClick={() => history.back()}
            className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            <span className="text-sm">Back</span>
          </button>
        </div>
        <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-white mb-3">Sentiment Analysis</h1>
        <p className="text-gray-400 mb-8 text-sm sm:text-base">Analyze market mood based on news or evaluate specific text using FinBERT.</p>

        {/* Tab Buttons */}
        <div className="flex border-b border-zinc-700 mb-6">
          <button
            onClick={() => setActiveTab("market")}
            className={`px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === "market"
                ? "border-b-2 border-emerald-500 text-white"
                : "text-gray-400 hover:text-gray-200"
            }`}
          >
            Market / Coin Sentiment
          </button>
          <button
            onClick={() => setActiveTab("custom")}
            className={`px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === "custom"
                ? "border-b-2 border-emerald-500 text-white"
                : "text-gray-400 hover:text-gray-200"
            }`}
          >
            Analyze Custom Text
          </button>
        </div>

        {/* Market Sentiment Tab */}
        {activeTab === "market" && (
          <div>
             {/* Coin Selection Dropdown */}
             <div className="mb-6 max-w-xs">
                 <label className="text-xs font-medium text-gray-400 mb-1.5 block px-1">Analyze Sentiment For</label>
                 <div className="relative" ref={dropdownRef}>
                    <button
                        onClick={() => setDropdownOpen(!dropdownOpen)}
                        className="w-full h-11 pl-3 pr-10 flex items-center justify-between rounded-lg border border-zinc-700 bg-zinc-800 text-white focus:outline-none focus:ring-1 focus:ring-emerald-500 text-sm hover:bg-zinc-700 transition-colors"
                    >
                        <span className="truncate">{getSelectedCoinSymbol() === 'MARKET' ? 'Market (Overall)' : `${getSelectedCoinSymbol()} - ${selectedCoinName}`}</span>
                        <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform flex-shrink-0 ${dropdownOpen ? 'rotate-180' : ''}`} />
                    </button>
                    {dropdownOpen && (
                         <div className="absolute z-10 top-full mt-1 w-full bg-zinc-800 border border-zinc-600 rounded-lg shadow-lg max-h-60 flex flex-col overflow-hidden">
                            <div className="p-2 border-b border-zinc-600">
                                <div className="relative">
                                <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                                <input
                                    type="text"
                                    placeholder="Search coin..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    className="w-full h-8 pl-8 pr-3 rounded border border-zinc-600 bg-zinc-900 text-white text-xs focus:outline-none"
                                />
                                </div>
                            </div>
                            <div className="overflow-y-auto flex-1 text-sm py-1">
                                {filteredCoins.length > 0 ? (
                                filteredCoins.map((coin) => (
                                    <button
                                    key={coin.name}
                                    onClick={() => { setSelectedCoinName(coin.name); setDropdownOpen(false); setSearchTerm(""); }}
                                    className={`w-full text-left px-3 py-1.5 flex items-center gap-2 ${selectedCoinName === coin.name ? 'bg-emerald-600 text-white' : 'text-gray-200 hover:bg-zinc-700'}`}
                                    >
                                    <span className="font-medium w-12 flex-shrink-0">{coin.symbol}</span>
                                    <span className="text-gray-300 truncate">{coin.name}</span>
                                    </button>
                                ))
                                ) : (
                                <div className="px-3 py-2 text-xs text-gray-500 text-center">No results</div>
                                )}
                            </div>
                         </div>
                    )}
                 </div>
             </div>

            {/* Loading/Error/Results */}
            {loadingMarket && (
                <div className="text-center py-10 text-gray-400 text-sm">
                    <svg className="animate-spin h-5 w-5 text-emerald-500 mx-auto mb-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Loading {selectedCoinName} sentiment...
                </div>
            )}
            {errorMarket && <div className="p-4 rounded-lg bg-red-900/50 border border-red-700 text-red-300 text-sm">{errorMarket}</div>}

            {marketSentiment && !loadingMarket && (
              <div className="space-y-6">
                {/* Sentiment Summary Card */}
                <div className="p-5 sm:p-6 bg-zinc-950 border border-zinc-800 rounded-xl">
                    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-5">
                         <div>
                            <h2 className="text-lg sm:text-xl font-semibold text-white">
                                {selectedCoinName} Sentiment
                            </h2>
                             <p className="text-xs sm:text-sm text-gray-500 mt-1">
                                Based on {marketSentiment.total_articles} recent news articles from{" "}
                                {marketSentiment.analysis_date ? new Date(marketSentiment.analysis_date).toLocaleString() : 'N/A'}.
                            </p>
                         </div>
                        {/* Sentiment Badge */}
                        <div className={`text-base font-bold flex items-center gap-2 px-3 py-1 rounded-full text-sm ${getSentimentStyle(marketSentiment.overall_sentiment).bgColor} ${getSentimentStyle(marketSentiment.overall_sentiment).color}`}>
                           {(() => {
                                const { Icon } = getSentimentStyle(marketSentiment.overall_sentiment);
                                return Icon ? <Icon className="w-4 h-4" /> : null;
                           })()}
                           <span>{getSentimentStyle(marketSentiment.overall_sentiment).name}</span>
                        </div>
                    </div>

                    {/* Sentiment Score Gauge */}
                    <div className="mb-6">
                          <div className="flex justify-between text-[10px] sm:text-xs text-gray-500 mb-1 px-1">
                             <span>Negative</span>
                             <span>Neutral</span>
                             <span>Positive</span>
                         </div>
                         <div title={`Sentiment Score: ${marketSentiment.sentiment_score?.toFixed(3) ?? 'N/A'}`} className="h-2 w-full rounded-full bg-gradient-to-r from-red-600 via-zinc-600 to-emerald-500 relative overflow-hidden border border-zinc-700">
                            <div className="absolute top-0 bottom-0 w-px bg-white/40 left-1/2 transform -translate-x-1/2"></div>
                            <div
                                className={`absolute top-1/2 -translate-y-1/2 transform -translate-x-1/2 w-2 h-4 rounded-sm border border-white/50 shadow-lg ${getScoreGaugeStyle(marketSentiment.sentiment_score).colorClass}`}
                                style={{ left: `${getScoreGaugeStyle(marketSentiment.sentiment_score).positionPercent}%` }}
                             />
                         </div>
                         <div className="text-center text-xs text-gray-400 mt-1.5">
                             Score: {marketSentiment.sentiment_score?.toFixed(3) ?? 'N/A'}
                         </div>
                    </div>

                  {/* Article Counts */}
                  <div className="grid grid-cols-3 gap-3 sm:gap-4 text-center border-t border-zinc-800 pt-5">
                     <div>
                      <div className="text-xl sm:text-2xl font-bold text-emerald-400">{marketSentiment.positive_count}</div>
                      <div className="text-[10px] sm:text-xs text-gray-500 uppercase tracking-wider">Positive</div>
                    </div>
                    <div>
                      <div className="text-xl sm:text-2xl font-bold text-gray-400">{marketSentiment.neutral_count}</div>
                      <div className="text-[10px] sm:text-xs text-gray-500 uppercase tracking-wider">Neutral</div>
                    </div>
                    <div>
                      <div className="text-xl sm:text-2xl font-bold text-red-400">{marketSentiment.negative_count}</div>
                      <div className="text-[10px] sm:text-xs text-gray-500 uppercase tracking-wider">Negative</div>
                    </div>
                  </div>
                </div>

                {/* Analyzed Articles List */}
                <div>
                  <h3 className="text-base sm:text-lg font-semibold mb-3 text-white px-1">Analyzed News Articles</h3>
                  <div className="space-y-3">
                    {marketSentiment.articles_analyzed && marketSentiment.articles_analyzed.length > 0 ? (
                      marketSentiment.articles_analyzed.map((article, index) => {
                        // *** CORRECTED ICON RENDERING (INSIDE MAP) ***
                        const sentimentValue = article.sentiment || 'neutral';
                        // Get style info, defaulting to neutral if somehow invalid
                        const styleInfo = getSentimentStyle(sentimentValue) || getSentimentStyle('neutral');
                        const { color, Icon, bgColor } = styleInfo;
                        const SentimentIconComponent = Icon; // Assign to uppercase variable

                        const isLink = article.url && article.url !== '#';
                        const Wrapper = isLink ? 'a' : 'div';

                        // Skip rendering if essential data like title is missing
                        if (!article || typeof article.title !== 'string') {
                            console.warn("Skipping article due to missing/invalid title:", index, article);
                            return null;
                        }

                        return (
                          <Wrapper
                            key={index}
                            href={isLink ? article.url : undefined}
                            target={isLink ? "_blank" : undefined}
                            rel={isLink ? "noopener noreferrer" : undefined}
                            className={`block p-3 sm:p-4 bg-zinc-950 border border-zinc-800 rounded-lg flex items-start gap-3 transition-colors ${isLink ? 'hover:border-emerald-700 hover:bg-zinc-900 group' : ''}`}
                           >
                            {/* Sentiment Icon Div */}
                            <div className={`mt-1 p-1.5 rounded-full ${bgColor}`}>
                                {/* Render the icon safely */}
                                {SentimentIconComponent && <SentimentIconComponent className={`w-4 h-4 flex-shrink-0 ${color}`} />}
                            </div>
                            {/* Text Content Div */}
                            <div className="flex-1">
                              <div
                                className={`text-gray-100 text-sm font-medium mb-1 ${isLink ? 'group-hover:text-emerald-400' : ''}`}
                              >
                                {article.title}
                                {isLink && <LinkIcon className="w-3 h-3 inline-block ml-1 text-gray-500 group-hover:text-emerald-500 transition-colors" />}
                              </div>
                              <div className="text-xs text-gray-500 flex flex-wrap gap-x-3 gap-y-1">
                                <span>Source: {article.source || "Unknown"}</span>
                                <span className="hidden sm:inline">|</span>
                                {/* Ensure confidence is a number before formatting */}
                                <span>Confidence: {typeof article.confidence === 'number' ? (article.confidence * 100).toFixed(0) + '%' : 'N/A'}</span>
                              </div>
                            </div>
                          </Wrapper>
                        );
                      })
                    ) : (
                      <div className="p-4 bg-zinc-950 border border-zinc-800 rounded-lg text-center text-sm text-gray-500">
                        No articles were found or analyzed for this selection.
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Custom Text Analysis Tab */}
        {activeTab === "custom" && (
          <div className="space-y-6">
            <div className="p-5 sm:p-6 bg-zinc-950 border border-zinc-800 rounded-xl">
              <label htmlFor="customText" className="block text-sm font-medium text-gray-400 mb-2">
                Enter text to analyze sentiment
              </label>
              <textarea
                id="customText"
                rows={4}
                value={customText}
                onChange={(e) => setCustomText(e.target.value)}
                placeholder="Paste a news headline, tweet, comment, or any crypto-related text here..."
                className="w-full p-3 rounded-lg border border-zinc-700 bg-zinc-800 text-white focus:outline-none focus:ring-1 focus:ring-emerald-500 text-sm custom-scrollbar"
              />
              <button
                onClick={analyzeCustomText}
                disabled={loadingCustom || !customText.trim()}
                className="mt-4 w-full h-10 rounded-lg bg-emerald-600 text-white font-medium disabled:opacity-50 flex items-center justify-center gap-2 transition-colors hover:bg-emerald-500 text-sm"
              >
                {loadingCustom ? (
                    <>
                        <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                           <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                           <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                         </svg>
                        Analyzing...
                    </>
                ) : "Analyze Text"}
              </button>
            </div>

            {errorCustom && <div className="p-4 rounded-lg bg-red-900/50 border border-red-700 text-red-300 text-sm">{errorCustom}</div>}

            {customResult && !loadingCustom && (
              <div className="p-5 sm:p-6 bg-zinc-950 border border-zinc-800 rounded-xl">
                <h3 className="text-base sm:text-lg font-semibold mb-4 text-white">Analysis Result</h3>
                <div className="flex items-center gap-3 sm:gap-4 mb-4">
                   <div className={`p-2 rounded-full ${getSentimentStyle(customResult.label).bgColor}`}>
                       {(() => {
                           // *** CORRECTED ICON RENDERING (CUSTOM RESULT) ***
                           const styleInfo = getSentimentStyle(customResult.label);
                           const { Icon } = styleInfo;
                           // Check if Icon is valid before rendering
                           return Icon ? <Icon className={`w-5 h-5 sm:w-6 sm:h-6 ${styleInfo.color}`} /> : null;
                       })()}
                   </div>
                   <div>
                       <div className={`text-lg sm:text-xl font-bold ${getSentimentStyle(customResult.label).color}`}>
                           {getSentimentStyle(customResult.label).name}
                       </div>
                       <div className="text-xs sm:text-sm text-gray-400 mt-0.5">
                           Confidence: {((customResult.confidence ?? customResult.score) * 100).toFixed(1)}%
                       </div>
                   </div>
                </div>
                 {customResult.text && (
                     <div className="mt-4 border-t border-zinc-800 pt-4">
                        <p className="text-xs text-gray-500 mb-1.5 uppercase tracking-wider">Analyzed Text:</p>
                        <p className="text-sm text-gray-300 bg-zinc-900 p-3 rounded border border-zinc-700 max-h-32 overflow-y-auto custom-scrollbar">
                           "{customResult.text}"
                         </p>
                     </div>
                 )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}