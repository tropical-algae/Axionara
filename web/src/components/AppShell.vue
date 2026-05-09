<template>
  <header class="topbar">
    <RouterLink class="brand" to="/">
      <span class="brand-mark">A</span>
      <span>
        <strong>Axionara</strong>
        <em>Data Asset Console</em>
      </span>
    </RouterLink>

    <nav class="nav-links">
      <RouterLink to="/catalog">数据市场</RouterLink>
      <RouterLink v-if="canUpload" to="/provider/upload">数据上传</RouterLink>
      <RouterLink v-if="auth.role === 'provider'" to="/provider">上传记录</RouterLink>
      <RouterLink v-if="auth.role === 'admin'" to="/admin">管理后台</RouterLink>
      <RouterLink v-if="auth.role === 'consumer'" to="/me">我的数据</RouterLink>
    </nav>

    <div class="top-actions">
      <button class="icon-text" type="button" @click="ui.openCopilot()">
        <Sparkles :size="16" />
        Copilot
      </button>
      <RouterLink v-if="!auth.isAuthenticated" class="ghost-link" to="/login">登录</RouterLink>
      <button v-else class="ghost-link" type="button" @click="logout">{{ auth.profile?.username || "退出" }}</button>
    </div>
  </header>

  <main class="main-stage">
    <slot />
  </main>
</template>

<script setup lang="ts">
import { Sparkles } from "lucide-vue-next";
import { computed } from "vue";
import { useRouter } from "vue-router";

import { useAuthStore } from "@/stores/auth";
import { useUiStore } from "@/stores/ui";

const auth = useAuthStore();
const router = useRouter();
const ui = useUiStore();
const canUpload = computed(() => auth.role === "provider" || auth.role === "admin");

function logout() {
  auth.logout();
  router.push("/");
}
</script>
