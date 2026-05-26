import { createRouter, createWebHistory } from "vue-router";

import { useAuthStore } from "@/stores/auth";
import { useUiStore } from "@/stores/ui";

const routes = [
  { path: "/", name: "home", component: () => import("@/pages/Home.vue"), meta: { tone: "home" } },
  { path: "/login", name: "login", component: () => import("@/pages/Login.vue"), meta: { public: true, tone: "home" } },
  { path: "/register", name: "register", component: () => import("@/pages/Register.vue"), meta: { public: true, tone: "home" } },
  { path: "/catalog", name: "catalog", component: () => import("@/pages/Catalog.vue"), meta: { tone: "market", chat: "catalog" } },
  { path: "/catalog/:id", name: "catalog-detail", component: () => import("@/pages/CatalogDetail.vue"), meta: { tone: "market", chat: "catalog-detail" } },
  { path: "/provider", name: "provider", component: () => import("@/pages/ProviderDashboard.vue"), meta: { auth: true, roles: ["provider", "admin"], tone: "provider" } },
  { path: "/provider/upload", name: "provider-upload", component: () => import("@/pages/ProviderUpload.vue"), meta: { auth: true, roles: ["provider", "admin"], tone: "provider" } },
  { path: "/admin", name: "admin", component: () => import("@/pages/AdminDashboard.vue"), meta: { auth: true, roles: ["admin"], tone: "admin" } },
  { path: "/admin/datasets", name: "admin-datasets", component: () => import("@/pages/AdminDatasets.vue"), meta: { auth: true, roles: ["admin"], tone: "admin" } },
  { path: "/admin/jobs", name: "admin-jobs", component: () => import("@/pages/AdminJobs.vue"), meta: { auth: true, roles: ["admin"], tone: "admin" } },
  { path: "/admin/reviews", name: "admin-reviews", component: () => import("@/pages/AdminReviews.vue"), meta: { auth: true, roles: ["admin"], tone: "admin" } },
  { path: "/me", name: "me", component: () => import("@/pages/MeDashboard.vue"), meta: { auth: true, roles: ["consumer"], tone: "vault" } },
  { path: "/me/datasets/:id", name: "me-detail", component: () => import("@/pages/MeDatasetDetail.vue"), meta: { auth: true, roles: ["consumer"], tone: "vault", chat: "me-detail" } },
  { path: "/me/exports", name: "me-exports", component: () => import("@/pages/MeExports.vue"), meta: { auth: true, roles: ["consumer"], tone: "vault" } },
  { path: "/:pathMatch(.*)*", name: "not-found", component: () => import("@/pages/NotFound.vue"), meta: { tone: "home" } }
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 })
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();
  const ui = useUiStore();
  ui.setTone((to.meta.tone as "home" | "market" | "admin" | "provider" | "vault") || "market");
  ui.setContext((to.meta.chat as never) || "general", typeof to.params.id === "string" ? to.params.id : null);

  if (auth.token && !auth.profile) await auth.refresh();
  if (to.meta.auth && !auth.isAuthenticated) return { path: "/login", query: { redirect: to.fullPath } };
  const roles = to.meta.roles as string[] | undefined;
  if (roles?.length && auth.profile && !roles.includes(String(auth.profile.role))) return auth.landing;
  return true;
});
