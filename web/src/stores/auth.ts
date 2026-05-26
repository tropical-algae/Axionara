import { defineStore } from "pinia";

import type { RegisterPayload, Role, UserProfile } from "@/api/types";
import { authApi } from "@/api/services";

const TOKEN_KEY = "axionara.token";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) as string | null,
    profile: null as UserProfile | null,
    loading: false,
    error: ""
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token),
    role: (state): Role | "guest" => (state.profile?.role as Role) || "guest",
    landing(): string {
      if (this.role === "admin") return "/admin";
      if (this.role === "provider") return "/provider";
      if (this.role === "consumer") return "/catalog";
      return "/catalog";
    }
  },
  actions: {
    setToken(token: string | null) {
      this.token = token;
      if (token) localStorage.setItem(TOKEN_KEY, token);
      else localStorage.removeItem(TOKEN_KEY);
    },
    async refresh() {
      if (!this.token) return;
      try {
        this.profile = await authApi.me();
      } catch {
        this.setToken(null);
        this.profile = null;
      }
    },
    async login(username: string, password: string) {
      this.loading = true;
      this.error = "";
      try {
        const response = await authApi.login(username, password);
        this.setToken(response.access_token);
        this.profile = await authApi.me();
      } catch (error) {
        this.error = error instanceof Error ? error.message : "登录失败";
        throw error;
      } finally {
        this.loading = false;
      }
    },
    async register(payload: RegisterPayload) {
      this.loading = true;
      this.error = "";
      try {
        this.profile = await authApi.register(payload);
        await this.login(payload.username, payload.password);
      } finally {
        this.loading = false;
      }
    },
    logout() {
      this.setToken(null);
      this.profile = null;
    }
  }
});
