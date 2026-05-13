<template>
  <section class="ops-layout page-grid">
    <header class="section-header span-all">
      <div><span class="eyebrow">REVIEW QUEUE</span><h1>数据审核</h1></div>
      <div class="chip-row">
        <button v-for="status in statuses" :key="status || 'all'" :class="{ active: filter === status }" @click="setStatus(status)">
          {{ status || "全部" }}
        </button>
      </div>
    </header>

    <main class="ops-board span-all">
      <LoadingState v-if="admin.loading" />
      <div v-else class="asset-list">
        <article v-for="dataset in admin.datasets" :key="dataset.id" class="list-card action-card">
          <StatusBadge :status="dataset.status" />
          <div>
            <h3>{{ dataset.title }}</h3>
            <p>{{ dataset.description || dataset.original_filename }}</p>
            <div class="meta-line">
              <span>{{ dataset.category || "未分类" }}</span>
              <span>{{ dataset.sensitivity_level || "未声明敏感性" }}</span>
              <span>{{ dataset.access_policy || "未声明授权" }}</span>
            </div>
          </div>
          <button @click="runAnalyze(dataset.id)">分析</button>
          <button @click="admin.latest(dataset.id)">结果</button>
          <button @click="act(dataset.id, 'approve')">通过</button>
          <button @click="act(dataset.id, 'publish')">发布</button>
          <button @click="act(dataset.id, 'reject')">拒绝</button>
          <button @click="act(dataset.id, 'archive')">归档</button>
        </article>
      </div>
      <section v-if="admin.analysis" class="analysis-panel">
        <h2>最新分析结果</h2>
        <div class="narrative-grid">
          <article><strong>分析状态</strong><p>{{ admin.analysis.analysis_status }}</p></article>
          <article><strong>表示类型</strong><p>{{ admin.analysis.representation_type || "-" }}</p></article>
          <article><strong>内部摘要</strong><p>{{ admin.analysis.internal_summary || "无" }}</p></article>
        </div>
      </section>
    </main>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";

import LoadingState from "@/components/LoadingState.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import { useAdminStore } from "@/stores/admin";

const admin = useAdminStore();
const filter = ref<string | undefined>();
const statuses = ["", "uploaded", "analyzing", "reviewing", "approved", "published", "rejected", "archived"];

function setStatus(status: string) {
  filter.value = status || undefined;
  admin.loadDatasets(filter.value);
}
async function runAnalyze(id: string) {
  await admin.analyze(id);
  await admin.loadDatasets(filter.value);
}
async function act(id: string, action: "approve" | "reject" | "publish" | "archive") {
  await admin.action(id, action);
  await admin.loadDatasets(filter.value);
}
onMounted(() => admin.loadDatasets());
</script>
