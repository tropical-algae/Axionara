<template>
  <section class="ops-layout review-workbench page-grid">
    <header class="section-header span-all">
      <div>
        <RouterLink class="back-link" to="/admin"><ArrowLeft :size="16" />返回管理后台</RouterLink>
        <span class="eyebrow">REVIEW QUEUE</span>
        <h1>数据审核</h1>
      </div>
      <div class="chip-row">
        <button v-for="status in statusFilters" :key="status.value || 'all'" :class="{ active: filter === status.value }" @click="setStatus(status.value)">
          {{ status.label }}
        </button>
      </div>
    </header>

    <aside class="review-queue">
      <div class="queue-toolbar">
        <label>
          <Search :size="15" />
          <input v-model="keyword" placeholder="搜索标题、机构或文件名" />
        </label>
        <button type="button" @click="refreshAll"><RefreshCw :size="15" />刷新</button>
      </div>

      <LoadingState v-if="admin.loading" text="正在加载审核队列..." />
      <EmptyState v-else-if="!filteredDatasets.length" title="暂无匹配数据" description="调整筛选条件后再查看审核队列。" />
      <div v-else class="review-list">
        <button
          v-for="dataset in filteredDatasets"
          :key="dataset.id"
          type="button"
          class="review-item"
          :class="{ active: selectedId === dataset.id }"
          @click="selectDataset(dataset.id)"
        >
          <StatusBadge :status="dataset.status" />
          <strong>{{ dataset.title }}</strong>
          <span>{{ dataset.source_organization || dataset.original_filename || dataset.id }}</span>
          <em>{{ dataset.source_format?.toUpperCase() }} / {{ bytes(dataset.file_size_bytes) }}</em>
        </button>
      </div>
    </aside>

    <main class="review-detail">
      <EmptyState v-if="!selectedDataset" title="选择数据资产" description="从左侧队列选择一项后查看完整登记信息、分析结果和审核动作。" />
      <template v-else>
        <section class="review-hero-panel">
          <div>
            <StatusBadge :status="selectedDataset.status" />
            <h2>{{ selectedDataset.title }}</h2>
            <p>{{ selectedDataset.description || '提供方未填写数据资产描述。' }}</p>
          </div>
          <div class="review-actions">
            <button v-if="canAnalyze" type="button" :disabled="isBusy('analyze')" @click="runAnalyze">
              <Play :size="16" />{{ isBusy('analyze') ? '排队中...' : '分析' }}
            </button>
            <button v-if="canApprove" type="button" :disabled="isBusy('approve')" @click="approveConfirmOpen = true">
              <CheckCircle2 :size="16" />{{ isBusy('approve') ? '处理中...' : '通过' }}
            </button>
            <button v-if="canPublish" type="button" :disabled="isBusy('publish')" @click="openAction('publish')">
              <Send :size="16" />发布
            </button>
            <button v-if="canReject" type="button" :disabled="isBusy('reject')" @click="openAction('reject')">
              <XCircle :size="16" />拒绝
            </button>
            <button v-if="canArchive" type="button" :disabled="isBusy('archive')" @click="openAction('archive')">
              <Archive :size="16" />归档
            </button>
          </div>
        </section>

        <section class="workflow-panel">
          <article v-for="step in workflow" :key="step.key" :class="step.state">
            <span>{{ step.index }}</span>
            <strong>{{ step.label }}</strong>
            <em>{{ step.caption }}</em>
          </article>
        </section>

        <p v-if="notice" class="inline-notice">{{ notice }}</p>
        <p v-if="error" class="inline-error">{{ error }}</p>

        <section v-if="selectedJob" class="analysis-progress-panel">
          <div>
            <StatusBadge :status="selectedJob.job_status" />
            <strong>分析任务</strong>
            <span>{{ selectedJob.current_stage || selectedJob.error_message || '等待调度' }}</span>
          </div>
          <button v-if="selectedJob.job_status === 'failed'" type="button" :disabled="isBusy('retry')" @click="retryJob(selectedJob.id)">
            <RefreshCw :size="15" />重试
          </button>
        </section>

        <section class="detail-grid">
          <article class="detail-card">
            <h3>登记信息</h3>
            <dl class="metadata-list">
              <div v-for="row in metadataRows" :key="row.label"><dt>{{ row.label }}</dt><dd>{{ row.value }}</dd></div>
            </dl>
          </article>
          <article class="detail-card">
            <h3>文件信息</h3>
            <dl class="metadata-list">
              <div><dt>文件名</dt><dd>{{ selectedDataset.original_filename || '-' }}</dd></div>
              <div><dt>格式</dt><dd>{{ selectedDataset.source_format?.toUpperCase() || '-' }}</dd></div>
              <div><dt>体积</dt><dd>{{ bytes(selectedDataset.file_size_bytes) }}</dd></div>
              <div><dt>内容类型</dt><dd>{{ selectedDataset.content_type || '-' }}</dd></div>
              <div><dt>创建时间</dt><dd>{{ dateTime(selectedDataset.create_date) }}</dd></div>
            </dl>
          </article>
        </section>

        <section class="analysis-panel review-analysis">
          <header>
            <div>
              <h2>分析结果</h2>
              <p>{{ selectedAnalysis ? selectedAnalysis.internal_summary || '分析已完成。' : '尚未生成分析结果。' }}</p>
            </div>
            <button type="button" :disabled="!selectedDataset" @click="loadSelectedContext"><RefreshCw :size="15" />同步结果</button>
          </header>

          <EmptyState v-if="!selectedAnalysis" title="暂无分析结果" description="先触发分析，任务完成后这里会展示结构、质量、风险与导出能力。" />
          <template v-else>
            <div class="dossier-band compact">
              <MetricTile v-for="tile in stats.tiles" :key="tile.label" :label="tile.label" :value="tile.value" :caption="tile.caption" />
            </div>

            <div class="narrative-grid">
              <article><strong>表示类型</strong><p>{{ selectedAnalysis.representation_type || '-' }}</p></article>
              <article><strong>解析状态</strong><p>{{ selectedAnalysis.parser_status || '-' }}</p></article>
              <article><strong>清洗状态</strong><p>{{ selectedAnalysis.cleaning_status || '-' }}</p></article>
              <article><strong>敏感性状态</strong><p>{{ selectedAnalysis.sensitivity_status || '-' }}</p></article>
            </div>

            <div class="review-section-split">
              <article>
                <h3>质量问题</h3>
                <ul v-if="issueItems.length">
                  <li v-for="issue in issueItems" :key="issue.issue_code || issue.summary_public">
                    <strong>{{ issue.severity || 'notice' }}</strong>{{ issue.summary_public || issue.issue_code }}
                  </li>
                </ul>
                <p v-else>未记录需要管理员处理的数据质量问题。</p>
              </article>
              <article>
                <h3>导出能力</h3>
                <div class="tag-row"><span v-for="format in allowedFormats" :key="format">{{ format }}</span></div>
                <p v-if="!allowedFormats.length">暂无可导出格式。</p>
              </article>
              <article>
                <h3>标签建议</h3>
                <div class="tag-row"><span v-for="tag in suggestedTags" :key="tag.slug || tag.name">{{ tag.name || tag.slug }}</span></div>
                <p v-if="!suggestedTags.length">暂无标签建议。</p>
              </article>
            </div>

            <section v-if="stats.fields.length" class="field-table compact-fields">
              <div class="field-row head"><span>字段</span><span>类型</span><span>缺失率</span><span>唯一值</span></div>
              <div v-for="field in stats.fields" :key="field.name" class="field-row">
                <span><strong>{{ field.name }}</strong><em>{{ field.normalizedName }}</em></span>
                <span>{{ field.type }}</span>
                <span>{{ (field.nullRatio * 100).toFixed(1) }}%</span>
                <span>{{ field.uniqueCount }}</span>
              </div>
            </section>
          </template>
        </section>

        <section class="analysis-panel review-ledger-panel">
          <h2>审核记录</h2>
          <EmptyState v-if="!selectedReviews.length" title="暂无审核记录" description="通过、拒绝、发布或归档后会记录在这里。" />
          <div v-else class="review-timeline">
            <article v-for="review in selectedReviews" :key="review.id">
              <StatusBadge :status="review.review_status" />
              <div>
                <strong>{{ review.review_comment || review.publish_comment || '无备注' }}</strong>
                <span>{{ dateTime(review.reviewed_at || review.published_at || review.create_date) }}</span>
              </div>
            </article>
          </div>
        </section>
      </template>
    </main>

    <ConfirmDialog
      :open="approveConfirmOpen"
      title="通过数据审核"
      description="确认后该数据会进入待发布状态，发布前仍不会展示在数据市场中。"
      confirm-label="确认通过"
      :busy="isBusy('approve')"
      @close="approveConfirmOpen = false"
      @confirm="approveNow"
    />

    <Modal :open="Boolean(pendingAction)" :title="actionConfig?.title || '确认操作'" @close="closeAction">
      <form class="review-modal-form" @submit.prevent="submitAction">
        <p>{{ actionConfig?.description }}</p>
        <label>
          备注
          <textarea v-model="actionComment" rows="4" :placeholder="actionConfig?.placeholder" />
        </label>
        <div class="modal-actions">
          <button type="button" @click="closeAction">取消</button>
          <button class="primary-action" type="submit" :disabled="!pendingAction || isBusy(pendingAction)">
            {{ isBusy(pendingAction || '') ? '处理中...' : actionConfig?.label || '确认' }}
          </button>
        </div>
      </form>
    </Modal>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { Archive, ArrowLeft, CheckCircle2, Play, RefreshCw, Search, Send, XCircle } from "lucide-vue-next";

