<template>
  <section class="ops-layout page-grid">
    <header class="section-header span-all"><div><span class="eyebrow">EXPORT OPERATIONS</span><h1>导出任务</h1></div></header>
    <main class="ops-board span-all">
      <EmptyState v-if="!me.exports.length" title="暂无导出任务" description="在授权数据详情页选择格式后会生成任务。" />
      <div v-else class="asset-list">
        <article v-for="job in me.exports" :key="job.id" class="list-card">
          <StatusBadge :status="job.job_status" />
          <div><h3>{{ job.output_filename || job.dataset_id }}</h3><p>{{ job.target_format?.toUpperCase() }} / {{ bytes(job.output_size_bytes) }}</p></div>
          <button @click="me.retry(job.id)">重试</button>
          <button @click="me.download(job)">下载</button>
        </article>
      </div>
    </main>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from "vue";

import EmptyState from "@/components/EmptyState.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import { useMeStore } from "@/stores/me";
import { bytes } from "@/utils/format";

const me = useMeStore();
onMounted(() => me.loadExports());
</script>
