<template>
  <section class="account-page page-grid">
    <header class="section-header span-all">
      <div>
        <span class="eyebrow">ACCOUNT</span>
        <h1>个人信息</h1>
      </div>
    </header>

    <main class="account-panel span-all">
      <section class="account-summary">
        <span class="account-avatar">{{ initials }}</span>
        <div>
          <strong>{{ auth.profile?.full_name || auth.profile?.username || "未登录用户" }}</strong>
          <p>{{ auth.profile?.organization || "未设置组织" }}</p>
        </div>
      </section>

      <dl class="account-fields">
        <div><dt>用户名</dt><dd>{{ auth.profile?.username || "-" }}</dd></div>
        <div><dt>邮箱</dt><dd>{{ auth.profile?.email || "-" }}</dd></div>
        <div><dt>角色</dt><dd>{{ roleLabel }}</dd></div>
        <div><dt>组织</dt><dd>{{ auth.profile?.organization || "-" }}</dd></div>
        <div><dt>创建时间</dt><dd>{{ dateTime(auth.profile?.create_date) }}</dd></div>
      </dl>

      <footer class="account-actions">
        <RouterLink class="secondary-action" to="/me">我的数据</RouterLink>
        <button class="secondary-action" type="button" @click="logout">退出登录</button>
      </footer>
    </main>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRouter } from "vue-router";

import { useAuthStore } from "@/stores/auth";
import { dateTime } from "@/utils/format";

const auth = useAuthStore();
const router = useRouter();
const roleLabels: Record<string, string> = {
  admin: "管理员",
  provider: "数据提供者",
  consumer: "数据使用者"
};
const roleLabel = computed(() => roleLabels[String(auth.profile?.role || "")] || auth.profile?.role || "-");
const initials = computed(() => (auth.profile?.full_name || auth.profile?.username || "A").slice(0, 1).toUpperCase());

function logout() {
  auth.logout();
  router.push("/");
}
</script>
