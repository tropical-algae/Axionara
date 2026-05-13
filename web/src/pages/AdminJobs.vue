<template>
  <section class="ops-layout page-grid">
    <header class="section-header span-all"><div><span class="eyebrow">ANALYSIS JOBS</span><h1>分析任务</h1></div></header>
    <main class="ops-board span-all">
      <div class="asset-list">
        <article v-for="job in admin.jobs" :key="job.id" class="list-card">
          <StatusBadge :status="job.job_status" />
          <div><h3>{{ job.dataset_id }}</h3><p>{{ job.current_stage || job.error_message || "等待调度" }}</p></div>
          <span>{{ dateTime(job.create_date) }}</span>
          <button @click="retry(job.id)">重试</button>
        </article>
      </div>
    </main>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from "vue";

import StatusBadge from "@/components/StatusBadge.vue";
import { useAdminStore } from "@/stores/admin";
import { dateTime } from "@/utils/format";

const admin = useAdminStore();
async function retry(id: string) {
  await admin.retryJob(id);
  await admin.loadJobs();
}
onMounted(() => admin.loadJobs());
</script>
