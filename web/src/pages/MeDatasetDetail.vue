<template>
  <section class="detail-layout page-grid">
    <template v-if="item">
      <div class="detail-content">
        <header class="detail-hero">
          <RouterLink class="back-link" to="/me"><ArrowLeft :size="16" />返回我的数据</RouterLink>
          <div>
            <span class="eyebrow">AUTHORIZED / {{ item.dataset.source_format?.toUpperCase() }}</span>
            <h1>{{ item.dataset.title }}</h1>
            <p>{{ item.profile?.public_summary || item.dataset.description }}</p>
          </div>
        </header>

        <main class="dossier-main">
          <section class="dossier-band">
            <MetricTile v-for="tile in stats.tiles" :key="tile.label" :label="tile.label" :value="tile.value" :caption="tile.caption" />
          </section>
          <section class="analysis-panel">
            <h2>授权说明</h2>
            <div class="narrative-grid">
              <article><strong>处理摘要</strong><p>{{ item.profile?.processing_summary || "暂无" }}</p></article>
              <article><strong>清洗摘要</strong><p>{{ item.profile?.cleaning_summary || "暂无" }}</p></article>
              <article><strong>标签</strong><p>{{ item.tags?.join(" / ") || "暂无标签" }}</p></article>
            </div>
          </section>

          <section v-if="metadataRows.length" class="analysis-panel">
            <h2>治理与使用边界</h2>
            <div class="metadata-grid">
              <article v-for="row in metadataRows" :key="row.label">
                <span>{{ row.label }}</span>
                <strong>{{ row.value }}</strong>
              </article>
            </div>
          </section>
        </main>
      </div>

      <aside class="detail-side">
        <MetricTile label="授权状态" :value="item.grant.grant_status" :caption="item.grant.grant_method" intense />
        <section class="export-panel">
          <div>
            <span class="eyebrow">EXPORT</span>
            <h2>数据导出</h2>
            <p>选择需要的目标格式，系统会创建导出任务并在任务完成后提供下载。</p>
          </div>
          <div class="export-format-list">
            <button v-for="format in formats" :key="format" type="button" @click="requestExport(format)">
              <FileDown :size="18" />
              <span>{{ format.toUpperCase() }}</span>
              <em>{{ exportCaption(format) }}</em>
            </button>
          </div>
          <RouterLink class="inline-link" to="/me/exports">查看导出任务</RouterLink>
        </section>
        <button class="icon-text full" type="button" @click="ui.openCopilot('me-detail', item.dataset.id)"><MessageSquareText :size="16" />询问授权内容</button>
      </aside>
    </template>
    <EmptyState v-else title="未找到授权数据" description="该数据不在你的授权空间中。" />
    <ConfirmDialog
      :open="Boolean(selectedFormat)"
      title="导出授权数据"
      :description="`将创建 ${selectedFormat?.toUpperCase() || ''} 格式导出任务，完成后可在导出任务页下载。`"
      confirm-label="确认导出"
      :busy="exporting"
      @close="selectedFormat = ''"
      @confirm="confirmExport"
    />
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ArrowLeft, FileDown, MessageSquareText } from "lucide-vue-next";

import ConfirmDialog from "@/components/ConfirmDialog.vue";
import EmptyState from "@/components/EmptyState.vue";
import MetricTile from "@/components/MetricTile.vue";
import { useMeStore } from "@/stores/me";
import { useUiStore } from "@/stores/ui";
import { governedMetadataRows } from "@/utils/datasetMetadata";
import { normalizePublicStatistics } from "@/utils/statistics";

const me = useMeStore();
const ui = useUiStore();
const route = useRoute();
const router = useRouter();
const selectedFormat = ref("");
const exporting = ref(false);
const id = computed(() => String(route.params.id));
const item = computed(() => me.datasets.find((entry) => entry.dataset.id === id.value));
const stats = computed(() => normalizePublicStatistics(item.value?.profile?.public_statistics));
const formats = computed(() => item.value?.profile?.allowed_export_formats?.length ? item.value.profile.allowed_export_formats : ["json", "csv"]);
const metadataRows = computed(() => governedMetadataRows(item.value?.dataset));

function requestExport(format: string) {
  selectedFormat.value = format;
}

function exportCaption(format: string) {
  const labels: Record<string, string> = {
    csv: "表格分析",
    json: "接口集成",
    xlsx: "办公处理",
    pdf: "阅读归档",
    txt: "轻量文本"
  };
  return labels[format.toLowerCase()] || "按授权生成";
}

async function confirmExport() {
  if (!selectedFormat.value) return;
  exporting.value = true;
  try {
    await me.requestExport(id.value, selectedFormat.value);
    await me.loadExports(id.value);
    selectedFormat.value = "";
    router.push("/me/exports");
  } finally {
    exporting.value = false;
  }
}

onMounted(async () => {
  ui.setContext("me-detail", id.value);
  await me.loadDatasets();
});
</script>
