import mongoose, { Schema, Document } from 'mongoose';

export interface IProduct extends Document {
  sku: string;
  name: string;
  price: number;
  category: string;
  imageUrl: string;
}

const ProductSchema: Schema = new Schema({
  sku: { type: String, required: true, unique: true },
  name: { type: String, required: true },
  price: { type: Number, required: true },
  category: { type: String, default: "General" },
  imageUrl: { type: String, default: "" },
}, { timestamps: true });

export default mongoose.model<IProduct>('Product', ProductSchema);
