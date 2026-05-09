import { defineStore } from "pinia";

import { providerApi } from "@/api/services";
import type { DatasetAsset, DatasetUploadPayload } from "@/api/types";

export const useProviderStore = defineStore("provider", {
  state: () => ({
    datasets: [] as DatasetAsset[],
    loading: false,
    error: ""
  }),
  actions: {
    async load() {
      this.loading = true;
      this.error = "";
      try {
        this.datasets = await providerApi.datasets();
      } catch (error) {
        this.error = error instanceof Error ? error.message : "无法加载上传数据";
      } finally {
        this.loading = false;
      }
    },
    upload(payload: DatasetUploadPayload) {
      return providerApi.upload(payload);
    }
  }
});
