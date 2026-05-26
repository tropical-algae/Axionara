<template>
  <section class="ops-layout page-grid">
    <header class="section-header span-all">
      <div>
        <span class="eyebrow">PROVIDER INGEST FACTORY</span>
        <h1>数据提供者工作台</h1>
      </div>
      <RouterLink class="primary-action" to="/provider/upload">上传新数据</RouterLink>
    </header>

    <aside class="ops-rail">
      <MetricTile label="Uploads" :value="provider.datasets.length" caption="已提交资产" intense />
      <MetricTile label="Pending" :value="pending" caption="等待分析或审核" />
      <div class="intel-panel">
        <strong>摄入节奏</strong>
        <p>上传后资产会进入解析、清洗、审查和发布链路，状态将在这里持续更新。</p>
      </div>
    </aside>

    <main class="ops-board">
      <LoadingState v-if="provider.loading" />
      <EmptyState v-else-if="!provider.datasets.length" title="还没有上传数据" description="创建第一份数据资产，让分析管线开始工作。" />
      <div v-else class="asset-list">
        <article v-for="dataset in provider.datasets" :key="dataset.id" class="list-card">
          <StatusBadge :status="dataset.status" />
          <div>
            <h3>{{ dataset.title }}</h3>
            <p>{{ dataset.description || dataset.original_filename }}</p>
            <div class="meta-line">
              <span>{{ dataset.category || "未分类" }}</span>
              <span>{{ dataset.source_organization || "未填写来源" }}</span>
              <span>{{ dataset.update_frequency || "未声明频率" }}</span>
            </div>
          </div>
          <span>{{ dataset.source_format?.toUpperCase() }}</span>
          <span>{{ bytes(dataset.file_size_bytes) }}</span>
        </article>
      </div>
    </main>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";

import EmptyState from "@/components/EmptyState.vue";
import LoadingState from "@/components/LoadingState.vue";
import MetricTile from "@/components/MetricTile.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import { useProviderStore } from "@/stores/provider";
import { bytes } from "@/utils/format";

const provider = useProviderStore();
const pending = computed(() => provider.datasets.filter((item) => !["published", "rejected", "archived"].includes(item.status)).length);
onMounted(() => provider.load());
</script>
