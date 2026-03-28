# AuraX: AI-Powered Hyper-Local Fashion Intelligence

AuraX is a next-generation quick-commerce fashion platform delivering curated apparel to customers' doorsteps within 60 minutes. It features a completely responsive, native-feeling mobile layout and intelligent real-time processing.

## 🌟 Key Features
1. **Multimodal Recommendation Engine:** Converts abstract text ("rainy cozy cafe vibe") into vector representations using OpenAI's CLIP, delivering hyper-personalized wardrobe curations.
2. **Hyper-Local Demand Forecasting:** Uses time-series models to predict SKU-level demand per pin code within specific delivery radiuses.
3. **Agentic Inventory Orchestration:** Autonomous stock reallocation (utilizing LangGraph/LLMs) across micro-warehouses to maintain strict 60-minute SLA targets.

## 🏗️ Tech Stack
- **Frontend:** Next.js 14, React, Tailwind CSS, TypeScript (Mobile-first Layout)
- **Backend:** Node.js, Express, TypeScript, MongoDB (Mongoose)
- **AI/ML:** Python, Jupyter, PyTorch, Transformers (`openai/clip-vit-base-patch32`)

---

## 🚀 Getting Started

### 1. Start the Backend (Node.js/Express)
The backend returns mock API data to ensure the frontend operates smoothly without needing the Mongoose/MongoDB connection immediately. To connect a database later, define `MONGO_URI` in `/backend/.env` and uncomment `connectDB()` in `backend/src/index.ts`.
```bash
cd backend
npm install
npm run dev
```
*API runs on: `http://localhost:8000`*
*(Tip: Import `AuraX_APIs.postman_collection.json` into Postman for instant route testing)*

### 2. Start the Frontend (Next.js Application)
```bash
cd frontend
npm install
npm run dev
```
*Web App runs on: `http://localhost:3000`*

---

## 📱 Mobile App Testing (Local Network)
AuraX was built with a mobile UI structure. To view the native app layout dynamically on your smartphone:
1. Find your computer's local IP address (e.g. `192.168.1.15`) typing `ipconfig` (Windows) or `ifconfig` (Mac/Linux).
2. Start the frontend securely to bypass SSL mixed-content restrictions on mobile devices:
   ```bash
   cd frontend
   npm run dev:mobile
   ```
3. On your mobile phone (on the same Wi-Fi), browse to `https://<YOUR-IP>:3000` 
*(Note: As this is a self-signed development certificate, bypass the browser warning by clicking "Advanced -> Proceed").*

---

## 🧠 Machine Learning & Data Pipeline
- All ML logic resides in `/models`. 
- Open `/models/pipeline_template.ipynb` for the boilerplates to generate and export HuggingFace CLIP image embeddings from the Kaggle Fashion dataset.

