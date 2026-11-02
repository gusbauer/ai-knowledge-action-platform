export interface AgentSource {
  chunk_id: number;
  document_id: number;
  position: number;
  similarity: number;
  content: string;
}

export interface AgentRequest {
  question: string;
  thread_id?: string;
  limit?: number;
  min_similarity?: number;
}

export interface AgentResumeRequest {
  thread_id: string;
  approved: boolean;
  note?: string;
}

export interface AgentResponse {
  thread_id: string;

  status: 'completed' | 'interrupted';

  question?: string;
  answer?: string;

  route?: 'knowledge' | 'system';

  handled_by?: 'knowledge' | 'system';

  tool_used?: string;

  sources: AgentSource[];

  interrupt?: Record<string, unknown>;
}

export interface HealthReadyResponse {
  status: string;
  database: string;
  cache: string;
}
