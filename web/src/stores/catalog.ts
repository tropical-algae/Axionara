import { defineStore } from "pinia";

import { catalogApi } from "@/api/services";
import type { CatalogDataset, CatalogQuery, RagResponse, Tag } from "@/api/types";

export const useCatalogStore = defineStore("catalog", {
  state: () => ({
    datasets: [] as CatalogDataset[],
    detail: null as CatalogDataset | null,
    tags: [] as Tag[],
    query: {} as CatalogQuery,
    loading: false,
    error: ""
  }),
  getters: {
    categories: (state) => Array.from(new Set(state.tags.map((tag) => tag.category).filter(Boolean))),
    formats: (state) => Array.from(new Set(state.datasets.map((item) => item.dataset.source_format).filter(Boolean)))
  },
  actions: {
    async loadTags() {
      this.tags = await catalogApi.tags();
    },
    async loadDatasets(query?: CatalogQuery) {
      this.loading = true;
      this.error = "";
      this.query = { ...(query ?? this.query) };
      try {
        this.datasets = await catalogApi.datasets(this.query);
      } catch (error) {
        this.error = error instanceof Error ? error.message : "数据市场暂不可用";
      } finally {
        this.loading = false;
      }
    },
    async loadDetail(id: string) {
      this.loading = true;
      this.error = "";
      try {
        this.detail = await catalogApi.detail(id);
      } catch (error) {
        this.error = error instanceof Error ? error.message : "数据详情暂不可用";
      } finally {
        this.loading = false;
      }
    },
    ask(question: string, datasetId?: string): Promise<RagResponse> {
      return datasetId ? catalogApi.askDataset(datasetId, question) : catalogApi.ask(question, undefined, this.query.tag_slug);
    },
    acquire(datasetId: string) {
      return catalogApi.acquire(datasetId);
    }
  }
});
