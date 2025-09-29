"use client";
import { useEffect, useState } from "react";
import { Bot, MessageSquare, TrendingUp, Zap, BarChart3, Shield, Database, Brain, Target } from "lucide-react";

export default function Home() {
  const [signedIn, setSignedIn] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    // Simulating auth check - in real app, check your auth token
    const token = false; // Replace with: localStorage.getItem("coinsense_token");
    setSignedIn(!!token);
  }, []);

  return (
    <div className="font-sans min-h-screen flex flex-col relative overflow-hidden bg-black text-white">
      {/* Floating Crypto Icons Background */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden opacity-10">
        <div className="absolute top-20 left-10 text-6xl animate-float">₿</div>
        <div className="absolute top-40 right-20 text-5xl animate-float-delayed">Ξ</div>
        <div className="absolute top-60 left-1/4 text-4xl animate-float-slow">◈</div>
        <div className="absolute bottom-40 right-1/3 text-7xl animate-float">₿</div>
        <div className="absolute bottom-20 left-1/3 text-5xl animate-float-delayed">Ξ</div>
        <div className="absolute top-1/3 right-10 text-6xl animate-float-slow">◈</div>
        <div className="absolute bottom-60 left-10 text-4xl animate-float">₿</div>
        <div className="absolute top-1/2 left-1/2 text-5xl animate-float-delayed">Ξ</div>
      </div>

      {/* Gradient overlays */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-black/50 to-black" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(255,255,255,0.1),transparent_50%)]" />
      </div>

      <main className="flex-1 relative z-10">
        {/* Hero */}
        <section className="px-6">
          <div className="mx-auto w-full max-w-7xl py-20 sm:py-32">
            <div className="text-center max-w-5xl mx-auto">
              <div className="inline-flex items-center gap-2 text-xs px-4 py-2 rounded-full border border-white/20 bg-white/5 backdrop-blur-sm mb-6">
                <span className="inline-block h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                Live Crypto Intelligence
              </div>
              
              <h1 className="text-5xl sm:text-7xl md:text-8xl font-bold leading-[1.1] tracking-tighter mb-6">
                <span className="inline-block bg-gradient-to-r from-white via-gray-300 to-white bg-clip-text text-transparent">
                  Master Crypto
                </span>
                <br />
                <span className="inline-block bg-gradient-to-r from-gray-400 via-white to-gray-400 bg-clip-text text-transparent">
                  with AI Insights
                </span>
              </h1>
              
              <p className="mt-6 text-lg sm:text-xl text-gray-400 max-w-3xl mx-auto leading-relaxed">
                Advanced LSTM price forecasting, real-time sentiment analysis, and AI-powered market intelligence for cryptocurrency traders and investors.
              </p>
              
              <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
                {!signedIn ? (
                  <>
                    <a href="/register" className="rounded-full bg-white text-black px-8 py-4 text-base font-semibold hover:bg-gray-200 transition shadow-2xl shadow-white/20 transform hover:scale-105">
                      Start Free Trial
                    </a>
                    <a href="/login" className="rounded-full border-2 border-white/20 px-8 py-4 text-base font-semibold hover:bg-white/10 transition backdrop-blur-sm">
                      Sign In
                    </a>
                  </>
                ) : (
                  <a href="/dashboard" className="rounded-full bg-white text-black px-8 py-4 text-base font-semibold hover:bg-gray-200 transition shadow-2xl shadow-white/20">
                    Go to Dashboard
                  </a>
                )}
              </div>
            </div>

            {/* Hero Visual */}
            <div className="mt-20 relative">
              <div className="relative rounded-3xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent overflow-hidden shadow-2xl backdrop-blur-sm">
                <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:4rem_4rem]" />
                
                <div className="relative grid md:grid-cols-2 divide-x divide-white/10">
                  <div className="p-8 md:p-12">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center">
                        <BarChart3 className="w-5 h-5 text-white" />
                      </div>
                      <h3 className="text-xl font-bold">Price Predictions</h3>
                    </div>
                    <p className="text-sm text-gray-400 mb-6">7-day forecasts powered by LSTM neural networks trained on 20+ cryptocurrencies</p>
                    <div className="h-48 rounded-2xl bg-gradient-to-br from-white/10 to-white/5 border border-white/10 relative overflow-hidden">
                      <div className="absolute inset-0 flex items-center justify-center">
                        <div className="w-full h-32 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer" />
                      </div>
                    </div>
                  </div>
                  
                  <div className="p-8 md:p-12">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center">
                        <Target className="w-5 h-5 text-white" />
                      </div>
                      <h3 className="text-xl font-bold">Market Sentiment</h3>
                    </div>
                    <p className="text-sm text-gray-400 mb-6">Real-time analysis of news and social signals using advanced NLP algorithms</p>
                    <div className="h-48 rounded-2xl bg-gradient-to-br from-white/10 to-white/5 border border-white/10 relative overflow-hidden">
                      <div className="absolute inset-0 flex items-center justify-center">
                        <div className="w-full h-32 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer-delayed" />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Features */}
        <section id="features" className="px-6 py-20">
          <div className="mx-auto w-full max-w-7xl">
            <div className="text-center mb-16">
              <h2 className="text-4xl sm:text-5xl font-bold mb-4">Powerful Features</h2>
              <p className="text-gray-400 text-lg">Everything you need to stay ahead in crypto markets</p>
            </div>
            
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="group p-8 rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent hover:from-white/10 hover:border-white/20 transition-all duration-300">
                <div className="mb-4">
                  <Brain className="w-10 h-10 text-white" />
                </div>
                <h3 className="text-xl font-bold mb-2">LSTM Forecasting</h3>
                <p className="text-gray-400">Neural network predictions trained on historical price data with high accuracy rates</p>
              </div>
              
              <div className="group p-8 rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent hover:from-white/10 hover:border-white/20 transition-all duration-300">
                <div className="mb-4">
                  <MessageSquare className="w-10 h-10 text-white" />
                </div>
                <h3 className="text-xl font-bold mb-2">AI Assistant</h3>
                <p className="text-gray-400">Natural language queries about trends, metrics, and trading strategies</p>
              </div>
              
              <div className="group p-8 rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent hover:from-white/10 hover:border-white/20 transition-all duration-300">
                <div className="mb-4">
                  <TrendingUp className="w-10 h-10 text-white" />
                </div>
                <h3 className="text-xl font-bold mb-2">Sentiment Analysis</h3>
                <p className="text-gray-400">Track market psychology through news and social media sentiment scores</p>
              </div>
              
              <div className="group p-8 rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent hover:from-white/10 hover:border-white/20 transition-all duration-300">
                <div className="mb-4">
                  <Zap className="w-10 h-10 text-white" />
                </div>
                <h3 className="text-xl font-bold mb-2">Real-time Data</h3>
                <p className="text-gray-400">Live price feeds and instant updates across all supported cryptocurrencies</p>
              </div>
              
              <div className="group p-8 rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent hover:from-white/10 hover:border-white/20 transition-all duration-300">
                <div className="mb-4">
                  <BarChart3 className="w-10 h-10 text-white" />
                </div>
                <h3 className="text-xl font-bold mb-2">Visual Analytics</h3>
                <p className="text-gray-400">Interactive charts and dashboards for comprehensive market analysis</p>
              </div>
              
              <div className="group p-8 rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent hover:from-white/10 hover:border-white/20 transition-all duration-300">
                <div className="mb-4">
                  <Shield className="w-10 h-10 text-white" />
                </div>
                <h3 className="text-xl font-bold mb-2">Secure & Private</h3>
                <p className="text-gray-400">Bank-level encryption and privacy protection for your data and assets</p>
              </div>
            </div>
          </div>
        </section>

        {/* How it Works */}
        <section id="how-it-works" className="px-6 py-20 bg-white/5">
          <div className="mx-auto w-full max-w-7xl">
            <div className="text-center mb-16">
              <h2 className="text-4xl sm:text-5xl font-bold mb-4">How It Works</h2>
              <p className="text-gray-400 text-lg">Three simple steps to smarter crypto trading</p>
            </div>
            
            <div className="grid md:grid-cols-3 gap-8">
              <div className="relative">
                <div className="text-center">
                  <div className="w-16 h-16 rounded-full bg-white text-black flex items-center justify-center text-2xl font-bold mx-auto mb-6">1</div>
                  <h3 className="text-2xl font-bold mb-3">Data Collection</h3>
                  <p className="text-gray-400">Aggregate OHLCV data from multiple exchanges and train LSTM models for accurate predictions</p>
                </div>
                <div className="hidden md:block absolute top-8 left-full w-full h-0.5 bg-gradient-to-r from-white/20 to-transparent -translate-x-1/2" />
              </div>
              
              <div className="relative">
                <div className="text-center">
                  <div className="w-16 h-16 rounded-full bg-white text-black flex items-center justify-center text-2xl font-bold mx-auto mb-6">2</div>
                  <h3 className="text-2xl font-bold mb-3">AI Analysis</h3>
                  <p className="text-gray-400">Process news and social signals with NLP to generate sentiment scores and market insights</p>
                </div>
                <div className="hidden md:block absolute top-8 left-full w-full h-0.5 bg-gradient-to-r from-white/20 to-transparent -translate-x-1/2" />
              </div>
              
              <div className="relative">
                <div className="text-center">
                  <div className="w-16 h-16 rounded-full bg-white text-black flex items-center justify-center text-2xl font-bold mx-auto mb-6">3</div>
                  <h3 className="text-2xl font-bold mb-3">Smart Decisions</h3>
                  <p className="text-gray-400">Get actionable insights through our AI assistant and make informed trading decisions</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Pricing */}
        <section id="pricing" className="px-6 py-20">
          <div className="mx-auto w-full max-w-7xl">
            <div className="text-center mb-16">
              <h2 className="text-4xl sm:text-5xl font-bold mb-4">Simple Pricing</h2>
              <p className="text-gray-400 text-lg">Choose the plan that fits your needs</p>
            </div>
            
            <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
              <div className="p-8 rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent hover:border-white/20 transition-all">
                <h3 className="text-2xl font-bold mb-2">Free</h3>
                <p className="text-gray-400 mb-6">Perfect for getting started</p>
                <div className="text-5xl font-bold mb-6">$0</div>
                <ul className="space-y-3 mb-8">
                  <li className="flex items-center gap-2 text-sm">
                    <span className="text-green-500">✓</span> Basic price forecasts
                  </li>
                  <li className="flex items-center gap-2 text-sm">
                    <span className="text-green-500">✓</span> Limited AI chat
                  </li>
                  <li className="flex items-center gap-2 text-sm">
                    <span className="text-green-500">✓</span> 5 coins supported
                  </li>
                </ul>
                <a href="/register" className="block w-full text-center rounded-full border-2 border-white/20 px-6 py-3 font-semibold hover:bg-white/10 transition">
                  Get Started
                </a>
              </div>
              
              <div className="p-8 rounded-2xl border-2 border-white bg-gradient-to-b from-white/10 to-white/5 transform scale-105 shadow-2xl shadow-white/10">
                <div className="inline-block px-3 py-1 rounded-full bg-white text-black text-xs font-bold mb-4">POPULAR</div>
                <h3 className="text-2xl font-bold mb-2">Pro</h3>
                <p className="text-gray-400 mb-6">For serious traders</p>
                <div className="text-5xl font-bold mb-6">$19<span className="text-xl font-normal text-gray-400">/mo</span></div>
                <ul className="space-y-3 mb-8">
                  <li className="flex items-center gap-2 text-sm">
                    <span className="text-green-500">✓</span> Advanced forecasts
                  </li>
                  <li className="flex items-center gap-2 text-sm">
                    <span className="text-green-500">✓</span> Unlimited AI chat
                  </li>
                  <li className="flex items-center gap-2 text-sm">
                    <span className="text-green-500">✓</span> 20+ coins supported
                  </li>
                  <li className="flex items-center gap-2 text-sm">
                    <span className="text-green-500">✓</span> Sentiment analysis
                  </li>
                  <li className="flex items-center gap-2 text-sm">
                    <span className="text-green-500">✓</span> Priority support
                  </li>
                </ul>
                <a href="/register" className="block w-full text-center rounded-full bg-white text-black px-6 py-3 font-semibold hover:bg-gray-200 transition">
                  Start Free Trial
                </a>
              </div>
              
              <div className="p-8 rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent hover:border-white/20 transition-all">
                <h3 className="text-2xl font-bold mb-2">Team</h3>
                <p className="text-gray-400 mb-6">For funds & institutions</p>
                <div className="text-5xl font-bold mb-6">$79<span className="text-xl font-normal text-gray-400">/mo</span></div>
                <ul className="space-y-3 mb-8">
                  <li className="flex items-center gap-2 text-sm">
                    <span className="text-green-500">✓</span> Everything in Pro
                  </li>
                  <li className="flex items-center gap-2 text-sm">
                    <span className="text-green-500">✓</span> 5 team seats
                  </li>
                  <li className="flex items-center gap-2 text-sm">
                    <span className="text-green-500">✓</span> API access
                  </li>
                  <li className="flex items-center gap-2 text-sm">
                    <span className="text-green-500">✓</span> Custom integrations
                  </li>
                  <li className="flex items-center gap-2 text-sm">
                    <span className="text-green-500">✓</span> Dedicated support
                  </li>
                </ul>
                <a href="/register" className="block w-full text-center rounded-full border-2 border-white/20 px-6 py-3 font-semibold hover:bg-white/10 transition">
                  Contact Sales
                </a>
              </div>
            </div>
          </div>
        </section>

        {/* FAQ */}
        <section id="faq" className="px-6 py-20 bg-white/5">
          <div className="mx-auto w-full max-w-4xl">
            <div className="text-center mb-16">
              <h2 className="text-4xl sm:text-5xl font-bold mb-4">Frequently Asked Questions</h2>
            </div>
            
            <div className="space-y-4">
              <details className="group rounded-xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent p-6 hover:border-white/20 transition">
                <summary className="font-semibold cursor-pointer text-lg">Is CoinSense financial advice?</summary>
                <p className="text-gray-400 mt-3 leading-relaxed">No. CoinSense provides research tools and data analysis, not investment advice. Always conduct your own research and consult with financial professionals before making investment decisions.</p>
              </details>
              
              <details className="group rounded-xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent p-6 hover:border-white/20 transition">
                <summary className="font-semibold cursor-pointer text-lg">Which cryptocurrencies are supported?</summary>
                <p className="text-gray-400 mt-3 leading-relaxed">We support 20+ major cryptocurrencies including Bitcoin, Ethereum, Solana, Cardano, Polkadot, and many more. Pro and Team plans include access to all supported assets.</p>
              </details>
              
              <details className="group rounded-xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent p-6 hover:border-white/20 transition">
                <summary className="font-semibold cursor-pointer text-lg">How accurate are the predictions?</summary>
                <p className="text-gray-400 mt-3 leading-relaxed">Our LSTM models are trained on extensive historical data and achieve competitive accuracy rates. However, crypto markets are highly volatile and no prediction can be 100% accurate. Use our forecasts as one tool in your research process.</p>
              </details>
              
              <details className="group rounded-xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent p-6 hover:border-white/20 transition">
                <summary className="font-semibold cursor-pointer text-lg">Can I export data and predictions?</summary>
                <p className="text-gray-400 mt-3 leading-relaxed">Yes! Pro and Team plans allow you to export predictions as CSV files and access our API for seamless integration with your existing workflows and tools.</p>
              </details>
              
              <details className="group rounded-xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent p-6 hover:border-white/20 transition">
                <summary className="font-semibold cursor-pointer text-lg">What payment methods do you accept?</summary>
                <p className="text-gray-400 mt-3 leading-relaxed">We accept all major credit cards, PayPal, and cryptocurrency payments. All subscriptions can be canceled at any time with no long-term commitments.</p>
              </details>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="px-6 py-20">
          <div className="mx-auto w-full max-w-5xl">
            <div className="relative rounded-3xl border border-white/20 bg-gradient-to-br from-white/10 to-white/5 p-12 md:p-16 text-center overflow-hidden">
              <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.05)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.05)_1px,transparent_1px)] bg-[size:4rem_4rem]" />
              <div className="relative">
                <h2 className="text-4xl sm:text-5xl font-bold mb-6">Ready to get started?</h2>
                <p className="text-xl text-gray-400 mb-8 max-w-2xl mx-auto">Join thousands of traders using AI-powered insights to make smarter crypto decisions</p>
                <a href="/register" className="inline-block rounded-full bg-white text-black px-8 py-4 text-lg font-semibold hover:bg-gray-200 transition shadow-2xl shadow-white/20 transform hover:scale-105">
                  Start Free Trial
                </a>
              </div>
            </div>
          </div>
        </section>
      </main>

      <style jsx>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-20px) rotate(5deg); }
        }
        
        @keyframes float-delayed {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-25px) rotate(-5deg); }
        }
        
        @keyframes float-slow {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-15px) rotate(3deg); }
        }
        
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        
        @keyframes shimmer-delayed {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        
        .animate-float {
          animation: float 6s ease-in-out infinite;
        }
        
        .animate-float-delayed {
          animation: float-delayed 7s ease-in-out infinite;
          animation-delay: 1s;
        }
        
        .animate-float-slow {
          animation: float-slow 8s ease-in-out infinite;
          animation-delay: 2s;
        }
        
        .animate-shimmer {
          animation: shimmer 3s ease-in-out infinite;
        }
        
        .animate-shimmer-delayed {
          animation: shimmer-delayed 3s ease-in-out infinite;
          animation-delay: 1s;
        }
      `}</style>
    </div>
  );
}