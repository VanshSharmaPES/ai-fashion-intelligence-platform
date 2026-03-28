import mongoose, { Schema, Document } from 'mongoose';

export interface IForecast extends Document {
  pincode: string;
  sku: string;
  hour: string;
  predictedDemand: number;
}

const ForecastSchema: Schema = new Schema({
  pincode: { type: String, required: true },
  sku: { type: String, required: true },
  hour: { type: String, required: true },
  predictedDemand: { type: Number, required: true }
});

export default mongoose.model<IForecast>('Forecast', ForecastSchema);
