"use client";

import React, { useState, useEffect, useRef } from "react";
import { Send, Bot, User, Trash2, ShieldCheck, Info, Loader2 } from "lucide-react";

interface Message {
  id: string;
  role: "user" | "bot";
  content: string;
  metadata?: {
    last_updated?: string;
    sources?: string[];
  };
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: input }),
      });

      if (!response.ok) throw new Error("Failed to fetch");

      const data = await response.json();
      
      const botMessage: Message = {
        id: data.id,
        role: "bot",
        content: data.content,
        metadata: data.metadata,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Error:", error);
      const errorMessage: Message = {
        id: "error-" + Date.now(),
        role: "bot",
        content: "Sorry, I encountered an error. Please try again.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <div className="flex flex-col h-screen bg-slate-950 text-slate-100">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <div className="bg-emerald-500/20 p-2 rounded-lg">
            <ShieldCheck className="text-emerald-400 w-6 h-6" />
          </div>
          <div>
            <h1 className="font-bold text-lg tracking-tight">Mutual Fund RAG</h1>
            <p className="text-xs text-slate-400 flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              Live Facts-Only Ingestion
            </p>
          </div>
        </div>
        <button 
          onClick={clearChat}
          className="p-2 hover:bg-slate-800 rounded-full transition-colors text-slate-400 hover:text-red-400"
          title="Clear Chat"
        >
          <Trash2 size={20} />
        </button>
      </header>

      {/* Chat Area */}
      <main 
        ref={scrollRef}
        className="flex-1 overflow-y-auto px-4 py-8 space-y-6 scroll-smooth"
      >
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-6 max-w-md mx-auto">
            <div className="bg-blue-500/10 p-6 rounded-full">
              <Bot className="w-12 h-12 text-blue-400" />
            </div>
            <div>
              <h2 className="text-2xl font-bold mb-2">Welcome to your Investment Assistant</h2>
              <p className="text-slate-400 text-sm leading-relaxed">
                I can provide factual details about NAV, fund performance, and metadata extracted directly from current market sources.
              </p>
            </div>
            <div className="grid grid-cols-1 gap-2 w-full">
              {[
                "What is the current NAV of HDFC Top 100?",
                "Show me performance of SBI Bluechip Fund",
                "Who is the fund manager for Axis Bluechip?"
              ].map((q) => (
                <button
                  key={q}
                  onClick={() => setInput(q)}
                  className="px-4 py-3 bg-slate-900 border border-slate-800 rounded-xl text-sm text-slate-300 hover:bg-slate-800 hover:border-slate-700 transition-all text-left"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m) => (
          <div 
            key={m.id} 
            className={`flex ${m.role === "user" ? "justify-end" : "justify-start"} animate-in fade-in slide-in-from-bottom-2 duration-300`}
          >
            <div className={`flex gap-3 max-w-[85%] ${m.role === "user" ? "flex-row-reverse" : ""}`}>
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                m.role === "user" ? "bg-blue-600" : "bg-slate-800 border border-slate-700"
              }`}>
                {m.role === "user" ? <User size={16} /> : <Bot size={16} className="text-emerald-400" />}
              </div>
              <div className="space-y-2">
                <div className={`rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-lg ${
                  m.role === "user" 
                    ? "bg-blue-600 text-white rounded-tr-none" 
                    : "bg-slate-900 text-slate-200 border border-slate-800 rounded-tl-none"
                }`}>
                  {m.content}
                </div>
                
                {m.metadata && (
                  <div className="flex flex-wrap gap-2 pt-1">
                    {m.metadata.last_updated && (
                      <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full flex items-center gap-1 uppercase tracking-wider font-semibold">
                        <Info size={10} />
                        Updated: {m.metadata.last_updated}
                      </span>
                    )}
                    {m.metadata.sources && m.metadata.sources.map((s, i) => (
                      <span key={i} className="text-[10px] bg-blue-500/10 text-blue-400 px-2 py-0.5 rounded-full uppercase tracking-wider font-semibold">
                        Source {i + 1}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="flex gap-3 max-w-[85%]">
              <div className="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center shrink-0">
                <Loader2 size={16} className="text-emerald-400 animate-spin" />
              </div>
              <div className="bg-slate-900 text-slate-400 border border-slate-800 rounded-2xl rounded-tl-none px-4 py-3 text-sm italic">
                Scanning corpus...
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Input Area */}
      <footer className="p-4 border-t border-slate-800 bg-slate-900/50">
        <div className="max-w-4xl mx-auto flex gap-2">
          <div className="flex-1 relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="Ask about any mutual fund..."
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all placeholder:text-slate-500"
            />
          </div>
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 disabled:hover:bg-emerald-600 text-white p-3 rounded-xl transition-all shadow-lg shadow-emerald-900/20"
          >
            <Send size={20} />
          </button>
        </div>
        <p className="text-[10px] text-center text-slate-500 mt-3 font-medium uppercase tracking-widest">
          Facts-only mode enabled. Not financial advice.
        </p>
      </footer>
    </div>
  );
}