import type { AnalysisJob, DatasetReview } from "@/api/types";
import ConfirmDialog from "@/components/ConfirmDialog.vue";
import EmptyState from "@/components/EmptyState.vue";
import LoadingState from "@/components/LoadingState.vue";
import MetricTile from "@/components/MetricTile.vue";
import Modal from "@/components/Modal.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import { useAdminStore } from "@/stores/admin";
import { governedMetadataRows } from "@/utils/datasetMetadata";
import { bytes, dateTime } from "@/utils/format";
import { normalizePublicStatistics } from "@/utils/statistics";

const admin = useAdminStore();
const filter = ref<string | undefined>();
const keyword = ref("");
const selectedId = ref<string | null>(null);
const selectedJob = ref<AnalysisJob | null>(null);
const selectedReviews = ref<DatasetReview[]>([]);
const busy = ref("");
const notice = ref("");
const error = ref("");
const pendingAction = ref<"reject" | "publish" | "archive" | null>(null);
const approveConfirmOpen = ref(false);
const actionComment = ref("");
let pollTimer: number | undefined;
let contextRequestId = 0;

const statusFilters = [
  { value: undefined, label: "全部" },
  { value: "uploaded", label: "已上传" },
  { value: "processing_review", label: "分析中" },
  { value: "reviewed", label: "待审核" },
  { value: "published", label: "已发布" },
  { value: "rejected", label: "已拒绝" },
  { value: "archived", label: "已归档" }
];

