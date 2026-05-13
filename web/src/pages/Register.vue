<template>
  <section class="auth-page">
    <form class="auth-panel wide" @submit.prevent="submit">
      <span class="eyebrow">ROLE PROVISIONING</span>
      <h1>创建平台身份</h1>
      <div class="role-grid">
        <button v-for="option in roles" :key="option.role" type="button" :class="{ active: role === option.role }" @click="role = option.role">
          <component :is="option.icon" :size="22" />
          <strong>{{ option.title }}</strong>
          <span>{{ option.copy }}</span>
        </button>
      </div>
      <div class="form-grid">
        <label>用户名<input v-model="form.username" /></label>
        <label>邮箱<input v-model="form.email" type="email" /></label>
        <label>姓名<input v-model="form.full_name" /></label>
        <label>组织<input v-model="form.organization" /></label>
      </div>
      <label>密码<input v-model="form.password" type="password" /></label>
      <button class="primary-action" type="submit" :disabled="auth.loading">创建并进入</button>
    </form>
  </section>
</template>

<script setup lang="ts">
import { Building2, Crown, UserRound } from "lucide-vue-next";
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";

import type { Role } from "@/api/types";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const router = useRouter();
const role = ref<Role>("consumer");
const form = reactive({ username: "", email: "", password: "", full_name: "", organization: "" });
const roles = [
  { role: "consumer" as Role, icon: UserRound, title: "数据使用者", copy: "发现、获取、问答与导出" },
  { role: "provider" as Role, icon: Building2, title: "数据提供者", copy: "上传资产并跟踪发布" },
  { role: "admin" as Role, icon: Crown, title: "管理员", copy: "审核、分析与治理" }
];

async function submit() {
  await auth.register({ ...form, role: role.value });
  router.push(auth.landing);
}
</script>
