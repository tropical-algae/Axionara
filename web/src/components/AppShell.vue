<template>
  <header class="topbar">
    <RouterLink class="brand" to="/">
      <img class="brand-mark" src="/axionara.svg" alt="" aria-hidden="true" />
      <span>
        <strong>Axionara</strong>
        <em>Data Asset Console</em>
      </span>
    </RouterLink>

    <nav class="nav-links">
      <RouterLink to="/catalog" :class="{ 'router-link-active': isActive('/catalog') }">数据市场</RouterLink>
      <RouterLink v-if="canUpload" to="/provider/upload" :class="{ 'router-link-active': route.path.startsWith('/provider/upload') }">数据上传</RouterLink>
      <RouterLink v-if="canUpload" to="/provider" :class="{ 'router-link-active': route.path === '/provider' }">上传记录</RouterLink>
      <RouterLink v-if="auth.role === 'admin'" to="/admin" :class="{ 'router-link-active': isActive('/admin') }">管理后台</RouterLink>
      <RouterLink v-if="auth.isAuthenticated" to="/me" :class="{ 'router-link-active': isActive('/me') }">我的数据</RouterLink>
    </nav>

    <div class="top-actions">
      <RouterLink v-if="!auth.isAuthenticated" class="ghost-link" to="/login">登录</RouterLink>
      <RouterLink v-else class="ghost-link" to="/account">{{ auth.profile?.username || "个人信息" }}</RouterLink>
    </div>
  </header>

  <main class="main-stage">
    <slot />
  </main>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const route = useRoute();
const canUpload = computed(() => auth.role === "provider" || auth.role === "admin");

function isActive(prefix: string) {
  return route.path === prefix || route.path.startsWith(`${prefix}/`);
}
</script>
