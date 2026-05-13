<template>
  <section class="admin-command page-grid">
    <header class="section-header span-all">
      <div>
        <span class="eyebrow">ADMIN COMMAND CENTER</span>
        <h1>治理控制台</h1>
      </div>
      <nav class="segment-nav">
        <RouterLink to="/admin/datasets">审核数据</RouterLink>
        <RouterLink to="/admin/jobs">分析任务</RouterLink>
        <RouterLink to="/admin/reviews">审核记录</RouterLink>
      </nav>
    </header>

    <div class="metric-matrix span-all">
      <MetricTile label="System" :value="admin.system?.status || 'unknown'" :caption="admin.system?.version || 'service status'" intense />
      <MetricTile label="Storage" :value="admin.storage?.status || 'unknown'" :caption="admin.storage?.backend || 'object layer'" />
      <MetricTile label="Datasets" :value="admin.datasets.length" caption="审核队列" />
      <MetricTile label="Jobs" :value="admin.jobs.length" caption="分析任务" />
    </div>

    <main class="ops-board span-all">
      <div class="status-river">
        <article v-for="item in distribution" :key="item.status">
          <span :style="{ width: `${Math.max(item.count * 16, 18)}%` }" />
          <strong>{{ item.status }}</strong>
          <em>{{ item.count }}</em>
        </article>
      </div>
    </main>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";

import MetricTile from "@/components/MetricTile.vue";
import { useAdminStore } from "@/stores/admin";

const admin = useAdminStore();
const distribution = computed(() => {
  const map = new Map<string, number>();
  admin.datasets.forEach((item) => map.set(item.status, (map.get(item.status) || 0) + 1));
  return Array.from(map, ([status, count]) => ({ status, count }));
});
onMounted(() => admin.overview());
</script>
