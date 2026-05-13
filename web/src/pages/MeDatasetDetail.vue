<template>
  <section class="detail-layout page-grid">
    <template v-if="item">
      <header class="detail-hero">
        <RouterLink class="inline-link" to="/me">返回我的数据</RouterLink>
        <div>
          <span class="eyebrow">AUTHORIZED / {{ item.dataset.source_format?.toUpperCase() }}</span>
          <h1>{{ item.dataset.title }}</h1>
          <p>{{ item.profile?.public_summary || item.dataset.description }}</p>
        </div>
      </header>

      <aside class="detail-side">
        <MetricTile label="授权状态" :value="item.grant.grant_status" :caption="item.grant.grant_method" intense />
        <button class="icon-text full" type="button" @click="ui.openCopilot('me-detail', item.dataset.id)">询问授权内容</button>
        <div class="chip-row">
          <button v-for="format in formats" :key="format" @click="exportNow(format)">{{ format.toUpperCase() }}</button>
        </div>
      </aside>

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
    </template>
    <EmptyState v-else title="未找到授权数据" description="该数据不在你的授权空间中。" />
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useRoute } from "vue-router";

import EmptyState from "@/components/EmptyState.vue";
import MetricTile from "@/components/MetricTile.vue";
import { useMeStore } from "@/stores/me";
import { useUiStore } from "@/stores/ui";
import { governedMetadataRows } from "@/utils/datasetMetadata";
import { normalizePublicStatistics } from "@/utils/statistics";

const me = useMeStore();
const ui = useUiStore();
const route = useRoute();
const id = computed(() => String(route.params.id));
const item = computed(() => me.datasets.find((entry) => entry.dataset.id === id.value));
const stats = computed(() => normalizePublicStatistics(item.value?.profile?.public_statistics));
const formats = computed(() => item.value?.profile?.allowed_export_formats?.length ? item.value.profile.allowed_export_formats : ["json", "csv"]);
const metadataRows = computed(() => governedMetadataRows(item.value?.dataset));

async function exportNow(format: string) {
  await me.requestExport(id.value, format);
  await me.loadExports(id.value);
}

onMounted(async () => {
  ui.setContext("me-detail", id.value);
  await me.loadDatasets();
});
</script>
