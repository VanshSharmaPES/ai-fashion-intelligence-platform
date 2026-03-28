import mongoose from 'mongoose';
import dotenv from 'dotenv';
import Product from '../models/Product';
import Inventory from '../models/Inventory';
import AgentLog from '../models/AgentLog';
import Forecast from '../models/Forecast';

dotenv.config();

const MONGO_URI = process.env.MONGO_URI || "mongodb://127.0.0.1:27017/aurax_hackathon";

const seedDatabase = async () => {
    try {
        await mongoose.connect(MONGO_URI);
        console.log("✅ Connected to DB, clearing old data...");

        await Product.deleteMany({});
        await Inventory.deleteMany({});
        await AgentLog.deleteMany({});
        await Forecast.deleteMany({});

        console.log("📦 Inserting Mock Products...");
        await Product.insertMany([
            { sku: "SKU-101", name: "Breezy White Linen Shirt", price: 1200, category: "Summer" },
            { sku: "SKU-102", name: "Yellow Cotton Polo", price: 950, category: "Casual" }
        ]);

        console.log("🏭 Inserting Mock Inventory...");
        await Inventory.insertMany([
            { sku: "SKU-101", warehouseId: "W1", pincode: "110001", currentStock: 50, reorderThreshold: 20 },
            { sku: "SKU-101", warehouseId: "W3", pincode: "110005", currentStock: 120, reorderThreshold: 20 }
        ]);

        console.log("📈 Inserting Mock Forecasts...");
        await Forecast.insertMany([
            { pincode: "110001", sku: "SKU-101", hour: "10:00", predictedDemand: 15 },
            { pincode: "110001", sku: "SKU-101", hour: "11:00", predictedDemand: 22 }
        ]);

        console.log("🤖 Inserting Mock Agent Logs...");
        await AgentLog.insertMany([
            {
                action: "Transfer 12 units of SKU-101 from W3 to W1",
                reason: "Forecasted demand spike at 2 PM in Pincode 110001",
                timestamp: new Date("2026-03-27T10:30:00Z")
            }
        ]);

        console.log("🎉 Database Seeded Successfully!");
        process.exit(0);
    } catch (err) {
        console.error("❌ Seeding Error:", err);
        process.exit(1);
    }
};

seedDatabase();
