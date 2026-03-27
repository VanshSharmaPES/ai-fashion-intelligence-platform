import express, { Request, Response } from 'express';
import cors from 'cors';
import connectDB from './config/db';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

// Initialize Database connection (Uncomment when you have a local MongoDB running or an Atlas URI in .env)
// connectDB();

const PORT = process.env.PORT || 8000;

// --- Mock Data ---
const FASHION_MOCK = [
    { sku: "SKU-101", name: "Breezy White Linen Shirt", similarity: 0.95, price: 1200 },
    { sku: "SKU-102", name: "Yellow Cotton Polo", similarity: 0.88, price: 950 }
];

const FORECAST_MOCK: Record<string, any[]> = {
    "110001": [
        { hour: "10:00", sku: "SKU-101", predicted_demand: 15 },
        { hour: "11:00", sku: "SKU-101", predicted_demand: 22 },
    ]
};

const AGENT_LOGS_MOCK = [
    {
        timestamp: "2026-03-27T10:30:00Z",
        action: "Transfer 12 units of SKU-101 from W3 to W1",
        reason: "Forecasted demand spike at 2 PM in Pincode 110001"
    }
];

// --- Endpoints ---

app.get('/', (req: Request, res: Response) => {
    res.json({ message: "Welcome to AuraX AI APIS." });
});

app.post('/api/recommend', (req: Request, res: Response) => {
    // req.body should have query, optionally user_id, image_url
    res.json(FASHION_MOCK);
});

app.get('/api/forecast/:pincode', (req: Request, res: Response) => {
    const pincode = req.params.pincode;
    if (!FORECAST_MOCK[pincode]) {
        res.json({ pincode, forecast: FORECAST_MOCK["110001"] });
    } else {
        res.json({ pincode, forecast: FORECAST_MOCK[pincode] });
    }
});

app.get('/api/inventory/agent-logs', (req: Request, res: Response) => {
    res.json(AGENT_LOGS_MOCK);
});

app.listen(PORT, () => {
    console.log(`Server is running at http://localhost:${PORT}`);
});
