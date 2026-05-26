import { defineStore } from "pinia";

import { adminApi, systemApi } from "@/api/services";
import type { AnalysisJob, DatasetAnalysis, DatasetAsset, DatasetReview, StorageHealth, SystemStatus } from "@/api/types";

export const useAdminStore = defineStore("admin", {
  state: () => ({
    datasets: [] as DatasetAsset[],
    jobs: [] as AnalysisJob[],
    reviews: [] as DatasetReview[],
    analysis: null as DatasetAnalysis | null,
    system: null as SystemStatus | null,
    storage: null as StorageHealth | null,
    loading: false,
    error: ""
  }),
  actions: {
    async overview() {
      const [system, storage, datasets, jobs] = await Promise.all([
        systemApi.status().catch(() => null),
        systemApi.storage().catch(() => null),
        adminApi.datasets().catch(() => []),
        adminApi.jobs().catch(() => [])
      ]);
      this.system = system;
      this.storage = storage;
      this.datasets = datasets;
      this.jobs = jobs;
    },
    async loadDatasets(status?: string) {
      this.loading = true;
      try {
        this.datasets = await adminApi.datasets(status);
      } finally {
        this.loading = false;
      }
    },
    async loadJobs(filters?: { dataset_id?: string; job_status?: string }) {
      this.jobs = await adminApi.jobs(filters);
    },
    async loadReviews(filters?: { dataset_id?: string; review_status?: string }) {
      this.reviews = await adminApi.reviews(filters);
    },
    analyze(datasetId: string) {
      return adminApi.analyze(datasetId, true);
    },
    async latest(datasetId: string) {
      this.analysis = await adminApi.latestAnalysis(datasetId);
    },
    action(datasetId: string, action: "approve" | "reject" | "publish" | "archive", comment?: string) {
      return adminApi[action](datasetId, comment);
    },
    retryJob(jobId: string) {
      return adminApi.retryJob(jobId, true);
    }
  }
});