const actionText = {
  reject: { title: "拒绝数据资产", label: "确认拒绝", description: "拒绝后提供方需要重新上传或补充材料。", placeholder: "说明拒绝原因，便于提供方修正。" },
  publish: { title: "发布到数据市场", label: "确认发布", description: "发布后消费者可以在市场中看到公开画像并获取授权。", placeholder: "说明发布范围或市场展示注意事项。" },
  archive: { title: "归档数据资产", label: "确认归档", description: "归档后该资产不再作为活跃市场资产展示。", placeholder: "说明归档原因。" }
};

const filteredDatasets = computed(() => {
  const q = keyword.value.trim().toLowerCase();
  if (!q) return admin.datasets;
  return admin.datasets.filter((item) => `${item.title} ${item.description || ""} ${item.source_organization || ""} ${item.original_filename || ""}`.toLowerCase().includes(q));
});
const selectedDataset = computed(() => admin.datasets.find((item) => item.id === selectedId.value) || null);
const metadataRows = computed(() => governedMetadataRows(selectedDataset.value));
const stats = computed(() => normalizePublicStatistics(selectedAnalysis.value?.statistics));
const selectedAnalysis = computed(() => admin.analysis && admin.analysis.dataset_id === selectedId.value ? admin.analysis : null);
const latestReview = computed(() => selectedReviews.value.find((review) => review.dataset_id === selectedId.value));
const analysisActive = computed(() => ["pending", "running"].includes(selectedJob.value?.job_status || ""));
const canAnalyze = computed(() => ["uploaded", "reviewed", "rejected"].includes(selectedDataset.value?.status || ""));
const reviewApproved = computed(() => ["approved", "published"].includes(latestReview.value?.review_status || ""));
const canApprove = computed(() => selectedDataset.value?.status === "reviewed" && !analysisActive.value && !reviewApproved.value);
const canReject = computed(() => ((selectedDataset.value?.status === "reviewed" && !reviewApproved.value) || selectedJob.value?.job_status === "failed") && !analysisActive.value);
const canPublish = computed(() => selectedDataset.value?.status === "reviewed" && !analysisActive.value && reviewApproved.value);
const canArchive = computed(() => ["published", "rejected"].includes(selectedDataset.value?.status || ""));
const actionConfig = computed(() => pendingAction.value ? actionText[pendingAction.value] : null);
const issueItems = computed(() => arrayItems(selectedAnalysis.value?.issues));
const allowedFormats = computed(() => {
  const caps = selectedAnalysis.value?.export_capabilities || {};
  const value = caps.allowed_formats;
  return Array.isArray(value) ? value.map(String) : [];
});
const suggestedTags = computed(() => arrayItems(selectedAnalysis.value?.suggested_tags));
const workflow = computed(() => buildWorkflow(selectedDataset.value?.status || "", latestReview.value?.review_status));

