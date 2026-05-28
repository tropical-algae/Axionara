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
        <article v-for="dataset in provider.datasets" :key="dataset.id" class="list-card provider-record-card">
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
          <div class="record-actions">
            <button type="button" @click="openProgress(dataset)"><ListChecks :size="15" />审核进度</button>
          </div>
        </article>
      </div>
    </main>
    <Modal :open="Boolean(progressDataset)" title="审核进度" @close="progressDataset = null">
      <div v-if="progressDataset" class="progress-dialog">
        <div class="progress-dialog-head">
          <StatusBadge :status="progressDataset.status" />
          <div>
            <strong>{{ progressDataset.title }}</strong>
            <span>{{ progressDataset.original_filename || progressDataset.id }}</span>
          </div>
        </div>
        <div class="progress-timeline">
          <article v-for="step in progressSteps(progressDataset.status)" :key="step.key" :class="step.state">
            <span>{{ step.index }}</span>
            <div>
              <strong>{{ step.label }}</strong>
              <em>{{ step.caption }}</em>
            </div>
          </article>
        </div>
      </div>
    </Modal>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import type { DatasetAsset } from "@/api/types";
import EmptyState from "@/components/EmptyState.vue";
import LoadingState from "@/components/LoadingState.vue";
import MetricTile from "@/components/MetricTile.vue";
import Modal from "@/components/Modal.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import { useProviderStore } from "@/stores/provider";
import { bytes } from "@/utils/format";
import { ListChecks } from "lucide-vue-next";

const provider = useProviderStore();
const pending = computed(() => provider.datasets.filter((item) => !["published", "rejected", "archived"].includes(item.status)).length);
const progressDataset = ref<DatasetAsset | null>(null);

function openProgress(dataset: DatasetAsset) {
  progressDataset.value = dataset;
}

function progressSteps(status: string) {
  const flow = [
    { key: "uploaded", label: "已提交", caption: "资产已进入审核队列" },
    { key: "processing_review", label: "管线分析", caption: "解析、清洗、质量统计和风险扫描" },
    { key: "reviewed", label: "待审核", caption: "管理员查看登记信息和分析结果" },
    { key: "approved", label: "审核通过", caption: "等待发布到数据市场" },
    { key: "published", label: "已发布", caption: "消费者可在市场中获取" }
  ];
  const activeKey = status === "published" ? "published" : status === "reviewed" ? "reviewed" : status === "processing_review" ? "processing_review" : "uploaded";
  const activeIndex = flow.findIndex((step) => step.key === activeKey);
  return flow.map((step, index) => {
    const rejected = status === "rejected" && step.key === "reviewed";
    const archived = status === "archived" && step.key === "published";
    return {
      ...step,
      index: String(index + 1).padStart(2, "0"),
      caption: rejected ? "管理员已拒绝，需要按意见重新提交" : archived ? "资产已归档，不再作为活跃市场资产展示" : step.caption,
      state: rejected ? "failed" : archived ? "active" : index < activeIndex ? "done" : index === activeIndex ? "active" : "idle"
    };
  });
}
onMounted(() => provider.load());
</script>
