"use client";
import { useEffect, useRef, useState } from "react";
import { TrendingUp, Calendar, MessageSquare, User, Sparkles, Plus, Menu, X, ArrowUp } from "lucide-react"; // Added ArrowUp
import Link from "next/link";

// Defines the structure for a chat message
type ChatMsg = {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
};

// --- Sub-components ---

function ChatMessage({ msg }: { msg: ChatMsg }) {
  const isUser = msg.role === "user";
  return (
    <div className="flex gap-4 mb-6"> {/* Unified gap and margin */}
      {/* Avatar */}
      <div className="flex-shrink-0">
        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-medium text-xs ${
          isUser ? "bg-blue-600" : "bg-emerald-600" // Slightly darker colors
        }`}>
          {isUser ? (
            <User className="w-4 h-4" />
          ) : (
            <Sparkles className="w-4 h-4" />
          )}
        </div>
      </div>
      
      {/* Message Content */}
      <div className="flex-1">
        <div className="font-semibold text-white mb-1.5"> {/* Increased margin */}
          {isUser ? "You" : "AI Assistant"}
        </div>
        <div className="text-gray-200 text-base leading-relaxed whitespace-pre-wrap"> {/* Slightly larger text */}
          {msg.content}
        </div>
        <div className="text-[11px] text-gray-500 mt-2"> {/* Increased margin */}
          {msg.timestamp}
        </div>
      </div>
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex gap-4 mb-6">
      <div className="flex-shrink-0">
        <div className="w-8 h-8 rounded-full flex items-center justify-center bg-emerald-600 text-white font-medium text-xs">
          <Sparkles className="w-4 h-4" />
        </div>
      </div>
      <div className="flex-1">
        <div className="font-semibold text-white mb-1.5">
          AI Assistant
        </div>
        <div className="bg-zinc-800 rounded-lg px-4 py-3 flex items-center gap-1.5 w-16">
          <span className="h-1.5 w-1.5 rounded-full bg-gray-400 animate-bounce" /> {/* Slightly smaller dots */}
          <span className="h-1.5 w-1.5 rounded-full bg-gray-400 animate-bounce [animation-delay:0.15s]" />
          <span className="h-1.5 w-1.5 rounded-full bg-gray-400 animate-bounce [animation-delay:0.3s]" />
        </div>
      </div>
    </div>
  );
}

function QuickPromptButton({ text, onClick }: { text: string; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="w-full text-left px-3 py-2.5 rounded-lg bg-zinc-800/60 hover:bg-zinc-700/60 text-sm text-gray-300 transition-colors flex items-center gap-2" // Added transition-colors
    >
      <MessageSquare className="w-4 h-4 text-gray-400 flex-shrink-0" />
      <span className="flex-1 truncate">{text}</span>
    </button>
  );
}

// --- Main Chat Page Component ---

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMsg[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [username, setUsername] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true); // Default to open on desktop
  const scroller = useRef<HTMLDivElement | null>(null);
  const textAreaRef = useRef<HTMLTextAreaElement | null>(null); // Ref for textarea

  // Check screen size on mount for sidebar default
  useEffect(() => {
     if (window.innerWidth < 768) { // Example breakpoint for mobile (Tailwind's 'md')
         setSidebarOpen(false);
     }
  }, []);

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
        } else {
            // Handle unauthorized or token expiry - redirect to login
             localStorage.removeItem("coinsense_token");
             window.location.href = "/login";
        }
      } catch (error) {
        console.error("Failed to fetch username:", error);
         localStorage.removeItem("coinsense_token"); // Also logout on fetch error
         window.location.href = "/login";
      }
    })();
  }, []);

  useEffect(() => {
    scroller.current?.scrollTo({ top: scroller.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  // Auto-resize textarea height
  useEffect(() => {
    if (textAreaRef.current) {
      textAreaRef.current.style.height = 'auto'; // Reset height
      textAreaRef.current.style.height = `${textAreaRef.current.scrollHeight}px`; // Set to scroll height
    }
  }, [input]);

  async function send() {
    const text = input.trim();
    if (!text || loading) return;

    const token = localStorage.getItem("coinsense_token");
    if (!token) { // Double check token before sending
        window.location.href = "/login";
        return;
    }
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

      if (res.status === 401) { // Handle expired token from API
          localStorage.removeItem("coinsense_token");
          window.location.href = "/login";
          throw new Error("Unauthorized");
      }

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Chat failed");

      const reply = data.response || "";
      const assistantTimestamp = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
      
      setMessages((m) => [...m, { role: "assistant", content: "", timestamp: assistantTimestamp }]);

      // Typewriter effect
      const words = reply.split(" ");
      for (let i = 0; i < words.length; i++) {
        await new Promise((r) => setTimeout(r, 40)); // Typing speed
        setMessages((currentMessages) => {
          // Prevent updates if component unmounted or state changed rapidly
          if (!currentMessages || currentMessages.length === 0) return []; 
          const newMessages = [...currentMessages];
          const lastMessage = newMessages[newMessages.length - 1];
          // Ensure we are updating the correct assistant message placeholder
          if (lastMessage && lastMessage.role === 'assistant' && lastMessage.timestamp === assistantTimestamp) { 
            newMessages[newMessages.length - 1] = {
              ...lastMessage,
              content: words.slice(0, i + 1).join(" "),
            };
          }
          return newMessages;
        });
      }
    } catch (error: any) {
       if (error.message === "Unauthorized") return; // Already handled redirect

      console.error("API Error:", error);
      const errorTimestamp = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
      // Replace the placeholder if error occurs during typing
      setMessages((m) => {
          // Prevent updates if component unmounted or state changed rapidly
          if (!m || m.length === 0) return []; 
          const last = m[m.length - 1];
          // Ensure we replace the correct placeholder
          if (last && last.role === 'assistant' && last.content === '' && last.timestamp === assistantTimestamp) {
              return [...m.slice(0, -1), { role: "assistant", content: "Sorry, something went wrong.", timestamp: errorTimestamp }];
          }
          // If placeholder wasn't found (e.g., user navigated away), add error as new message
          return [...m, { role: "assistant", content: "Sorry, something went wrong.", timestamp: errorTimestamp }];
      });
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

  const handleNewChat = () => {
    setMessages([]);
    setInput("");
     if (window.innerWidth < 768) { // Close sidebar on mobile after new chat
         setSidebarOpen(false);
     }
  };

  return (
    // Root container ensures full height and prevents scrolling on body
    <div className="flex h-screen max-h-screen overflow-hidden bg-black text-gray-100">

      {/* Sidebar */}
      <aside className={`${sidebarOpen ? "w-64 md:w-72" : "w-0"} flex-shrink-0 transition-width duration-300 bg-zinc-900 border-r border-zinc-700/50 flex flex-col`}>
        {/* Added flex-shrink-0 to prevent shrinking sections */}
        <div className="p-4 flex-shrink-0 border-b border-zinc-700/50"> 
          <button
            onClick={handleNewChat}
            className="w-full flex items-center justify-between gap-2 px-3 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-sm transition-colors"
          >
            <span>New Chat</span>
            <Plus className="w-5 h-5" />
          </button>
        </div>
        
        {/* Suggestions list scrolls */}
        <div className="flex-1 overflow-y-auto px-4 pt-4 pb-4"> 
          <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Suggestions</h3>
          <div className="space-y-2">
            <QuickPromptButton 
              text="BTC outlook this week?" 
              onClick={() => { setInput("What is the outlook for BTC this week?"); if (window.innerWidth < 768) setSidebarOpen(false); }} 
            />
            <QuickPromptButton 
              text="ETH 3-day prediction" 
              onClick={() => { setInput("Show ETH prediction for 3 days"); if (window.innerWidth < 768) setSidebarOpen(false); }} 
            />
            <QuickPromptButton 
              text="Solana sentiment today" 
              onClick={() => { setInput("Sentiment for Solana today"); if (window.innerWidth < 768) setSidebarOpen(false); }} 
            />
             <QuickPromptButton 
              text="Compare BTC vs ETH" 
              onClick={() => { setInput("Compare BTC vs ETH volatility"); if (window.innerWidth < 768) setSidebarOpen(false); }} 
            />
             {/* Add more suggestions if needed */}
             <QuickPromptButton 
              text="What is DeFi?" 
              onClick={() => { setInput("What is DeFi?"); if (window.innerWidth < 768) setSidebarOpen(false); }} 
            />
            <QuickPromptButton 
              text="Explain NFTs" 
              onClick={() => { setInput("Explain NFTs simply"); if (window.innerWidth < 768) setSidebarOpen(false); }} 
            />
          </div>
        </div>
        
        {/* Profile section at bottom */}
        <div className="border-t border-zinc-700/50 p-4 flex-shrink-0"> 
          <Link href="/profile" className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-zinc-800 transition-colors"> 
            <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-xs font-medium flex-shrink-0">
              {username ? username[0].toUpperCase() : "U"}
            </div>
            <div className="flex-1 text-left overflow-hidden">
              <div className="text-sm font-medium text-gray-200 truncate">{username || "User"}</div>
            </div>
            <User className="w-4 h-4 text-gray-400 flex-shrink-0" />
          </Link>
        </div>
      </aside>

      {/* Main Content Area */}
      {/* Takes remaining space, column layout, prevents overflow */}
      <main className="flex-1 flex flex-col h-full max-h-screen overflow-hidden"> 
        
        {/* Header Bar */}
        {/* No shrinking */}
        <header className="border-b border-zinc-800/50 flex-shrink-0 bg-black z-10"> 
          <div className="px-4 sm:px-6 py-3 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-2 hover:bg-zinc-800 rounded-lg transition-colors text-gray-400 hover:text-gray-100"
              >
                {/* Icon changes based on sidebar state */}
                {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />} 
              </button>
              <h1 className="text-base font-semibold text-gray-100">Crypto AI Assistant</h1>
            </div>
            
            <Link href="/profile" className="flex items-center gap-2 px-2 py-1 rounded-full hover:bg-zinc-800 transition-colors">
              <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center text-white text-xs font-medium">
                {username ? username[0].toUpperCase() : "U"}
              </div>
            </Link>
          </div>
        </header>

        {/* Chat Area - Scrolls */}
        {/* Takes up available space, scrolls vertically */}
        <div ref={scroller} className="flex-1 overflow-y-auto bg-black"> 
          <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
            {messages.length === 0 && (
              <div className="text-center pt-10 pb-16">
                <div className="w-16 h-16 bg-gradient-to-br from-emerald-600 to-green-700 rounded-full flex items-center justify-center mx-auto mb-5 shadow-lg">
                  <Sparkles className="w-8 h-8 text-white" />
                </div>
                <h2 className="text-2xl font-semibold mb-2 text-gray-100">
                  {username ? `Hello, ${username}!` : "How can I help you today?"}
                </h2>
                <p className="text-gray-400 mb-8 max-w-md mx-auto">Ask me anything about cryptocurrencies, market trends, or trading strategies</p>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 max-w-3xl mx-auto"> {/* Adjusted grid for mobile */}
                  {[
                    { Icon: TrendingUp, text: "Outlook for BTC?" },
                    { Icon: Calendar, text: "ETH 3-day forecast" },
                    { Icon: MessageSquare, text: "SOL sentiment?" },
                    { Icon: TrendingUp, text: "BTC vs ETH compare" },
                  ].map((item, i) => (
                    <button
                      key={i}
                      // Use the shorter text directly for the input
                      onClick={() => { setInput(item.text); if (window.innerWidth < 768) setSidebarOpen(false); }} 
                      className="text-left p-4 rounded-xl bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 hover:border-zinc-700 transition-all group min-h-[100px] flex flex-col justify-start" // Flex column layout
                    >
                      <item.Icon className="w-5 h-5 text-gray-400 mb-2" />
                      <div className="text-sm font-medium text-gray-300 group-hover:text-gray-200 mt-auto">{item.text}</div> {/* Pushed text down */}
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
        {/* No shrinking, background added */}
        <div className="bg-black border-t border-zinc-800/50 flex-shrink-0"> 
          <div className="max-w-3xl mx-auto px-4 sm:px-6 py-3"> {/* Reduced padding */}
            {/* Input Wrapper */}
            <div className="relative flex items-end p-1 bg-zinc-800/70 border border-zinc-700 rounded-2xl focus-within:ring-2 focus-within:ring-emerald-500/50 focus-within:border-emerald-500/50 transition-all"> 
              <textarea
                ref={textAreaRef} // Add ref here
                className="flex-1 bg-transparent px-4 py-2.5 text-base text-gray-100 placeholder-gray-500 resize-none focus:outline-none overflow-y-auto" // Adjusted padding/size, added overflow-y-auto
                placeholder="Ask anything..."
                value={input}
                onChange={(e) => setInput(e.target.value)} // <<< --- *** CORRECTED HANDLER ***
                onKeyDown={onKeyDown}
                disabled={loading}
                rows={1} // Start with 1 row
                style={{ maxHeight: "120px" }} // Limit max height
              />
              <button
                onClick={send}
                disabled={loading || !input.trim()}
                className="ml-2 flex-shrink-0 w-9 h-9 mb-1 rounded-full bg-emerald-600 hover:bg-emerald-500 disabled:bg-zinc-700 disabled:opacity-50 disabled:cursor-not-allowed text-white flex items-center justify-center transition-colors" // Adjusted colors/disabled style
              >
                {/* Changed send icon to ArrowUp */}
                <ArrowUp className="w-5 h-5" /> 
              </button>
            </div>
             {/* Removed the small text below input */}
          </div>
        </div>
      </main>
    </div>
  );
}