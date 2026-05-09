import { defineStore } from "pinia";

export type ChatContext = "catalog" | "catalog-detail" | "me-detail" | "general";

export const useUiStore = defineStore("ui", {
  state: () => ({
    copilotOpen: false,
    chatContext: "general" as ChatContext,
    chatDatasetId: null as string | null,
    pageTone: "market" as "home" | "market" | "admin" | "provider" | "vault"
  }),
  actions: {
    openCopilot(context?: ChatContext, datasetId?: string | null) {
      if (context) this.chatContext = context;
      this.chatDatasetId = datasetId ?? null;
      this.copilotOpen = true;
    },
    closeCopilot() {
      this.copilotOpen = false;
    },
    setContext(context: ChatContext, datasetId?: string | null) {
      this.chatContext = context;
      this.chatDatasetId = datasetId ?? null;
    },
    setTone(tone: "home" | "market" | "admin" | "provider" | "vault") {
      this.pageTone = tone;
    }
  }
});
