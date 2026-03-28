import mongoose, { Schema, Document } from 'mongoose';

export interface IAgentLog extends Document {
  action: string;
  reason: string;
  timestamp: Date;
}

const AgentLogSchema: Schema = new Schema({
  action: { type: String, required: true },
  reason: { type: String, required: true },
  timestamp: { type: Date, default: Date.now }
});

export default mongoose.model<IAgentLog>('AgentLog', AgentLogSchema);
