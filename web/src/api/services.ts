import { api } from "@/api/client";
import type {
  AccessGrant,
  AnalysisJob,
  CatalogDataset,
  CatalogQuery,
  DatasetAnalysis,
  DatasetAsset,
  DatasetUploadPayload,
  DatasetReview,
  ExportJob,
  MyDataset,
  RagResponse,
  RegisterPayload,
  StorageHealth,
  SystemStatus,
  Tag,
  TokenResponse,
  UserProfile
} from "@/api/types";

export const authApi = {
  register: (payload: RegisterPayload) => api.post<UserProfile>("/api/v1/auth/register", payload),
  login(username: string, password: string) {
    const form = new URLSearchParams();
    form.set("username", username);
    form.set("password", password);
    return api.post<TokenResponse>("/api/v1/auth/access-token", form);
  },
  me: () => api.get<UserProfile>("/api/v1/auth/me")
};

export const systemApi = {
  status: () => api.get<SystemStatus>("/api/v1/system/status"),
  storage: () => api.get<StorageHealth>("/api/v1/system/storage")
};

export const catalogApi = {
  datasets: (query?: CatalogQuery) => api.get<CatalogDataset[]>("/api/v1/catalog/datasets", query),
  detail: (id: string) => api.get<CatalogDataset>(`/api/v1/catalog/datasets/${id}`),
  tags: () => api.get<Tag[]>("/api/v1/catalog/tags"),
  ask: (question: string, dataset_id?: string, tag_slug?: string, limit = 5) =>
    api.post<RagResponse>("/api/v1/catalog/ask", { question, dataset_id, tag_slug, limit }),
  askDataset: (datasetId: string, question: string, limit = 5) =>
    api.post<RagResponse>(`/api/v1/catalog/datasets/${datasetId}/ask`, { question, limit }),
  acquire: (datasetId: string) => api.post<AccessGrant>(`/api/v1/catalog/datasets/${datasetId}/acquire`)
};

export const providerApi = {
  datasets: () => api.get<DatasetAsset[]>("/api/v1/provider/datasets"),
  detail: (id: string) => api.get<DatasetAsset>(`/api/v1/provider/datasets/${id}`),
  upload(payload: DatasetUploadPayload) {
    const form = new FormData();
    const fields: Array<keyof Omit<DatasetUploadPayload, "file">> = [
      "title",
      "description",
      "category",
      "source_organization",
      "coverage_start",
      "coverage_end",
      "update_frequency",
      "sensitivity_level",
      "intended_visibility",
      "access_policy",
      "usage_restrictions",
      "contact_name",
      "contact_email"
    ];
    fields.forEach((key) => {
      const value = payload[key];
      if (value) form.append(key, value);
    });
    form.append("file", payload.file);
    return api.post<DatasetAsset>("/api/v1/provider/datasets/upload", form);
  }
};

export const adminApi = {
  datasets: (status?: string) => api.get<DatasetAsset[]>("/api/v1/admin/datasets", { status }),
  analyze: (datasetId: string, use_llm = true) =>
    api.post<AnalysisJob>(`/api/v1/admin/datasets/${datasetId}/analyze`, undefined, { use_llm }),
  latestAnalysis: (datasetId: string) => api.get<DatasetAnalysis>(`/api/v1/admin/datasets/${datasetId}/analysis/latest`),
  approve: (datasetId: string, comment?: string) => api.post<DatasetReview>(`/api/v1/admin/datasets/${datasetId}/approve`, { comment }),
  reject: (datasetId: string, comment?: string) => api.post<DatasetReview>(`/api/v1/admin/datasets/${datasetId}/reject`, { comment }),
  publish: (datasetId: string, comment?: string) => api.post<DatasetReview>(`/api/v1/admin/datasets/${datasetId}/publish`, { comment }),
  archive: (datasetId: string, comment?: string) => api.post<DatasetReview>(`/api/v1/admin/datasets/${datasetId}/archive`, { comment }),
  jobs: (filters?: { dataset_id?: string; job_status?: string }) => api.get<AnalysisJob[]>("/api/v1/admin/analysis-jobs", filters),
  retryJob: (jobId: string, use_llm = true) => api.post<AnalysisJob>(`/api/v1/admin/analysis-jobs/${jobId}/retry`, undefined, { use_llm }),
  reviews: (filters?: { dataset_id?: string; review_status?: string }) => api.get<DatasetReview[]>("/api/v1/admin/reviews", filters)
};

export const meApi = {
  datasets: () => api.get<MyDataset[]>("/api/v1/me/datasets"),
  ask: (datasetId: string, question: string, limit = 5) => api.post<RagResponse>(`/api/v1/me/datasets/${datasetId}/ask`, { question, limit }),
  requestExport: (datasetId: string, target_format: string) =>
    api.post<ExportJob>(`/api/v1/me/datasets/${datasetId}/exports`, { target_format }),
  exports: (dataset_id?: string) => api.get<ExportJob[]>("/api/v1/me/exports", { dataset_id }),
  retryExport: (jobId: string) => api.post<ExportJob>(`/api/v1/me/exports/${jobId}/retry`),
  download(job: ExportJob) {
    return api.download(`/api/v1/me/exports/${job.id}/download`, job.output_filename || `${job.dataset_id}.${job.target_format}`);
  }
};
