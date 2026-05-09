export type Role = "admin" | "provider" | "consumer";

export interface UserProfile {
  id: string;
  username: string;
  email: string;
  full_name?: string | null;
  organization?: string | null;
  role: Role | string;
  is_active?: boolean | null;
  create_date?: string | null;
}

export interface TokenResponse {
  user_id: string;
  access_token: string;
  token_type: string;
  scopes: string[];
}

export interface RegisterPayload {
  username: string;
  password: string;
  email: string;
  full_name?: string;
  organization?: string;
  role: Role;
}

export interface SystemStatus {
  status: string;
  version?: string;
}

export interface StorageHealth {
  status: string;
  backend?: string;
  details?: Record<string, unknown>;
}

export interface DatasetAsset {
  id: string;
  title: string;
  description?: string | null;
  category?: string | null;
  source_organization?: string | null;
  coverage_start?: string | null;
  coverage_end?: string | null;
  update_frequency?: string | null;
  sensitivity_level?: string | null;
  intended_visibility?: string | null;
  access_policy?: string | null;
  usage_restrictions?: string | null;
  contact_name?: string | null;
  contact_email?: string | null;
  owner_id?: string;
  source_format: string;
  representation_hint?: string | null;
  original_filename?: string;
  storage_uri?: string;
  raw_bucket?: string | null;
  raw_object_key?: string | null;
  content_type?: string | null;
  etag?: string | null;
  file_size_bytes?: number;
  status: string;
  create_date?: string | null;
  update_date?: string | null;
}

export interface DatasetUploadPayload {
  title: string;
  description?: string;
  category?: string;
  source_organization?: string;
  coverage_start?: string;
  coverage_end?: string;
  update_frequency?: string;
  sensitivity_level?: string;
  intended_visibility?: string;
  access_policy?: string;
  usage_restrictions?: string;
  contact_name?: string;
  contact_email?: string;
  file: File;
}

export interface DatasetProfile {
  id: string;
  dataset_id: string;
  analysis_id?: string;
  public_summary?: string;
  processing_summary?: string;
  cleaning_summary?: string;
  risk_summary?: string | null;
  public_statistics?: Record<string, unknown>;
  allowed_export_formats?: string[];
  public_rag_text?: string;
  tag_summary?: string | null;
  update_date?: string | null;
}

export interface CatalogDataset {
  dataset: DatasetAsset;
  profile?: DatasetProfile | null;
  tags?: string[];
}

export interface Tag {
  id: string;
  name: string;
  slug: string;
  category: string;
  description?: string | null;
  source?: string;
  is_active?: boolean;
}

export interface CatalogQuery {
  keyword?: string;
  tag_slug?: string;
  category?: string;
  source_format?: string;
}

export interface RagMatch {
  dataset_id: string;
  title?: string;
  chunk_id?: string;
  score: number;
  tags?: string[];
  snippet: string;
}

export interface RagResponse {
  question: string;
  answer: string;
  matches?: RagMatch[];
  source_scope?: string;
  raw_content_used?: boolean;
}

export interface AccessGrant {
  id: string;
  dataset_id: string;
  user_id: string;
  grant_method: string;
  grant_status: string;
  note?: string | null;
  granted_at?: string | null;
  expires_at?: string | null;
  create_date?: string | null;
}

export interface MyDataset {
  grant: AccessGrant;
  dataset: DatasetAsset;
  profile?: DatasetProfile | null;
  tags?: string[];
}

export interface AnalysisJob {
  id: string;
  dataset_id: string;
  triggered_by?: string;
  job_status: string;
  current_stage?: string | null;
  error_message?: string | null;
  started_at?: string | null;
  finished_at?: string | null;
  create_date?: string | null;
}

export interface DatasetAnalysis {
  id: string;
  dataset_id: string;
  job_id?: string | null;
  analysis_version?: number;
  analysis_status: string;
  representation_type?: string;
  parser_status?: string;
  cleaning_status?: string;
  sensitivity_status?: string;
  summary_status?: string;
  tag_status?: string;
  schema_snapshot?: Record<string, unknown>;
  statistics?: Record<string, unknown>;
  issues?: Record<string, unknown>;
  cleaning_actions?: Record<string, unknown>;
  skipped_steps?: Record<string, unknown>;
  export_capabilities?: Record<string, unknown>;
  sensitivity_report?: Record<string, unknown>;
  suggested_tags?: Record<string, unknown>;
  internal_summary?: string | null;
  llm_output_json?: Record<string, unknown> | null;
  create_date?: string | null;
  update_date?: string | null;
}

export interface DatasetReview {
  id: string;
  dataset_id: string;
  analysis_id?: string;
  reviewer_id?: string;
  review_status: string;
  review_comment?: string | null;
  publish_comment?: string | null;
  reviewed_at?: string | null;
  published_at?: string | null;
  create_date?: string | null;
}

export interface ExportJob {
  id: string;
  dataset_id: string;
  user_id?: string;
  grant_id?: string;
  target_format: string;
  job_status: string;
  error_message?: string | null;
  output_bucket?: string | null;
  output_object_key?: string | null;
  output_filename?: string | null;
  output_content_type?: string | null;
  output_size_bytes?: number;
  started_at?: string | null;
  finished_at?: string | null;
  create_date?: string | null;
  update_date?: string | null;
}
