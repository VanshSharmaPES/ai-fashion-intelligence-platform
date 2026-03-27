"use client";
import { useState } from 'react';

const API_URL = "http://localhost:8000";

export default function Home() {
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [query, setQuery] = useState("");
  
  const handleRecommend = async () => {
    try {
      const res = await fetch(`${API_URL}/api/recommend`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query })
      });
      const data = await res.json();
      setRecommendations(data);
    } catch (e) {
      console.error(e);
      alert("Error reaching backend. Make sure it is running on port 8000.");
    }
  };

  return (
    <div style={{ padding: "40px", fontFamily: "sans-serif" }}>
      <h1>AuraX: AI-Powered Hyper-Local Fashion</h1>
      <hr />
      
      <div style={{ marginTop: "20px" }}>
        <h2>🛍️ Vibe-to-Wardrobe</h2>
        <input 
          type="text" 
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your vibe..." 
          style={{ padding: "8px", width: "300px" }}
        />
        <button onClick={handleRecommend} style={{ padding: "8px 16px", marginLeft: "10px" }}>
          Find Outfits
        </button>

        <div style={{ marginTop: "20px" }}>
          {recommendations.map(item => (
            <div key={item.sku} style={{ border: "1px solid #ccc", padding: "10px", marginBottom: "10px" }}>
              <h4>{item.name}</h4>
              <p>Price: ₹{item.price} | Similarity: {item.similarity}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
