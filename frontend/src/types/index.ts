// API Response Types
export interface ApiResponse {
  summary: string;
  visualization?: VisualizationData;
  tableData?: TableData;
  sqlQuery: string;
  executionTime: number;
}

export interface VisualizationData {
  type: 'bar_chart' | 'line_chart' | 'pie_chart' | 'table';
  data: any[];
  dataKey?: string;
  barKey?: string;
  title?: string;
}

export interface TableData {
  columns: string[];
  rows: string[][];
}

// Chat Message Types
export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  data?: ApiResponse;
}

// Sample Query Types
export interface SampleQuery {
  id: string;
  question: string;
  category: string;
}

// Database Schema Types
export interface DatabaseTable {
  name: string;
  columns: Record<string, ColumnInfo>;
  primary_keys: string[];
  foreign_keys: ForeignKey[];
}

export interface ColumnInfo {
  data_type: string;
  is_nullable: boolean;
  column_default: string | null;
}

export interface ForeignKey {
  column: string;
  references_table: string;
  references_column: string;
}

// Application State Types
export interface AppState {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  sampleQueries: SampleQuery[];
  databaseTables: string[];
}
