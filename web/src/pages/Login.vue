<template>
  <section class="auth-page login-page">
    <form class="auth-panel login-panel" @submit.prevent="submit">
      <div class="login-heading">
        <span class="eyebrow">IDENTITY ACCESS</span>
        <h1>登录 Axionara</h1>
        <p>进入数据资产控制台，继续上传、审核、获取和问答工作流。</p>
      </div>

      <div class="login-fields">
        <label>用户名<input v-model="username" autocomplete="username" placeholder="输入用户名" /></label>
        <label>密码<input v-model="password" type="password" autocomplete="current-password" placeholder="输入密码" /></label>
      </div>

      <p v-if="auth.error" class="form-error">{{ auth.error }}</p>

      <div class="login-actions">
        <button class="primary-action" type="submit" :disabled="auth.loading">进入控制面</button>
        <RouterLink class="inline-link" to="/register">注册角色身份</RouterLink>
      </div>
    </form>

    <aside class="login-context">
      <div>
        <span class="eyebrow">ROLE WORKSPACE</span>
        <h2>一个入口，三类工作台。</h2>
        <p>登录后会根据你的角色进入对应页面，减少重复导航和无关入口。</p>
      </div>

      <div class="login-role-list">
        <article>
          <strong>Provider</strong>
          <span>上传资产、查看处理状态、等待审核发布。</span>
        </article>
        <article>
          <strong>Admin</strong>
          <span>运行分析、处理审核队列、管理发布状态。</span>
        </article>
        <article>
          <strong>Consumer</strong>
          <span>获取授权数据、发起问答、创建导出任务。</span>
        </article>
      </div>
    </aside>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const route = useRoute();
const router = useRouter();
const username = ref("");
const password = ref("");

async function submit() {
  await auth.login(username.value, password.value);
  router.push(String(route.query.redirect || auth.landing));
}
</script>