function arrayItems(value: unknown): Array<Record<string, string>> {
  if (!value || typeof value !== "object" || Array.isArray(value)) return [];
  const items = (value as Record<string, unknown>).items;
  return Array.isArray(items) ? items.filter((item): item is Record<string, string> => Boolean(item && typeof item === "object")) : [];
}

function buildWorkflow(status: string, reviewStatus?: string) {
  const approved = reviewStatus === "approved" || reviewStatus === "published" || status === "published";
  const keys = ["uploaded", "processing_review", "reviewed", "approved", "published"];
  const activeKey = status === "published" ? "published" : approved ? "approved" : status;
  const activeIndex = Math.max(0, keys.indexOf(activeKey));
  const labels = ["已上传", "分析处理中", "待人工审核", "审核通过", "市场发布"];
  const captions = ["完成资产登记", "解析、清洗与画像", "检查风险和授权", "等待发布确认", "消费者可见"];
  return keys.map((key, index) => ({
    key,
    index: String(index + 1).padStart(2, "0"),
    label: labels[index],
    caption: status === "rejected" && index === activeIndex ? "已拒绝" : captions[index],
    state: status === "rejected" && index === 2 ? "failed" : index < activeIndex ? "done" : index === activeIndex ? "active" : "idle"
  }));
}

function isBusy(action: string) {
  return busy.value === action;
}

function setStatus(status?: string) {
  filter.value = status;
  refreshAll();
}

async function refreshAll() {
  await admin.loadDatasets(filter.value);
  if (!selectedId.value || !admin.datasets.some((item) => item.id === selectedId.value)) {
    selectedId.value = admin.datasets[0]?.id || null;
  }
  await loadSelectedContext();
}

async function selectDataset(id: string) {
  selectedId.value = id;
  resetSelectedContext();
  await loadSelectedContext();
}

function resetSelectedContext() {
  stopPolling();
  admin.analysis = null;
  selectedJob.value = null;
  selectedReviews.value = [];
  notice.value = "";
  error.value = "";
}

