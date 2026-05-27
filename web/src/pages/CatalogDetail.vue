<template>
  <section class="detail-layout page-grid">
    <LoadingState v-if="catalog.loading" />
    <template v-else-if="item">
      <header class="detail-hero">
        <RouterLink class="back-link" to="/catalog"><ArrowLeft :size="16" />返回数据市场</RouterLink>
        <div>
          <span class="eyebrow">{{ item.dataset.source_format?.toUpperCase() }} / {{ stats.representation }}</span>
          <h1>{{ item.dataset.title }}</h1>
          <p>{{ item.profile?.public_summary || item.dataset.description || "该数据资产暂无公开摘要。" }}</p>
        </div>
        <button class="primary-action" type="button" :disabled="acquiring" @click="confirmOpen = true">{{ acquiring ? "获取中..." : "获取数据" }}</button>
      </header>

      <aside class="detail-side">
        <StatusBadge :status="item.dataset.status" />
        <MetricTile label="文件体积" :value="stats.fileSize" :caption="item.dataset.content_type || stats.contentType" />
        <MetricTile label="导出格式" :value="formats" caption="后端授权后可生成" />
        <button class="icon-text full" type="button" @click="ui.openCopilot('catalog-detail', item.dataset.id)"><MessageSquareText :size="16" />询问该资产</button>
      </aside>

      <main class="dossier-main">
        <section class="dossier-band">
          <MetricTile v-for="tile in stats.tiles" :key="tile.label" :label="tile.label" :value="tile.value" :caption="tile.caption" intense />
        </section>

        <section class="analysis-panel">
          <h2>清洗与处理说明</h2>
          <div class="narrative-grid">
            <article><strong>处理摘要</strong><p>{{ item.profile?.processing_summary || "等待分析任务生成处理摘要。" }}</p></article>
            <article><strong>清洗摘要</strong><p>{{ item.profile?.cleaning_summary || "暂无清洗动作记录。" }}</p></article>
            <article><strong>风险摘要</strong><p>{{ item.profile?.risk_summary || "未发现公开风险摘要。" }}</p></article>
          </div>
        </section>

        <section v-if="metadataRows.length" class="analysis-panel">
          <h2>资产登记信息</h2>
          <div class="metadata-grid">
            <article v-for="row in metadataRows" :key="row.label">
              <span>{{ row.label }}</span>
              <strong>{{ row.value }}</strong>
            </article>
          </div>
        </section>

        <section v-if="stats.fields.length" class="analysis-panel">
          <h2>字段画像</h2>
          <div class="field-table">
            <div class="field-row head"><span>字段</span><span>类型</span><span>缺失率</span><span>唯一值</span></div>
            <div v-for="field in stats.fields" :key="field.name" class="field-row">
              <span><strong>{{ field.name }}</strong><em>{{ field.normalizedName }}</em></span>
              <span>{{ field.type }}</span>
              <span>{{ (field.nullRatio * 100).toFixed(1) }}%</span>
              <span>{{ field.uniqueCount }}</span>
            </div>
          </div>
        </section>

        <section v-else-if="stats.structure.length" class="dossier-band compact">
          <MetricTile v-for="tile in stats.structure" :key="tile.label" :label="tile.label" :value="tile.value" :caption="tile.caption" />
        </section>

        <section v-if="stats.fallback" class="analysis-panel">
          <h2>原始统计</h2>
          <pre>{{ JSON.stringify(stats.raw, null, 2) }}</pre>
        </section>
      </main>
    </template>
    <section v-else class="not-found page-grid span-all">
      <div>
        <span class="eyebrow">DATASET DOSSIER</span>
        <h1>数据资产暂不可用。</h1>
        <p>{{ catalog.error || "该公开数据集可能尚未发布，或已被归档。" }}</p>
        <RouterLink class="primary-action" to="/catalog">返回数据市场</RouterLink>
      </div>
    </section>
    <ConfirmDialog
      :open="confirmOpen"
      title="获取数据授权"
      description="确认后系统会为你创建该数据资产的访问授权，并跳转到我的数据详情页。"
      confirm-label="确认获取"
      :busy="acquiring"
      @close="confirmOpen = false"
      @confirm="acquire"
    />
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ArrowLeft, MessageSquareText } from "lucide-vue-next";

import ConfirmDialog from "@/components/ConfirmDialog.vue";
import LoadingState from "@/components/LoadingState.vue";
import MetricTile from "@/components/MetricTile.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import { normalizePublicStatistics } from "@/utils/statistics";
import { publicMetadataRows } from "@/utils/datasetMetadata";
import { useCatalogStore } from "@/stores/catalog";
import { useUiStore } from "@/stores/ui";

const route = useRoute();
const router = useRouter();
const catalog = useCatalogStore();
const ui = useUiStore();
const confirmOpen = ref(false);
const acquiring = ref(false);
const item = computed(() => catalog.detail);
const stats = computed(() => normalizePublicStatistics(item.value?.profile?.public_statistics));
const formats = computed(() => item.value?.profile?.allowed_export_formats?.join(" / ") || "按权限开放");
const metadataRows = computed(() => publicMetadataRows(item.value?.dataset));

async function acquire() {
  if (!item.value) return;
  acquiring.value = true;
  try {
    await catalog.acquire(item.value.dataset.id);
    confirmOpen.value = false;
    router.push(`/me/datasets/${item.value.dataset.id}`);
  } finally {
    acquiring.value = false;
  }
}

onMounted(async () => {
  const id = String(route.params.id);
  ui.setContext("catalog-detail", id);
  await catalog.loadDetail(id);
});
</script>
