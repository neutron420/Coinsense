"use client";
import { useEffect, useRef, useState } from "react";
import { Menu, X, TrendingUp, Calendar, MessageSquare, BarChart3, ShoppingCart, FileText, User, LucideIcon } from "lucide-react";

// Defines the structure for a chat message
type ChatMsg = {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
};

// --- Sub-components for a cleaner structure ---

// Component for rendering a single chat message bubble
function ChatMessage({ msg }: { msg: ChatMsg }) {
  const isUser = msg.role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div className={`flex gap-3 max-w-[80%] ${isUser ? "flex-row-reverse" : "flex-row"}`}>
        {/* Avatar */}
        <div className="flex-shrink-0">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-medium text-xs ${
            isUser ? "bg-blue-500" : "bg-emerald-500"
          }`}>
            {isUser ? "U" : "AI"}
          </div>
        </div>
        
        {/* Message Bubble */}
        <div>
          <div className={`rounded-2xl px-4 py-2.5 ${
            isUser 
              ? "bg-blue-500 text-white rounded-tr-sm" 
              : "bg-zinc-800 text-gray-100 rounded-tl-sm"
          }`}>
            <div className="whitespace-pre-wrap text-[15px] leading-relaxed">{msg.content}</div>
          </div>
          <div className={`text-[11px] text-gray-500 mt-1 px-1 ${isUser ? "text-right" : "text-left"}`}>
            {msg.timestamp}
          </div>
        </div>
      </div>
    </div>
  );
}

// Component for the "Assistant is typing..." animation
function TypingIndicator() {
  return (
    <div className="flex justify-start mb-4">
      <div className="flex gap-3 max-w-[80%]">
        <div className="flex-shrink-0">
          <div className="w-8 h-8 rounded-full flex items-center justify-center bg-emerald-500 text-white font-medium text-xs">
            AI
          </div>
        </div>
        <div className="bg-zinc-800 rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-1">
          <span className="h-2 w-2 rounded-full bg-gray-400 animate-bounce" />
          <span className="h-2 w-2 rounded-full bg-gray-400 animate-bounce [animation-delay:0.15s]" />
          <span className="h-2 w-2 rounded-full bg-gray-400 animate-bounce [animation-delay:0.3s]" />
        </div>
      </div>
    </div>
  );
}

// Reusable button for quick prompts
function QuickPromptButton({ icon: Icon, text, onClick }: { icon: LucideIcon; text: string; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="text-left px-3 py-2.5 rounded-lg bg-zinc-800/50 hover:bg-zinc-700/50 text-sm text-gray-300 transition-all border border-zinc-700/50 hover:border-zinc-600 flex items-center gap-2"
    >
      <Icon className="w-4 h-4 text-gray-400" />
      <span className="flex-1">{text}</span>
    </button>
  );
}

// --- Main Chat Page Component ---

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMsg[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [username, setUsername] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const scroller = useRef<HTMLDivElement | null>(null);

  // Effect to handle authentication and fetching username
  useEffect(() => {
    const token = localStorage.getItem("coinsense_token");
    if (!token) {
      window.location.href = "/login";
      return;
    }
    (async () => {
      try {
        const res = await fetch(process.env.NEXT_PUBLIC_API_URL + "/api/auth/me", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setUsername(data.username || null);
        }
      } catch (error) {
        console.error("Failed to fetch username:", error);
      }
    })();
  }, []);

  // Effect to auto-scroll to the latest message
  useEffect(() => {
    scroller.current?.scrollTo({ top: scroller.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  // Main function to handle sending a message
  async function send() {
    const text = input.trim();
    if (!text || loading) return;

    const token = localStorage.getItem("coinsense_token");
    const timestamp = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

    setMessages((m) => [...m, { role: "user", content: text, timestamp }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(process.env.NEXT_PUBLIC_API_URL + "/api/chat/message", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ message: text }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Chat failed");

      const reply = data.response || "";
      const assistantTimestamp = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
      
      // Add a placeholder for the assistant's message
      setMessages((m) => [...m, { role: "assistant", content: "", timestamp: assistantTimestamp }]);

      // Typewriter effect (word by word)
      const words = reply.split(" ");
      for (let i = 0; i < words.length; i++) {
        await new Promise((r) => setTimeout(r, 60));
        setMessages((currentMessages) => {
          const newMessages = [...currentMessages];
          const lastMessage = newMessages[newMessages.length - 1];
          newMessages[newMessages.length - 1] = {
            ...lastMessage,
            content: words.slice(0, i + 1).join(" "),
          };
          return newMessages;
        });
      }
    } catch (error) {
      console.error("API Error:", error);
      const errorTimestamp = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
      setMessages((m) => [...m, { role: "assistant", content: "Sorry, something went wrong.", timestamp: errorTimestamp }]);
    } finally {
      setLoading(false);
    }
  }

  function onKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  return (
    <div className="min-h-screen bg-black text-gray-100 flex">
      {/* Sidebar - Left Side */}
      <aside className={`${sidebarOpen ? "w-64" : "w-0"} flex-shrink-0 transition-all duration-300 border-r border-zinc-800/50 bg-zinc-950 flex flex-col overflow-hidden`}>
        <div className="flex-1 overflow-y-auto">
          <div className="p-4">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-sm font-semibold text-gray-300">Suggested Questions</h3>
              <button
                onClick={() => setSidebarOpen(false)}
                className="p-1 hover:bg-zinc-800 rounded transition-colors"
              >
                <X className="w-4 h-4 text-gray-400" />
              </button>
            </div>
            
            <div className="space-y-2">
              <QuickPromptButton 
                icon={TrendingUp}
                text="BTC outlook this week?" 
                onClick={() => setInput("What is the outlook for BTC this week?")} 
              />
              <QuickPromptButton 
                icon={Calendar}
                text="ETH 3-day prediction" 
                onClick={() => setInput("Show ETH prediction for 3 days")} 
              />
              <QuickPromptButton 
                icon={MessageSquare}
                text="Solana sentiment today" 
                onClick={() => setInput("Sentiment for Solana today")} 
              />
              <QuickPromptButton 
                icon={BarChart3}
                text="BTC vs ETH volatility" 
                onClick={() => setInput("Compare BTC vs ETH volatility")} 
              />
              <QuickPromptButton 
                icon={ShoppingCart}
                text="Best crypto to buy now?" 
                onClick={() => setInput("Best crypto to buy now?")} 
              />
              <QuickPromptButton 
                icon={FileText}
                text="Market analysis summary" 
                onClick={() => setInput("Market analysis summary")} 
              />
            </div>
            
            <div className="mt-6 p-3 rounded-lg bg-zinc-900/50 border border-zinc-800">
              <div className="flex items-start gap-2">
                <div className="text-yellow-500 text-sm">💡</div>
                <div>
                  <h4 className="text-xs font-medium mb-1 text-gray-300">Pro Tip</h4>
                  <p className="text-xs text-gray-500 leading-relaxed">
                    Ask specific questions about price predictions, market sentiment, or technical analysis for better insights.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Profile Section at Bottom */}
        <div className="border-t border-zinc-800/50 p-4">
          <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-zinc-800/50 transition-colors">
            <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white text-xs font-medium">
              {username ? username[0].toUpperCase() : "U"}
            </div>
            <div className="flex-1 text-left">
              <div className="text-sm font-medium text-gray-200">{username || "User"}</div>
              <div className="text-xs text-gray-500">View Profile</div>
            </div>
            <User className="w-4 h-4 text-gray-400" />
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Navbar - Replace this comment with your imported Navbar component */}
        {/* <Navbar /> */}
        
        <div className="border-b border-zinc-800/50">
          <div className="px-4 sm:px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              {!sidebarOpen && (
                <button
                  onClick={() => setSidebarOpen(true)}
                  className="p-2 hover:bg-zinc-800 rounded-lg transition-colors"
                >
                  <Menu className="w-5 h-5 text-gray-400" />
                </button>
              )}
              <button
                onClick={() => history.back()}
                className="flex items-center gap-2 text-gray-400 hover:text-gray-200 transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                <span className="text-sm font-medium">Back</span>
              </button>
            </div>
            
            <div className="text-center">
              <h1 className="text-lg font-semibold">Crypto AI Assistant</h1>
              {username && <div className="text-xs text-gray-500 mt-0.5">@{username}</div>}
            </div>
            
            <div className="w-32"></div>
          </div>
        </div>

        {/* Chat Area */}
        <div ref={scroller} className="flex-1 overflow-y-auto">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6">
            {messages.length === 0 && (
              <div className="text-center py-16">
                <div className="w-16 h-16 bg-zinc-900 rounded-2xl flex items-center justify-center mx-auto mb-6 border border-zinc-800">
                  <MessageSquare className="w-8 h-8 text-emerald-500" />
                </div>
                <h2 className="text-2xl font-semibold mb-3 text-gray-100">How can I help you today?</h2>
                <p className="text-gray-500 mb-10">Ask me anything about cryptocurrencies, market trends, or trading strategies</p>
                
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl mx-auto">
                  {[
                    { Icon: TrendingUp, text: "What is the outlook for BTC this week?" },
                    { Icon: Calendar, text: "Show ETH prediction for 3 days" },
                    { Icon: MessageSquare, text: "Sentiment for Solana today" },
                    { Icon: BarChart3, text: "Compare BTC vs ETH volatility" },
                  ].map((item, i) => (
                    <button
                      key={i}
                      onClick={() => setInput(item.text)}
                      className="text-left px-4 py-4 rounded-xl bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 hover:border-zinc-700 transition-all group"
                    >
                      <item.Icon className="w-6 h-6 text-emerald-500 mb-3" />
                      <div className="text-sm text-gray-300 group-hover:text-gray-200">{item.text}</div>
                    </button>
                  ))}
                </div>
              </div>
            )}
            
            {messages.map((m, i) => <ChatMessage key={i} msg={m} />)}
            {loading && <TypingIndicator />}
          </div>
        </div>

        {/* Input Area - Fixed at bottom */}
        <div className="border-t border-zinc-800/50 bg-zinc-950/80 backdrop-blur-xl">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 py-4">
            <div className="relative">
              <div className="flex items-end gap-2 bg-zinc-900 rounded-2xl border border-zinc-800 focus-within:border-zinc-700 transition-colors">
                <textarea
                  className="flex-1 bg-transparent px-5 py-4 text-[15px] text-gray-100 placeholder-gray-500 resize-none focus:outline-none"
                  placeholder="Ask anything about crypto..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={onKeyDown}
                  disabled={loading}
                  rows={1}
                  style={{ maxHeight: "200px" }}
                />
                <button
                  onClick={send}
                  disabled={loading || !input.trim()}
                  className="flex-shrink-0 w-10 h-10 mb-2 mr-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 disabled:bg-zinc-800 disabled:cursor-not-allowed text-white flex items-center justify-center transition-colors"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                </button>
              </div>
            </div>
            <p className="text-[11px] text-gray-600 mt-2 text-center">
              AI-powered insights • Always verify important information
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}