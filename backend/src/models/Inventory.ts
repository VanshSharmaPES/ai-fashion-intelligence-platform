import mongoose, { Schema, Document } from 'mongoose';

export interface IInventory extends Document {
  sku: string;
  warehouseId: string;
  pincode: string;
  currentStock: number;
  reorderThreshold: number;
}

const InventorySchema: Schema = new Schema({
  sku: { type: String, required: true },
  warehouseId: { type: String, required: true },
  pincode: { type: String, required: true },
  currentStock: { type: Number, required: true, default: 0 },
  reorderThreshold: { type: Number, required: true, default: 10 },
}, { timestamps: true });

export default mongoose.model<IInventory>('Inventory', InventorySchema);