async function loadSelectedContext() {
  const datasetId = selectedId.value;
  if (!datasetId) return;
  const requestId = ++contextRequestId;
  error.value = "";
  selectedJob.value = null;
  selectedReviews.value = [];
  try {
    await admin.latest(datasetId);
  } catch {
    admin.analysis = null;
  }
  if (requestId !== contextRequestId || selectedId.value !== datasetId) return;
  await admin.loadJobs({ dataset_id: datasetId });
  if (requestId !== contextRequestId || selectedId.value !== datasetId) return;
  selectedJob.value = admin.jobs[0] || null;
  await admin.loadReviews({ dataset_id: datasetId });
  if (requestId !== contextRequestId || selectedId.value !== datasetId) return;
  selectedReviews.value = [...admin.reviews];
  if (selectedJob.value && ["pending", "running"].includes(selectedJob.value.job_status)) {
    startPolling(selectedJob.value.id);
  }
}

async function runAnalyze() {
  if (!selectedDataset.value) return;
  busy.value = "analyze";
  notice.value = "";
  error.value = "";
  try {
    const job = await admin.analyze(selectedDataset.value.id);
    selectedJob.value = job;
    notice.value = "分析任务已排队，正在同步进度。";
    await admin.loadDatasets(filter.value);
    startPolling(job.id);
  } catch (err) {
    error.value = err instanceof Error ? err.message : "分析任务创建失败。";
  } finally {
    busy.value = "";
  }
}

async function retryJob(jobId: string) {
  busy.value = "retry";
  try {
    const job = await admin.retryJob(jobId);
    selectedJob.value = job;
    notice.value = "重试任务已排队。";
    startPolling(job.id);
  } catch (err) {
    error.value = err instanceof Error ? err.message : "重试失败。";
  } finally {
    busy.value = "";
  }
}

function startPolling(jobId: string) {
  stopPolling();
  pollTimer = window.setInterval(async () => {
    try {
      const job = await admin.jobDetail(jobId);
      selectedJob.value = job;
      if (["succeeded", "failed"].includes(job.job_status)) {
        stopPolling();
        await admin.loadDatasets(filter.value);
        await loadSelectedContext();
        notice.value = job.job_status === "succeeded" ? "分析已完成，结果已同步。" : "分析失败，请查看错误后重试。";
      }
    } catch (err) {
      stopPolling();
      error.value = err instanceof Error ? err.message : "任务进度同步失败。";
    }
  }, 1600);
}

function stopPolling() {
  if (pollTimer) window.clearInterval(pollTimer);
  pollTimer = undefined;
}


async function approveNow() {
  if (!selectedDataset.value) return;
  busy.value = "approve";
  notice.value = "";
  error.value = "";
  try {
    await admin.action(selectedDataset.value.id, "approve");
    approveConfirmOpen.value = false;
    notice.value = "审核已通过，下一步可以发布到数据市场。";
    await refreshAll();
  } catch (err) {
    error.value = err instanceof Error ? err.message : "操作失败。";
  } finally {
    busy.value = "";
  }
}

function openAction(action: "reject" | "publish" | "archive") {
  pendingAction.value = action;
  actionComment.value = "";
}

function closeAction() {
  pendingAction.value = null;
  actionComment.value = "";
}

async function submitAction() {
  if (!pendingAction.value || !selectedDataset.value) return;
  const action = pendingAction.value;
  busy.value = action;
  notice.value = "";
  error.value = "";
  try {
    await admin.action(selectedDataset.value.id, action, actionComment.value.trim() || undefined);
    notice.value = `${actionText[action].label}已完成。`;
    closeAction();
    await refreshAll();
  } catch (err) {
    error.value = err instanceof Error ? err.message : "操作失败。";
  } finally {
    busy.value = "";
  }
}

watch(filteredDatasets, (items) => {
  if (!selectedId.value && items[0]) selectedId.value = items[0].id;
});

onMounted(refreshAll);
onBeforeUnmount(stopPolling);
</script>
