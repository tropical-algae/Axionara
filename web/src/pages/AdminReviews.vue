<template>
  <section class="ops-layout page-grid">
    <header class="section-header span-all">
      <div><span class="eyebrow">REVIEW LEDGER</span><h1>审核记录</h1></div>
      <div class="chip-row">
        <button v-for="status in filters" :key="status.value || 'all'" :class="{ active: activeStatus === status.value }" @click="setStatus(status.value)">
          {{ status.label }}
        </button>
      </div>
    </header>
    <main class="ops-board span-all">
      <LoadingState v-if="loading" text="正在加载审核记录..." />
      <EmptyState v-else-if="!admin.reviews.length" title="暂无审核记录" description="管理员执行通过、拒绝、发布或归档后会形成记录。" />
      <div v-else class="asset-list review-ledger-list">
        <article v-for="review in admin.reviews" :key="review.id" class="list-card ledger-card">
          <StatusBadge :status="review.review_status" />
          <div>
            <h3>{{ datasetTitle(review.dataset_id) }}</h3>
            <p>{{ review.review_comment || review.publish_comment || '无审核备注' }}</p>
            <div class="meta-line">
              <span>{{ review.dataset_id }}</span>
              <span>分析 {{ review.analysis_id || '-' }}</span>
              <span>审核人 {{ review.reviewer_id || '-' }}</span>
            </div>
          </div>
          <span>{{ dateTime(review.reviewed_at || review.published_at || review.create_date) }}</span>
        </article>
      </div>
    </main>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import EmptyState from "@/components/EmptyState.vue";
import LoadingState from "@/components/LoadingState.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import { useAdminStore } from "@/stores/admin";
import { dateTime } from "@/utils/format";

const admin = useAdminStore();
const activeStatus = ref<string | undefined>();
const loading = ref(false);
const filters = [
  { value: undefined, label: "全部" },
  { value: "approved", label: "已通过" },
  { value: "published", label: "已发布" },
  { value: "rejected", label: "已拒绝" },
  { value: "archived", label: "已归档" }
];
const datasetMap = computed(() => new Map(admin.datasets.map((item) => [item.id, item.title])));

function datasetTitle(datasetId: string) {
  return datasetMap.value.get(datasetId) || datasetId;
}

async function load() {
  loading.value = true;
  try {
    await Promise.all([admin.loadDatasets(), admin.loadReviews({ review_status: activeStatus.value })]);
  } finally {
    loading.value = false;
  }
}

function setStatus(status?: string) {
  activeStatus.value = status;
  load();
}

onMounted(load);
</script>
