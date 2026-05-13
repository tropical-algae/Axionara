<template>
  <section class="vault-layout page-grid">
    <header class="section-header span-all">
      <div><span class="eyebrow">AUTHORIZED DATA VAULT</span><h1>我的数据空间</h1></div>
      <RouterLink class="primary-action" to="/me/exports">导出任务</RouterLink>
    </header>

    <aside class="ops-rail">
      <MetricTile label="Granted" :value="me.datasets.length" caption="已授权数据资产" intense />
      <MetricTile label="Exports" :value="me.exports.length" caption="导出任务总数" />
      <div class="intel-panel"><strong>使用边界</strong><p>这里展示已经获取授权的数据，内容问答会使用更完整的数据上下文。</p></div>
    </aside>

    <main class="ops-board">
      <LoadingState v-if="me.loading" />
      <EmptyState v-else-if="!me.datasets.length" title="暂无授权数据" description="先从数据市场获取公开资产。" />
      <div v-else class="asset-grid">
        <DataCard v-for="item in asCatalogItems" :key="item.dataset.id" :item="item" :to="`/me/datasets/${item.dataset.id}`" />
      </div>
    </main>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";

import DataCard from "@/components/DataCard.vue";
import EmptyState from "@/components/EmptyState.vue";
import LoadingState from "@/components/LoadingState.vue";
import MetricTile from "@/components/MetricTile.vue";
import { useMeStore } from "@/stores/me";

const me = useMeStore();
const asCatalogItems = computed(() => me.datasets.map((item) => ({ dataset: item.dataset, profile: item.profile, tags: item.tags })));
onMounted(async () => {
  await Promise.all([me.loadDatasets(), me.loadExports().catch(() => undefined)]);
});
</script>
