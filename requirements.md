# AuraX: AI-Powered Hyper-Local Fashion Intelligence

## 🎯 Core Objectives (Hackathon Baseline)
1. **Multimodal Recommendation Engine:** Text + Image input suggesting products.
2. **Hyper-Local Demand Forecasting:** Predicting SKU demand per pincode using weather/events.
3. **Agentic Inventory Orchestration:** Autonomous stock reallocation between micro-warehouses.

---

## 🚀 Unique Features (To Stand Out to Judges)
*If you have time, focus on one of these to differentiate AuraX from standard e-commerce apps.*

### 1. "Vibe-to-Wardrobe" Translation (Elevated Recommendation)
Instead of just accepting "casual kurta", allow users to input a *vibe* or abstract concept.
- **Feature:** User pastes a Spotify playlist link, a Pinterest aesthetic board, or types "Rainy day working in a cozy cafe vibe."
- **Tech implementation:** Use LLMs to translate the abstract vibe into concrete fashion attributes (e.g., "dark academia", "cozy knits", "earth tones") before passing to the vector search (CLIP).

### 2. Micro-Climate & "Event-Triggered" Dynamic Pricing
- **Feature:** If unexpected rain is forecasted in a specific 5km radius via the Open-Meteo API, the system doesn't just restock umbrellas/jackets—it dynamically pops a temporary 10% discount notification to users currently active in that pincode.
- **Tech implementation:** Time-series forecasting combined with a LangChain agent that generates both a stock reallocation command *and* a marketing push notification payload.

### 3. The "Try-and-Buy" Agentic Negotiation
This capitalizes on AuraX's unique business model (delivery agent waits 15 mins for trial).
- **Feature:** If a customer is trying on 3 items and seems likely to return 1 because of price hesitation, the app's AI agent checks real-time inventory. If the warehouse is overstocked on that specific item, the agent instantly flashes a "Keep this too for 15% off right now" offer on the app while the delivery exec is at the door.
- **Tech implementation:** A small rule-based or LLM agent evaluating `current_stock_level` + `cart_abandonment_probability` to trigger a localized discount.

---

## 🏗️ Minimum Viable Demo (The "Golden Path")
*Focus the 24 hours on executing this exact flow perfectly:*

1. **User Persona (Frontend):** "Aarav" opens the Streamlit/Web UI, uploads a picture of a celebrity jacket, and types "Make it cheaper and suitable for Delhi summer."
2. **Recommendation (ML):** System returns 3 similar but breathable jackets.
3. **The Incident (Backend/Forecasting):** The dashboard shows a sudden spike in demand for these jackets in Pincode 110001 due to a local college fest.
4. **The Agent (Orchestration):** The LangGraph agent autonomously logs: *"Warehouse W1 is at 10% capacity for SKU-Jacket. Reallocating 50 units from W3 to W1 to prevent 60-min SLA failure."*
5. **Success:** Aarav completes the order, and the demo ends with a success metric dashboard.
