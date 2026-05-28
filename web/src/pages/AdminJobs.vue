<template>
  <section class="ops-layout page-grid">
    <header class="section-header span-all">
      <div>
        <RouterLink class="back-link" to="/admin"><ArrowLeft :size="16" />返回管理后台</RouterLink>
        <span class="eyebrow">ANALYSIS JOBS</span>
        <h1>分析任务</h1>
      </div>
      <div class="chip-row">
        <button v-for="status in filters" :key="status.value || 'all'" :class="{ active: activeStatus === status.value }" @click="setStatus(status.value)">
          {{ status.label }}
        </button>
      </div>
    </header>
    <main class="ops-board span-all">
      <LoadingState v-if="loading" text="正在加载分析任务..." />
      <EmptyState v-else-if="!admin.jobs.length" title="暂无分析任务" description="在审核队列中触发分析后会生成任务。" />
      <div v-else class="asset-list job-list">
        <article v-for="job in admin.jobs" :key="job.id" class="list-card job-card">
          <StatusBadge :status="job.job_status" />
          <div>
            <h3>{{ datasetTitle(job.dataset_id) }}</h3>
            <p>{{ job.current_stage || job.error_message || '等待调度' }}</p>
            <div class="meta-line">
              <span>{{ job.dataset_id }}</span>
              <span>创建 {{ dateTime(job.create_date) }}</span>
              <span v-if="job.started_at">开始 {{ dateTime(job.started_at) }}</span>
              <span v-if="job.finished_at">结束 {{ dateTime(job.finished_at) }}</span>
            </div>
          </div>
          <button :disabled="job.job_status !== 'failed' || busy === job.id" @click="retry(job.id)">
            <RefreshCw :size="15" />{{ busy === job.id ? '排队中' : '重试' }}
          </button>
        </article>
      </div>
    </main>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { ArrowLeft, RefreshCw } from "lucide-vue-next";

import EmptyState from "@/components/EmptyState.vue";
import LoadingState from "@/components/LoadingState.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import { useAdminStore } from "@/stores/admin";
import { dateTime } from "@/utils/format";

const admin = useAdminStore();
const activeStatus = ref<string | undefined>();
const loading = ref(false);
const busy = ref("");
const filters = [
  { value: undefined, label: "全部" },
  { value: "pending", label: "待处理" },
  { value: "running", label: "运行中" },
  { value: "succeeded", label: "已完成" },
  { value: "failed", label: "失败" }
];
const datasetMap = computed(() => new Map(admin.datasets.map((item) => [item.id, item.title])));

function datasetTitle(datasetId: string) {
  return datasetMap.value.get(datasetId) || datasetId;
}

async function load() {
  loading.value = true;
  try {
    await Promise.all([admin.loadDatasets(), admin.loadJobs({ job_status: activeStatus.value })]);
  } finally {
    loading.value = false;
  }
}

function setStatus(status?: string) {
  activeStatus.value = status;
  load();
}

async function retry(id: string) {
  busy.value = id;
  try {
    await admin.retryJob(id);
    await load();
  } finally {
    busy.value = "";
  }
}

onMounted(load);
</script>
