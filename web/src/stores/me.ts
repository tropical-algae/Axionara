import { defineStore } from "pinia";

import { meApi } from "@/api/services";
import type { ExportJob, MyDataset, RagResponse, RagStreamDone } from "@/api/types";

export const useMeStore = defineStore("me", {
  state: () => ({
    datasets: [] as MyDataset[],
    exports: [] as ExportJob[],
    loading: false,
    error: ""
  }),
  actions: {
    async loadDatasets() {
      this.loading = true;
      try {
        this.datasets = await meApi.datasets();
      } finally {
        this.loading = false;
      }
    },
    async loadExports(datasetId?: string) {
      this.exports = await meApi.exports(datasetId);
    },
    ask(datasetId: string, question: string): Promise<RagResponse> {
      return meApi.ask(datasetId, question);
    },
    streamAsk(
      datasetId: string,
      question: string,
      onDelta: (delta: string) => void | Promise<void>,
      onDone?: (payload: RagStreamDone) => void,
      signal?: AbortSignal
    ) {
      return meApi.askStream(datasetId, question, onDelta, onDone, signal);
    },
    requestExport(datasetId: string, format: string) {
      return meApi.requestExport(datasetId, format);
    },
    retry(jobId: string) {
      return meApi.retryExport(jobId);
    },
    download(job: ExportJob) {
      return meApi.download(job);
    }
  }
});
