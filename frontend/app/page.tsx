"use client";
import { useState } from 'react';

export default function Home() {
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  
  const handleRecommend = async () => {
    if (!query) return;
    setLoading(true);
    try {
      // Replaced localhost:8000 with a relative path to trigger the Next.js rewrite proxy.
      // This prevents "Mixed Content" SSL errors when viewing the Secure Mobile layout while running an HTTP backend.
      const res = await fetch(`/api/recommend`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query })
      });
      const data = await res.json();
      setRecommendations(data);
    } catch (e) {
      console.error(e);
      alert("Error reaching backend. Is the Node server running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100 sm:max-w-md sm:mx-auto sm:border-x sm:shadow-2xl relative">
      {/* Mobile Top Header */}
      <header className="bg-white px-5 py-4 shadow-sm sticky top-0 z-20 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-extrabold text-indigo-600 tracking-tight flex items-center gap-1">
            <span className="text-2xl">👗</span> AuraX
          </h1>
          <p className="text-[10px] text-gray-500 uppercase tracking-widest font-semibold mt-0.5">hyper-local</p>
        </div>
        <div className="w-10 h-10 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center font-bold border border-indigo-100 shadow-inner">
          VS
        </div>
      </header>
      
      {/* Scrollable Main Application Content */}
      <main className="flex-1 overflow-y-auto w-full pb-24 px-4 pt-4">
        
        {/* Vibe input Card */}
        <div className="bg-white rounded-2xl p-5 shadow-sm mb-6 border border-gray-100">
          <h2 className="font-bold text-gray-800 text-lg">Vibe-to-Wardrobe ✨</h2>
          <p className="text-sm text-gray-500 mb-4 mt-1 leading-relaxed">Describe your vibe or occasion and let AI curate your outfit instantly.</p>
          
          <div className="flex gap-2">
            <input 
              type="text" 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g. Rainy day cafe..." 
              className="flex-1 bg-gray-50 border border-gray-200 text-sm rounded-xl px-4 py-3 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 transition text-gray-800"
            />
            <button 
              onClick={handleRecommend}
              disabled={loading}
              className="bg-indigo-600 text-white px-5 py-3 rounded-xl text-sm font-semibold hover:bg-indigo-700 active:scale-95 transition shadow-sm disabled:opacity-70 flex items-center justify-center min-w-[80px]"
            >
              {loading ? '...' : 'Find'}
            </button>
          </div>
        </div>

        {/* Feed area */}
        <div className="flex flex-col gap-4">
          <h3 className="font-bold text-gray-800 px-1">Curated Matches</h3>
          
          {recommendations.length === 0 && !loading && (
            <div className="text-center text-gray-400 text-sm mt-8 bg-gray-50 rounded-xl p-8 border border-dashed border-gray-200">
              No items discovered yet <br />Enter your vibe above!
            </div>
          )}

          {/* Product Cards Loop */}
          {recommendations.map(item => (
            <div key={item.sku} className="bg-white rounded-2xl overflow-hidden shadow-sm border border-gray-100 flex flex-col group hover:shadow-md transition">
              {/* Product Mock Image Block */}
              <div className="h-56 bg-slate-200 w-full flex items-center justify-center text-slate-400 text-xs font-medium relative">
                [Product Image Placeholder: {item.sku}]
                <button className="absolute top-3 right-3 bg-white w-8 h-8 rounded-full shadow flex items-center justify-center text-gray-400 active:text-red-500 transition">
                  🤍
                </button>
              </div>
              
              <div className="p-4">
                <h4 className="font-semibold text-gray-800 text-[15px] leading-tight mb-1">{item.name}</h4>
                <div className="flex justify-between items-end mt-3 border-t border-gray-50 pt-3">
                  <span className="text-indigo-600 font-extrabold text-lg">₹{item.price}</span>
                  <span className="text-[11px] bg-green-50 text-green-700 px-2.5 py-1 rounded-full font-bold uppercase tracking-wider border border-green-100">
                    {Math.round(item.similarity * 100)}% Match
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </main>

      {/* App Bottom Navigation Bar */}
      <nav className="bg-white border-t border-gray-200 flex justify-around p-2 pb-6 absolute bottom-0 w-full z-20 shadow-[0_-4px_10px_rgba(0,0,0,0.02)]">
        <button className="flex flex-col items-center p-2 text-indigo-600 transition-colors">
          <span className="text-2xl mb-1 drop-shadow-sm">🛍️</span>
          <span className="text-[10px] font-bold tracking-wide">Shop</span>
        </button>
        <button className="flex flex-col items-center p-2 text-gray-400 hover:text-indigo-500 transition-colors">
          <span className="text-2xl mb-1 grayscale opacity-70">📈</span>
          <span className="text-[10px] font-semibold tracking-wide">Predict</span>
        </button>
        <button className="flex flex-col items-center p-2 text-gray-400 hover:text-indigo-500 transition-colors">
          <span className="text-2xl mb-1 grayscale opacity-70">🤖</span>
          <span className="text-[10px] font-semibold tracking-wide">AI Engine</span>
        </button>
      </nav>
    </div>
  );
}
